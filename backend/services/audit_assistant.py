"""
AI 审计助手：支持 Mock 模式和真实 LLM 调用。

Mock 模式：USE_MOCK_MODE=true（无需 API Key）
真实模式：USE_MOCK_MODE=false（调用 SenseNova / OpenAI 兼容接口）
"""

import os
import json
from dotenv import load_dotenv

load_dotenv()


class AuditAssistant:
    """AI 审计助手，根据 .env 配置自动切换 Mock / 真实模式"""

    def __init__(self):
        self.mock_mode = os.getenv("USE_MOCK_MODE", "true").lower() == "true"
        if not self.mock_mode:
            from openai import OpenAI
            self.client = OpenAI(
                api_key=os.getenv("OPENAI_API_KEY", ""),
                base_url=os.getenv("OPENAI_BASE_URL", "https://token.sensenova.cn/v1"),
            )
            self.model = os.getenv("MODEL_NAME", "sensenova-6.7-flash-lite")
            print(f"✓ [AuditAssistant] 真实 LLM 模式，模型: {self.model}")
        else:
            self.client = None
            print("ℹ [AuditAssistant] Mock 模式")

    def analyze(self, query: str) -> dict:
        if self.mock_mode:
            return self._mock_analyze(query)
        return self._llm_analyze(query)

    def _llm_analyze(self, query: str) -> dict:
        """调用真实大模型"""
        system_prompt = (
            "你是一个企业 IT 资产审计助手。你负责回答关于公司资产、设备、许可证、"
            "部门分配、维护记录等方面的问题。\n\n"
            "当前公司资产概况（供你参考回答）：\n"
            "- 总资产 10 项，总价值约 271300 元\n"
            "- 部门分布：IT部3台(176800元), 开发部1台(32000元), 设计部2台(22200元), "
            "销售一部1台(14000元), 全公司1台(12000元), 市场部1台(7500元), 财务部1台(6800元)\n"
            "- 资产类别：服务器x2, 台式机x2, 显示器x1, 软件许可x2, 网络设备x1, 笔记本x1, 外设x1\n"
            "- 状态：活跃9项，维护中1项(MacBook Pro M3 Max，已持续120天)\n"
            "- 软件许可：Microsoft 365 E5(即将到期), Adobe Creative Cloud(约半年后续订)\n\n"
            "回答要求：\n"
            "1. 简洁专业，用中文回答\n"
            "2. 如果问题适合用图表展示，请在回答末尾附加一个 JSON 块，格式：\n"
            '   {"chart": {"type": "bar", "title": "图表标题", "data": {"labels": [...], "values": [...]}}}\n'
            "3. 如果不需要图表，不要附加 JSON\n"
            "4. 给出实用建议"
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

            # SenseNova 思考模型：content 可能为 None，回答在 reasoning 里
            if not content:
                reasoning = getattr(response.choices[0].message, "reasoning", None)
                if reasoning:
                    content = reasoning
                else:
                    return {
                        "query": query,
                        "answer": "AI 返回了空内容，请重试。",
                        "chart_config": None,
                        "source": "error",
                    }

            # 尝试提取图表配置
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

            return {
                "query": query,
                "answer": answer,
                "chart_config": chart_config,
                "source": "llm",
            }

        except Exception as e:
            return {
                "query": query,
                "answer": f"AI 服务暂时不可用：{str(e)}\n\n已自动降级为离线模式，请稍后重试。",
                "chart_config": None,
                "source": "error",
            }

    def _mock_analyze(self, query: str) -> dict:
        """Mock 模式（原有逻辑）"""
        q = query.lower()

        if any(k in q for k in ["异常", "登录", "活跃", "最近"]):
            return {
                "query": query,
                "answer": (
                    "近7天活跃资产报告\n\n"
                    "共检测到 8 台设备在 48 小时内有维护记录\n"
                    "MacBook Pro M3 Max 处于维护状态，已持续 120 天\n"
                    "Dell PowerEdge R740 于 15 天前执行固件升级，状态正常\n\n"
                    "提醒：Synology DS923+ 上次维护为 300 天前，建议检查备份状态。"
                ),
                "chart_config": None,
                "source": "mock_audit",
            }

        elif any(k in q for k in ["部门", "分布", "分类", "统计", "分配"]):
            return {
                "query": query,
                "answer": (
                    "各部门资产分布\n\n"
                    "IT部: 3 台, 176800 元\n"
                    "市场部: 1 台, 7500 元\n"
                    "设计部: 2 台, 22200 元\n"
                    "开发部: 1 台, 32000 元\n"
                    "销售一部: 1 台, 14000 元\n"
                    "财务部: 1 台, 6800 元\n"
                    "全公司: 1 台, 12000 元\n\n"
                    "总计：10 台资产，合计 271300 元"
                ),
                "chart_config": {
                    "type": "bar",
                    "title": "各部门资产价值对比",
                    "data": {
                        "labels": ["IT部", "开发部", "设计部", "销售部", "全公司", "市场部", "财务部"],
                        "values": [176800, 32000, 22200, 14000, 12000, 7500, 6800],
                    },
                },
                "source": "mock_audit",
            }

        elif any(k in q for k in ["过期", "续订", "到期", "license", "software"]):
            return {
                "query": query,
                "answer": (
                    "许可与合同到期提醒\n\n"
                    "Microsoft 365 E5 - 购买日期 2025-07-21，每年续费一次，即将到期！\n"
                    "Adobe Creative Cloud - 购买日期 2025-12-03，年度订阅，约半年后续订\n\n"
                    "建议：优先处理 Microsoft 365 续订，否则将影响全公司员工邮箱和 Office 使用。"
                ),
                "chart_config": None,
                "source": "mock_audit",
            }

        else:
            return {
                "query": query,
                "answer": (
                    "企业资产管理概览\n\n"
                    "总资产数量：10 项\n"
                    "总资产价值：271300 元\n"
                    "资产类别：服务器x2, 台式机x2, 显示器x1, 软件许可x2, 网络设备x1, 笔记本x1, 外设x1\n"
                    "使用状态：活跃 9 项，维护中 1 项\n"
                    "涉及部门：7 个\n\n"
                    "您可以问我：各部门资产分布 / 最近有哪些异常 / 有哪些许可证快到期了"
                ),
                "chart_config": None,
                "source": "mock_audit",
            }


def run_audit(query: str) -> dict:
    assistant = AuditAssistant()
    return assistant.analyze(query)