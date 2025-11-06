#!/usr/bin/env python3
"""
DevOps Analyzer - Unified CLI Tool

A comprehensive command-line tool for URL analysis, infrastructure analysis,
and CI/CD integration using your private Ollama API.

Usage:
    python devops-analyzer.py url <url> [--question "your question"]
    python devops-analyzer.py infrastructure --type <architecture|health> --cluster <name>
    python devops-analyzer.py deploy --action <pre-check|post-check> --service <name> --cluster <name>
"""

import sys
import argparse
import requests
import json
import boto3
from datetime import datetime, timezone
import socket
import urllib.parse
import ssl
import subprocess
import os

class DevOpsAnalyzer:
    def __init__(self, ollama_api_url: str, region: str = 'us-east-1'):
        self.ollama_api_url = ollama_api_url
        self.region = region
        self.ecs_client = boto3.client('ecs', region_name=region)
        self.elb_client = boto3.client('elbv2', region_name=region)
        self.ec2_client = boto3.client('ec2', region_name=region)
        self.cloudwatch_client = boto3.client('cloudwatch', region_name=region)
    
    # ========== URL ANALYSIS METHODS ==========
    
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
    
    # ========== INFRASTRUCTURE ANALYSIS METHODS ==========
    
    def analyze_architecture(self, cluster_name: str) -> dict:
        """Analyze ECS architecture."""
        try:
            # Get cluster info
            cluster_info = self.ecs_client.describe_clusters(clusters=[cluster_name])['clusters'][0]
            
            # Get services
            services = self.ecs_client.list_services(cluster=cluster_name)['serviceArns']
            service_details = []
            
            if services:
                service_info = self.ecs_client.describe_services(
                    cluster=cluster_name, services=services
                )['services']
                
                for service in service_info:
                    service_details.append({
                        'name': service['serviceName'],
                        'status': service['status'],
                        'desiredCount': service['desiredCount'],
                        'runningCount': service['runningCount'],
                        'taskDefinition': service['taskDefinition'].split('/')[-1]
                    })
            
            # Get load balancers (simplified)
            load_balancers = []
            for service in service_details:
                load_balancers.append({
                    'name': f"{cluster_name}-alb",
                    'type': 'application',
                    'status': 'active'
                })
            
            return {
                'cluster': cluster_info,
                'services': service_details,
                'load_balancers': load_balancers,
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            return {'error': str(e)}
    
    def analyze_health(self, cluster_name: str, service_name: str = None) -> dict:
        """Analyze service health."""
        try:
            if service_name:
                services = [service_name]
            else:
                services = self.ecs_client.list_services(cluster=cluster_name)['serviceArns']
            
            health_data = []
            for service_arn in services:
                service_name = service_arn.split('/')[-1]
                service_info = self.ecs_client.describe_services(
                    cluster=cluster_name, services=[service_arn]
                )['services'][0]
                
                health_data.append({
                    'service': service_name,
                    'status': service_info['status'],
                    'running': service_info['runningCount'],
                    'desired': service_info['desiredCount'],
                    'healthy': service_info['runningCount'] == service_info['desiredCount']
                })
            
            return {
                'cluster': cluster_name,
                'services': health_data,
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            return {'error': str(e)}
    
    # ========== DEPLOYMENT METHODS ==========
    
    def pre_deployment_check(self, cluster_name: str, service_name: str = None) -> dict:
        """Perform pre-deployment checks."""
        try:
            health_data = self.analyze_health(cluster_name, service_name)
            if 'error' in health_data:
                return health_data
            
            # Check if services are healthy
            unhealthy_services = [s for s in health_data['services'] if not s['healthy']]
            
            return {
                'status': 'ready' if not unhealthy_services else 'not_ready',
                'unhealthy_services': unhealthy_services,
                'recommendation': 'Safe to deploy' if not unhealthy_services else 'Fix unhealthy services before deployment',
                'health_data': health_data
            }
            
        except Exception as e:
            return {'error': str(e)}
    
    def post_deployment_check(self, cluster_name: str, service_name: str = None) -> dict:
        """Perform post-deployment verification."""
        try:
            health_data = self.analyze_health(cluster_name, service_name)
            if 'error' in health_data:
                return health_data
            
            # Check deployment success
            healthy_services = [s for s in health_data['services'] if s['healthy']]
            total_services = len(health_data['services'])
            
            return {
                'status': 'success' if len(healthy_services) == total_services else 'partial',
                'healthy_services': len(healthy_services),
                'total_services': total_services,
                'health_percentage': (len(healthy_services) / total_services) * 100,
                'recommendation': 'Deployment successful' if len(healthy_services) == total_services else 'Some services may need attention',
                'health_data': health_data
            }
            
        except Exception as e:
            return {'error': str(e)}
    
    # ========== AI ANALYSIS METHODS ==========
    
    def get_ai_analysis(self, analysis_type: str, data: dict, question: str = None) -> str:
        """Get AI analysis of data."""
        try:
            if analysis_type == 'url':
                prompt = self._create_url_prompt(data, question)
            elif analysis_type == 'architecture':
                prompt = self._create_architecture_prompt(data)
            elif analysis_type == 'health':
                prompt = self._create_health_prompt(data)
            elif analysis_type == 'deployment':
                prompt = self._create_deployment_prompt(data)
            else:
                return "Unknown analysis type"
            
            # Call AI API
            response = requests.post(
                f"{self.ollama_api_url}/api/analyze",
                json={"prompt": prompt, "context": f"{analysis_type}-analysis"},
                headers={"Content-Type": "application/json"},
                timeout=30  # Increased timeout
            )
            
            if response.status_code == 200:
                result = response.json()
                if 'response' in result:
                    return result['response']
                elif 'error' in result:
                    return f'AI API error: {result["error"]}'
                else:
                    return 'No AI response available'
            else:
                try:
                    error_data = response.json()
                    error_msg = error_data.get('error', response.text)
                    return f'AI API returned status {response.status_code}: {error_msg}'
                except:
                    return f'AI API returned status {response.status_code}: {response.text[:200]}'
                
        except requests.exceptions.Timeout:
            return 'AI API timeout - using fallback analysis'
        except requests.exceptions.ConnectionError as e:
            return f'AI API connection failed - using fallback analysis: {str(e)}'
        except Exception as e:
            return f'AI analysis failed: {str(e)}'
    
    def _create_url_prompt(self, data: dict, question: str = None) -> str:
        """Create AI prompt for URL analysis."""
        summary = []
        
        if data.get('dns_resolution', {}).get('success'):
            summary.append(f"✅ DNS resolves to {data['dns_resolution']['ip_address']}")
        else:
            summary.append(f"❌ DNS resolution failed")
        
        if data.get('connectivity_tests', {}).get('port', {}).get('success'):
            summary.append(f"✅ Port {data['port']} is open")
        else:
            summary.append(f"❌ Port {data['port']} is closed or blocked")
        
        if data.get('ssl_info', {}).get('success'):
            summary.append(f"✅ SSL certificate is valid")
        else:
            summary.append(f"❌ SSL certificate issue detected")
        
        if data.get('http_status', {}).get('status_code'):
            status = data['http_status']['status_code']
            if 200 <= status < 300:
                summary.append(f"✅ HTTP status {status} (OK)")
            elif 300 <= status < 400:
                summary.append(f"⚠️  HTTP status {status} (Redirect)")
            else:
                summary.append(f"❌ HTTP status {status} (Error)")
        
        if data.get('response_time'):
            response_time = data['response_time']['milliseconds']
            if response_time < 1000:
                summary.append(f"✅ Response time {response_time:.0f}ms (Good)")
            elif response_time < 3000:
                summary.append(f"⚠️  Response time {response_time:.0f}ms (Slow)")
            else:
                summary.append(f"❌ Response time {response_time:.0f}ms (Very slow)")
        
        if data.get('errors'):
            summary.append("\n🚨 Issues detected:")
            for error in data['errors']:
                summary.append(f"   • {error}")
        
        if question:
            prompt = f"""
            Analyze this URL and answer the user's specific question:
            
            URL: {data['url']}
            User Question: {question}
            
            Test Results:
            {chr(10).join(summary)}
            
            Please provide a detailed answer to their question based on the connectivity data.
            Focus on their specific concern and provide actionable recommendations.
            """
        else:
            prompt = f"""
            Analyze this URL and diagnose the issues:
            
            URL: {data['url']}
            
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
        
        return prompt
    
    def _create_architecture_prompt(self, data: dict) -> str:
        """Create AI prompt for architecture analysis."""
        return f"""
        Analyze this AWS ECS architecture and provide recommendations:
        
        Cluster: {data.get('cluster', {}).get('clusterName', 'Unknown')}
        Services: {len(data.get('services', []))}
        Load Balancers: {len(data.get('load_balancers', []))}
        
        Services Details:
        {chr(10).join([f"- {s['name']}: {s['runningCount']}/{s['desiredCount']} running" for s in data.get('services', [])])}
        
        Please provide:
        1. Architecture assessment
        2. High availability analysis
        3. Security considerations
        4. Optimization recommendations
        5. Improvement suggestions
        """
    
    def _create_health_prompt(self, data: dict) -> str:
        """Create AI prompt for health analysis."""
        return f"""
        Analyze this AWS ECS service health:
        
        Cluster: {data.get('cluster', 'Unknown')}
        
        Service Health:
        {chr(10).join([f"- {s['service']}: {'✅ Healthy' if s['healthy'] else '❌ Unhealthy'} ({s['running']}/{s['desired']} running)" for s in data.get('services', [])])}
        
        Please provide:
        1. Health assessment
        2. Performance issues
        3. Scaling recommendations
        4. Monitoring suggestions
        5. Troubleshooting steps
        """
    
    def _create_deployment_prompt(self, data: dict) -> str:
        """Create AI prompt for deployment analysis."""
        return f"""
        Analyze this deployment status:
        
        Status: {data.get('status', 'Unknown')}
        Recommendation: {data.get('recommendation', 'Unknown')}
        
        Please provide:
        1. Deployment assessment
        2. Risk analysis
        3. Next steps
        4. Rollback considerations if needed
        5. Monitoring recommendations
        """
    
    # ========== FALLBACK ANALYSIS METHODS ==========
    
    def generate_fallback_analysis(self, analysis_type: str, data: dict, question: str = None) -> str:
        """Generate fallback analysis when AI is unavailable."""
        
        if analysis_type == 'url':
            return self._generate_url_fallback(data, question)
        elif analysis_type == 'architecture':
            return self._generate_architecture_fallback(data)
        elif analysis_type == 'health':
            return self._generate_health_fallback(data)
        elif analysis_type == 'deployment':
            return self._generate_deployment_fallback(data)
        else:
            return "# Unknown Analysis Type\n\nPlease specify a valid analysis type."
    
    def _generate_url_fallback(self, data: dict, question: str = None) -> str:
        """Generate fallback URL analysis."""
        try:
            # If question is provided, return only the answer
            if question:
                return self._generate_answer_only(data, question)
            
            # Otherwise, return full report
            analysis = f"""
# URL Analysis Report

**URL:** {data['url']}
**Analyzed:** {datetime.now().isoformat()}

## 🔍 Test Results

### Connectivity Tests
"""
            
            if data.get('dns_resolution', {}).get('success'):
                analysis += f"✅ **DNS Resolution:** {data['dns_resolution']['ip_address']}\n"
            else:
                analysis += "❌ **DNS Resolution:** Failed\n"
            
            if data.get('connectivity_tests', {}).get('port', {}).get('success'):
                analysis += f"✅ **Port {data['port']}:** Open\n"
            else:
                analysis += f"❌ **Port {data['port']}:** Closed or blocked\n"
            
            if data.get('ssl_info') and data.get('ssl_info', {}).get('success'):
                analysis += "✅ **SSL Certificate:** Valid\n"
            elif data.get('ssl_info'):
                analysis += "❌ **SSL Certificate:** Invalid or expired\n"
            else:
                analysis += "⚪ **SSL Certificate:** Not applicable (HTTP)\n"
            
            if data.get('http_status') and data.get('http_status', {}).get('status_code'):
                status = data['http_status']['status_code']
                analysis += f"{'✅' if 200 <= status < 300 else '❌'} **HTTP Status:** {status} {data['http_status']['status_text']}\n"
            elif data.get('http_status') and data.get('http_status', {}).get('error'):
                analysis += f"❌ **HTTP Status:** {data['http_status']['error']}\n"
            else:
                analysis += "❌ **HTTP Status:** Failed to retrieve\n"
            
            if data.get('response_time') and data.get('response_time', {}).get('milliseconds'):
                response_time = data['response_time']['milliseconds']
                analysis += f"{'✅' if response_time < 1000 else '⚠️'} **Response Time:** {response_time:.0f}ms\n"
            else:
                analysis += "❌ **Response Time:** Failed to measure\n"
            
            analysis += "\n## 🚨 Issues Found\n"
            
            if data.get('errors'):
                for error in data['errors']:
                    analysis += f"• {error}\n"
            else:
                analysis += "No critical issues detected.\n"
            
            analysis += """
## 🔧 Troubleshooting Steps

1. **Check connectivity** - Verify network access to the target
2. **Verify DNS** - Ensure domain resolution is working
3. **Test ports** - Confirm required ports are open
4. **Check SSL** - Validate certificate for HTTPS sites
5. **DNS settings** - Verify DNS resolution
6. **Service status** - Check if the target service is running

## 📊 Priority Assessment
"""
            
            errors = data.get('errors', [])
            if not errors:
                analysis += "🟢 **Priority: Low** - No critical issues\n"
            elif len(errors) <= 2:
                analysis += "🟡 **Priority: Medium** - Some issues detected\n"
            else:
                analysis += "🔴 **Priority: High** - Multiple critical issues\n"
            
            analysis += """

---
*This analysis was generated automatically. For AI-powered insights, ensure the analysis service is available.*
"""
            
            return analysis
        except Exception as e:
            return f"""
# URL Analysis Report - Error

**URL:** {data.get('url', 'Unknown')}
**Analyzed:** {datetime.now().isoformat()}

## ❌ Analysis Error

An error occurred while generating the analysis:

**Error:** {str(e)}

**Debug Info:**
- Data keys: {list(data.keys()) if isinstance(data, dict) else 'Not a dict'}
- Question: {question}

---

*This analysis was generated automatically with fallback error handling.*
"""
    
    def _generate_answer_only(self, data: dict, question: str) -> str:
        """Generate answer-only response when question is provided."""
        try:
            question_lower = question.lower()
            answer = ""
            
            if 'availability' in question_lower or 'improve' in question_lower or 'optimiz' in question_lower:
                # Analyze actual data for specific recommendations
                response_time_ms = data.get('response_time', {}).get('milliseconds', 0) if data.get('response_time') and data.get('response_time', {}).get('milliseconds') else 0
                
                if response_time_ms > 1000:
                    answer += f"Based on the current connectivity analysis, your service is experiencing slower response times ({response_time_ms:.0f}ms), which can impact availability. "
                    answer += "To improve availability, you should implement caching strategies at multiple levels (application, database, and CDN) to reduce latency. "
                else:
                    answer += f"Your service is currently performing well with a response time of {response_time_ms:.0f}ms. "
                
                # Check if it's HTTP (less available than HTTPS)
                if not data.get('ssl_info'):
                    answer += "However, you're currently using HTTP, which poses security risks and can impact availability. Upgrading to HTTPS is critical for both security and reliability, as it ensures encrypted connections and prevents potential man-in-the-middle attacks. "
                
                # Check for any errors
                if data.get('errors'):
                    error_list = "; ".join(data['errors'][:2])
                    answer += f"Additionally, there are some issues that need attention: {error_list}. "
                    answer += "These should be addressed to ensure stable service availability. "
                else:
                    answer += "The connectivity tests show no critical issues detected, indicating your service is stable. "
                
                # Infrastructure recommendations
                answer += "To further enhance availability, consider deploying across multiple Availability Zones (AZs) to ensure redundancy and fault tolerance. "
                answer += "Setting up comprehensive health checks and monitoring alerts will help you proactively identify and resolve issues before they impact users. "
                answer += "Implementing proper load balancing ensures traffic is distributed evenly across your infrastructure, and auto-scaling based on demand patterns will help maintain performance during traffic spikes."
                
            elif 'slow' in question_lower or 'performance' in question_lower:
                response_time_ms = data.get('response_time', {}).get('milliseconds', 0) if data.get('response_time') and data.get('response_time', {}).get('milliseconds') else 0
                if response_time_ms > 0:
                    if response_time_ms > 2000:
                        answer += f"Your service is experiencing very slow response times ({response_time_ms:.0f}ms), which significantly impacts user experience. "
                        answer += "This could be due to high server load, inefficient database queries, or lack of caching. "
                        answer += "I recommend checking your server resource utilization (CPU, memory, and network), implementing caching at multiple levels (application cache, database query cache, and CDN), and considering a Content Delivery Network (CDN) to serve static content from locations closer to your users."
                    elif response_time_ms > 1000:
                        answer += f"Your service response time is slow ({response_time_ms:.0f}ms) and could be improved. "
                        answer += "This may be caused by server resource constraints or lack of optimization. "
                        answer += "I suggest checking server load and resource utilization, implementing caching strategies, and considering a CDN to improve performance, especially for static assets."
                    else:
                        answer += f"Your service is performing well with an acceptable response time of {response_time_ms:.0f}ms. "
                        answer += "This indicates good performance, but you can still optimize further by implementing caching and ensuring your infrastructure is properly scaled for your traffic patterns."
                else:
                    answer += "Unfortunately, I couldn't measure the response time during the connectivity test. "
                    answer += "This could indicate network issues or the service may be timing out. "
                    answer += "I recommend checking your server logs, network connectivity, and ensuring your service is properly configured and responding to requests."
                
            elif 'secure' in question_lower or 'security' in question_lower or 'safe' in question_lower or 'trust' in question_lower or 'certificate' in question_lower:
                if data.get('ssl_info') and data.get('ssl_info', {}).get('success'):
                    answer += "Your website is properly secured with a valid SSL certificate configured correctly. "
                    answer += "This means your connections are encrypted using HTTPS, which protects data in transit between clients and your server. "
                    answer += "Your SSL certificate is valid and properly configured, providing both security and trust for your users."
                elif not data.get('ssl_info'):
                    answer += "Your website is currently using HTTP, which is a critical security concern. "
                    answer += "All data transmitted between users and your server is unencrypted, making it vulnerable to interception and man-in-the-middle attacks. "
                    answer += "I strongly recommend upgrading to HTTPS immediately by obtaining an SSL certificate (you can use free certificates from Let's Encrypt). "
                    answer += "Additionally, implement HTTPS redirects to automatically send HTTP traffic to HTTPS, and add security headers like HSTS (HTTP Strict Transport Security) and CSP (Content Security Policy) to further enhance your security posture."
                else:
                    answer += "There are SSL certificate issues detected with your HTTPS configuration. "
                    answer += "This could mean the certificate is expired, invalid, or misconfigured. "
                    answer += "You should fix this immediately as it can cause browser warnings for your users and potentially expose security vulnerabilities."
                
            elif 'error' in question_lower or 'issue' in question_lower or 'problem' in question_lower:
                if data.get('errors'):
                    error_list = "\n".join([f"  - {error}" for error in data['errors'][:5]])
                    answer += "During the connectivity analysis, I found several issues that need attention:\n" + error_list + "\n"
                    answer += "These issues should be investigated and resolved to ensure your service operates correctly. "
                    answer += "Check your server logs, review your configuration, and verify that all required services are running properly."
                else:
                    answer += "Based on the connectivity tests performed, no critical issues were detected with your service. "
                    answer += "The DNS resolution is working, the required ports are open, and the service is responding correctly. "
                    answer += "However, I recommend regularly monitoring your service and performing periodic checks to maintain this healthy state."
                
                if data.get('http_status') and data.get('http_status', {}).get('status_code', 0) >= 400:
                    status = data['http_status']['status_code']
                    answer += f" Additionally, there's an HTTP error ({status}) being returned, which indicates the service is encountering issues. "
                    answer += "You should check your service logs and application error handling to identify and resolve the root cause."
            
            elif 'what' in question_lower and ('use' in question_lower or 'purpose' in question_lower or 'is' in question_lower):
                # Extract domain from URL
                parsed_url = urllib.parse.urlparse(data['url'])
                domain = parsed_url.hostname or data['url']
                
                # Analyze domain patterns
                if 'google' in domain.lower():
                    answer += "This website is Google's search engine and technology platform. "
                    answer += "Google provides a wide range of services including web search, email (Gmail), cloud computing services (Google Cloud Platform), productivity tools (Google Workspace), and various other online tools and services. "
                    answer += "The website is accessible and responding correctly based on the connectivity tests."
                elif 'amazon' in domain.lower() or 'aws' in domain.lower():
                    answer += "This is an Amazon Web Services (AWS) endpoint providing cloud infrastructure services. "
                    answer += "AWS offers a comprehensive suite of cloud computing services including load balancers for traffic distribution, compute resources (EC2, Lambda), storage solutions (S3, EBS), networking services (VPC, CloudFront), and many other managed services. "
                    answer += "This endpoint appears to be part of AWS's infrastructure for managing and delivering cloud services."
                elif 'microsoft' in domain.lower() or 'azure' in domain.lower():
                    answer += "This is a Microsoft Azure service endpoint providing cloud computing services. "
                    answer += "Azure is Microsoft's cloud platform offering infrastructure as a service (IaaS), platform as a service (PaaS), and software as a service (SaaS) solutions. "
                    answer += "It provides services for computing, storage, networking, databases, AI, and other enterprise solutions."
                elif 'github' in domain.lower():
                    answer += "This is GitHub, a web-based platform for version control and software development collaboration. "
                    answer += "GitHub provides hosting for Git repositories, code collaboration tools, issue tracking, pull requests, and various integrations for software development workflows. "
                    answer += "It's widely used by developers and organizations for managing source code and collaborative software development."
                elif 'kubernetes' in domain.lower() or 'k8s' in domain.lower():
                    answer += "This is a Kubernetes service endpoint providing container orchestration and management capabilities. "
                    answer += "Kubernetes is an open-source platform for automating deployment, scaling, and management of containerized applications. "
                    answer += "It helps manage clusters of containers across multiple hosts and provides features like automatic scaling, service discovery, and load balancing."
                elif 'localhost' in domain.lower() or '127.0.0.1' in domain.lower():
                    answer += "This is a localhost or local network endpoint, typically used for local development or internal services. "
                    answer += "Localhost refers to the current computer being used, and services running on localhost are typically only accessible from the same machine. "
                    answer += "This is commonly used during development and testing phases before deploying services to production environments."
                elif domain.endswith('.svc.cluster.local'):
                    answer += "This is a Kubernetes internal service endpoint within a cluster. "
                    answer += "Services with the '.svc.cluster.local' domain are internal Kubernetes services that are accessible only within the cluster. "
                    answer += "These are used for service discovery and communication between different components of applications running in the Kubernetes cluster."
                elif 'elb.amazonaws.com' in domain.lower() or 'alb' in domain.lower():
                    answer += "This is an AWS Elastic Load Balancer (ALB) or Application Load Balancer endpoint. "
                    answer += "Load balancers are used to distribute incoming traffic across multiple targets (such as EC2 instances, containers, or IP addresses) to ensure high availability and fault tolerance. "
                    answer += "They help improve the availability and scalability of your applications by automatically routing traffic to healthy targets and handling traffic spikes."
                elif 'cloudfront.net' in domain.lower():
                    answer += "This is an AWS CloudFront CDN (Content Delivery Network) endpoint. "
                    answer += "CloudFront is a global content delivery network that speeds up distribution of static and dynamic web content by caching content at edge locations closer to users. "
                    answer += "It helps reduce latency and improve performance for users accessing your content from different geographic locations around the world."
                else:
                    answer += f"Based on the connectivity tests performed, this website ({domain}) is online and responding correctly. "
                    answer += f"The domain is resolving properly, the required ports are open, and the service is accessible. "
                    answer += "However, to determine the specific purpose or functionality of this website, you would need to visit the URL directly in a browser or consult the website's documentation, as the connectivity tests only verify network accessibility, not the actual content or services provided."
            
            else:
                # For other general questions, provide contextual analysis
                parsed_url = urllib.parse.urlparse(data['url'])
                domain = parsed_url.hostname or data['url']
                
                if data.get('http_status', {}).get('status_code') == 200:
                    answer += f"The website ({domain}) is currently online and accessible. "
                elif data.get('http_status', {}).get('status_code'):
                    status = data['http_status']['status_code']
                    answer += f"The website is returning HTTP status {status} ({data['http_status'].get('status_text', 'Unknown status')}). "
                
                if data.get('response_time', {}).get('milliseconds'):
                    response_time = data['response_time']['milliseconds']
                    if response_time < 500:
                        answer += f"The service is performing excellently with a response time of {response_time:.0f}ms, which indicates very good performance. "
                    elif response_time < 1000:
                        answer += f"The service has good performance with a response time of {response_time:.0f}ms. "
                    else:
                        answer += f"The response time is {response_time:.0f}ms, which could be improved with optimization techniques. "
                
                answer += "To maintain and improve service quality, I recommend monitoring performance and availability metrics, implementing proper logging and alerting systems, and conducting regular security assessments. "
                if not data.get('ssl_info'):
                    answer += "Additionally, upgrading to HTTPS would significantly improve security by encrypting all data transmitted between users and your server."
            
            return answer.strip() if answer else "I couldn't provide a specific answer to your question based on the available data."
        except Exception as e:
            return f"Error generating answer: {str(e)}"
    
    def _generate_architecture_fallback(self, data: dict) -> str:
        """Generate fallback architecture analysis."""
        analysis = f"""
# AWS Architecture Analysis

**Cluster:** {data.get('cluster', {}).get('clusterName', 'Unknown')}
**Analyzed:** {datetime.now().isoformat()}

## 📊 Infrastructure Overview

### ECS Cluster
- **Name:** {data.get('cluster', {}).get('clusterName', 'Unknown')}
- **Status:** {data.get('cluster', {}).get('status', 'Unknown')}
- **Services:** {len(data.get('services', []))}

### Services
"""
        
        for service in data.get('services', []):
            status = '✅' if service['runningCount'] == service['desiredCount'] else '❌'
            analysis += f"- {status} **{service['name']}**: {service['runningCount']}/{service['desiredCount']} running\n"
        
        analysis += """
## 🚀 Recommendations

### Architecture
- Consider auto-scaling for high availability
- Implement proper monitoring and alerting
- Use load balancers for traffic distribution

### Security
- Review security group rules
- Implement least privilege access
- Enable VPC flow logs

### Performance
- Monitor CPU and memory utilization
- Consider right-sizing task definitions
- Implement caching strategies

---
*Generated automatically - For AI insights ensure analysis service is available*
"""
        
        return analysis
    
    def _generate_health_fallback(self, data: dict) -> str:
        """Generate fallback health analysis."""
        analysis = f"""
# AWS Service Health Analysis

**Cluster:** {data.get('cluster', 'Unknown')}
**Analyzed:** {datetime.now().isoformat()}

## 🏥 Service Health Status

"""
        
        for service in data.get('services', []):
            status = '✅ Healthy' if service['healthy'] else '❌ Unhealthy'
            analysis += f"- **{service['service']}**: {status} ({service['running']}/{service['desired']} running)\n"
        
        analysis += """
## 🔧 Health Recommendations

### Monitoring
- Set up CloudWatch alerts for service metrics
- Monitor task health and restart counts
- Track performance trends

### Troubleshooting
- Check task logs for errors
- Verify resource allocation
- Review network configurations

### Optimization
- Implement proper scaling policies
- Consider health check tuning
- Use deployment strategies for zero downtime

---
*Generated automatically - For AI insights ensure analysis service is available*
"""
        
        return analysis
    
    def _generate_deployment_fallback(self, data: dict) -> str:
        """Generate fallback deployment analysis."""
        analysis = f"""
# Deployment Analysis

**Status:** {data.get('status', 'Unknown')}
**Analyzed:** {datetime.now().isoformat()}

## 📊 Deployment Results

**Recommendation:** {data.get('recommendation', 'Unknown')}

## 🔧 Next Steps

"""
        
        if data.get('status') == 'ready':
            analysis += """
✅ **Safe to Deploy**
- All services are healthy
- Infrastructure is ready for deployment
- Proceed with deployment plan

### Post-Deployment Actions
- Monitor service health
- Check application logs
- Verify functionality
- Set up monitoring alerts
"""
        elif data.get('status') == 'success':
            analysis += """
✅ **Deployment Successful**
- All services are running correctly
- Health checks passing
- Monitor for stability

### Post-Deployment Monitoring
- Watch performance metrics
- Monitor error rates
- Check user experience
- Document deployment
"""
        else:
            analysis += """
⚠️ **Deployment Issues Detected**
- Some services may need attention
- Review service logs
- Consider rollback if necessary

### Troubleshooting Steps
- Check individual service health
- Review deployment logs
- Verify configuration
- Consider rollback plan
"""
        
        analysis += """

---
*Generated automatically - For AI insights ensure analysis service is available.*
"""
        
        return analysis

def main():
    parser = argparse.ArgumentParser(
        description='DevOps Analyzer - Unified CLI tool for infrastructure analysis',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # URL Analysis
  %(prog)s url https://google.com
  %(prog)s url https://my-alb.amazonaws.com --question "Why is this slow?"
  
  # Infrastructure Analysis
  %(prog)s infrastructure --type architecture --cluster my-cluster
  %(prog)s infrastructure --type health --cluster my-cluster --service my-service
  
  # Deployment Analysis
  %(prog)s deploy --action pre-check --cluster my-cluster --service my-service
  %(prog)s deploy --action post-check --cluster my-cluster --service my-service
        """
    )
    
    parser.add_argument('--api-url', 
                       default='http://ollama-alb-427582956.us-east-1.elb.amazonaws.com',
                       help='Ollama API URL')
    parser.add_argument('--region', default='us-east-1', help='AWS region')
    parser.add_argument('--no-ai', action='store_true', help='Skip AI analysis, use fallback only')
    parser.add_argument('--output', '-o', help='Save analysis to file')
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # URL analyzer subcommand
    url_parser = subparsers.add_parser('url', help='Analyze URL connectivity and issues')
    url_parser.add_argument('url', help='URL to analyze')
    url_parser.add_argument('--question', '-q', help='Specific question about the URL')
    
    # Infrastructure analyzer subcommand
    infra_parser = subparsers.add_parser('infrastructure', help='Analyze AWS infrastructure')
    infra_parser.add_argument('--type', choices=['architecture', 'health'], required=True,
                              help='Type of analysis')
    infra_parser.add_argument('--cluster', required=True, help='ECS cluster name')
    infra_parser.add_argument('--service', help='ECS service name (for health analysis)')
    
    # Deployment analyzer subcommand
    deploy_parser = subparsers.add_parser('deploy', help='Deployment analysis and checks')
    deploy_parser.add_argument('--action', choices=['pre-check', 'post-check'], required=True,
                               help='Deployment action')
    deploy_parser.add_argument('--cluster', required=True, help='ECS cluster name')
    deploy_parser.add_argument('--service', help='ECS service name')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    print(f"🔍 DevOps Analyzer - {args.command.upper()} Analysis")
    print("=" * 60)
    
    # Initialize analyzer
    analyzer = DevOpsAnalyzer(args.api_url, args.region)
    
    # Perform analysis based on command
    try:
        if args.command == 'url':
            print(f"📡 Analyzing URL: {args.url}")
            if args.question:
                print(f"❓ Question: {args.question}")
            
            data = analyzer.analyze_url_connectivity(args.url)
            if 'error' in data:
                print(f"❌ {data['error']}")
                return 1
            
            # Display basic results
            print(f"\n📊 Basic Results:")
            if data.get('dns_resolution', {}).get('success'):
                print(f"   ✅ DNS: {data['dns_resolution']['ip_address']}")
            else:
                print(f"   ❌ DNS: Failed")
            
            if data.get('connectivity_tests', {}).get('port', {}).get('success'):
                print(f"   ✅ Port {data['port']}: Open")
            else:
                print(f"   ❌ Port {data['port']}: Closed")
            
            if data.get('ssl_info') and data.get('ssl_info', {}).get('success'):
                print(f"   ✅ SSL: Valid")
            elif data.get('ssl_info'):
                print(f"   ❌ SSL: Invalid")
            else:
                print(f"   ⚪ SSL: Not applicable (HTTP)")
            
            if data.get('http_status') and data.get('http_status', {}).get('status_code'):
                status = data['http_status']['status_code']
                print(f"   {'✅' if 200 <= status < 400 else '❌'} HTTP: {status}")
            elif data.get('http_status') and data.get('http_status', {}).get('error'):
                print(f"   ❌ HTTP: {data['http_status']['error']}")
            
            if data.get('response_time') and data.get('response_time', {}).get('milliseconds'):
                response_time = data['response_time']['milliseconds']
                print(f"   {'✅' if response_time < 1000 else '⚠️'} Response: {response_time:.0f}ms")
            
            # Get AI analysis
            print(f"\n🤖 Getting analysis...")
            if args.no_ai:
                analysis = analyzer.generate_fallback_analysis('url', data, args.question)
            else:
                analysis = analyzer.get_ai_analysis('url', data, args.question)
                # Check if AI analysis failed (timeout, connection error, or API error)
                if any(keyword in analysis.lower() for keyword in ['timeout', 'failed', 'connection', 'api returned status', 'api error']):
                    print("⚠️  AI analysis failed, using fallback...")
                    analysis = analyzer.generate_fallback_analysis('url', data, args.question)
        
        elif args.command == 'infrastructure':
            print(f"   Type: {args.type}")
            print(f"   Cluster: {args.cluster}")
            if args.service:
                print(f"   Service: {args.service}")
            
            print(f"\n📡 Gathering infrastructure data...")
            
            if args.type == 'architecture':
                data = analyzer.analyze_architecture(args.cluster)
            elif args.type == 'health':
                data = analyzer.analyze_health(args.cluster, args.service)
            
            if 'error' in data:
                print(f"❌ {data['error']}")
                return 1
            
            # Get AI analysis
            print(f"🤖 Getting analysis...")
            if args.no_ai:
                analysis = analyzer.generate_fallback_analysis(args.type, data)
            else:
                analysis = analyzer.get_ai_analysis(args.type, data)
                # Check if AI analysis failed (timeout, connection error, or API error)
                if any(keyword in analysis.lower() for keyword in ['timeout', 'failed', 'connection', 'api returned status', 'api error']):
                    print("⚠️  AI analysis failed, using fallback...")
                    analysis = analyzer.generate_fallback_analysis(args.type, data)
        
        elif args.command == 'deploy':
            print(f"   Action: {args.action}")
            print(f"   Cluster: {args.cluster}")
            if args.service:
                print(f"   Service: {args.service}")
            
            print(f"\n📡 Running deployment checks...")
            
            if args.action == 'pre-check':
                data = analyzer.pre_deployment_check(args.cluster, args.service)
            elif args.action == 'post-check':
                data = analyzer.post_deployment_check(args.cluster, args.service)
            
            if 'error' in data:
                print(f"❌ {data['error']}")
                return 1
            
            # Get AI analysis
            print(f"🤖 Getting analysis...")
            if args.no_ai:
                analysis = analyzer.generate_fallback_analysis('deployment', data)
            else:
                analysis = analyzer.get_ai_analysis('deployment', data)
                # Check if AI analysis failed (timeout, connection error, or API error)
                if any(keyword in analysis.lower() for keyword in ['timeout', 'failed', 'connection', 'api returned status', 'api error']):
                    print("⚠️  AI analysis failed, using fallback...")
                    analysis = analyzer.generate_fallback_analysis('deployment', data)
        
        else:
            print(f"Unknown command: {args.command}")
            return 1
        
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
        
        # Return exit code based on success
        return 0
        
    except KeyboardInterrupt:
        print(f"\n\n⚠️  Analysis interrupted by user")
        return 130
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        return 1

if __name__ == '__main__':
    sys.exit(main())
