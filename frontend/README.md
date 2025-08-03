# Jung AI Frontend

A modern, responsive frontend for the Jung AI Analysis System built with Next.js, TypeScript, and Tailwind CSS. Features a clean, professional design inspired by the Jain Family Institute's aesthetic.

## 🚀 Features

- **Modern Chat Interface**: Real-time therapeutic conversations with Jung AI
- **JFI-Inspired Design**: Clean, professional styling with excellent typography
- **Responsive Layout**: Optimized for desktop and mobile devices
- **Session Management**: Anonymous and authenticated session handling
- **Sources Panel**: Display Jung text references and citations
- **Real-time Messaging**: Live chat with typing indicators
- **Error Handling**: Graceful error states and recovery

## 🛠️ Tech Stack

- **Framework**: Next.js 14 with App Router
- **Styling**: Tailwind CSS with custom design tokens
- **State Management**: Zustand with Immer
- **Authentication**: Supabase Auth
- **API Client**: Axios with interceptors
- **Icons**: Lucide React
- **TypeScript**: Full type safety

## 📱 Components

### Core Chat Components
- `ChatInterface`: Main chat container with JFI styling
- `MessageBubble`: Individual message display with sources
- `MessageInput`: Auto-resizing textarea with send functionality
- `TypingIndicator`: Animated typing indicator
- `SessionHeader`: Session controls and user menu
- `SourcesPanel`: Jung text sources display

### UI Components
- `WelcomeMessage`: Therapeutic onboarding
- `ErrorMessage`: Error handling and recovery
- Custom buttons, inputs, and cards

## 🎨 Design System

### Color Palette
- **Primary**: Professional grays for main content
- **Accent**: Blue tones for interactive elements
- **Therapeutic**: Warm tones for Jung AI responses

### Typography
- **Font**: Inter (Google Fonts)
- **Sizes**: Responsive typography scale
- **Spacing**: Consistent vertical rhythm

## 📦 Installation

```bash
npm install
```

## 🔧 Environment Variables

Create a `.env.local` file:

```env
# Supabase Configuration
NEXT_PUBLIC_SUPABASE_URL=your-supabase-url
NEXT_PUBLIC_SUPABASE_ANON_KEY=your-supabase-anon-key

# Backend API
NEXT_PUBLIC_API_URL=https://jung-bot-production.up.railway.app

# App Configuration
NEXT_PUBLIC_APP_URL=http://localhost:3000
```

## 🚀 Development

```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) to view the Jung AI interface.

## 📁 Project Structure

```
src/
├── app/                 # Next.js App Router
├── components/
│   ├── chat/           # Chat interface components
│   ├── auth/           # Authentication components
│   ├── session/        # Session management
│   └── ui/             # Reusable UI components
├── hooks/              # Custom React hooks
├── lib/                # Utility libraries
├── stores/             # Zustand stores
└── types/              # TypeScript definitions
```

## 🎯 Key Features Implemented

### ✅ Phase 1: Frontend Setup (COMPLETED)
- [x] Next.js project with TypeScript and Tailwind
- [x] Supabase client configuration
- [x] Authentication hooks
- [x] Core chat interface components
- [x] Session management store
- [x] Vercel deployment configuration

### 🔄 Next Steps (Phase 2)
- [ ] RAG implementation with sources display
- [ ] Session history and management
- [ ] Real-time features with SSE
- [ ] Production deployment to Vercel

## 🎨 Design Inspiration

The design draws inspiration from the [Jain Family Institute](https://jainfamilyinstitute.org/) with:
- Clean, typography-focused layout
- Professional color scheme
- Excellent use of white space
- Clear content hierarchy
- Readable, accessible design

## 🚀 Deployment

The frontend is configured for deployment on Vercel with automatic deployments from GitHub.

```bash
vercel --prod
```

## 📄 License

This project is part of the Jung AI Analysis System.
