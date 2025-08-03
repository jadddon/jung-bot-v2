export interface Database {
  public: {
    Tables: {
      users: {
        Row: {
          id: string
          email: string
          preferred_name: string | null
          created_at: string
          updated_at: string
          timezone: string | null
          total_sessions: number
          total_messages: number
        }
        Insert: {
          id?: string
          email: string
          preferred_name?: string | null
          created_at?: string
          updated_at?: string
          timezone?: string | null
          total_sessions?: number
          total_messages?: number
        }
        Update: {
          id?: string
          email?: string
          preferred_name?: string | null
          created_at?: string
          updated_at?: string
          timezone?: string | null
          total_sessions?: number
          total_messages?: number
        }
      }
      sessions: {
        Row: {
          id: string
          user_id: string | null
          title: string
          created_at: string
          updated_at: string
          last_activity: string
          is_anonymous: boolean
          context_summary: string | null
          message_count: number
        }
        Insert: {
          id?: string
          user_id?: string | null
          title: string
          created_at?: string
          updated_at?: string
          last_activity?: string
          is_anonymous?: boolean
          context_summary?: string | null
          message_count?: number
        }
        Update: {
          id?: string
          user_id?: string | null
          title?: string
          created_at?: string
          updated_at?: string
          last_activity?: string
          is_anonymous?: boolean
          context_summary?: string | null
          message_count?: number
        }
      }
      messages: {
        Row: {
          id: string
          session_id: string
          role: 'user' | 'assistant'
          content: string
          timestamp: string
          sources: any | null
          cost: number | null
          model_used: string | null
          tokens_used: number | null
        }
        Insert: {
          id?: string
          session_id: string
          role: 'user' | 'assistant'
          content: string
          timestamp?: string
          sources?: any | null
          cost?: number | null
          model_used?: string | null
          tokens_used?: number | null
        }
        Update: {
          id?: string
          session_id?: string
          role?: 'user' | 'assistant'
          content?: string
          timestamp?: string
          sources?: any | null
          cost?: number | null
          model_used?: string | null
          tokens_used?: number | null
        }
      }
    }
  }
} 