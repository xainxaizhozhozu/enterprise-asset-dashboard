import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, act } from '@testing-library/react'
import Dashboard from '../pages/Dashboard'

// Mock recharts - jsdom has no layout engine
vi.mock('recharts', () => {
  const Stub = ({ children }) => <div data-testid="recharts-stub">{children}</div>
  return {
    ResponsiveContainer: Stub,
    BarChart: Stub,
    Bar: () => null,
    XAxis: () => null,
    YAxis: () => null,
    CartesianGrid: () => null,
    Tooltip: () => null,
    PieChart: Stub,
    Pie: ({ children }) => <div>{children}</div>,
    Cell: () => null,
  }
})

// Mock the api module
vi.mock('../api', () => ({
  assetAPI: {
    list: vi.fn().mockResolvedValue({ data: [] }),
    get: vi.fn(),
    create: vi.fn(),
    update: vi.fn(),
    delete: vi.fn(),
  },
  auditAPI: {
    chat: vi.fn(),
  },
  auditLogAPI: {
    list: vi.fn().mockResolvedValue({ data: [] }),
  },
}))

describe('Dashboard Page', () => {
  const adminUser = { username: 'admin', role: 'admin' }
  const viewerUser = { username: 'viewer_li', role: 'viewer' }
  let onLogoutMock

  beforeEach(() => {
    onLogoutMock = vi.fn()
    vi.clearAllMocks()
  })

  it('renders nav tabs including overview, assets, and audit', async () => {
    await act(async () => {
      render(<Dashboard user={adminUser} onLogout={onLogoutMock} />)
    })

    expect(screen.getByText('总览')).toBeInTheDocument()
    expect(screen.getByText('资产管理')).toBeInTheDocument()
    expect(screen.getByText('AI 审计助手')).toBeInTheDocument()
  })

  it('renders audit log tab for admin users', async () => {
    await act(async () => {
      render(<Dashboard user={adminUser} onLogout={onLogoutMock} />)
    })

    expect(screen.getByText('审计日志')).toBeInTheDocument()
  })

  it('does not render audit log tab for viewer users', async () => {
    await act(async () => {
      render(<Dashboard user={viewerUser} onLogout={onLogoutMock} />)
    })

    expect(screen.queryByText('审计日志')).not.toBeInTheDocument()
  })

  it('renders overview stats on default tab', async () => {
    await act(async () => {
      render(<Dashboard user={adminUser} onLogout={onLogoutMock} />)
    })

    expect(screen.getByText('工作台总览')).toBeInTheDocument()
  })

  it('logout button is present', async () => {
    await act(async () => {
      render(<Dashboard user={adminUser} onLogout={onLogoutMock} />)
    })

    expect(screen.getByText('退出登录')).toBeInTheDocument()
  })

  it('displays user info in sidebar', async () => {
    await act(async () => {
      render(<Dashboard user={adminUser} onLogout={onLogoutMock} />)
    })

    expect(screen.getByText('admin')).toBeInTheDocument()
    expect(screen.getByText('管理员')).toBeInTheDocument()
  })
})
