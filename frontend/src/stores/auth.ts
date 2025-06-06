import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import { authApi } from '@/lib/api'

export interface User {
  id: string
  email: string
  full_name: string
  is_active: boolean
  is_superuser: boolean
  organization_id?: string
}

interface AuthState {
  user: User | null
  accessToken: string | null
  refreshToken: string | null
  isLoading: boolean
  isAuthenticated: boolean
  
  // Actions
  login: (credentials: { email: string; password: string }) => Promise<void>
  logout: () => void
  register: (userData: { email: string; password: string; full_name: string }) => Promise<void>
  getCurrentUser: () => Promise<void>
  setTokens: (accessToken: string, refreshToken: string) => void
  clearAuth: () => void
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      user: null,
      accessToken: null,
      refreshToken: null,
      isLoading: false,
      isAuthenticated: false,

      login: async (credentials) => {
        try {
          set({ isLoading: true })
          
          // For demo purposes, if API is not available, use mock authentication
          try {
            const response = await authApi.login(credentials)
            const { access_token, refresh_token, user } = response.data
            
            set({
              user,
              accessToken: access_token,
              refreshToken: refresh_token,
              isAuthenticated: true,
              isLoading: false,
            })
            
            localStorage.setItem('accessToken', access_token)
            localStorage.setItem('refreshToken', refresh_token)
          } catch (networkError) {
            // Mock authentication for demo - remove in production
            if (credentials.email === 'rfp@kzahhar.com' && credentials.password === 'password123') {
              const mockUser = {
                id: '1',
                email: credentials.email,
                full_name: 'Admin User',
                is_active: true,
                is_superuser: true,
                organization_id: '1'
              }
              
              const mockAccessToken = 'mock-access-token'
              const mockRefreshToken = 'mock-refresh-token'
              
              set({
                user: mockUser,
                accessToken: mockAccessToken,
                refreshToken: mockRefreshToken,
                isAuthenticated: true,
                isLoading: false,
              })
              
              localStorage.setItem('accessToken', mockAccessToken)
              localStorage.setItem('refreshToken', mockRefreshToken)
              
              console.warn('Using mock authentication - backend not available')
              return
            }
            
            throw networkError
          }
        } catch (error) {
          set({ isLoading: false })
          throw error
        }
      },

      register: async (userData) => {
        try {
          set({ isLoading: true })
          const response = await authApi.register(userData)
          const { access_token, refresh_token, user } = response.data
          
          set({
            user,
            accessToken: access_token,
            refreshToken: refresh_token,
            isAuthenticated: true,
            isLoading: false,
          })
          
          localStorage.setItem('accessToken', access_token)
          localStorage.setItem('refreshToken', refresh_token)
        } catch (error) {
          set({ isLoading: false })
          throw error
        }
      },

      getCurrentUser: async () => {
        try {
          const response = await authApi.getCurrentUser()
          set({ user: response.data })
        } catch (error) {
          // If getting current user fails, clear auth
          get().clearAuth()
          throw error
        }
      },

      setTokens: (accessToken, refreshToken) => {
        set({ accessToken, refreshToken, isAuthenticated: true })
        localStorage.setItem('accessToken', accessToken)
        localStorage.setItem('refreshToken', refreshToken)
      },

      logout: () => {
        // Call logout API (fire and forget)
        authApi.logout().catch(() => {})
        
        get().clearAuth()
      },

      clearAuth: () => {
        set({
          user: null,
          accessToken: null,
          refreshToken: null,
          isAuthenticated: false,
          isLoading: false,
        })
        
        localStorage.removeItem('accessToken')
        localStorage.removeItem('refreshToken')
      },
    }),
    {
      name: 'tenderwise-auth',
      partialize: (state) => ({
        user: state.user,
        accessToken: state.accessToken,
        refreshToken: state.refreshToken,
        isAuthenticated: state.isAuthenticated,
      }),
    }
  )
)