import { useMemo } from 'react'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts'
import { CATEGORY_LABELS, COLORS } from './constants'

export default function OverviewTab({ assets, stats, onQuickAction }) {
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

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-xl font-bold text-slate-800">工作台总览</h2>
        <span className="text-sm text-slate-400">{new Date().toLocaleDateString('zh-CN', { year: 'numeric', month: 'long', day: 'numeric', weekday: 'long' })}</span>
      </div>

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
              <Pie data={categoryData} dataKey="value" nameKey="name" cx="50%" cy="50%" outerRadius={90}
                label={({ name, value }) => `${name} ${value}台`} labelLine fontSize={11}>
                {categoryData.map((_, i) => <Cell key={i} fill={COLORS[i % COLORS.length]} />)}
              </Pie>
              <Tooltip formatter={(v) => [v + ' 台', '数量']} />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </div>

      <div className="bg-white rounded-xl p-6 shadow-sm border border-gray-100">
        <h3 className="text-sm font-semibold text-slate-700 mb-3">快捷操作</h3>
        <div className="flex gap-3">
          <button onClick={() => onQuickAction('assets')} className="px-4 py-2 bg-blue-50 text-blue-700 rounded-lg text-sm hover:bg-blue-100 transition">查看全部资产</button>
          <button onClick={() => onQuickAction('audit:各部门资产分布情况')} className="px-4 py-2 bg-purple-50 text-purple-700 rounded-lg text-sm hover:bg-purple-100 transition">AI 分析部门分布</button>
          <button onClick={() => onQuickAction('audit:有哪些需要关注的异常')} className="px-4 py-2 bg-amber-50 text-amber-700 rounded-lg text-sm hover:bg-amber-100 transition">AI 检查异常</button>
        </div>
      </div>
    </div>
  )
}
