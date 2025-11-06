#!/usr/bin/env python3
"""
URL Analyzer - CLI Tool for URL Issue Analysis

A command-line tool to analyze any URL (websites, ALBs, Kubernetes endpoints)
and get AI-powered troubleshooting recommendations.

Usage:
    python analyze_url.py <url> [--question "your question"]
    python analyze_url.py https://your-alb.amazonaws.com
    python analyze_url.py https://example.com --question "Why is this slow?"
"""

import sys
import argparse
import requests
import json
from datetime import datetime
import socket
import urllib.parse
import ssl

class URLAnalyzer:
    def __init__(self, ollama_api_url: str):
        self.ollama_api_url = ollama_api_url
    
    def analyze_url_connectivity(self, url: str) -> dict:
        """Analyze URL connectivity and basic issues."""
        try:
            parsed = urllib.parse.urlparse(url)
            hostname = parsed.hostname
            port = parsed.port or (443 if parsed.scheme == 'https' else 80)
            
            result = {
                'url': url,
                'hostname': hostname,
                'port': port,
                'scheme': parsed.scheme,
                'connectivity_tests': {},
                'dns_resolution': None,
                'ssl_info': None,
                'http_status': None,
                'response_time': None,
                'errors': []
            }
            
            # DNS Resolution Test
            try:
                ip_address = socket.gethostbyname(hostname)
                result['dns_resolution'] = {
                    'success': True,
                    'ip_address': ip_address
                }
            except Exception as e:
                result['dns_resolution'] = {
                    'success': False,
                    'error': str(e)
                }
                result['errors'].append(f"DNS Resolution failed: {str(e)}")
            
            # Port Connectivity Test
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(5)
                connection_result = sock.connect_ex((hostname, port))
                result['connectivity_tests']['port'] = {
                    'success': connection_result == 0,
                    'port_open': connection_result == 0
                }
                sock.close()
            except Exception as e:
                result['connectivity_tests']['port'] = {
                    'success': False,
                    'error': str(e)
                }
                result['errors'].append(f"Port connection failed: {str(e)}")
            
            # SSL Certificate Test (for HTTPS)
            if parsed.scheme == 'https':
                try:
                    ssl_context = ssl.create_default_context()
                    with socket.create_connection((hostname, port), timeout=5) as sock:
                        with ssl_context.wrap_socket(sock, server_hostname=hostname) as ssock:
                            cert = ssock.getpeercert()
                            result['ssl_info'] = {
                                'success': True,
                                'subject': cert.get('subject'),
                                'issuer': cert.get('issuer'),
                                'version': cert.get('version'),
                                'serial_number': cert.get('serialNumber'),
                                'not_before': cert.get('notBefore'),
                                'not_after': cert.get('notAfter')
                            }
                except Exception as e:
                    result['ssl_info'] = {
                        'success': False,
                        'error': str(e)
                    }
                    result['errors'].append(f"SSL Certificate issue: {str(e)}")
            
            # HTTP Status Test
            try:
                start_time = datetime.now()
                response = requests.get(url, timeout=10, allow_redirects=True)
                end_time = datetime.now()
                
                result['http_status'] = {
                    'status_code': response.status_code,
                    'status_text': response.reason,
                    'redirects': len(response.history),
                    'final_url': response.url
                }
                result['response_time'] = {
                    'milliseconds': (end_time - start_time).total_seconds() * 1000
                }
                
                if response.status_code >= 400:
                    result['errors'].append(f"HTTP Error {response.status_code}: {response.reason}")
                    
            except requests.exceptions.Timeout:
                result['http_status'] = {'error': 'Request timeout'}
                result['errors'].append("Request timed out")
            except requests.exceptions.ConnectionError as e:
                result['http_status'] = {'error': 'Connection error'}
                result['errors'].append(f"Connection error: {str(e)}")
            except Exception as e:
                result['http_status'] = {'error': str(e)}
                result['errors'].append(f"HTTP request failed: {str(e)}")
            
            return result
            
        except Exception as e:
            return {
                'url': url,
                'error': f"Analysis failed: {str(e)}",
                'errors': [str(e)]
            }
    
    def get_ai_analysis(self, url: str, question: str = None, connectivity_data: dict = None) -> str:
        """Get AI analysis of URL issues."""
        try:
            if not connectivity_data:
                connectivity_data = self.analyze_url_connectivity(url)
            
            # Create a summary of connectivity data
            summary = []
            
            if connectivity_data.get('dns_resolution', {}).get('success'):
                summary.append(f"✅ DNS resolves to {connectivity_data['dns_resolution']['ip_address']}")
            else:
                summary.append(f"❌ DNS resolution failed")
            
            if connectivity_data.get('connectivity_tests', {}).get('port', {}).get('success'):
                summary.append(f"✅ Port {connectivity_data['port']} is open")
            else:
                summary.append(f"❌ Port {connectivity_data['port']} is closed or blocked")
            
            if connectivity_data.get('ssl_info', {}).get('success'):
                summary.append(f"✅ SSL certificate is valid")
            else:
                summary.append(f"❌ SSL certificate issue detected")
            
            if connectivity_data.get('http_status', {}).get('status_code'):
                status = connectivity_data['http_status']['status_code']
                if 200 <= status < 300:
                    summary.append(f"✅ HTTP status {status} (OK)")
                elif 300 <= status < 400:
                    summary.append(f"⚠️  HTTP status {status} (Redirect)")
                else:
                    summary.append(f"❌ HTTP status {status} (Error)")
            
            if connectivity_data.get('response_time'):
                response_time = connectivity_data['response_time']['milliseconds']
                if response_time < 1000:
                    summary.append(f"✅ Response time {response_time:.0f}ms (Good)")
                elif response_time < 3000:
                    summary.append(f"⚠️  Response time {response_time:.0f}ms (Slow)")
                else:
                    summary.append(f"❌ Response time {response_time:.0f}ms (Very slow)")
            
            if connectivity_data.get('errors'):
                summary.append("\n🚨 Issues detected:")
                for error in connectivity_data['errors']:
                    summary.append(f"   • {error}")
            
            # Create prompt for AI
            if question:
                prompt = f"""
                Analyze this URL and answer the user's specific question:
                
                URL: {url}
                User Question: {question}
                
                Test Results:
                {chr(10).join(summary)}
                
                Please provide a detailed answer to their question based on the connectivity data.
                Focus on their specific concern and provide actionable recommendations.
                """
            else:
                prompt = f"""
                Analyze this URL and diagnose the issues:
                
                URL: {url}
                
                Test Results:
                {chr(10).join(summary)}
                
                Please provide:
                1. Root cause analysis of the issues
                2. Specific troubleshooting steps
                3. Priority level (Critical/High/Medium/Low)
                4. Estimated time to resolve
                5. Prevention recommendations
                
                Be concise and actionable.
                """
            
            # Call AI API
            response = requests.post(
                f"{self.ollama_api_url}/api/analyze",
                json={"prompt": prompt, "context": "url-analysis"},
                headers={"Content-Type": "application/json"},
                timeout=15
            )
            
            if response.status_code == 200:
                return response.json().get('response', 'No AI response available')
            else:
                return f'AI API returned status {response.status_code}: {response.text}'
                
        except requests.exceptions.Timeout:
            return 'AI API timeout - using fallback analysis'
        except Exception as e:
            return f'AI analysis failed: {str(e)}'
    
    def generate_fallback_analysis(self, url: str, question: str = None, connectivity_data: dict = None) -> str:
        """Generate fallback analysis when AI is unavailable."""
        if not connectivity_data:
            connectivity_data = self.analyze_url_connectivity(url)
        
        analysis = f"""
# URL Analysis Report

**URL:** {url}
**Analyzed:** {datetime.now().isoformat()}

## 🔍 Test Results

### Connectivity Tests
"""
        
        if connectivity_data.get('dns_resolution', {}).get('success'):
            analysis += f"✅ **DNS Resolution:** {connectivity_data['dns_resolution']['ip_address']}\n"
        else:
            analysis += "❌ **DNS Resolution:** Failed\n"
        
        if connectivity_data.get('connectivity_tests', {}).get('port', {}).get('success'):
            analysis += f"✅ **Port {connectivity_data['port']}:** Open\n"
        else:
            analysis += f"❌ **Port {connectivity_data['port']}:** Closed or blocked\n"
        
        if connectivity_data.get('ssl_info', {}).get('success'):
            analysis += "✅ **SSL Certificate:** Valid\n"
        else:
            analysis += "❌ **SSL Certificate:** Invalid or expired\n"
        
        if connectivity_data.get('http_status', {}).get('status_code'):
            status = connectivity_data['http_status']['status_code']
            analysis += f"{'✅' if 200 <= status < 300 else '❌'} **HTTP Status:** {status} {connectivity_data['http_status']['status_text']}\n"
        
        if connectivity_data.get('response_time'):
            response_time = connectivity_data['response_time']['milliseconds']
            analysis += f"{'✅' if response_time < 1000 else '⚠️'} **Response Time:** {response_time:.0f}ms\n"
        
        analysis += "\n## 🚨 Issues Found\n"
        
        if connectivity_data.get('errors'):
            for error in connectivity_data['errors']:
                analysis += f"• {error}\n"
        else:
            analysis += "No critical issues detected.\n"
        
        if question:
            analysis += f"\n## 🤖 Analysis for Your Question\n\n**Question:** {question}\n\n"
            
            # Provide specific recommendations based on question
            question_lower = question.lower()
            
            if 'improve' in question_lower or 'optimiz' in question_lower:
                analysis += "### 🚀 Improvement Recommendations:\n"
                if connectivity_data.get('response_time', {}).get('milliseconds', 0) > 1000:
                    analysis += "• Response time is slow - consider caching and CDN\n"
                analysis += "• Set up comprehensive monitoring\n"
                analysis += "• Implement automated health checks\n"
                analysis += "• Use performance monitoring tools\n"
            elif 'slow' in question_lower or 'performance' in question_lower:
                analysis += "### ⚡ Performance Analysis:\n"
                analysis += "• Check server load and resource utilization\n"
                analysis += "• Implement caching at multiple levels\n"
                analysis += "• Consider using a Content Delivery Network (CDN)\n"
            elif 'secure' in question_lower or 'security' in question_lower:
                analysis += "### 🔒 Security Recommendations:\n"
                if not connectivity_data.get('ssl_info', {}).get('success'):
                    analysis += "• Fix SSL certificate issues immediately\n"
                analysis += "• Implement HTTPS redirects\n"
                analysis += "• Add security headers (HSTS, CSP)\n"
            else:
                analysis += "### 📊 General Recommendations:\n"
                analysis += "• Monitor performance and availability\n"
                analysis += "• Implement proper logging and alerting\n"
                analysis += "• Regular security assessments\n"
        
        analysis += """
## 🔧 General Troubleshooting Steps

### Immediate Steps
1. **Check URL spelling** - Ensure the URL is correct
2. **Network connectivity** - Verify internet connection
3. **Firewall settings** - Check if ports are blocked
4. **DNS settings** - Verify DNS resolution
5. **Service status** - Check if the target service is running

### Specific Issues
- **DNS Failures:** Check DNS configuration, try alternative DNS
- **Port Blocked:** Verify firewall rules, check service listening port
- **SSL Issues:** Update certificate, check certificate chain
- **HTTP Errors:** Check service logs, verify configuration
- **Slow Response:** Check server load, network latency

## 📊 Priority Assessment
"""
        
        errors = connectivity_data.get('errors', [])
        if not errors:
            analysis += "🟢 **Priority: Low** - No critical issues\n"
        elif len(errors) <= 2:
            analysis += "🟡 **Priority: Medium** - Some issues detected\n"
        else:
            analysis += "🔴 **Priority: High** - Multiple critical issues\n"
        
        analysis += """
## 🛡️ Prevention Recommendations
- Implement monitoring and alerting
- Use load balancers for high availability
- Regular SSL certificate renewal
- Performance monitoring and optimization
- Backup DNS configurations

---
*This analysis was generated automatically. For AI-powered insights, ensure the analysis service is available.*
"""
        
        return analysis

def main():
    parser = argparse.ArgumentParser(
        description='URL Analyzer - CLI tool for URL issue analysis',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s https://google.com
  %(prog)s https://your-alb.amazonaws.com --question "Why is this slow?"
  %(prog)s https://api.example.com --question "Is this secure?"
        """
    )
    
    parser.add_argument('url', help='URL to analyze')
    parser.add_argument('--question', '-q', help='Specific question about the URL')
    parser.add_argument('--api-url', default='http://ollama-alb-427582956.us-east-1.elb.amazonaws.com', 
                       help='Ollama API URL (default: http://ollama-alb-427582956.us-east-1.elb.amazonaws.com)')
    parser.add_argument('--output', '-o', help='Save analysis to file')
    parser.add_argument('--no-ai', action='store_true', help='Skip AI analysis, use fallback only')
    
    args = parser.parse_args()
    
    # Validate URL
    url = args.url
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    
    print(f"🔍 Analyzing URL: {url}")
    if args.question:
        print(f"❓ Question: {args.question}")
    print("=" * 60)
    
    # Initialize analyzer
    analyzer = URLAnalyzer(args.api_url)
    
    # Perform connectivity analysis
    print("📡 Running connectivity tests...")
    connectivity_data = analyzer.analyze_url_connectivity(url)
    
    if 'error' in connectivity_data:
        print(f"❌ {connectivity_data['error']}")
        return 1
    
    # Display basic results
    print(f"\n📊 Basic Results:")
    if connectivity_data.get('dns_resolution', {}).get('success'):
        print(f"   ✅ DNS: {connectivity_data['dns_resolution']['ip_address']}")
    else:
        print(f"   ❌ DNS: Failed")
    
    if connectivity_data.get('connectivity_tests', {}).get('port', {}).get('success'):
        print(f"   ✅ Port {connectivity_data['port']}: Open")
    else:
        print(f"   ❌ Port {connectivity_data['port']}: Closed")
    
    if connectivity_data.get('ssl_info', {}).get('success'):
        print(f"   ✅ SSL: Valid")
    else:
        print(f"   ❌ SSL: Invalid")
    
    if connectivity_data.get('http_status', {}).get('status_code'):
        status = connectivity_data['http_status']['status_code']
        print(f"   {'✅' if 200 <= status < 400 else '❌'} HTTP: {status}")
    
    if connectivity_data.get('response_time'):
        response_time = connectivity_data['response_time']['milliseconds']
        print(f"   {'✅' if response_time < 1000 else '⚠️'} Response: {response_time:.0f}ms")
    
    # Get AI analysis
    print(f"\n🤖 Getting analysis...")
    if args.no_ai:
        analysis = analyzer.generate_fallback_analysis(url, args.question, connectivity_data)
    else:
        try:
            analysis = analyzer.get_ai_analysis(url, args.question, connectivity_data)
            if 'timeout' in analysis.lower() or 'failed' in analysis.lower():
                print("⚠️  AI analysis failed, using fallback...")
                analysis = analyzer.generate_fallback_analysis(url, args.question, connectivity_data)
        except Exception as e:
            print(f"⚠️  AI analysis error: {e}")
            analysis = analyzer.generate_fallback_analysis(url, args.question, connectivity_data)
    
    # Display analysis
    print(f"\n{analysis}")
    
    # Save to file if requested
    if args.output:
        try:
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(analysis)
            print(f"\n💾 Analysis saved to: {args.output}")
        except Exception as e:
            print(f"❌ Failed to save file: {e}")
    
    # Return exit code based on issues
    errors = connectivity_data.get('errors', [])
    return 1 if errors else 0

if __name__ == '__main__':
    sys.exit(main())
