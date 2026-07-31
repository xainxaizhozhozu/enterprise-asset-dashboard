// 共享常量：角色标签、类别标签、状态映射、图表配色

export const ROLE_LABELS = { admin: '管理员', manager: '部门经理', viewer: '查看者' }

export const CATEGORY_LABELS = {
  server: '服务器', desktop: '台式机', laptop: '笔记本', monitor: '显示器',
  network: '网络设备', software: '软件许可', peripheral: '外设',
}

export const STATUS_MAP = {
  active: { label: '在用', cls: 'bg-green-100 text-green-700' },
  inactive: { label: '停用', cls: 'bg-gray-100 text-gray-600' },
  maintenance: { label: '维护中', cls: 'bg-amber-100 text-amber-700' },
  disposed: { label: '已报废', cls: 'bg-red-100 text-red-600' },
}

export const COLORS = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#06b6d4', '#ec4899']
