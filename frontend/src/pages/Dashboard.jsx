import { useState, useEffect } from 'react'
import { assetAPI, auditAPI } from '../api'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'

const ROLE_LABELS = { admin: '管理员', manager: '经理', viewer: '查看者' }

export default function Dashboard({ user, onLogout }) {
  const [tab, setTab] = useState('assets')
  const [assets, setAssets] = useState([])
  const [loading, setLoading] = useState(true)
  const [chatMessages, setChatMessages] = useState([])
  const [chatInput, setChatInput] = useState('')
  const [chatLoading, setChatLoading] = useState(false)
  const [chartData, setChartData] = useState(null)

  useEffect(() => {
    loadAssets()
  }, [])

  const loadAssets = async () => {
    try {
      const res = await assetAPI.list()
      setAssets(res.data)
    } catch (err) {
      console.error('加载资产失败', err)
    } finally {
      setLoading(false)
    }
  }

  const handleChat = async (e) => {
    e.preventDefault()
    if (!chatInput.trim()) return
    const query = chatInput.trim()
    setChatInput('')
    setChatMessages((prev) => [...prev, { role: 'user', content: query }])
    setChatLoading(true)
    try {
      const res = await auditAPI.chat(query)
      const data = res.data
      setChatMessages((prev) => [...prev, { role: 'assistant', content: data.answer }])
      if (data.chart_config) {
        const labels = data.chart_config.data.labels
        const values = data.chart_config.data.values
        setChartData(labels.map((label, i) => ({ name: label, value: values[i] })))
      } else {
        setChartData(null)
      }
    } catch (err) {
      setChatMessages((prev) => [...prev, { role: 'assistant', content: '抱歉，审计助手暂时无法回答。' }])
    } finally {
      setChatLoading(false)
    }
  }

  const totalValue = assets.reduce((sum, a) => sum + (a.value || 0), 0)
  const activeCount = assets.filter((a) => a.status === 'active').length

  return (
    <div className="min-h-screen bg-slate-100 flex">
      {/* 侧边栏 */}
      <aside className="w-64 bg-slate-900 text-white flex flex-col">
        <div className="p-6 border-b border-slate-700">
          <h1 className="text-lg font-bold">资产管理系统</h1>
          <p className="text-sm text-slate-400 mt-1">
            {user.username} · {ROLE_LABELS[user.role] || user.role}
          </p>
        </div>
        <nav className="flex-1 p-4 space-y-2">
          <button
            onClick={() => setTab('assets')}
            className={`w-full text-left px-4 py-2.5 rounded-lg transition ${tab === 'assets' ? 'bg-blue-600 text-white' : 'text-slate-300 hover:bg-slate-800'}`}
          >
            资产列表
          </button>
          <button
            onClick={() => setTab('audit')}
            className={`w-full text-left px-4 py-2.5 rounded-lg transition ${tab === 'audit' ? 'bg-blue-600 text-white' : 'text-slate-300 hover:bg-slate-800'}`}
          >
            AI 审计助手
          </button>
          {(user.role === 'admin' || user.role === 'manager') && (
            <button
              onClick={() => setTab('stats')}
              className={`w-full text-left px-4 py-2.5 rounded-lg transition ${tab === 'stats' ? 'bg-blue-600 text-white' : 'text-slate-300 hover:bg-slate-800'}`}
            >
              统计概览
            </button>
          )}
        </nav>
        <div className="p-4 border-t border-slate-700">
          <button onClick={onLogout} className="w-full text-left px-4 py-2.5 rounded-lg text-red-400 hover:bg-slate-800 transition">
            退出登录
          </button>
        </div>
      </aside>

      {/* 主内容区 */}
      <main className="flex-1 p-8 overflow-auto">
        {tab === 'assets' && (
          <div>
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-2xl font-bold text-slate-800">资产列表</h2>
              <div className="flex gap-4 text-sm text-slate-500">
                <span>共 {assets.length} 项</span>
                <span>活跃 {activeCount} 项</span>
                <span>总价值 ¥{totalValue.toLocaleString()}</span>
              </div>
            </div>

            {loading ? (
              <p className="text-slate-500">加载中...</p>
            ) : (
              <div className="bg-white rounded-xl shadow overflow-hidden">
                <table className="w-full text-sm">
                  <thead className="bg-slate-50 text-slate-600">
                    <tr>
                      <th className="px-4 py-3 text-left">名称</th>
                      <th className="px-4 py-3 text-left">类别</th>
                      <th className="px-4 py-3 text-left">部门</th>
                      <th className="px-4 py-3 text-left">状态</th>
                      <th className="px-4 py-3 text-right">价值(¥)</th>
                      <th className="px-4 py-3 text-left">序列号</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-100">
                    {assets.map((asset) => (
                      <tr key={asset.id} className="hover:bg-slate-50">
                        <td className="px-4 py-3 font-medium text-slate-800">{asset.name}</td>
                        <td className="px-4 py-3">
                          <span className="px-2 py-1 bg-blue-50 text-blue-700 rounded text-xs">{asset.category}</span>
                        </td>
                        <td className="px-4 py-3 text-slate-600">{asset.department}</td>
                        <td className="px-4 py-3">
                          <span className={`px-2 py-1 rounded text-xs ${asset.status === 'active' ? 'bg-green-50 text-green-700' : 'bg-yellow-50 text-yellow-700'}`}>
                            {asset.status === 'active' ? '活跃' : '维护中'}
                          </span>
                        </td>
                        <td className="px-4 py-3 text-right text-slate-700">{asset.value?.toLocaleString()}</td>
                        <td className="px-4 py-3 text-slate-400 text-xs">{asset.serial_number}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        )}

        {tab === 'audit' && (
          <div className="max-w-3xl">
            <h2 className="text-2xl font-bold text-slate-800 mb-6">AI 审计助手</h2>

            {chartData && (
              <div className="bg-white rounded-xl shadow p-6 mb-6">
                <ResponsiveContainer width="100%" height={250}>
                  <BarChart data={chartData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="name" fontSize={12} />
                    <YAxis fontSize={12} />
                    <Tooltip />
                    <Bar dataKey="value" fill="#3b82f6" radius={[4, 4, 0, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            )}

            <div className="bg-white rounded-xl shadow p-6 space-y-4 mb-4 max-h-96 overflow-auto">
              {chatMessages.length === 0 && (
                <p className="text-slate-400 text-center py-8">
                  试着问我："各部门资产分布"、"最近有哪些异常"、"有哪些许可证快到期了"
                </p>
              )}
              {chatMessages.map((msg, i) => (
                <div key={i} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                  <div className={`max-w-[80%] px-4 py-3 rounded-xl text-sm whitespace-pre-wrap ${msg.role === 'user' ? 'bg-blue-600 text-white' : 'bg-slate-100 text-slate-800'}`}>
                    {msg.content}
                  </div>
                </div>
              ))}
              {chatLoading && <p className="text-slate-400 text-sm">审计助手思考中...</p>}
            </div>

            <form onSubmit={handleChat} className="flex gap-2">
              <input
                type="text"
                value={chatInput}
                onChange={(e) => setChatInput(e.target.value)}
                placeholder="输入审计问题..."
                className="flex-1 px-4 py-2.5 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none"
              />
              <button type="submit" disabled={chatLoading} className="px-6 py-2.5 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 disabled:opacity-50">
                发送
              </button>
            </form>
          </div>
        )}

        {tab === 'stats' && (
          <div>
            <h2 className="text-2xl font-bold text-slate-800 mb-6">统计概览</h2>
            <div className="grid grid-cols-3 gap-6">
              <div className="bg-white rounded-xl shadow p-6">
                <p className="text-slate-500 text-sm">总资产数</p>
                <p className="text-3xl font-bold text-slate-800 mt-2">{assets.length}</p>
              </div>
              <div className="bg-white rounded-xl shadow p-6">
                <p className="text-slate-500 text-sm">活跃资产</p>
                <p className="text-3xl font-bold text-green-600 mt-2">{activeCount}</p>
              </div>
              <div className="bg-white rounded-xl shadow p-6">
                <p className="text-slate-500 text-sm">总价值</p>
                <p className="text-3xl font-bold text-blue-600 mt-2">¥{totalValue.toLocaleString()}</p>
              </div>
            </div>
          </div>
        )}
      </main>
    </div>
  )
}