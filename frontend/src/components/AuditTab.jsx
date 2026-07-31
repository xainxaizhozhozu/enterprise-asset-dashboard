import { useState } from 'react'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'
import { auditAPI } from '../api'

const SUGGESTIONS = ['各部门资产分布', '有哪些需要关注的异常', '资产总览', '哪些许可证快到期了']

export default function AuditTab() {
  const [chatMessages, setChatMessages] = useState([])
  const [chatInput, setChatInput] = useState('')
  const [chatLoading, setChatLoading] = useState(false)
  const [chartData, setChartData] = useState(null)
  const [chartTitle, setChartTitle] = useState('')

  const handleChat = async (e) => {
    e?.preventDefault?.()
    const query = typeof e === 'string' ? e : chatInput.trim()
    if (!query) return
    setChatInput('')
    setChatMessages(prev => [...prev, { role: 'user', content: query }])
    setChatLoading(true)
    try {
      const res = await auditAPI.chat(query)
      const data = res.data
      setChatMessages(prev => [...prev, { role: 'assistant', content: data.answer }])
      if (data.chart_config) {
        const labels = data.chart_config.data.labels
        const values = data.chart_config.data.values
        setChartData(labels.map((label, i) => ({ name: label, value: values[i] })))
        setChartTitle(data.chart_config.title || '')
      } else {
        setChartData(null)
      }
    } catch {
      setChatMessages(prev => [...prev, { role: 'assistant', content: '抱歉，审计助手暂时无法回答，请稍后重试。' }])
    } finally {
      setChatLoading(false)
    }
  }

  // 暴露 handleChat 给父组件（用于快捷操作跳转）
  AuditTab._handleChat = handleChat

  return (
    <div className="max-w-3xl space-y-5">
      <div className="flex items-center gap-3">
        <h2 className="text-xl font-bold text-slate-800">AI 审计助手</h2>
        <span className="px-2.5 py-1 bg-green-100 text-green-700 rounded-full text-xs font-medium">Function Calling</span>
      </div>

      {chartData && (
        <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
          <h3 className="text-sm font-semibold text-slate-700 mb-3">{chartTitle}</h3>
          <ResponsiveContainer width="100%" height={220}>
            <BarChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" fontSize={11} />
              <YAxis fontSize={11} tickFormatter={v => v >= 10000 ? (v / 10000).toFixed(0) + '万' : v} />
              <Tooltip formatter={(v) => ['¥' + v.toLocaleString(), '价值']} />
              <Bar dataKey="value" fill="#8b5cf6" radius={[4, 4, 0, 0]} barSize={32} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      )}

      <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6 space-y-4 min-h-[320px] max-h-[420px] overflow-auto">
        {chatMessages.length === 0 && (
          <div className="text-center py-10">
            <p className="text-slate-400 text-sm mb-4">你好，我是 AI 审计助手，通过按需查询资产数据来回答你的问题。</p>
            <div className="flex flex-wrap justify-center gap-2">
              {SUGGESTIONS.map(q => (
                <button key={q} onClick={() => handleChat(q)} className="px-3 py-1.5 bg-slate-100 text-slate-600 rounded-lg text-xs hover:bg-blue-50 hover:text-blue-600 transition">{q}</button>
              ))}
            </div>
          </div>
        )}
        {chatMessages.map((msg, i) => (
          <div key={i} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
            <div className={`max-w-[80%] px-4 py-3 rounded-2xl text-sm leading-relaxed whitespace-pre-wrap ${msg.role === 'user' ? 'bg-blue-600 text-white rounded-br-md' : 'bg-slate-100 text-slate-800 rounded-bl-md'}`}>
              {msg.content}
            </div>
          </div>
        ))}
        {chatLoading && (
          <div className="flex justify-start">
            <div className="bg-slate-100 px-4 py-3 rounded-2xl rounded-bl-md text-sm text-slate-400">
              <span className="animate-pulse">正在查询资产数据...</span>
            </div>
          </div>
        )}
      </div>

      <form onSubmit={handleChat} className="flex gap-2">
        <input type="text" value={chatInput} onChange={e => setChatInput(e.target.value)} placeholder="输入审计问题，如：各部门资产分布..."
          className="flex-1 px-4 py-2.5 border border-gray-200 rounded-xl text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none" />
        <button type="submit" disabled={chatLoading} className="px-6 py-2.5 bg-blue-600 text-white rounded-xl text-sm font-medium hover:bg-blue-700 disabled:opacity-50 transition shadow-sm">
          发送
        </button>
      </form>
    </div>
  )
}
