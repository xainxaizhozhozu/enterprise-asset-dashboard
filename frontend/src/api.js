import axios from 'axios'

const api = axios.create({
  baseURL: '/api/v1',
  timeout: 10000,
})

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

export const authAPI = {
  login: (data) => api.post('/auth/login', data),
  register: (data) => api.post('/auth/register', data),
  me: () => api.get('/auth/me'),
}

export const assetAPI = {
  list: (params) => api.get('/assets/', { params }),
  get: (id) => api.get(`/assets/${id}`),
  create: (data) => api.post('/assets/', data),
  update: (id, data) => api.put(`/assets/${id}`, data),
  delete: (id) => api.delete(`/assets/${id}`),
}

export const auditAPI = {
  chat: (query) => api.post('/audit/chat', { query }),
}

export default api