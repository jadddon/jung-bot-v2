'use client'

import { useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { supabase } from '@/lib/supabase'
import { Loader2 } from 'lucide-react'

export default function AuthCallbackPage() {
  const router = useRouter()

  useEffect(() => {
    const handleAuthCallback = async () => {
      try {
        const { data, error } = await supabase.auth.getSession()
        
        if (error) {
          console.error('Auth callback error:', error)
          router.push('/?error=auth_failed')
          return
        }

        if (data.session) {
          // Check if user already exists in our database
          const { data: userData, error: userError } = await supabase
            .from('users')
            .select('*')
            .eq('id', data.session.user.id)
            .single()

          // If user doesn't exist, create them
          if (userError && userError.code === 'PGRST116') {
            const { error: insertError } = await supabase
              .from('users')
              .insert([
                {
                  id: data.session.user.id,
                  email: data.session.user.email,
                  preferred_name: data.session.user.user_metadata?.preferred_name || 
                                 data.session.user.user_metadata?.full_name || 
                                 data.session.user.user_metadata?.name || 
                                 null,
                  created_at: new Date().toISOString(),
                  updated_at: new Date().toISOString(),
                }
              ])

            if (insertError) {
              console.error('Error creating user:', insertError)
              // Continue anyway, as the auth user exists
            }
          }

          // Redirect to home with success
          router.push('/?auth=success')
        } else {
          // No session, redirect to home
          router.push('/')
        }
      } catch (error) {
        console.error('Auth callback error:', error)
        router.push('/?error=auth_failed')
      }
    }

    handleAuthCallback()
  }, [router])

  return (
    <div className="min-h-screen bg-gradient-to-br from-primary-50 to-therapeutic-50 flex items-center justify-center">
      <div className="text-center">
        <Loader2 className="h-8 w-8 animate-spin text-therapeutic-600 mx-auto mb-4" />
        <h2 className="text-xl font-semibold text-primary-900 mb-2">
          Completing Sign In
        </h2>
        <p className="text-primary-600">
          Please wait while we sign you in...
        </p>
      </div>
    </div>
  )
} 