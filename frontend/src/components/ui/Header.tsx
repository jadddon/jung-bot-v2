'use client'
import { useState } from 'react'
import { Menu, X, User, Settings, LogOut } from 'lucide-react'
import { useAuth } from '@/hooks/useAuth'

export const Header = () => {
  const [isMenuOpen, setIsMenuOpen] = useState(false)
  const { user, signOut } = useAuth()

  const handleSignOut = async () => {
    try {
      await signOut()
    } catch (error) {
      console.error('Error signing out:', error)
    }
  }

  return (
    <header className="bg-white border-b border-gray-100 sticky top-0 z-50">
      <div className="content-container">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <div className="flex items-center">
            <h1 className="text-2xl font-bold text-gray-900">
              Jung AI Analysis
            </h1>
          </div>

          {/* Desktop Navigation */}
          <nav className="hidden md:flex items-center space-x-8">
            <a href="#" className="nav-link">Our Work</a>
            <a href="#" className="nav-link">Publications</a>
            <a href="#" className="nav-link">About</a>
            
            {user ? (
              <div className="flex items-center space-x-4">
                <div className="flex items-center space-x-2">
                  <User className="h-5 w-5 text-gray-500" />
                  <span className="text-sm text-gray-600">
                    {user.email}
                  </span>
                </div>
                <button
                  onClick={handleSignOut}
                  className="btn-ghost text-sm flex items-center"
                >
                  <LogOut className="h-4 w-4 mr-1" />
                  Sign Out
                </button>
              </div>
            ) : (
              <div className="flex items-center space-x-4">
                <button className="btn-ghost text-sm">Sign In</button>
                <button className="btn-primary text-sm">Get Started</button>
              </div>
            )}
          </nav>

          {/* Mobile menu button */}
          <div className="md:hidden">
            <button
              onClick={() => setIsMenuOpen(!isMenuOpen)}
              className="inline-flex items-center justify-center p-2 rounded-md text-gray-600 hover:text-gray-900 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-inset focus:ring-gray-500"
            >
              {isMenuOpen ? (
                <X className="h-6 w-6" />
              ) : (
                <Menu className="h-6 w-6" />
              )}
            </button>
          </div>
        </div>

        {/* Mobile menu */}
        {isMenuOpen && (
          <div className="md:hidden border-t border-gray-100 py-4">
            <div className="flex flex-col space-y-4">
              <a href="#" className="nav-link">Our Work</a>
              <a href="#" className="nav-link">Publications</a>
              <a href="#" className="nav-link">About</a>
              
              {user ? (
                <div className="flex flex-col space-y-4 pt-4 border-t border-gray-100">
                  <div className="flex items-center space-x-2">
                    <User className="h-5 w-5 text-gray-500" />
                    <span className="text-sm text-gray-600">
                      {user.email}
                    </span>
                  </div>
                  <button
                    onClick={handleSignOut}
                    className="btn-ghost text-sm justify-start flex items-center"
                  >
                    <LogOut className="h-4 w-4 mr-2" />
                    Sign Out
                  </button>
                </div>
              ) : (
                <div className="flex flex-col space-y-4 pt-4 border-t border-gray-100">
                  <button className="btn-ghost text-sm">Sign In</button>
                  <button className="btn-primary text-sm">Get Started</button>
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </header>
  )
} 