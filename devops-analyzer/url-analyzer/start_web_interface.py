#!/usr/bin/env python3
"""
Quick Start Script for URL Issue Analyzer Web Interface

This script starts the web interface and opens it in your browser.
"""

import webbrowser
import time
import subprocess
import sys
import os

def main():
    print("🚀 Starting URL Issue Analyzer Web Interface")
    print("=" * 60)
    print("📋 Features:")
    print("   • Analyze any URL (websites, ALBs, Kubernetes endpoints)")
    print("   • DNS resolution testing")
    print("   • SSL certificate validation")
    print("   • Port connectivity checks")
    print("   • HTTP status monitoring")
    print("   • AI-powered issue diagnosis")
    print("   • Private analysis (no external data sharing)")
    print("=" * 60)
    
    # Check if Flask is installed
    try:
        import flask
        print("✅ Flask is installed")
    except ImportError:
        print("❌ Flask is not installed. Installing...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "flask"])
        print("✅ Flask installed successfully")
    
    print("\n🌐 Starting web server...")
    print("   Local: http://localhost:8080")
    print("   Network: http://0.0.0.0:8080")
    print("\n🔧 API Endpoints:")
    print("   • Web Interface: http://localhost:8080")
    print("   • Health Check: http://localhost:8080/health")
    print("   • Analysis API: http://localhost:8080/analyze")
    print("\n⏳ Waiting for server to start...")
    
    # Start the web interface in a subprocess
    try:
        # Start the web interface
        import threading
        import web_interface
        
        def run_server():
            web_interface.app.run(host='0.0.0.0', port=8080, debug=False, use_reloader=False)
        
        # Start server in background thread
        server_thread = threading.Thread(target=run_server, daemon=True)
        server_thread.start()
        
        # Wait a moment for server to start
        time.sleep(3)
        
        # Open browser
        print("🌐 Opening web interface in browser...")
        webbrowser.open('http://localhost:8080')
        
        print("\n✅ Web interface is running!")
        print("📝 Usage:")
        print("   1. Enter any URL in the input field")
        print("   2. Click 'Analyze Issues' to diagnose problems")
        print("   3. Review connectivity tests and AI analysis")
        print("   4. Get actionable troubleshooting steps")
        print("\n🔒 Privacy: All analysis happens on your local infrastructure")
        print("\n⚠️  Press Ctrl+C to stop the server")
        
        # Keep the main thread alive
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n\n🛑 Stopping web interface...")
            print("✅ Server stopped")
            
    except Exception as e:
        print(f"❌ Failed to start web interface: {e}")
        print("\n🔧 Manual start:")
        print("   python web_interface.py")
        print("   Then open http://localhost:8080 in your browser")

if __name__ == "__main__":
    main()
