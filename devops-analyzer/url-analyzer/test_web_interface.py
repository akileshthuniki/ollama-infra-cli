#!/usr/bin/env python3
"""
Test script for the web interface URL analysis
"""

import requests
import json
import time

def test_url_analysis():
    """Test the URL analysis endpoint."""
    
    base_url = "http://localhost:8080"
    
    print("🧪 Testing URL Issue Analyzer Web Interface")
    print("=" * 50)
    
    # Test health endpoint
    try:
        response = requests.get(f"{base_url}/health", timeout=5)
        print(f"✅ Health check: {response.status_code}")
        print(f"   Response: {response.json()}")
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return
    
    # Test URL analysis with a simple site
    test_urls = [
        "https://httpbin.org/status/200",  # Should work quickly
        "https://google.com",              # Reliable site
        "https://ollama-alb-427582956.us-east-1.elb.amazonaws.com"  # Your ALB
    ]
    
    for url in test_urls:
        print(f"\n🔍 Testing: {url}")
        print("-" * 30)
        
        try:
            start_time = time.time()
            response = requests.post(
                f"{base_url}/analyze",
                json={"url": url},
                headers={"Content-Type": "application/json"},
                timeout=60
            )
            end_time = time.time()
            
            print(f"✅ Analysis completed in {end_time - start_time:.2f}s")
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"   URL: {data.get('url')}")
                print(f"   Timestamp: {data.get('timestamp')}")
                
                connectivity = data.get('connectivity', {})
                print(f"   DNS: {'✅' if connectivity.get('dns_resolution', {}).get('success') else '❌'}")
                print(f"   Port: {'✅' if connectivity.get('connectivity_tests', {}).get('port', {}).get('success') else '❌'}")
                print(f"   SSL: {'✅' if connectivity.get('ssl_info', {}).get('success') else '❌'}")
                
                if connectivity.get('http_status', {}).get('status_code'):
                    print(f"   HTTP: {connectivity['http_status']['status_code']}")
                
                print(f"   Errors: {len(connectivity.get('errors', []))}")
                
                # Show AI analysis preview
                ai_analysis = data.get('ai_analysis', '')
                if ai_analysis:
                    preview = ai_analysis[:200] + "..." if len(ai_analysis) > 200 else ai_analysis
                    print(f"   AI Preview: {preview}")
                
                ai_metadata = data.get('ai_metadata', {})
                if ai_metadata.get('processing_time_ms'):
                    print(f"   AI Processing: {ai_metadata['processing_time_ms']:.2f}ms")
                
            else:
                print(f"   Error: {response.text}")
                
        except requests.exceptions.Timeout:
            print("⏰ Request timed out")
        except Exception as e:
            print(f"❌ Test failed: {e}")

if __name__ == "__main__":
    test_url_analysis()
