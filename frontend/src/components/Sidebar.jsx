import { ROLE_LABELS } from './constants'

export default function Sidebar({ user, tab, setTab, onLogout, navItems, onNavClick }) {
  return (
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
          <button key={item.key} onClick={() => { setTab(item.key); onNavClick?.(item.key) }}
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
  )
}
