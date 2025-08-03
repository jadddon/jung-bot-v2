'use client'
import { Brain, Heart, Moon, Star } from 'lucide-react'

export const WelcomeMessage = () => {
  return (
    <div className="text-center max-w-2xl mx-auto py-12 animate-fade-in">
      {/* Jung AI Logo/Icon */}
      <div className="w-16 h-16 mx-auto mb-6 bg-therapeutic-100 rounded-full flex items-center justify-center">
        <Brain size={32} className="text-therapeutic-600" />
      </div>

      {/* Welcome Title */}
      <h2 className="text-3xl font-bold text-primary-900 mb-4">
        Welcome to Jung AI Analysis
      </h2>

      {/* Subtitle */}
      <p className="text-lg text-primary-700 mb-8 leading-relaxed">
        I am here to help you explore your thoughts, dreams, and inner world through the lens of Jungian psychology.
      </p>

      {/* Feature Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
        <div className="card p-4 text-center">
          <div className="w-10 h-10 mx-auto mb-3 bg-accent-100 rounded-full flex items-center justify-center">
            <Moon size={20} className="text-accent-600" />
          </div>
          <h3 className="font-semibold text-primary-900 mb-2">Dream Analysis</h3>
          <p className="text-sm text-primary-600">Explore the symbols and meanings in your dreams</p>
        </div>

        <div className="card p-4 text-center">
          <div className="w-10 h-10 mx-auto mb-3 bg-therapeutic-100 rounded-full flex items-center justify-center">
            <Heart size={20} className="text-therapeutic-600" />
          </div>
          <h3 className="font-semibold text-primary-900 mb-2">Shadow Work</h3>
          <p className="text-sm text-primary-600">Understand your unconscious patterns</p>
        </div>

        <div className="card p-4 text-center">
          <div className="w-10 h-10 mx-auto mb-3 bg-accent-100 rounded-full flex items-center justify-center">
            <Star size={20} className="text-accent-600" />
          </div>
          <h3 className="font-semibold text-primary-900 mb-2">Individuation</h3>
          <p className="text-sm text-primary-600">Journey toward psychological wholeness</p>
        </div>
      </div>

      {/* Starter Prompts */}
      <div className="text-left space-y-3">
        <h3 className="text-lg font-semibold text-primary-900 mb-4">
          What would you like to explore today?
        </h3>
        <div className="space-y-2">
          <div className="text-sm text-primary-600 p-3 bg-primary-50 rounded-lg border border-primary-200">
            💭 "I had a strange dream last night..."
          </div>
          <div className="text-sm text-primary-600 p-3 bg-primary-50 rounded-lg border border-primary-200">
            🌟 "I'm feeling conflicted about a decision..."
          </div>
          <div className="text-sm text-primary-600 p-3 bg-primary-50 rounded-lg border border-primary-200">
            🔍 "I keep noticing patterns in my relationships..."
          </div>
        </div>
      </div>
    </div>
  )
} 