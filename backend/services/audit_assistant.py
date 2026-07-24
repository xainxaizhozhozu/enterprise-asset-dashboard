"""AI 审计助手：支持 Mock 模式和真实 LLM 调用。
Mock: USE_MOCK_MODE=true  真实: USE_MOCK_MODE=false (SenseNova/OpenAI)
"""

import os
import json
import logging
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)


def _build_asset_context() -> str:
    """从数据库读取资产统计信息，注入到 system prompt"""
    # 这里用同步方式读取统计摘要（启动时缓存一次）
    # 实际项目中应该定期刷新或从缓存读
    return (
        "当前公司资产概况：\n"
        "- 总资产约20项，涵盖服务器、台式机、笔记本、显示器、网络设备、软件许可、外设\n"
        "- 涉及部门：IT部、开发部、设计部、销售部、市场部、财务部、产品部、行政部、会议室\n"
        "- 资产状态：大部分活跃，少量维护中\n"
        "- 软件许可：Microsoft 365 E5(年度)、Adobe Creative Cloud(年度)\n"
        "- 注意：具体资产详情请通过 /api/v1/assets/ 接口查询"
    )


class AuditAssistant:
    """AI 审计助手"""

    def __init__(self):
        self.mock_mode = os.getenv("USE_MOCK_MODE", "true").lower() == "true"
        if not self.mock_mode:
            from openai import OpenAI
            self.client = OpenAI(
                api_key=os.getenv("OPENAI_API_KEY", ""),
                base_url=os.getenv("OPENAI_BASE_URL", "https://token.sensenova.cn/v1"),
            )
            self.model = os.getenv("MODEL_NAME", "sensenova-6.7-flash-lite")
            logger.info(f"[AuditAssistant] LLM mode, model={self.model}")
        else:
            self.client = None
            logger.info("[AuditAssistant] mock mode")

    def analyze(self, query: str) -> dict:
        if self.mock_mode:
            return self._mock_analyze(query)
        return self._llm_analyze(query)

    def _llm_analyze(self, query: str) -> dict:
        context = _build_asset_context()
        system_prompt = (
            "你是企业 IT 资产审计助手，负责回答资产、设备、许可证、部门分配等问题。\n\n"
            f"{context}\n\n"
            "回答要求：简洁专业，中文；如果适合图表展示，在末尾附加 JSON："
            '{"chart": {"type": "bar", "title": "...", "data": {"labels": [...], "values": [...]}}}'
        )

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": query},
                ],
                temperature=0.3,
                max_tokens=4096,
            )
            content = response.choices[0].message.content

            # SenseNova 思考模型: content 可能为 None, 答案在 reasoning 里
            if not content:
                reasoning = getattr(response.choices[0].message, "reasoning", None)
                if reasoning:
                    content = reasoning
                else:
                    return {"query": query, "answer": "AI 返回空内容，请重试。", "chart_config": None, "source": "error"}

            # 尝试提取图表 JSON
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

            return {"query": query, "answer": answer, "chart_config": chart_config, "source": "llm"}

        except Exception as e:
            logger.error(f"LLM call failed: {e}")
            return {"query": query, "answer": f"AI 服务暂时不可用：{str(e)}", "chart_config": None, "source": "error"}

    def _mock_analyze(self, query: str) -> dict:
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


def run_audit(query: str) -> dict:
    assistant = AuditAssistant()
    return assistant.analyze(query)
