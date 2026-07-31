import { useState, useMemo } from 'react'
import { CATEGORY_LABELS, STATUS_MAP } from './constants'

export default function AssetsTab({ assets, loading, canDelete, onDelete }) {
  const [search, setSearch] = useState('')
  const [filterCategory, setFilterCategory] = useState('')
  const [filterStatus, setFilterStatus] = useState('')

  const filteredAssets = useMemo(() => {
    return assets.filter(a => {
      if (search && !a.name.toLowerCase().includes(search.toLowerCase()) && !(a.serial_number || '').toLowerCase().includes(search.toLowerCase())) return false
      if (filterCategory && a.category !== filterCategory) return false
      if (filterStatus && a.status !== filterStatus) return false
      return true
    })
  }, [assets, search, filterCategory, filterStatus])

  return (
    <div className="space-y-5">
      <div className="flex items-center justify-between">
        <h2 className="text-xl font-bold text-slate-800">资产管理</h2>
        <span className="text-sm text-slate-400">共 {filteredAssets.length} 项</span>
      </div>

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
          <option value="inactive">停用</option>
          <option value="maintenance">维护中</option>
          <option value="disposed">已报废</option>
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
                {canDelete && <th className="px-5 py-3.5 text-center font-medium">操作</th>}
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
                    {canDelete && (
                      <td className="px-5 py-3.5 text-center">
                        <button onClick={() => onDelete(asset.id, asset.name)}
                          className="text-red-500 hover:text-red-700 text-xs font-medium transition">删除</button>
                      </td>
                    )}
                  </tr>
                )
              })}
            </tbody>
          </table>
          {filteredAssets.length === 0 && <div className="text-center py-12 text-slate-400 text-sm">没有匹配的资产记录</div>}
        </div>
      )}
    </div>
  )
}
