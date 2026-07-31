import { Routes, Route, Navigate } from 'react-router-dom'
import { AuthProvider, useAuth } from './contexts/AuthContext'
import Login from './pages/Login'
import Dashboard from './pages/Dashboard'
import ErrorBoundary from './ErrorBoundary'

function AppRoutes() {
  const { user, loading, login, logout } = useAuth()

  if (loading) return <div className="flex items-center justify-center h-screen">加载中...</div>

  return (
    <Routes>
      <Route path="/login" element={!user ? <Login onLogin={login} /> : <Navigate to="/" />} />
      <Route path="/*" element={user ? <ErrorBoundary><Dashboard user={user} onLogout={logout} /></ErrorBoundary> : <Navigate to="/login" />} />
    </Routes>
  )
}

function App() {
  return (
    <AuthProvider>
      <AppRoutes />
    </AuthProvider>
  )
}

export default App
