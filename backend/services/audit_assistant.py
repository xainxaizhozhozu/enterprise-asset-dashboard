"""AI 审计助手：通过 Function Calling 按需查询资产数据，支持 Mock 和 LLM 双模式。
Mock: USE_MOCK_MODE=true  真实: USE_MOCK_MODE=false (SenseNova/OpenAI)
"""

import os
import json
import asyncio
import logging
from dotenv import load_dotenv
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from models import Asset

load_dotenv()
logger = logging.getLogger(__name__)


# ─── Function Calling 工具定义 ───

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_asset_summary",
            "description": "获取资产总体统计信息，包括总数、总价值、平均价值等",
            "parameters": {"type": "object", "properties": {}, "required": []},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_assets_by_department",
            "description": "按部门查询资产数量和总价值",
            "parameters": {
                "type": "object",
                "properties": {
                    "department": {
                        "type": "string",
                        "description": "部门名称，如：IT部、开发部、设计部。传空字符串则返回所有部门的统计",
                    }
                },
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_assets_by_category",
            "description": "按类别查询资产统计信息",
            "parameters": {
                "type": "object",
                "properties": {
                    "category": {
                        "type": "string",
                        "description": "资产类别: server, desktop, laptop, monitor, network, software, peripheral",
                    }
                },
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_assets_by_status",
            "description": "按状态查询资产，可用于查找维护中或异常设备",
            "parameters": {
                "type": "object",
                "properties": {
                    "status": {
                        "type": "string",
                        "description": "资产状态: active, inactive, maintenance, disposed",
                    }
                },
                "required": [],
            },
        },
    },
]


# ─── 数据库查询函数 ───

async def _query_asset_summary(session: AsyncSession) -> dict:
    result = await session.execute(
        select(
            func.count(Asset.id).label("total_count"),
            func.sum(Asset.value).label("total_value"),
            func.avg(Asset.value).label("avg_value"),
            func.count(func.distinct(Asset.category)).label("category_count"),
            func.count(func.distinct(Asset.department)).label("dept_count"),
        )
    )
    row = result.one()
    return {
        "total_count": row.total_count,
        "total_value": round(row.total_value or 0, 2),
        "avg_value": round(row.avg_value or 0, 2),
        "category_count": row.category_count,
        "dept_count": row.dept_count,
    }


async def _query_by_department(session: AsyncSession, department: str = "") -> list:
    if department:
        stmt = select(Asset).where(Asset.department == department)
        result = await session.execute(stmt)
        assets = result.scalars().all()
        return [
            {"name": a.name, "category": a.category, "value": a.value, "status": a.status}
            for a in assets
        ]
    else:
        stmt = select(
            Asset.department,
            func.count(Asset.id).label("count"),
            func.sum(Asset.value).label("total_value"),
        ).group_by(Asset.department).order_by(func.sum(Asset.value).desc())
        result = await session.execute(stmt)
        return [
            {"department": r.department, "count": r.count, "total_value": round(r.total_value or 0, 2)}
            for r in result.all()
        ]


async def _query_by_category(session: AsyncSession, category: str = "") -> list:
    if category:
        stmt = select(Asset).where(Asset.category == category)
        result = await session.execute(stmt)
        assets = result.scalars().all()
        return [
            {"name": a.name, "department": a.department, "value": a.value, "status": a.status}
            for a in assets
        ]
    else:
        stmt = select(
            Asset.category,
            func.count(Asset.id).label("count"),
            func.sum(Asset.value).label("total_value"),
        ).group_by(Asset.category).order_by(func.sum(Asset.value).desc())
        result = await session.execute(stmt)
        return [
            {"category": r.category, "count": r.count, "total_value": round(r.total_value or 0, 2)}
            for r in result.all()
        ]


async def _query_by_status(session: AsyncSession, status_filter: str = "") -> list:
    if status_filter:
        stmt = select(Asset).where(Asset.status == status_filter)
    else:
        stmt = select(Asset)
    result = await session.execute(stmt)
    assets = result.scalars().all()
    return [
        {"name": a.name, "category": a.category, "department": a.department, "value": a.value, "status": a.status}
        for a in assets
    ]


# ─── 工具分发 ───

TOOL_DISPATCH = {
    "get_asset_summary": lambda args, session: _query_asset_summary(session),
    "get_assets_by_department": lambda args, session: _query_by_department(session, args.get("department", "")),
    "get_assets_by_category": lambda args, session: _query_by_category(session, args.get("category", "")),
    "get_assets_by_status": lambda args, session: _query_by_status(session, args.get("status", "")),
}


# ─── LLM 模式（Function Calling）───

async def _llm_analyze(query: str, session: AsyncSession) -> dict:
    from openai import AsyncOpenAI, APITimeoutError, RateLimitError, APIConnectionError

    api_key = os.getenv("OPENAI_API_KEY", "")
    if not api_key or api_key == "your-api-key-here":
        return {"query": query, "answer": "AI 服务未配置，请联系管理员设置 OPENAI_API_KEY。", "chart_config": None, "source": "error"}

    client = AsyncOpenAI(
        api_key=api_key,
        base_url=os.getenv("OPENAI_BASE_URL", "https://token.sensenova.cn/v1"),
        timeout=30.0,
    )
    model = os.getenv("MODEL_NAME", "deepseek-v4-flash")

    system_prompt = (
        "你是企业 IT 资产审计助手。你可以调用工具查询资产数据来回答用户问题。\n"
        "回答要求：简洁专业，中文。如果数据适合图表展示，在回答末尾附加 JSON：\n"
        '{"chart": {"type": "bar", "title": "...", "data": {"labels": [...], "values": [...]}}}'
    )

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": query},
    ]

    # 第一轮：带 tools 让模型决定调哪个函数
    try:
        response = await client.chat.completions.create(
            model=model,
            messages=messages,
            tools=TOOLS,
            tool_choice="auto",
            temperature=0.3,
            max_tokens=4096,
        )
    except APITimeoutError:
        logger.warning("LLM API timeout for query: %s", query[:100])
        return {"query": query, "answer": "AI 响应超时，请稍后重试。", "chart_config": None, "source": "error"}
    except RateLimitError:
        logger.warning("LLM rate limit hit")
        return {"query": query, "answer": "AI 服务请求过于频繁，请稍后再试。", "chart_config": None, "source": "error"}
    except APIConnectionError:
        logger.error("LLM API connection failed")
        return {"query": query, "answer": "无法连接 AI 服务，请检查网络配置。", "chart_config": None, "source": "error"}

    msg = response.choices[0].message

    # 如果模型没调用工具，直接返回文本
    if not msg.tool_calls:
        content = msg.content or ""
        if not content:
            reasoning = getattr(msg, "reasoning", None)
            content = reasoning or "AI 返回空内容，请重试。"
        chart_config = _extract_chart(content)
        return {"query": query, "answer": chart_config[0], "chart_config": chart_config[1], "source": "llm"}

    # 处理工具调用
    messages.append(msg)

    for tool_call in msg.tool_calls:
        func_name = tool_call.function.name
        try:
            func_args = json.loads(tool_call.function.arguments) if tool_call.function.arguments else {}
        except json.JSONDecodeError:
            func_args = {}

        logger.info(f"[Audit] tool_call: {func_name}({func_args})")

        handler = TOOL_DISPATCH.get(func_name)
        if handler:
            try:
                result_data = await handler(func_args, session)
            except Exception as e:
                logger.error("Tool %s failed: %s", func_name, e)
                result_data = {"error": f"查询执行失败"}
        else:
            result_data = {"error": f"未知工具: {func_name}"}

        messages.append({
            "role": "tool",
            "tool_call_id": tool_call.id,
            "content": json.dumps(result_data, ensure_ascii=False),
        })

    # 第二轮：把工具结果给模型，生成最终回答
    try:
        response2 = await client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=0.3,
            max_tokens=4096,
        )
    except (APITimeoutError, RateLimitError, APIConnectionError) as e:
        logger.warning("LLM second call failed: %s", type(e).__name__)
        # 有工具结果，可以返回一个简化的回答
        return {"query": query, "answer": "数据已查询，但 AI 总结生成失败，请稍后重试。", "chart_config": None, "source": "error"}

    content = response2.choices[0].message.content or ""
    if not content:
        reasoning = getattr(response2.choices[0].message, "reasoning", None)
        content = reasoning or "AI 返回空内容，请重试。"

    chart_config = _extract_chart(content)
    return {"query": query, "answer": chart_config[0], "chart_config": chart_config[1], "source": "llm"}


def _extract_chart(content: str) -> tuple:
    """从 LLM 回答中提取图表 JSON"""
    chart_config = None
    answer = content
    if "{" in content and '"chart"' in content:
        try:
            start = content.index('{"chart"')
            end = content.rindex("}") + 1
            chart_json = json.loads(content[start:end])
            chart_config = chart_json.get("chart")
            answer = content[:start].strip()
        except (ValueError, json.JSONDecodeError):
            pass
    return answer, chart_config


# ─── Mock 模式 ───

def _mock_analyze(query: str) -> dict:
    q = query.lower()

    if any(k in q for k in ["异常", "登录", "活跃", "最近"]):
        return {
            "query": query,
            "answer": "近7天活跃资产报告\n\n共检测到 8 台设备在 48 小时内有维护记录\nMacBook Pro M3 Max 处于维护状态\nDell PowerEdge R740 于 15 天前执行固件升级\n\n提醒：Synology DS923+ 上次维护为 300 天前，建议检查备份状态。",
            "chart_config": None, "source": "mock_audit",
        }
    elif any(k in q for k in ["部门", "分布", "分类", "统计", "分配"]):
        return {
            "query": query,
            "answer": "各部门资产分布\n\nIT部: 3 台, 176800 元\n开发部: 2 台, 53999 元\n设计部: 3 台, 26799 元\n销售部: 1 台, 14000 元\n市场部: 2 台, 18499 元\n财务部: 2 台, 13000 元\n\n总计：20 台资产",
            "chart_config": {
                "type": "bar", "title": "各部门资产价值对比",
                "data": {
                    "labels": ["IT部", "开发部", "设计部", "销售部", "市场部", "财务部"],
                    "values": [176800, 53999, 26799, 14000, 18499, 13000],
                },
            }, "source": "mock_audit",
        }
    elif any(k in q for k in ["过期", "续订", "到期", "license", "software"]):
        return {
            "query": query,
            "answer": "许可到期提醒\n\nMicrosoft 365 E5 - 年度订阅，即将到期\nAdobe Creative Cloud - 年度订阅，约半年后续订\n\n建议：优先处理 Microsoft 365 续订。",
            "chart_config": None, "source": "mock_audit",
        }
    else:
        return {
            "query": query,
            "answer": "企业资产管理概览\n\n总资产：20 项\n类别：服务器、台式机、笔记本、显示器、网络设备、软件许可、外设\n状态：大部分活跃\n部门：9 个\n\n可以问：各部门分布 / 最近异常 / 许可证到期",
            "chart_config": None, "source": "mock_audit",
        }


# ─── 入口 ───

async def run_audit(query: str, session: AsyncSession) -> dict:
    mock_mode = os.getenv("USE_MOCK_MODE", "true").lower() == "true"
    if mock_mode:
        return _mock_analyze(query)
    try:
        return await _llm_analyze(query, session)
    except Exception as e:
        logger.error(f"LLM audit failed: {e}")
        return {"query": query, "answer": f"AI 服务暂时不可用：{str(e)}", "chart_config": None, "source": "error"}
