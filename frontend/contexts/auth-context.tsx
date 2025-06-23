"use client"

import { createContext, useContext, useEffect, useState, type ReactNode } from "react"
import { apiClient } from "@/lib/api"

interface User {
  username: string
  email: string
  first_name: string
  last_name: string
  role: string
}

interface AuthContextType {
  user: User | null
  login: (username: string, password: string) => Promise<void>
  register: (userData: any) => Promise<void>
  logout: () => void
  loading: boolean
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const token = localStorage.getItem("access_token")
    if (token) {
      apiClient.setToken(token)
      fetchUser()
    } else {
      setLoading(false)
    }
  }, [])

  const fetchUser = async () => {
    try {
      const userData = await apiClient.getProfile()
      setUser(userData)
    } catch (error) {
      console.error("Failed to fetch user:", error)
      apiClient.clearToken()
    } finally {
      setLoading(false)
    }
  }

  const login = async (username: string, password: string) => {
    const response = await apiClient.login({ username, password })
    await fetchUser()
  }

  const register = async (userData: any) => {
    await apiClient.register(userData)
  }

  const logout = () => {
    apiClient.clearToken()
    setUser(null)
  }

  return <AuthContext.Provider value={{ user, login, register, logout, loading }}>{children}</AuthContext.Provider>
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (context === undefined) {
    throw new Error("useAuth must be used within an AuthProvider")
  }
  return context
}
