'use client'

import React, { useState } from 'react'
import { useRouter } from 'next/navigation'
import { useAuth } from '@/contexts/AuthContext'
import Button from '@/components/common/Button'
import Input from '@/components/common/Input'
import { EnvelopeIcon, LockClosedIcon } from '@heroicons/react/24/outline'

const LoginPage: React.FC = () => {
  const [credentials, setCredentials] = useState({
    username: '',
    password: ''
  })
  const [loading, setLoading] = useState(false)
  const { login, isAuthenticated } = useAuth()
  const router = useRouter()

  // Redirect if already authenticated
  React.useEffect(() => {
    if (isAuthenticated) {
      router.push('/dashboard')
    }
  }, [isAuthenticated, router])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    if (!credentials.username || !credentials.password) {
      return
    }

    try {
      setLoading(true)
      await login(credentials)
    } catch (error) {
      console.error('Login failed:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target
    setCredentials(prev => ({
      ...prev,
      [name]: value
    }))
  }

  // Demo credentials helper
  const fillDemoCredentials = () => {
    setCredentials({
      username: 'rfp@kzahhar.com',
      password: 'password123'
    })
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full space-y-8">
        {/* Header */}
        <div className="text-center">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">
            TenderWise AI
          </h1>
          <h2 className="text-2xl font-semibold text-gray-700 mb-6">
            Sign in to your account
          </h2>
          <p className="text-sm text-gray-600">
            AI-powered RFP & Tendering Platform
          </p>
        </div>

        {/* Login Form */}
        <form onSubmit={handleSubmit} className="mt-8 space-y-6">
          <div className="space-y-4">
            <Input
              label="Email Address"
              type="email"
              name="username"
              value={credentials.username}
              onChange={handleChange}
              required
              autoComplete="email"
              leftIcon={<EnvelopeIcon className="h-5 w-5" />}
              placeholder="Enter your email"
            />

            <Input
              label="Password"
              type="password"
              name="password"
              value={credentials.password}
              onChange={handleChange}
              required
              autoComplete="current-password"
              leftIcon={<LockClosedIcon className="h-5 w-5" />}
              placeholder="Enter your password"
            />
          </div>

          <div className="space-y-4">
            <Button
              type="submit"
              loading={loading}
              fullWidth
              size="lg"
            >
              Sign in
            </Button>

            {/* Demo Credentials Button */}
            <Button
              type="button"
              variant="outline"
              fullWidth
              onClick={fillDemoCredentials}
              disabled={loading}
            >
              Use Demo Credentials
            </Button>
          </div>

          {/* Additional Links */}
          <div className="text-center space-y-2">
            <p className="text-sm text-gray-600">
              Demo Admin: rfp@kzahhar.com / password123
            </p>
            <div className="flex items-center justify-center space-x-4 text-sm">
              <button
                type="button"
                className="text-primary-600 hover:text-primary-500"
                onClick={() => router.push('/forgot-password')}
              >
                Forgot password?
              </button>
              <span className="text-gray-300">|</span>
              <button
                type="button"
                className="text-primary-600 hover:text-primary-500"
                onClick={() => router.push('/register')}
              >
                Create account
              </button>
            </div>
          </div>
        </form>

        {/* Features */}
        <div className="mt-8 border-t border-gray-200 pt-6">
          <div className="text-center">
            <h3 className="text-lg font-medium text-gray-900 mb-4">
              Platform Features
            </h3>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-sm text-gray-600">
              <div className="flex items-center">
                <div className="w-2 h-2 bg-primary-500 rounded-full mr-2"></div>
                AI-Powered RFP Analysis
              </div>
              <div className="flex items-center">
                <div className="w-2 h-2 bg-primary-500 rounded-full mr-2"></div>
                Proposal Management
              </div>
              <div className="flex items-center">
                <div className="w-2 h-2 bg-primary-500 rounded-full mr-2"></div>
                Document Processing
              </div>
              <div className="flex items-center">
                <div className="w-2 h-2 bg-primary-500 rounded-full mr-2"></div>
                Risk Assessment
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default LoginPage