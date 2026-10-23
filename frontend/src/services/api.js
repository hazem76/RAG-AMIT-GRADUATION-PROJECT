import axios from 'axios'
import useAuthStore from '../store/authStore'

const API_BASE_URL = 'http://localhost:9000/api'

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Add token to requests
api.interceptors.request.use((config) => {
  const token = useAuthStore.getState().token
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// Handle errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      useAuthStore.getState().logout()
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

// Auth APIs
export const authAPI = {
  register: (data) => api.post('/auth/register', data),
  login: (data) => api.post('/auth/login', data),
  getMe: () => api.get('/auth/me'),
}

// Chat APIs
export const chatAPI = {
  createChat: (data) => api.post('/chat', data),
  getChats: (skip = 0, limit = 20) => api.get(`/chat?skip=${skip}&limit=${limit}`),
  getChat: (chatId) => api.get(`/chat/${chatId}`),
  sendMessage: (chatId, data) => api.post(`/chat/${chatId}/message`, data),
  updateTitle: (chatId, title) => api.put(`/chat/${chatId}/title?new_title=${title}`),
  deleteChat: (chatId) => api.delete(`/chat/${chatId}`),
}

// Ticket APIs
export const ticketAPI = {
  createTicket: (data) => api.post('/tickets', data),
  getTickets: (skip = 0, limit = 20) => api.get(`/tickets?skip=${skip}&limit=${limit}`),
  getTicket: (ticketId) => api.get(`/tickets/${ticketId}`),
  updateTicket: (ticketId, data) => api.put(`/tickets/${ticketId}`, data),
  deleteTicket: (ticketId) => api.delete(`/tickets/${ticketId}`),
  getAllTickets: (skip = 0, limit = 50) => api.get(`/tickets/admin/all?skip=${skip}&limit=${limit}`),
}

// Knowledge Base APIs
export const knowledgeBaseAPI = {
  uploadDocument: (formData) => api.post('/knowledge-base/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  }),
  getDocuments: (skip = 0, limit = 50) => api.get(`/knowledge-base?skip=${skip}&limit=${limit}`),
  getDocument: (docId) => api.get(`/knowledge-base/${docId}`),
  deleteDocument: (docId) => api.delete(`/knowledge-base/${docId}`),
  searchDocuments: (query, topK = 5) => api.post('/knowledge-base/search', { query, top_k: topK }),
}

// Analytics APIs
export const analyticsAPI = {
  getDashboard: () => api.get('/analytics/dashboard'),
  getChatAnalytics: (days = 7) => api.get(`/analytics/chat-analytics?days=${days}`),
  getTicketAnalytics: (days = 7) => api.get(`/analytics/ticket-analytics?days=${days}`),
  getConfidenceDistribution: () => api.get('/analytics/confidence-distribution'),
  getUserActivity: (userId) => api.get(`/analytics/user-activity/${userId}`),
}

export default api
