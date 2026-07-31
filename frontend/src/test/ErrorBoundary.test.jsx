import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import ErrorBoundary from '../ErrorBoundary'

// A component that always throws on render
function Thrower() {
  throw new Error('Test render error')
}

// A simple child component
function GoodChild() {
  return <div>Hello from child</div>
}

describe('ErrorBoundary', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('renders children when no error', () => {
    render(
      <ErrorBoundary>
        <GoodChild />
      </ErrorBoundary>
    )

    expect(screen.getByText('Hello from child')).toBeInTheDocument()
  })

  it('shows error UI when child throws', () => {
    // Suppress expected console.error from ErrorBoundary
    const spy = vi.spyOn(console, 'error').mockImplementation(() => {})

    render(
      <ErrorBoundary>
        <Thrower />
      </ErrorBoundary>
    )

    expect(screen.getByText('渲染出错')).toBeInTheDocument()
    expect(screen.getByText('Test render error')).toBeInTheDocument()
    expect(screen.getByText('重试')).toBeInTheDocument()

    spy.mockRestore()
  })

  it('retry button resets the error state and re-renders children', async () => {
    const user = userEvent.setup()
    const spy = vi.spyOn(console, 'error').mockImplementation(() => {})

    // Track render attempts
    let shouldThrow = true

    function ConditionalThrower() {
      if (shouldThrow) {
        throw new Error('Temporary error')
      }
      return <div>Recovered successfully</div>
    }

    const { rerender } = render(
      <ErrorBoundary>
        <ConditionalThrower />
      </ErrorBoundary>
    )

    // Should show error state
    expect(screen.getByText('渲染出错')).toBeInTheDocument()

    // Fix the thrower and click retry
    shouldThrow = false
    await user.click(screen.getByText('重试'))

    // After retry with shouldThrow=false, should render child
    expect(screen.getByText('Recovered successfully')).toBeInTheDocument()

    spy.mockRestore()
  })
})
