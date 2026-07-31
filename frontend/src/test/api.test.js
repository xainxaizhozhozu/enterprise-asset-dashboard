import { describe, it, expect, vi, beforeEach } from 'vitest'

// Mock axios before importing api
vi.mock('axios', () => {
  const mockAxiosInstance = {
    get: vi.fn().mockResolvedValue({ data: {} }),
    post: vi.fn().mockResolvedValue({ data: {} }),
    put: vi.fn().mockResolvedValue({ data: {} }),
    delete: vi.fn().mockResolvedValue({ data: {} }),
    interceptors: {
      request: { use: vi.fn() },
      response: { use: vi.fn() },
    },
  }
  return {
    default: {
      create: vi.fn(() => mockAxiosInstance),
    },
  }
})

import { authAPI, assetAPI, auditAPI, auditLogAPI } from '../api'
import api from '../api'

describe('API Module', () => {
  it('exports a default axios instance', () => {
    expect(api).toBeDefined()
  })

  it('authAPI has login and register methods', () => {
    expect(typeof authAPI.login).toBe('function')
    expect(typeof authAPI.register).toBe('function')
    expect(typeof authAPI.me).toBe('function')
  })

  it('assetAPI has list, get, create, update, delete methods', () => {
    expect(typeof assetAPI.list).toBe('function')
    expect(typeof assetAPI.get).toBe('function')
    expect(typeof assetAPI.create).toBe('function')
    expect(typeof assetAPI.update).toBe('function')
    expect(typeof assetAPI.delete).toBe('function')
  })

  it('auditAPI has chat method', () => {
    expect(typeof auditAPI.chat).toBe('function')
  })

  it('auditLogAPI has list method', () => {
    expect(typeof auditLogAPI.list).toBe('function')
  })

  it('authAPI.login returns a promise', async () => {
    const result = authAPI.login({ username: 'admin', password: 'pass' })
    await expect(result).resolves.toBeDefined()
  })

  it('assetAPI.list returns a promise', async () => {
    const result = assetAPI.list()
    await expect(result).resolves.toBeDefined()
  })
})
