import { useState, useEffect, useMemo } from 'react'
import { assetAPI } from '../api'
import useApi from '../hooks/useApi'
import Sidebar from '../components/Sidebar'
import OverviewTab from '../components/OverviewTab'
import AssetsTab from '../components/AssetsTab'
import AuditTab from '../components/AuditTab'
import AuditLogsTab from '../components/AuditLogsTab'

export default function Dashboard({ user, onLogout }) {
  const [tab, setTab] = useState('overview')
  const { data: assets, loading, execute: loadAssets } = useApi(assetAPI.list)

  const canDelete = user.role === 'admin'
  const canViewLogs = user.role === 'admin'

  useEffect(() => { loadAssets() }, [])

  const handleDelete = async (id, name) => {
    if (!window.confirm(`确认删除资产 "${name}"？`)) return
    try {
      await assetAPI.delete(id)
      loadAssets()
    } catch (err) {
      alert(err.response?.data?.detail || '删除失败')
    }
  }

  const stats = useMemo(() => {
    const list = assets || []
    const totalValue = list.reduce((s, a) => s + (a.value || 0), 0)
    const activeCount = list.filter(a => a.status === 'active').length
    const maintenanceCount = list.filter(a => a.status === 'maintenance').length
    const departments = [...new Set(list.map(a => a.department))]
    return { totalValue, activeCount, maintenanceCount, deptCount: departments.length }
  }, [assets])

  const navItems = [
    { key: 'overview', label: '总览', icon: '📊' },
    { key: 'assets', label: '资产管理', icon: '💻' },
    { key: 'audit', label: 'AI 审计助手', icon: '🤖' },
  ]
  if (canViewLogs) navItems.push({ key: 'logs', label: '审计日志', icon: '📋' })

  const handleQuickAction = (action) => {
    if (action === 'assets') {
      setTab('assets')
    } else if (action.startsWith('audit:')) {
      const query = action.slice(6)
      setTab('audit')
      setTimeout(() => AuditTab._handleChat?.(query), 100)
    }
  }

  return (
    <div className="min-h-screen bg-gray-50 flex">
      <Sidebar user={user} tab={tab} setTab={setTab} onLogout={onLogout} navItems={navItems} />

      <main className="flex-1 ml-60 p-8">
        {tab === 'overview' && (
          <OverviewTab assets={assets || []} stats={stats} onQuickAction={handleQuickAction} />
        )}
        {tab === 'assets' && (
          <AssetsTab assets={assets || []} loading={loading} canDelete={canDelete} onDelete={handleDelete} />
        )}
        {tab === 'audit' && <AuditTab />}
        {tab === 'logs' && canViewLogs && <AuditLogsTab />}
      </main>
    </div>
  )
}
