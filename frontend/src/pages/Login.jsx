import { useState } from 'react'
import { authAPI } from '../api'

export default function Login({ onLogin }) {
  const [isRegister, setIsRegister] = useState(false)
  const [form, setForm] = useState({ username: '', email: '', password: '' })
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      const endpoint = isRegister ? authAPI.register : authAPI.login
      const payload = isRegister ? form : { username: form.username, password: form.password }
      const res = await endpoint(payload)
      onLogin(res.data.user, res.data.access_token)
    } catch (err) {
      setError(err.response?.data?.detail || '操作失败，请重试')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 to-blue-900 flex items-center justify-center p-4">
      <div className="bg-white rounded-2xl shadow-2xl p-8 w-full max-w-md">
        <h1 className="text-2xl font-bold text-center text-slate-800 mb-2">
          企业资产管理系统
        </h1>
        <p className="text-center text-slate-500 mb-6">
          {isRegister ? '创建新账户' : '登录您的账户'}
        </p>

        {error && (
          <div className="bg-red-50 text-red-600 px-4 py-2 rounded-lg mb-4 text-sm">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">用户名</label>
            <input
              type="text"
              value={form.username}
              onChange={(e) => setForm({ ...form, username: e.target.value })}
              className="w-full px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none"
              placeholder="请输入用户名"
              required
            />
          </div>

          {isRegister && (
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">邮箱</label>
              <input
                type="email"
                value={form.email}
                onChange={(e) => setForm({ ...form, email: e.target.value })}
                className="w-full px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none"
                placeholder="请输入邮箱"
                required
              />
            </div>
          )}

          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">密码</label>
            <input
              type="password"
              value={form.password}
              onChange={(e) => setForm({ ...form, password: e.target.value })}
              className="w-full px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none"
              placeholder="请输入密码"
              required
            />
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full bg-blue-600 text-white py-2.5 rounded-lg font-medium hover:bg-blue-700 transition disabled:opacity-50"
          >
            {loading ? '处理中...' : isRegister ? '注册' : '登录'}
          </button>
        </form>

        <p className="text-center text-sm text-slate-500 mt-4">
          {isRegister ? '已有账户？' : '没有账户？'}
          <button
            onClick={() => { setIsRegister(!isRegister); setError('') }}
            className="text-blue-600 font-medium ml-1 hover:underline"
          >
            {isRegister ? '去登录' : '去注册'}
          </button>
        </p>

        <div className="mt-6 p-3 bg-slate-50 rounded-lg text-xs text-slate-500">
          <p className="font-medium mb-1">测试账号：</p>
          <p>管理员：admin / admin123</p>
          <p>经理：manager_zhang / manager123</p>
          <p>查看者：viewer_li / viewer123</p>
        </div>
      </div>
    </div>
  )
}