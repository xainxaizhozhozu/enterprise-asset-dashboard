import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import Login from '../pages/Login'

// Mock the api module
vi.mock('../api', () => ({
  authAPI: {
    login: vi.fn(),
    register: vi.fn(),
  },
}))

describe('Login Page', () => {
  let onLoginMock

  beforeEach(() => {
    onLoginMock = vi.fn()
    vi.clearAllMocks()
  })

  it('renders login form with username and password fields', () => {
    render(<Login onLogin={onLoginMock} />)

    expect(screen.getByPlaceholderText('请输入用户名')).toBeInTheDocument()
    expect(screen.getByPlaceholderText('请输入密码')).toBeInTheDocument()
  })

  it('renders the login submit button by default', () => {
    render(<Login onLogin={onLoginMock} />)

    expect(screen.getByRole('button', { name: '登录' })).toBeInTheDocument()
  })

  it('renders register option and toggles to register mode', async () => {
    const user = userEvent.setup()
    render(<Login onLogin={onLoginMock} />)

    // Initially shows "去注册" link
    expect(screen.getByText('没有账户？')).toBeInTheDocument()
    const toggleBtn = screen.getByText('去注册')
    expect(toggleBtn).toBeInTheDocument()

    // Click to switch to register mode
    await user.click(toggleBtn)

    // Now shows register form with email field
    expect(screen.getByPlaceholderText('请输入邮箱')).toBeInTheDocument()
    expect(screen.getByRole('button', { name: '注册' })).toBeInTheDocument()
    expect(screen.getByText('已有账户？')).toBeInTheDocument()
  })

  it('typing in username field works', async () => {
    const user = userEvent.setup()
    render(<Login onLogin={onLoginMock} />)

    const usernameInput = screen.getByPlaceholderText('请输入用户名')
    await user.type(usernameInput, 'admin')

    expect(usernameInput.value).toBe('admin')
  })

  it('typing in password field works', async () => {
    const user = userEvent.setup()
    render(<Login onLogin={onLoginMock} />)

    const passwordInput = screen.getByPlaceholderText('请输入密码')
    await user.type(passwordInput, 'secret123')

    expect(passwordInput.value).toBe('secret123')
  })
})
