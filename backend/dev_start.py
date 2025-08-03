import os
import uvicorn

# Load environment variables from .env
env_file = '.env'
if os.path.exists(env_file):
    with open(env_file, 'r') as f:
        for line in f:
            if '=' in line and not line.startswith('#'):
                key, value = line.strip().split('=', 1)
                os.environ[key] = value

# Set required placeholder values
required_placeholders = {
    'SUPABASE_URL': 'placeholder',
    'SUPABASE_KEY': 'placeholder', 
    'SUPABASE_SERVICE_ROLE_KEY': 'placeholder',
    'SECRET_KEY': 'placeholder'
}

for key, value in required_placeholders.items():
    if key not in os.environ:
        os.environ[key] = value

print("🚀 Starting Jung Bot Backend (DEV MODE - Auto-reload enabled)...")
print(f"✅ OpenAI API Key: {'Set' if os.environ.get('OPENAI_API_KEY') else 'Not set'}")
print(f"✅ Pinecone API Key: {'Set' if os.environ.get('PINECONE_API_KEY') else 'Not set'}")
print(f"🌐 Backend will be available at: http://localhost:8000")
print("🔄 Auto-reload enabled - changes will restart the server automatically")

if __name__ == "__main__":
    uvicorn.run("api.main:app", host="0.0.0.0", port=8000, log_level="info", reload=True) 