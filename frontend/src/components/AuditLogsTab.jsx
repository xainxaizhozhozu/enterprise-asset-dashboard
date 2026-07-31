import { useState, useEffect } from 'react'
import { auditLogAPI } from '../api'

export default function AuditLogsTab() {
  const [auditLogs, setAuditLogs] = useState([])
  const [logsLoading, setLogsLoading] = useState(false)

  const loadLogs = async () => {
    setLogsLoading(true)
    try {
      const res = await auditLogAPI.list()
      setAuditLogs(res.data)
    } catch (err) {
      console.error('加载审计日志失败', err)
    } finally {
      setLogsLoading(false)
    }
  }

  useEffect(() => { loadLogs() }, [])

  return (
    <div className="space-y-5">
      <div className="flex items-center justify-between">
        <h2 className="text-xl font-bold text-slate-800">操作审计日志</h2>
        <button onClick={loadLogs} className="px-4 py-2 bg-blue-50 text-blue-700 rounded-lg text-sm hover:bg-blue-100 transition">刷新</button>
      </div>

      {logsLoading ? (
        <div className="text-center py-16 text-slate-400">加载中...</div>
      ) : (
        <div className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
          <table className="w-full text-sm">
            <thead className="bg-slate-50/80 text-slate-500 text-xs uppercase">
              <tr>
                <th className="px-5 py-3.5 text-left font-medium">时间</th>
                <th className="px-5 py-3.5 text-left font-medium">操作</th>
                <th className="px-5 py-3.5 text-left font-medium">操作人ID</th>
                <th className="px-5 py-3.5 text-left font-medium">详情</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-50">
              {auditLogs.map((log) => (
                <tr key={log.id} className="hover:bg-blue-50/30 transition">
                  <td className="px-5 py-3.5 text-slate-500 text-xs font-mono whitespace-nowrap">{log.created_at?.slice(0, 19)}</td>
                  <td className="px-5 py-3.5">
                    <span className={`px-2.5 py-1 rounded-md text-xs font-medium ${
                      log.action === 'create' ? 'bg-green-100 text-green-700' :
                      log.action === 'update' ? 'bg-blue-100 text-blue-700' :
                      'bg-red-100 text-red-700'
                    }`}>
                      {log.action === 'create' ? '新增' : log.action === 'update' ? '修改' : '删除'}
                    </span>
                  </td>
                  <td className="px-5 py-3.5 text-slate-600">#{log.user_id}</td>
                  <td className="px-5 py-3.5 text-slate-700 text-xs">{log.details}</td>
                </tr>
              ))}
            </tbody>
          </table>
          {auditLogs.length === 0 && <div className="text-center py-12 text-slate-400 text-sm">暂无审计日志</div>}
        </div>
      )}
    </div>
  )
}
