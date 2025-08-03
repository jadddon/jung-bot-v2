
## 🚀 **[Try Jung AI Live →](https://jung-bot.vercel.app/)**

# Jung AI - Analytical Psychology Chatbot

## 🌙 **The Story Behind This Project**

I started having a series of strange, vivid dreams that left me curious about their deeper meaning. As I dove into Carl Jung's work on dream analysis and the unconscious mind, I realized I wanted a way to engage directly with his insights—not just read about them, but have conversations about my dreams and psychological experiences.

That's when I decided to build this **Retrieval-Augmented Generation (RAG)** system: an AI that could discuss analytical psychology while **directly citing specific passages and page numbers** from Jung's complete collected works. Now, when the AI explains a concept like the "shadow" or interprets a dream symbol, it can reference the exact text where Jung wrote about it.



## 📋 **Overview**

This full-stack application enables meaningful conversations about dreams, archetypes, individuation, and other Jungian concepts. The system processes over **57,000 text chunks** from Jung's collected works, allowing the AI to provide contextually relevant responses with **direct citations to specific passages and page numbers** from the original texts.

## 🛠 **Tech Stack**

### **Frontend**
- **Next.js 14** with TypeScript
- **Tailwind CSS** for styling  
- **Zustand** for state management
- **Axios** for API communication
- **Vercel** deployment

### **Backend**
- **FastAPI** with Python
- **Pydantic** for data validation
- **Uvicorn** ASGI server
- **Railway** deployment

### **AI & Data**
- **OpenAI GPT-4** for conversational AI
- **OpenAI text-embedding-3-small** for vector embeddings
- **Pinecone** vector database (57k+ embeddings)
- **Custom text processing pipeline** with page-level granularity

### **Authentication & Database**
- **Supabase** for user authentication
- **PostgreSQL** for session storage
- **Anonymous sessions** supported

## ✨ **Key Features**

- **🧠 RAG Architecture**: Retrieves relevant Jung passages before generating responses
- **📖 Direct Citations**: Shows exact passages and page numbers from Jung's collected works
- **💬 Contextual Conversations**: Maintains session history for coherent dialogue  
- **🌙 Dream Analysis**: Specialized in interpreting dreams through Jungian lens
- **🔐 Flexible Auth**: Support for both authenticated and anonymous users
- **📱 Responsive Design**: Clean, therapeutic UI across all devices
- **⚡ Real-time Processing**: Fast vector similarity search and response generation

## 🏗 **Architecture**

```
┌─────────────────┐    ┌───────────────────┐    ┌─────────────────┐
│   Next.js UI   │────│   FastAPI Backend │────│  Pinecone VectorDB │
│   (Vercel)     │    │   (Railway)       │    │   (57k+ chunks)   │
└─────────────────┘    └───────────────────┘    └─────────────────┘
         │                        │                        │
         │                        │                        │
    ┌─────────┐              ┌─────────┐              ┌─────────┐
    │Supabase │              │OpenAI   │              │Jung's   │
    │Auth     │              │GPT-4    │              │Collected│
    │         │              │         │              │Works    │
    └─────────┘              └─────────┘              └─────────┘
```

## 📊 **Project Highlights**

- **Direct Source Citations**: AI responses include specific page references from Jung's texts
- **Sophisticated Data Pipeline**: Custom text processing preserving page-level metadata
- **Vector Similarity Search**: Efficient retrieval from 57,000+ text embeddings  
- **Production Architecture**: Scalable deployment on Railway + Vercel
- **Enterprise-Ready**: Authentication, session management, error handling
- **Cost-Optimized**: Smart chunking and embedding strategies

## 🚀 **Getting Started**

### **Prerequisites**
- Node.js 18+
- Python 3.9+
- OpenAI API key
- Pinecone API key
- Supabase project


## 📈 **Development Process**

This project demonstrates:
- **Full-stack AI application** development
- **RAG system** implementation with citation tracking
- **Vector database** integration and metadata preservation
- **Production deployment** and DevOps practices
- **API design** and documentation
- **Modern frontend** development with TypeScript

## 🎯 **Future Enhancements**

- Advanced conversation memory
- Enhanced dream symbol database
- Multi-language support  
- Voice interface integration
- Academic citation formatting
- Integration with dream journaling
