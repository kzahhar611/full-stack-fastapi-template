"use client"

import { useEffect, useState } from "react"
import { useRouter } from "next/navigation"
import { Sidebar } from "@/components/layout/sidebar"
import { Header } from "@/components/layout/header"
import { useAuthStore } from "@/stores/auth"

export default function AuthenticatedLayout({
  children,
}: {
  children: React.ReactNode
}) {
  const { isAuthenticated, user, getCurrentUser } = useAuthStore()
  const router = useRouter()
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    const checkAuth = async () => {
      if (!isAuthenticated) {
        router.push("/login")
        return
      }

      // Fetch current user data if we don't have it
      if (!user) {
        try {
          await getCurrentUser()
        } catch (error) {
          console.warn("Could not fetch user data:", error)
          // Don't redirect if it's just a network error in demo mode
        }
      }
      
      setIsLoading(false)
    }

    checkAuth()
  }, [isAuthenticated, user, router, getCurrentUser])

  if (!isAuthenticated) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-purple-50 dark:from-gray-900 dark:to-gray-800">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-4 border-blue-600 border-t-transparent mx-auto mb-4"></div>
          <p className="text-muted-foreground">Checking authentication...</p>
        </div>
      </div>
    )
  }

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-purple-50 dark:from-gray-900 dark:to-gray-800">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-4 border-blue-600 border-t-transparent mx-auto mb-4"></div>
          <p className="text-muted-foreground">Loading your workspace...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="flex h-screen bg-gray-50 dark:bg-gray-900">
      <Sidebar />
      <div className="flex flex-1 flex-col overflow-hidden">
        <Header />
        <main className="flex-1 overflow-auto custom-scrollbar">
          <div className="container mx-auto p-6 max-w-7xl">
            {children}
          </div>
        </main>
      </div>
    </div>
  )
}