#!/usr/bin/env python3
"""
Web Interface for URL Issue Analysis

A simple web interface where users can input any URL (website, ALB, Kubernetes)
and get instant AI-powered issue analysis using their private Ollama API.

Usage:
    python web_interface.py
    Then open http://localhost:8080 in your browser
"""

from flask import Flask, render_template, request, jsonify
import requests
import json
from datetime import datetime
import socket
import urllib.parse
import ssl
import subprocess
import sys

app = Flask(__name__, template_folder='templates')

class URLAnalyzer:
    def __init__(self, ollama_api_url: str):
        self.ollama_api_url = ollama_api_url
    
    def analyze_url_connectivity(self, url: str) -> dict:
        """Analyze URL connectivity and basic issues."""
        try:
            # Parse URL
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
                
                # Check for common issues
                if response.status_code >= 400:
                    result['errors'].append(f"HTTP Error {response.status_code}: {response.reason}")
                    
            except requests.exceptions.Timeout:
                result['http_status'] = {
                    'error': 'Request timeout'
                }
                result['errors'].append("Request timed out")
            except requests.exceptions.ConnectionError as e:
                result['http_status'] = {
                    'error': 'Connection error'
                }
                result['errors'].append(f"Connection error: {str(e)}")
            except Exception as e:
                result['http_status'] = {
                    'error': str(e)
                }
                result['errors'].append(f"HTTP request failed: {str(e)}")
            
            return result
            
        except Exception as e:
            return {
                'url': url,
                'error': f"Analysis failed: {str(e)}",
                'errors': [str(e)]
            }
    
    def get_ai_analysis(self, url: str, connectivity_data: dict) -> dict:
        """Get AI analysis of URL issues."""
        try:
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
            
            # List all errors
            if connectivity_data.get('errors'):
                summary.append("\n🚨 Issues detected:")
                for error in connectivity_data['errors']:
                    summary.append(f"   • {error}")
            
            # Create prompt for AI
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
                json={"prompt": prompt, "context": "url-troubleshooting"},
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                return {
                    'error': f'AI API returned status {response.status_code}',
                    'response': response.text
                }
                
        except requests.exceptions.Timeout:
            return {'error': 'AI API timeout - using fallback analysis'}
        except Exception as e:
            return {'error': f'AI analysis failed: {str(e)}'}
    
    def get_custom_ai_analysis(self, url: str, question: str, connectivity_data: dict) -> dict:
        """Get custom AI analysis based on user's specific question."""
        try:
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
            
            # List all errors
            if connectivity_data.get('errors'):
                summary.append("\n🚨 Issues detected:")
                for error in connectivity_data['errors']:
                    summary.append(f"   • {error}")
            
            # Create custom prompt for AI based on user's question
            prompt = f"""
            A user is asking about this URL: {url}
            
            Their specific question is: "{question}"
            
            Here are the connectivity test results:
            {chr(10).join(summary)}
            
            Please provide a detailed, specific answer to their question based on the connectivity data.
            Focus on their specific concern and provide actionable recommendations.
            Be thorough but concise.
            """
            
            # Call AI API
            response = requests.post(
                f"{self.ollama_api_url}/api/analyze",
                json={"prompt": prompt, "context": "custom-url-analysis"},
                headers={"Content-Type": "application/json"},
                timeout=15  # Reduced timeout for faster response
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                return {
                    'error': f'AI API returned status {response.status_code}',
                    'response': response.text
                }
                
        except requests.exceptions.Timeout:
            return {'error': 'AI API timeout - using fallback analysis'}
        except Exception as e:
            return {'error': f'AI analysis failed: {str(e)}'}
    
    def generate_fallback_custom_analysis(self, url: str, question: str, connectivity_data: dict) -> str:
        """Generate fallback analysis when AI is unavailable."""
        analysis = f"""
# Custom Analysis for: {question}

**URL:** {url}
**Analyzed:** {datetime.now().isoformat()}

## 🔍 Connectivity Summary

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
        
        analysis += f"""
## 🤖 Specific Analysis for Your Question

**Your Question:** "{question}"

### Analysis Based on Connectivity Data

"""
        
        # Provide specific analysis based on the actual question and connectivity data
        question_lower = question.lower()
        
        # Check for specific issues in connectivity data
        has_dns_issues = not connectivity_data.get('dns_resolution', {}).get('success')
        has_port_issues = not connectivity_data.get('connectivity_tests', {}).get('port', {}).get('success')
        has_ssl_issues = not connectivity_data.get('ssl_info', {}).get('success')
        has_http_errors = connectivity_data.get('http_status', {}).get('status_code', 200) >= 400
        has_slow_response = connectivity_data.get('response_time', {}).get('milliseconds', 0) > 2000
        
        if 'improve' in question_lower or 'optimiz' in question_lower:
            analysis += "### 🚀 Improvement Opportunities:\n\n"
            
            if has_slow_response:
                analysis += "**Performance Issues Detected:**\n"
                analysis += f"• Response time is {connectivity_data['response_time']['milliseconds']:.0f}ms (should be <1000ms)\n"
                analysis += "• Consider implementing caching (CDN, Redis)\n"
                analysis += "• Optimize images and static assets\n"
                analysis += "• Use compression (gzip, brotli)\n"
                analysis += "• Consider load balancing for better distribution\n\n"
            
            if has_dns_issues:
                analysis += "**DNS Issues:**\n"
                analysis += "• DNS resolution is failing - check DNS configuration\n"
                analysis += "• Consider using a faster DNS provider\n"
                analysis += "• Implement DNS caching and monitoring\n\n"
            
            if has_ssl_issues:
                analysis += "**SSL/TLS Issues:**\n"
                analysis += "• SSL certificate problems detected\n"
                analysis += "• Update to modern TLS protocols (1.2, 1.3)\n"
                analysis += "• Implement certificate auto-renewal\n"
                analysis += "• Use HSTS for better security\n\n"
            
            if not any([has_slow_response, has_dns_issues, has_ssl_issues, has_port_issues]):
                analysis += "**Current Status:** No major connectivity issues detected.\n\n"
                analysis += "**General Improvements:**\n"
                analysis += "• Set up comprehensive monitoring\n"
                analysis += "• Implement automated health checks\n"
                analysis += "• Use performance monitoring tools\n"
                analysis += "• Consider implementing a CDN for global performance\n"
                analysis += "• Set up alerting for proactive issue detection\n\n"
        
        elif 'slow' in question_lower or 'performance' in question_lower:
            analysis += "### ⚡ Performance Analysis:\n\n"
            
            if has_slow_response:
                analysis += f"**Performance Issues Found:**\n"
                analysis += f"• Response time: {connectivity_data['response_time']['milliseconds']:.0f}ms (slow)\n"
                analysis += "• Server appears to be under load or experiencing latency\n"
                analysis += "• Network latency may be affecting performance\n\n"
                analysis += "**Recommendations:**\n"
                analysis += "• Check server CPU/memory utilization\n"
                analysis += "• Implement caching at multiple levels\n"
                analysis += "• Use a Content Delivery Network (CDN)\n"
                analysis += "• Optimize database queries and indexing\n"
                analysis += "• Consider horizontal scaling with load balancers\n"
            else:
                analysis += "**Performance Status:** Response times are acceptable\n"
                analysis += "**Monitoring Recommendations:**\n"
                analysis += "• Set up performance baselines\n"
                analysis += "• Monitor response time trends\n"
                analysis += "• Implement performance alerting\n"
        
        elif 'secure' in question_lower or 'security' in question_lower:
            analysis += "### 🔒 Security Analysis:\n\n"
            
            if has_ssl_issues:
                analysis += "**Security Issues Detected:**\n"
                analysis += "• SSL certificate problems - this is a critical security issue\n"
                analysis += "• Encrypted traffic may not be working properly\n\n"
                analysis += "**Immediate Actions:**\n"
                analysis += "• Renew or fix SSL certificate immediately\n"
                analysis += "• Implement HTTPS redirects\n"
                analysis += "• Add security headers (HSTS, CSP, X-Frame-Options)\n"
                analysis += "• Regular security scanning and vulnerability assessment\n"
            else:
                analysis += "**Security Status:** Basic security measures appear functional\n"
                analysis += "**Additional Security Recommendations:**\n"
                analysis += "• Implement Web Application Firewall (WAF)\n"
                analysis += "• Use security monitoring and logging\n"
                analysis += "• Regular penetration testing\n"
                analysis += "• Implement rate limiting and DDoS protection\n"
        
        elif 'reliable' in question_lower or 'avail' in question_lower:
            analysis += "### 🛡️ Reliability Analysis:\n\n"
            
            if any([has_dns_issues, has_port_issues, has_ssl_issues, has_http_errors]):
                analysis += "**Reliability Issues Detected:**\n"
                if has_dns_issues:
                    analysis += "• DNS resolution failures affect reliability\n"
                if has_port_issues:
                    analysis += "• Port connectivity issues indicate service downtime\n"
                if has_ssl_issues:
                    analysis += "• SSL issues may prevent secure connections\n"
                if has_http_errors:
                    analysis += f"• HTTP errors ({connectivity_data['http_status']['status_code']}) indicate service problems\n\n"
                
                analysis += "**Reliability Improvements:**\n"
                analysis += "• Implement health checks and monitoring\n"
                analysis += "• Set up automated failover mechanisms\n"
                analysis += "• Use multiple availability zones\n"
                analysis += "• Implement circuit breakers for resilience\n"
            else:
                analysis += "**Reliability Status:** Service appears stable\n"
                analysis += "**Enhancement Recommendations:**\n"
                analysis += "• Set up comprehensive monitoring dashboards\n"
                analysis += "• Implement proactive alerting\n"
                analysis += "• Regular disaster recovery testing\n"
                analysis += "• Consider multi-region deployment for critical services\n"
        
        else:
            # Generic analysis for other questions
            analysis += "### 📊 Analysis Based on Current Status:\n\n"
            
            if any([has_dns_issues, has_port_issues, has_ssl_issues, has_http_errors]):
                analysis += "**Issues Requiring Attention:**\n"
                if has_dns_issues:
                    analysis += "• Fix DNS resolution issues\n"
                if has_port_issues:
                    analysis += "• Investigate port connectivity problems\n"
                if has_ssl_issues:
                    analysis += "• Address SSL certificate problems\n"
                if has_http_errors:
                    analysis += f"• Resolve HTTP error {connectivity_data['http_status']['status_code']}\n"
            else:
                analysis += "**Status:** No critical connectivity issues detected\n"
            
            analysis += f"\n**General Recommendations:**\n"
            analysis += "• Implement continuous monitoring\n"
            analysis += "• Set up automated health checks\n"
            analysis += "• Document current architecture and configurations\n"
            analysis += "• Regular performance and security assessments\n"
        
        analysis += f"""

## 📊 Immediate Action Items

1. **Fix Critical Issues**: Address any ❌ items above first
2. **Monitor Performance**: Set up alerts for response time >1000ms
3. **Security Check**: Ensure SSL certificates are valid and renewed
4. **Documentation**: Keep track of current configuration and changes

## 🔍 Technical Details

- **URL Tested**: {url}
- **Test Time**: {datetime.now().isoformat()}
- **Connectivity Issues**: {len(connectivity_data.get('errors', []))}
- **Response Time**: {connectivity_data.get('response_time', {}).get('milliseconds', 'N/A')}ms

---
*This analysis was generated automatically based on connectivity tests. For AI-powered insights, ensure the analysis service is available.*
"""
        
        return analysis

    def generate_fallback_analysis(self, url: str, connectivity_data: dict) -> str:
        """Generate fallback analysis when AI is unavailable."""
        analysis = f"""
# URL Issue Analysis Report

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
        
        analysis += """
## 🔧 Troubleshooting Steps

### General Steps
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
        
        # Determine priority
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

# Initialize analyzer
OLLAMA_API_URL = "http://ollama-alb-427582956.us-east-1.elb.amazonaws.com"
analyzer = URLAnalyzer(OLLAMA_API_URL)

@app.route('/')
def index():
    """Main page with URL input form."""
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze_url():
    """Analyze URL and return results."""
    try:
        data = request.get_json()
        url = data.get('url', '').strip()
        
        if not url:
            return jsonify({'error': 'URL is required'}), 400
        
        # Add scheme if missing
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        
        # Perform connectivity analysis
        print(f"🔍 Analyzing URL: {url}")
        connectivity_data = analyzer.analyze_url_connectivity(url)
        
        # Get AI analysis
        print("🤖 Getting AI analysis...")
        ai_result = analyzer.get_ai_analysis(url, connectivity_data)
        
        # Prepare response
        response = {
            'url': url,
            'connectivity': connectivity_data,
            'timestamp': datetime.now().isoformat()
        }
        
        if ai_result and not ai_result.get('error'):
            response['ai_analysis'] = ai_result.get('response', 'No AI response available')
            response['ai_metadata'] = {
                'processing_time_ms': ai_result.get('processing_time_ms', 0),
                'model': ai_result.get('model', 'unknown')
            }
        else:
            response['ai_analysis'] = analyzer.generate_fallback_analysis(url, connectivity_data)
            response['ai_metadata'] = {
                'error': ai_result.get('error', 'AI analysis unavailable'),
                'fallback': True
            }
        
        return jsonify(response)
        
    except Exception as e:
        return jsonify({'error': f'Analysis failed: {str(e)}'}), 500

@app.route('/analyze-custom', methods=['POST'])
def analyze_url_custom():
    """Analyze URL with custom user question."""
    try:
        data = request.get_json()
        url = data.get('url', '').strip()
        question = data.get('question', '').strip()
        
        if not url:
            return jsonify({'error': 'URL is required'}), 400
        
        if not question:
            return jsonify({'error': 'Question is required'}), 400
        
        # Add scheme if missing
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        
        # Perform basic connectivity analysis
        print(f"🔍 Analyzing URL: {url}")
        print(f"❓ User question: {question}")
        connectivity_data = analyzer.analyze_url_connectivity(url)
        
        # Get custom AI analysis
        print("🤖 Getting custom AI analysis...")
        ai_result = analyzer.get_custom_ai_analysis(url, question, connectivity_data)
        
        # Prepare response
        response = {
            'url': url,
            'question': question,
            'connectivity': connectivity_data,
            'timestamp': datetime.now().isoformat()
        }
        
        if ai_result and not ai_result.get('error'):
            response['custom_ai_analysis'] = ai_result.get('response', 'No AI response available')
            response['ai_metadata'] = {
                'processing_time_ms': ai_result.get('processing_time_ms', 0),
                'model': ai_result.get('model', 'unknown')
            }
        else:
            response['custom_ai_analysis'] = analyzer.generate_fallback_custom_analysis(url, question, connectivity_data)
            response['ai_metadata'] = {
                'error': ai_result.get('error', 'AI analysis unavailable'),
                'fallback': True
            }
        
        return jsonify(response)
        
    except Exception as e:
        return jsonify({'error': f'Analysis failed: {str(e)}'}), 500

@app.route('/health')
def health():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'service': 'URL Issue Analyzer'
    })

if __name__ == '__main__':
    print("🚀 Starting URL Issue Analyzer Web Interface")
    print("=" * 50)
    print("📋 Features:")
    print("   • URL connectivity analysis")
    print("   • DNS resolution testing")
    print("   • SSL certificate validation")
    print("   • HTTP status checking")
    print("   • AI-powered issue diagnosis")
    print("   • Private analysis (no external data sharing)")
    print("=" * 50)
    print("🌐 Open http://localhost:8080 in your browser")
    print("🔧 API endpoint: http://localhost:8080/analyze")
    print("❤️  Health check: http://localhost:8080/health")
    print("=" * 50)
    
    app.run(host='0.0.0.0', port=8080, debug=True)
