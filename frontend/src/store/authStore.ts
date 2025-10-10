import { create } from 'zustand'

interface User {
  id: number
  email: string
  username: string
  full_name?: string
  avatar?: string
}

interface AuthState {
  isAuthenticated: boolean
  user: User | null
  setAuth: (user: User | null, token?: string) => void
  logout: () => void
  checkAuth: () => boolean
}

export const useAuthStore = create<AuthState>((set, get) => ({
  isAuthenticated: !!localStorage.getItem('access_token'),
  user: null,
  
  setAuth: (user, token) => {
    if (user && token) {
      localStorage.setItem('access_token', token)
      set({ isAuthenticated: true, user })
    } else if (user) {
      set({ isAuthenticated: true, user })
    } else {
      set({ isAuthenticated: false, user: null })
    }
  },
  
  logout: () => {
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
    set({ isAuthenticated: false, user: null })
  },
  
  checkAuth: () => {
    const token = localStorage.getItem('access_token')
    const isAuth = !!token
    if (isAuth !== get().isAuthenticated) {
      set({ isAuthenticated: isAuth })
    }
    return isAuth
  },
}))

// Initialize auth state on app load
if (typeof window !== 'undefined') {
  const token = localStorage.getItem('access_token')
  if (token) {
    useAuthStore.setState({ isAuthenticated: true })
  }
}

