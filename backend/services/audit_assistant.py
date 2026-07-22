class AuditAssistant:
    """Mock LLM 模式的 AI 审计助手"""

    def analyze(self, query: str) -> dict:
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