import axios, { AxiosInstance, AxiosResponse } from 'axios'
import toast from 'react-hot-toast'

// Create axios instance
const api: AxiosInstance = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000/api/v1',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Token management
let authToken: string | null = null

export const setAuthToken = (token: string | null) => {
  authToken = token
  if (token) {
    api.defaults.headers.common['Authorization'] = `Bearer ${token}`
    localStorage.setItem('auth_token', token)
  } else {
    delete api.defaults.headers.common['Authorization']
    localStorage.removeItem('auth_token')
  }
}

// Initialize token from localStorage
if (typeof window !== 'undefined') {
  const savedToken = localStorage.getItem('auth_token')
  if (savedToken) {
    setAuthToken(savedToken)
  }
}

// Request interceptor
api.interceptors.request.use(
  (config) => {
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response interceptor
api.interceptors.response.use(
  (response: AxiosResponse) => {
    return response
  },
  (error) => {
    const { response } = error

    if (response?.status === 401) {
      // Token expired or invalid
      setAuthToken(null)
      window.location.href = '/login'
      toast.error('Session expired. Please login again.')
    } else if (response?.status === 403) {
      toast.error('You do not have permission to perform this action.')
    } else if (response?.status === 404) {
      toast.error('Resource not found.')
    } else if (response?.status >= 500) {
      toast.error('Server error. Please try again later.')
    } else if (response?.data?.detail) {
      // API error with detail message
      if (typeof response.data.detail === 'string') {
        toast.error(response.data.detail)
      } else if (Array.isArray(response.data.detail)) {
        // Validation errors
        const errorMessages = response.data.detail.map((err: any) => {
          if (err.msg) return err.msg
          if (err.message) return err.message
          return JSON.stringify(err)
        }).join(', ')
        toast.error(errorMessages)
      }
    } else if (error.message) {
      toast.error(error.message)
    }

    return Promise.reject(error)
  }
)

export default api

// Utility functions
export const handleApiError = (error: any) => {
  console.error('API Error:', error)
  
  if (error.response?.data?.detail) {
    return error.response.data.detail
  } else if (error.message) {
    return error.message
  }
  
  return 'An unexpected error occurred'
}

export const createFormData = (data: Record<string, any>): FormData => {
  const formData = new FormData()
  
  Object.keys(data).forEach((key) => {
    const value = data[key]
    if (value !== undefined && value !== null) {
      if (value instanceof File) {
        formData.append(key, value)
      } else if (typeof value === 'object') {
        formData.append(key, JSON.stringify(value))
      } else {
        formData.append(key, String(value))
      }
    }
  })
  
  return formData
}