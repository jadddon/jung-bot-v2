#!/usr/bin/env python3
"""
Deployment helper utilities for Jung AI Analysis System
"""

import secrets
import string
import requests
import json
import sys
import os
from typing import Dict, Any, Optional

def generate_secret_key(length: int = 32) -> str:
    """Generate a secure secret key for JWT authentication."""
    return secrets.token_urlsafe(length)

def test_api_endpoint(url: str, endpoint: str = "/health") -> Dict[str, Any]:
    """Test API endpoint availability."""
    try:
        full_url = f"{url.rstrip('/')}{endpoint}"
        response = requests.get(full_url, timeout=10)
        return {
            "success": True,
            "status_code": response.status_code,
            "response": response.json() if response.headers.get('content-type', '').startswith('application/json') else response.text,
            "url": full_url
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "url": full_url
        }

def test_session_creation(api_url: str) -> Dict[str, Any]:
    """Test session creation endpoint."""
    try:
        url = f"{api_url.rstrip('/')}/sessions"
        data = {
            "title": "Test Session",
            "is_anonymous": True
        }
        response = requests.post(url, json=data, timeout=10)
        return {
            "success": True,
            "status_code": response.status_code,
            "response": response.json() if response.headers.get('content-type', '').startswith('application/json') else response.text,
            "url": url
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "url": url
        }

def test_auth_register(api_url: str, email: str = "test@example.com", password: str = "testpassword123") -> Dict[str, Any]:
    """Test user registration endpoint."""
    try:
        url = f"{api_url.rstrip('/')}/auth/register"
        data = {
            "email": email,
            "password": password,
            "preferred_name": "Test User"
        }
        response = requests.post(url, json=data, timeout=10)
        return {
            "success": True,
            "status_code": response.status_code,
            "response": response.json() if response.headers.get('content-type', '').startswith('application/json') else response.text,
            "url": url
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "url": url
        }

def generate_env_template() -> str:
    """Generate environment variables template with secure values."""
    secret_key = generate_secret_key()
    
    template = f"""# Jung AI Backend - Environment Variables
# Generated on: {__import__('datetime').datetime.now().isoformat()}

# Application Settings
DEBUG=false
HOST=0.0.0.0
PORT=8000
WORKERS=1

# Supabase Configuration (Get from supabase.com)
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_KEY=your-anon-key
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key

# Authentication (Generated secure key)
SECRET_KEY={secret_key}
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# OpenAI Configuration
OPENAI_API_KEY=your-openai-api-key
OPENAI_ORGANIZATION=your-openai-organization-id

# Cost Management
DAILY_BUDGET=1.00
MONTHLY_BUDGET=25.00
DEFAULT_MODEL=gpt-3.5-turbo
COMPLEX_MODEL=gpt-4-turbo-preview
EMBEDDING_MODEL=text-embedding-ada-002

# Pinecone Configuration (Optional)
PINECONE_API_KEY=your-pinecone-api-key
PINECONE_ENVIRONMENT=your-pinecone-environment
PINECONE_INDEX_NAME=jung-analysis

# Rate Limiting
RATE_LIMIT_PER_MINUTE=10
RATE_LIMIT_PER_HOUR=100
ANONYMOUS_RATE_LIMIT=5

# Session Management
SESSION_TIMEOUT_MINUTES=30
MAX_ANONYMOUS_SESSIONS=1000

# Memory Optimization (Railway 512MB)
MAX_REQUEST_SIZE=1048576
MAX_RESPONSE_SIZE=2097152

# Caching
CACHE_TTL=3600
MAX_CACHE_SIZE=1000

# Jung-specific Settings
MAX_CONTEXT_LENGTH=4000
MAX_RETRIEVAL_CHUNKS=5

# CORS Settings (Update with your domains)
CORS_ORIGINS=http://localhost:3000,https://your-app.vercel.app

# Logging
LOG_LEVEL=INFO
LOG_FORMAT=%(asctime)s - %(name)s - %(levelname)s - %(message)s

# Health Check
HEALTH_CHECK_INTERVAL=30
"""
    return template

def run_deployment_tests(api_url: str) -> Dict[str, Any]:
    """Run comprehensive deployment tests."""
    print(f"🧪 Testing Jung AI API deployment at: {api_url}")
    print("=" * 60)
    
    results = {}
    
    # Test 1: Health Check
    print("1. Testing health endpoint...")
    health_result = test_api_endpoint(api_url, "/health")
    results["health"] = health_result
    
    if health_result["success"]:
        print(f"   ✅ Health check passed (Status: {health_result['status_code']})")
    else:
        print(f"   ❌ Health check failed: {health_result['error']}")
    
    # Test 2: Session Creation
    print("\n2. Testing session creation...")
    session_result = test_session_creation(api_url)
    results["session"] = session_result
    
    if session_result["success"]:
        print(f"   ✅ Session creation passed (Status: {session_result['status_code']})")
    else:
        print(f"   ❌ Session creation failed: {session_result['error']}")
    
    # Test 3: Authentication
    print("\n3. Testing user registration...")
    auth_result = test_auth_register(api_url)
    results["auth"] = auth_result
    
    if auth_result["success"]:
        print(f"   ✅ User registration passed (Status: {auth_result['status_code']})")
    else:
        print(f"   ❌ User registration failed: {auth_result['error']}")
    
    # Summary
    print("\n" + "=" * 60)
    passed = sum(1 for r in results.values() if r["success"])
    total = len(results)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Your Jung AI API is ready.")
    else:
        print("⚠️  Some tests failed. Check the deployment guide for troubleshooting.")
    
    return results

def main():
    """Main CLI interface."""
    if len(sys.argv) < 2:
        print("Jung AI Deployment Helper")
        print("Usage:")
        print("  python deploy_helpers.py generate-key     # Generate secure secret key")
        print("  python deploy_helpers.py generate-env     # Generate environment template")
        print("  python deploy_helpers.py test <api-url>   # Test API deployment")
        print("  python deploy_helpers.py full-test <api-url>  # Run full deployment tests")
        sys.exit(1)
    
    command = sys.argv[1].lower()
    
    if command == "generate-key":
        key = generate_secret_key()
        print(f"🔑 Generated secure secret key:")
        print(key)
        print("\n💡 Add this to your Railway environment variables as SECRET_KEY")
    
    elif command == "generate-env":
        env_template = generate_env_template()
        print("📝 Generated environment variables template:")
        print(env_template)
        print("\n💡 Copy this to your .env file or Railway environment variables")
    
    elif command == "test":
        if len(sys.argv) < 3:
            print("❌ Please provide API URL: python deploy_helpers.py test <api-url>")
            sys.exit(1)
        
        api_url = sys.argv[2]
        result = test_api_endpoint(api_url)
        
        if result["success"]:
            print(f"✅ API test passed!")
            print(f"Status: {result['status_code']}")
            print(f"Response: {json.dumps(result['response'], indent=2)}")
        else:
            print(f"❌ API test failed: {result['error']}")
    
    elif command == "full-test":
        if len(sys.argv) < 3:
            print("❌ Please provide API URL: python deploy_helpers.py full-test <api-url>")
            sys.exit(1)
        
        api_url = sys.argv[2]
        run_deployment_tests(api_url)
    
    else:
        print(f"❌ Unknown command: {command}")
        print("Use 'python deploy_helpers.py' for usage instructions")
        sys.exit(1)

if __name__ == "__main__":
    main() 