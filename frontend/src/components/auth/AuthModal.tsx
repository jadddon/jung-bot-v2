'use client'
import { useState } from 'react'
import { X, Mail, Lock, User, Eye, EyeOff, Loader2 } from 'lucide-react'
import { useAuth } from '@/hooks/useAuth'

interface AuthModalProps {
  isOpen: boolean
  onClose: () => void
  defaultMode?: 'signin' | 'signup'
}

export const AuthModal = ({ isOpen, onClose, defaultMode = 'signin' }: AuthModalProps) => {
  const [mode, setMode] = useState<'signin' | 'signup'>(defaultMode)
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [preferredName, setPreferredName] = useState('')
  const [showPassword, setShowPassword] = useState(false)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')

  const { signIn, signUp, signInWithGoogle } = useAuth()

  const resetForm = () => {
    setEmail('')
    setPassword('')
    setPreferredName('')
    setError('')
    setSuccess('')
    setShowPassword(false)
  }

  const handleClose = () => {
    resetForm()
    onClose()
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setSuccess('')
    setLoading(true)

    try {
      if (mode === 'signin') {
        await signIn(email, password)
        setSuccess('Successfully signed in!')
        setTimeout(() => {
          handleClose()
        }, 1000)
      } else {
        await signUp(email, password, preferredName)
        setSuccess('Account created successfully! Please check your email to verify your account.')
        setTimeout(() => {
          setMode('signin')
          setSuccess('')
        }, 2000)
      }
    } catch (error: any) {
      setError(error.message || 'An error occurred')
    } finally {
      setLoading(false)
    }
  }

  const switchMode = () => {
    setMode(mode === 'signin' ? 'signup' : 'signin')
    resetForm()
  }

  const handleGoogleSignIn = async () => {
    setError('')
    setSuccess('')
    setLoading(true)
    
    try {
      await signInWithGoogle()
      // The redirect will handle the success case
    } catch (error: any) {
      setError(error.message || 'Google sign-in failed')
      setLoading(false)
    }
  }

  if (!isOpen) return null

  return (
    <div 
      className="fixed inset-0 z-[9999] bg-black bg-opacity-100 backdrop-blur-sm"
      onClick={handleClose}
    >
      {/* Modal Container */}
      <div className="flex min-h-screen items-center justify-center p-4">
        <div 
          className="relative w-full max-w-md bg-white rounded-xl shadow-2xl"
          onClick={(e) => e.stopPropagation()}
        >
          {/* Header */}
          <div className="flex items-center justify-between p-6 border-b border-primary-200">
            <h2 className="text-2xl font-bold text-primary-900">
              {mode === 'signin' ? 'Sign In' : 'Create Account'}
            </h2>
            <button
              onClick={handleClose}
              className="rounded-full p-2 text-primary-400 hover:text-primary-600 hover:bg-primary-100 transition-colors"
            >
              <X size={20} />
            </button>
          </div>

          {/* Content */}
          <div className="p-6">
            {/* Welcome Message */}
            <div className="mb-6 text-center">
              <h3 className="text-lg font-semibold text-primary-900 mb-2">
                {mode === 'signin' ? 'Welcome back!' : 'Join Jung AI Analysis'}
              </h3>
              <p className="text-primary-600 text-sm">
                {mode === 'signin' 
                  ? 'Access your previous sessions and continue your psychological journey'
                  : 'Create an account to save your sessions and track your progress'
                }
              </p>
            </div>

            {/* Error/Success Messages */}
            {error && (
              <div className="mb-4 p-3 bg-error-50 border border-error-200 rounded-lg">
                <p className="text-error-700 text-sm">{error}</p>
              </div>
            )}
            {success && (
              <div className="mb-4 p-3 bg-success-50 border border-success-200 rounded-lg">
                <p className="text-success-700 text-sm">{success}</p>
              </div>
            )}

            {/* Form */}
            <form onSubmit={handleSubmit} className="space-y-4">
              {/* Name Field (Sign Up Only) */}
              {mode === 'signup' && (
                <div>
                  <label htmlFor="preferredName" className="block text-sm font-medium text-primary-700 mb-2">
                    Preferred Name (Optional)
                  </label>
                  <div className="relative">
                    <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                      <User className="h-5 w-5 text-primary-400" />
                    </div>
                    <input
                      type="text"
                      id="preferredName"
                      value={preferredName}
                      onChange={(e) => setPreferredName(e.target.value)}
                      className="w-full pl-10 pr-3 py-2 border border-primary-300 rounded-lg focus:ring-2 focus:ring-therapeutic-500 focus:border-transparent transition-colors"
                      placeholder="How would you like to be addressed?"
                    />
                  </div>
                </div>
              )}

              {/* Email Field */}
              <div>
                <label htmlFor="email" className="block text-sm font-medium text-primary-700 mb-2">
                  Email Address
                </label>
                <div className="relative">
                  <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                    <Mail className="h-5 w-5 text-primary-400" />
                  </div>
                  <input
                    type="email"
                    id="email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    className="w-full pl-10 pr-3 py-2 border border-primary-300 rounded-lg focus:ring-2 focus:ring-therapeutic-500 focus:border-transparent transition-colors"
                    placeholder="your@email.com"
                    required
                  />
                </div>
              </div>

              {/* Password Field */}
              <div>
                <label htmlFor="password" className="block text-sm font-medium text-primary-700 mb-2">
                  Password
                </label>
                <div className="relative">
                  <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                    <Lock className="h-5 w-5 text-primary-400" />
                  </div>
                  <input
                    type={showPassword ? 'text' : 'password'}
                    id="password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    className="w-full pl-10 pr-12 py-2 border border-primary-300 rounded-lg focus:ring-2 focus:ring-therapeutic-500 focus:border-transparent transition-colors"
                    placeholder="Enter your password"
                    required
                    minLength={8}
                  />
                  <button
                    type="button"
                    className="absolute inset-y-0 right-0 pr-3 flex items-center text-primary-400 hover:text-primary-600 transition-colors"
                    onClick={() => setShowPassword(!showPassword)}
                  >
                    {showPassword ? (
                      <EyeOff className="h-5 w-5" />
                    ) : (
                      <Eye className="h-5 w-5" />
                    )}
                  </button>
                </div>
                {mode === 'signup' && (
                  <p className="text-xs text-primary-600 mt-1">
                    Password must be at least 8 characters long
                  </p>
                )}
              </div>

              {/* Submit Button */}
              <button
                type="submit"
                disabled={loading}
                className="w-full py-3 px-4 bg-gradient-to-r from-therapeutic-600 to-therapeutic-700 hover:from-therapeutic-700 hover:to-therapeutic-800 text-white font-medium rounded-lg transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center focus:outline-none focus:ring-2 focus:ring-therapeutic-500 focus:ring-offset-2"
              >
                {loading ? (
                  <>
                    <Loader2 className="animate-spin h-5 w-5 mr-2" />
                    {mode === 'signin' ? 'Signing in...' : 'Creating account...'}
                  </>
                ) : (
                  mode === 'signin' ? 'Sign In' : 'Create Account'
                )}
              </button>
            </form>

            {/* Divider */}
            <div className="my-6 flex items-center">
              <div className="flex-1 border-t border-primary-200"></div>
              <div className="px-4 text-sm text-primary-500">or</div>
              <div className="flex-1 border-t border-primary-200"></div>
            </div>

            {/* Google Sign In */}
            <button
              onClick={handleGoogleSignIn}
              disabled={loading}
              className="w-full py-3 px-4 bg-white border border-primary-300 hover:bg-primary-50 text-primary-700 font-medium rounded-lg transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center focus:outline-none focus:ring-2 focus:ring-therapeutic-500 focus:ring-offset-2"
            >
              {loading ? (
                <>
                  <Loader2 className="animate-spin h-5 w-5 mr-2" />
                  Signing in with Google...
                </>
              ) : (
                <>
                  <svg className="h-5 w-5 mr-2" viewBox="0 0 24 24">
                    <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
                    <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
                    <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/>
                    <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/>
                  </svg>
                  Continue with Google
                </>
              )}
            </button>

            {/* Switch Mode */}
            <div className="mt-6 text-center">
              <p className="text-sm text-primary-600">
                {mode === 'signin' ? "Don't have an account?" : 'Already have an account?'}
                <button
                  onClick={switchMode}
                  className="ml-2 text-therapeutic-600 hover:text-therapeutic-700 font-medium transition-colors focus:outline-none focus:underline"
                >
                  {mode === 'signin' ? 'Create one' : 'Sign in'}
                </button>
              </p>
            </div>

            {/* Guest Mode */}
            <div className="mt-6 pt-4 border-t border-primary-200 text-center">
              <p className="text-sm text-primary-600 mb-2">
                Or continue as a guest
              </p>
              <button
                onClick={handleClose}
                className="text-sm text-primary-500 hover:text-primary-700 underline transition-colors focus:outline-none focus:text-primary-700"
              >
                Continue without account
              </button>
              <p className="text-xs text-primary-400 mt-1">
                Note: Guest sessions are not saved
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
} 