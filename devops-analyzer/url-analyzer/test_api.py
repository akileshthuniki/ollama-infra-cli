#!/usr/bin/env python3
"""
Simple test script to verify API connectivity
"""

import requests
import json

def test_api():
    api_url = "http://ollama-alb-427582956.us-east-1.elb.amazonaws.com"
    
    print("🧪 Testing Ollama API connectivity...")
    
    # Test 1: Health check
    try:
        response = requests.get(f"{api_url}/health", timeout=10)
        print(f"✅ Health check: {response.status_code}")
        print(f"   Response: {response.json()}")
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return
    
    # Test 2: Simple analyze request
    try:
        simple_prompt = "Analyze this AWS ECS cluster with 2 services and 4 running tasks. Provide a brief architecture overview."
        
        response = requests.post(
            f"{api_url}/api/analyze",
            json={"prompt": simple_prompt, "context": "test"},
            headers={"Content-Type": "application/json"},
            timeout=60
        )
        
        print(f"✅ Analyze API: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"   Processing time: {result.get('processing_time_ms', 0)}ms")
            print(f"   Model: {result.get('model', 'unknown')}")
            print(f"   Response preview: {result.get('response', '')[:200]}...")
        else:
            print(f"   Error: {response.text}")
            
    except Exception as e:
        print(f"❌ Analyze API failed: {e}")

if __name__ == "__main__":
    test_api()
