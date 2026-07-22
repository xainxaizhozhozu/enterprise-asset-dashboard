import { useState, useEffect, useMemo } from 'react'
import { assetAPI, auditAPI } from '../api'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts'

const ROLE_LABELS = { admin: '管理员', manager: '部门经理', viewer: '查看者' }
const CATEGORY_LABELS = { server: '服务器', desktop: '台式机', laptop: '笔记本', monitor: '显示器', network: '网络设备', software: '软件许可', peripheral: '外设' }
const STATUS_MAP = { active: { label: '在用', cls: 'bg-green-100 text-green-700' }, maintenance: { label: '维护中', cls: 'bg-amber-100 text-amber-700' }, retired: { label: '已报废', cls: 'bg-red-100 text-red-600' } }
const COLORS = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#06b6d4', '#ec4899']

export default function Dashboard({ user, onLogout }) {
  const [tab, setTab] = useState('overview')
  const [assets, setAssets] = useState([])
  const [loading, setLoading] = useState(true)
  const [search, setSearch] = useState('')
  const [filterCategory, setFilterCategory] = useState('')
  const [filterStatus, setFilterStatus] = useState('')
  const [chatMessages, setChatMessages] = useState([])
  const [chatInput, setChatInput] = useState('')
  const [chatLoading, setChatLoading] = useState(false)
  const [chartData, setChartData] = useState(null)
  const [chartTitle, setChartTitle] = useState('')

  useEffect(() => { loadAssets() }, [])

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
    e?.preventDefault?.()
    const query = typeof e === 'string' ? e : chatInput.trim()
    if (!query) return
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
        setChartTitle(data.chart_config.title || '')
      } else {
        setChartData(null)
      }
    } catch (err) {
      setChatMessages((prev) => [...prev, { role: 'assistant', content: '抱歉，审计助手暂时无法回答，请稍后重试。' }])
    } finally {
      setChatLoading(false)
    }
  }

  const stats = useMemo(() => {
    const totalValue = assets.reduce((s, a) => s + (a.value || 0), 0)
    const activeCount = assets.filter(a => a.status === 'active').length
    const maintenanceCount = assets.filter(a => a.status === 'maintenance').length
    const departments = [...new Set(assets.map(a => a.department))]
    return { totalValue, activeCount, maintenanceCount, deptCount: departments.length }
  }, [assets])

  const deptData = useMemo(() => {
    const map = {}
    assets.forEach(a => { map[a.department] = (map[a.department] || 0) + (a.value || 0) })
    return Object.entries(map).map(([name, value]) => ({ name, value })).sort((a, b) => b.value - a.value)
  }, [assets])

  const categoryData = useMemo(() => {
    const map = {}
    assets.forEach(a => { const label = CATEGORY_LABELS[a.category] || a.category; map[label] = (map[label] || 0) + 1 })
    return Object.entries(map).map(([name, value]) => ({ name, value }))
  }, [assets])

  const filteredAssets = useMemo(() => {
    return assets.filter(a => {
      if (search && !a.name.toLowerCase().includes(search.toLowerCase()) && !(a.serial_number || '').toLowerCase().includes(search.toLowerCase())) return false
      if (filterCategory && a.category !== filterCategory) return false
      if (filterStatus && a.status !== filterStatus) return false
      return true
    })
  }, [assets, search, filterCategory, filterStatus])

  const navItems = [
    { key: 'overview', label: '总览', icon: '📊' },
    { key: 'assets', label: '资产管理', icon: '💻' },
    { key: 'audit', label: 'AI 审计助手', icon: '🤖' },
  ]

  return (
    <div className="min-h-screen bg-gray-50 flex">
      {/* 侧边栏 */}
      <aside className="w-60 bg-slate-900 text-white flex flex-col fixed h-full">
        <div className="p-5 border-b border-slate-700/50">
          <h1 className="text-base font-bold tracking-wide">企业资产管理平台</h1>
          <div className="flex items-center gap-2 mt-3">
            <div className="w-8 h-8 rounded-full bg-blue-500 flex items-center justify-center text-sm font-bold">
              {user.username[0].toUpperCase()}
            </div>
            <div>
              <p className="text-sm font-medium">{user.username}</p>
              <p className="text-xs text-slate-400">{ROLE_LABELS[user.role] || user.role}</p>
            </div>
          </div>
        </div>
        <nav className="flex-1 p-3 space-y-1">
          {navItems.map(item => (
            <button key={item.key} onClick={() => setTab(item.key)}
              className={`w-full text-left px-4 py-2.5 rounded-lg text-sm transition flex items-center gap-3 ${tab === item.key ? 'bg-blue-600 text-white shadow-lg shadow-blue-600/20' : 'text-slate-300 hover:bg-slate-800 hover:text-white'}`}>
              <span>{item.icon}</span>
              <span>{item.label}</span>
            </button>
          ))}
        </nav>
        <div className="p-3 border-t border-slate-700/50">
          <button onClick={onLogout} className="w-full text-left px-4 py-2.5 rounded-lg text-sm text-red-400 hover:bg-red-500/10 hover:text-red-300 transition">
            退出登录
          </button>
        </div>
      </aside>

      {/* 主内容区 */}
      <main className="flex-1 ml-60 p-8">
        {/* ═══ 总览页 ═══ */}
        {tab === 'overview' && (
          <div className="space-y-6">
            <div className="flex items-center justify-between">
              <h2 className="text-xl font-bold text-slate-800">工作台总览</h2>
              <span className="text-sm text-slate-400">{new Date().toLocaleDateString('zh-CN', { year: 'numeric', month: 'long', day: 'numeric', weekday: 'long' })}</span>
            </div>

            {/* 核心指标卡片 */}
            <div className="grid grid-cols-4 gap-5">
              <div className="bg-white rounded-xl p-5 shadow-sm border border-gray-100">
                <p className="text-sm text-slate-500">资产总数</p>
                <p className="text-3xl font-bold text-slate-800 mt-1">{assets.length}</p>
                <p className="text-xs text-slate-400 mt-2">覆盖 {stats.deptCount} 个部门</p>
              </div>
              <div className="bg-white rounded-xl p-5 shadow-sm border border-gray-100">
                <p className="text-sm text-slate-500">资产总价值</p>
                <p className="text-3xl font-bold text-blue-600 mt-1">{(stats.totalValue / 10000).toFixed(1)}<span className="text-base font-normal"> 万</span></p>
                <p className="text-xs text-slate-400 mt-2">全部在册资产</p>
              </div>
              <div className="bg-white rounded-xl p-5 shadow-sm border border-gray-100">
                <p className="text-sm text-slate-500">在用资产</p>
                <p className="text-3xl font-bold text-green-600 mt-1">{stats.activeCount}</p>
                <p className="text-xs text-green-500 mt-2">占比 {assets.length ? Math.round(stats.activeCount / assets.length * 100) : 0}%</p>
              </div>
              <div className="bg-white rounded-xl p-5 shadow-sm border border-gray-100">
                <p className="text-sm text-slate-500">维护中</p>
                <p className="text-3xl font-bold text-amber-500 mt-1">{stats.maintenanceCount}</p>
                <p className="text-xs text-amber-500 mt-2">需要关注</p>
              </div>
            </div>

            {/* 图表区 */}
            <div className="grid grid-cols-2 gap-6">
              <div className="bg-white rounded-xl p-6 shadow-sm border border-gray-100">
                <h3 className="text-sm font-semibold text-slate-700 mb-4">各部门资产价值分布</h3>
                <ResponsiveContainer width="100%" height={240}>
                  <BarChart data={deptData} layout="vertical" margin={{ left: 20 }}>
                    <CartesianGrid strokeDasharray="3 3" horizontal={false} />
                    <XAxis type="number" fontSize={11} tickFormatter={v => v >= 10000 ? (v / 10000).toFixed(0) + '万' : v} />
                    <YAxis type="category" dataKey="name" fontSize={12} width={70} />
                    <Tooltip formatter={(v) => ['¥' + v.toLocaleString(), '价值']} />
                    <Bar dataKey="value" fill="#3b82f6" radius={[0, 4, 4, 0]} barSize={18} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
              <div className="bg-white rounded-xl p-6 shadow-sm border border-gray-100">
                <h3 className="text-sm font-semibold text-slate-700 mb-4">资产类别构成</h3>
                <ResponsiveContainer width="100%" height={240}>
                  <PieChart>
                    <Pie data={categoryData} dataKey="value" nameKey="name" cx="50%" cy="50%" outerRadius={90} label={({ name, value }) => `${name} ${value}台`} labelLine={true} fontSize={11}>
                      {categoryData.map((_, i) => <Cell key={i} fill={COLORS[i % COLORS.length]} />)}
                    </Pie>
                    <Tooltip formatter={(v) => [v + ' 台', '数量']} />
                  </PieChart>
                </ResponsiveContainer>
              </div>
            </div>

            {/* 快捷入口 */}
            <div className="bg-white rounded-xl p-6 shadow-sm border border-gray-100">
              <h3 className="text-sm font-semibold text-slate-700 mb-3">快捷操作</h3>
              <div className="flex gap-3">
                <button onClick={() => setTab('assets')} className="px-4 py-2 bg-blue-50 text-blue-700 rounded-lg text-sm hover:bg-blue-100 transition">查看全部资产</button>
                <button onClick={() => { setTab('audit'); handleChat('各部门资产分布情况') }} className="px-4 py-2 bg-purple-50 text-purple-700 rounded-lg text-sm hover:bg-purple-100 transition">AI 分析部门分布</button>
                <button onClick={() => { setTab('audit'); handleChat('有哪些需要关注的异常') }} className="px-4 py-2 bg-amber-50 text-amber-700 rounded-lg text-sm hover:bg-amber-100 transition">AI 检查异常</button>
              </div>
            </div>
          </div>
        )}

        {/* ═══ 资产管理页 ═══ */}
        {tab === 'assets' && (
          <div className="space-y-5">
            <div className="flex items-center justify-between">
              <h2 className="text-xl font-bold text-slate-800">资产管理</h2>
              <span className="text-sm text-slate-400">共 {filteredAssets.length} 项</span>
            </div>

            {/* 搜索和筛选 */}
            <div className="flex gap-3">
              <input type="text" value={search} onChange={e => setSearch(e.target.value)} placeholder="搜索名称或序列号..."
                className="flex-1 max-w-xs px-4 py-2 border border-gray-200 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none" />
              <select value={filterCategory} onChange={e => setFilterCategory(e.target.value)}
                className="px-3 py-2 border border-gray-200 rounded-lg text-sm text-slate-600 outline-none focus:ring-2 focus:ring-blue-500">
                <option value="">全部类别</option>
                {Object.entries(CATEGORY_LABELS).map(([k, v]) => <option key={k} value={k}>{v}</option>)}
              </select>
              <select value={filterStatus} onChange={e => setFilterStatus(e.target.value)}
                className="px-3 py-2 border border-gray-200 rounded-lg text-sm text-slate-600 outline-none focus:ring-2 focus:ring-blue-500">
                <option value="">全部状态</option>
                <option value="active">在用</option>
                <option value="maintenance">维护中</option>
                <option value="retired">已报废</option>
              </select>
            </div>

            {loading ? (
              <div className="text-center py-16 text-slate-400">加载中...</div>
            ) : (
              <div className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
                <table className="w-full text-sm">
                  <thead className="bg-slate-50/80 text-slate-500 text-xs uppercase">
                    <tr>
                      <th className="px-5 py-3.5 text-left font-medium">资产名称</th>
                      <th className="px-5 py-3.5 text-left font-medium">类别</th>
                      <th className="px-5 py-3.5 text-left font-medium">使用部门</th>
                      <th className="px-5 py-3.5 text-left font-medium">状态</th>
                      <th className="px-5 py-3.5 text-right font-medium">价值</th>
                      <th className="px-5 py-3.5 text-left font-medium">序列号</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-50">
                    {filteredAssets.map((asset) => {
                      const st = STATUS_MAP[asset.status] || STATUS_MAP.active
                      return (
                        <tr key={asset.id} className="hover:bg-blue-50/30 transition">
                          <td className="px-5 py-3.5 font-medium text-slate-800">{asset.name}</td>
                          <td className="px-5 py-3.5">
                            <span className="px-2.5 py-1 bg-slate-100 text-slate-600 rounded-md text-xs">{CATEGORY_LABELS[asset.category] || asset.category}</span>
                          </td>
                          <td className="px-5 py-3.5 text-slate-600">{asset.department}</td>
                          <td className="px-5 py-3.5">
                            <span className={`px-2.5 py-1 rounded-full text-xs font-medium ${st.cls}`}>{st.label}</span>
                          </td>
                          <td className="px-5 py-3.5 text-right text-slate-700 font-medium">¥{asset.value?.toLocaleString()}</td>
                          <td className="px-5 py-3.5 text-slate-400 text-xs font-mono">{asset.serial_number}</td>
                        </tr>
                      )
                    })}
                  </tbody>
                </table>
                {filteredAssets.length === 0 && <div className="text-center py-12 text-slate-400 text-sm">没有匹配的资产记录</div>}
              </div>
            )}
          </div>
        )}

        {/* ═══ AI 审计助手页 ═══ */}
        {tab === 'audit' && (
          <div className="max-w-3xl space-y-5">
            <div className="flex items-center gap-3">
              <h2 className="text-xl font-bold text-slate-800">AI 审计助手</h2>
              <span className="px-2.5 py-1 bg-green-100 text-green-700 rounded-full text-xs font-medium">SenseNova 驱动</span>
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
                  <p className="text-slate-400 text-sm mb-4">你好，我是 AI 审计助手，可以帮你分析企业资产状况。</p>
                  <div className="flex flex-wrap justify-center gap-2">
                    {['各部门资产分布', '有哪些需要关注的异常', '资产总览', '哪些许可证快到期了'].map(q => (
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
                    <span className="animate-pulse">正在分析中...</span>
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
        )}
      </main>
    </div>
  )
}
