"use client"

import { useState } from "react"
import { useRouter } from "next/navigation"
import { Eye, EyeOff, Mail, Lock, Zap } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { useAuthStore } from "@/stores/auth"
import { toast } from "sonner"

export default function LoginPage() {
  const [email, setEmail] = useState("rfp@kzahhar.com")
  const [password, setPassword] = useState("password123")
  const [showPassword, setShowPassword] = useState(false)
  const [isLoading, setIsLoading] = useState(false)
  
  const { login } = useAuthStore()
  const router = useRouter()

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    if (!email || !password) {
      toast.error("Please fill in all fields")
      return
    }

    setIsLoading(true)
    
    try {
      await login({ email, password })
      toast.success("Login successful!")
      router.push("/dashboard")
    } catch (error: any) {
      console.error("Login error:", error)
      const message = error.response?.data?.detail || "Login failed. Please check your credentials."
      toast.error(message)
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50 dark:from-gray-900 dark:via-blue-900 dark:to-indigo-900 p-4 relative overflow-hidden">
      {/* Background decorations */}
      <div className="absolute inset-0 overflow-hidden">
        <div className="absolute -top-40 -right-40 w-80 h-80 rounded-full bg-gradient-to-br from-blue-200 to-purple-200 dark:from-blue-800 dark:to-purple-800 opacity-20 blur-3xl"></div>
        <div className="absolute -bottom-40 -left-40 w-80 h-80 rounded-full bg-gradient-to-br from-purple-200 to-pink-200 dark:from-purple-800 dark:to-pink-800 opacity-20 blur-3xl"></div>
      </div>
      
      <div className="w-full max-w-md relative z-10">
        {/* Logo and Branding */}
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-20 h-20 bg-gradient-to-r from-blue-600 to-purple-600 rounded-3xl mb-6 shadow-2xl shadow-blue-500/25">
            <Zap className="w-10 h-10 text-white" />
          </div>
          <h1 className="text-4xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent mb-2">
            TenderWise AI
          </h1>
          <p className="text-muted-foreground text-lg">
            Enterprise RFP Management Platform
          </p>
          <div className="flex items-center justify-center gap-2 mt-4">
            <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
            <span className="text-sm text-green-600 dark:text-green-400 font-medium">System Online</span>
          </div>
        </div>

        <Card className="shadow-2xl border-0 bg-white/95 dark:bg-gray-900/95 backdrop-blur-xl">
          <CardHeader className="space-y-2 text-center pb-6">
            <CardTitle className="text-3xl font-bold bg-gradient-to-r from-gray-900 to-gray-600 dark:from-white dark:to-gray-300 bg-clip-text text-transparent">
              Welcome back
            </CardTitle>
            <CardDescription className="text-base">
              Sign in to your TenderWise AI account
            </CardDescription>
          </CardHeader>
          <CardContent className="px-8 pb-8">
            <form onSubmit={handleSubmit} className="space-y-6">
              <div className="space-y-3">
                <Label htmlFor="email" className="text-sm font-semibold">Email Address</Label>
                <div className="relative">
                  <Mail className="absolute left-4 top-1/2 h-5 w-5 -translate-y-1/2 text-muted-foreground" />
                  <Input
                    id="email"
                    type="email"
                    placeholder="Enter your email address"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    className="pl-12 h-12 text-base rounded-xl border-2 border-gray-200 dark:border-gray-700 focus:border-blue-500 dark:focus:border-blue-400 transition-colors"
                    required
                  />
                </div>
              </div>
              
              <div className="space-y-3">
                <Label htmlFor="password" className="text-sm font-semibold">Password</Label>
                <div className="relative">
                  <Lock className="absolute left-4 top-1/2 h-5 w-5 -translate-y-1/2 text-muted-foreground" />
                  <Input
                    id="password"
                    type={showPassword ? "text" : "password"}
                    placeholder="Enter your password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    className="pl-12 pr-12 h-12 text-base rounded-xl border-2 border-gray-200 dark:border-gray-700 focus:border-blue-500 dark:focus:border-blue-400 transition-colors"
                    required
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword(!showPassword)}
                    className="absolute right-4 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground transition-colors"
                  >
                    {showPassword ? (
                      <EyeOff className="h-5 w-5" />
                    ) : (
                      <Eye className="h-5 w-5" />
                    )}
                  </button>
                </div>
              </div>

              <Button 
                type="submit" 
                size="lg"
                className="w-full h-12 bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white font-semibold rounded-xl shadow-lg hover:shadow-xl transition-all duration-200"
                disabled={isLoading}
              >
                {isLoading ? (
                  <div className="flex items-center gap-2">
                    <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin"></div>
                    Signing in...
                  </div>
                ) : (
                  "Sign in to TenderWise AI"
                )}
              </Button>
            </form>

            <div className="mt-6 p-4 bg-blue-50 dark:bg-blue-950 rounded-xl border border-blue-200 dark:border-blue-800">
              <p className="text-sm font-semibold text-blue-700 dark:text-blue-300 text-center mb-2">Demo Credentials</p>
              <div className="space-y-1 text-xs font-mono text-blue-600 dark:text-blue-400">
                <p><span className="font-semibold">Email:</span> rfp@kzahhar.com</p>
                <p><span className="font-semibold">Password:</span> password123</p>
              </div>
            </div>

            <div className="mt-6 text-center">
              <p className="text-sm text-muted-foreground">
                Don&apos;t have an account?{" "}
                <a 
                  href="/register" 
                  className="font-medium text-primary hover:underline"
                >
                  Sign up
                </a>
              </p>
            </div>
          </CardContent>
        </Card>

        <div className="mt-8 text-center text-xs text-muted-foreground">
          <p>© 2024 TenderWise AI. All rights reserved.</p>
        </div>
      </div>
    </div>
  )
}