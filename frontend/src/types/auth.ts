export interface User {
  id: number
  email: string
  full_name: string
  is_active: boolean
  is_superuser: boolean
  is_verified: boolean
  organization?: string
  position?: string
  language: string
  timezone: string
}

export interface LoginCredentials {
  username: string
  password: string
}

export interface LoginResponse {
  access_token: string
  token_type: string
  user: User
}

export interface RegisterData {
  email: string
  password: string
  full_name: string
  organization?: string
  position?: string
  language?: string
  timezone?: string
}

export interface AuthContextType {
  user: User | null
  token: string | null
  isLoading: boolean
  login: (credentials: LoginCredentials) => Promise<void>
  logout: () => void
  register: (data: RegisterData) => Promise<void>
  updateProfile: (data: Partial<User>) => Promise<void>
  isAuthenticated: boolean
}