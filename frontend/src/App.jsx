import { Routes, Route, Navigate } from 'react-router-dom'
import { useState, useEffect } from 'react'
import Login from './pages/Login'
import Dashboard from './pages/Dashboard'

function App() {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const token = localStorage.getItem('token')
    const savedUser = localStorage.getItem('user')
    if (token && savedUser) {
      setUser(JSON.parse(savedUser))
    }
    setLoading(false)
  }, [])

  const handleLogin = (userData, token) => {
    localStorage.setItem('token', token)
    localStorage.setItem('user', JSON.stringify(userData))
    setUser(userData)
  }

  const handleLogout = () => {
    localStorage.removeItem('token')
    localStorage.removeItem('user')
    setUser(null)
  }

  if (loading) return <div className="flex items-center justify-center h-screen">加载中...</div>

  return (
    <Routes>
      <Route path="/login" element={!user ? <Login onLogin={handleLogin} /> : <Navigate to="/" />} />
      <Route path="/*" element={user ? <Dashboard user={user} onLogout={handleLogout} /> : <Navigate to="/login" />} />
    </Routes>
  )
}

export default App