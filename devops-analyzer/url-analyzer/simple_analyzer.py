#!/usr/bin/env python3
"""
Simple AWS Infrastructure Analyzer with Fallback Analysis

This tool provides AWS infrastructure analysis with graceful fallback
when the Ollama API is slow or unavailable.
"""

import boto3
import json
import argparse
import sys
from datetime import datetime, timezone
from typing import Dict, List, Any
import requests

class SimpleAWSAnalyzer:
    def __init__(self, ollama_api_url: str):
        self.ollama_api_url = ollama_api_url
        self.session = boto3.Session()
        self.ecs = self.session.client('ecs')
        self.elbv2 = self.session.client('elbv2')
        self.ec2 = self.session.client('ec2')
        self.cloudwatch = self.session.client('cloudwatch')
        
    def query_ollama_api(self, prompt: str, context: str = "aws", timeout: int = 30) -> Dict[str, Any]:
        """Send analysis request to Ollama API with short timeout."""
        try:
            response = requests.post(
                f"{self.ollama_api_url}/api/analyze",
                json={"prompt": prompt, "context": context},
                headers={"Content-Type": "application/json"},
                timeout=timeout
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.Timeout:
            print(f"⏰ API timeout after {timeout}s - using fallback analysis")
            return None
        except requests.exceptions.RequestException as e:
            print(f"❌ API error: {e} - using fallback analysis")
            return None

    def get_cluster_summary(self, cluster_name: str) -> Dict[str, Any]:
        """Get basic cluster information."""
        try:
            response = self.ecs.describe_clusters(clusters=[cluster_name])
            cluster = response['clusters'][0]
            
            services_response = self.ecs.list_services(cluster=cluster_name)
            services = []
            if services_response['serviceArns']:
                services_detail = self.ecs.describe_services(
                    cluster=cluster_name, 
                    services=services_response['serviceArns']
                )
                services = services_detail['services']
            
            return {
                'cluster_name': cluster.get('clusterName', 'Unknown'),
                'status': cluster.get('status', 'Unknown'),
                'running_tasks': cluster.get('runningTasksCount', 0),
                'pending_tasks': cluster.get('pendingTasksCount', 0),
                'active_services': len(services),
                'service_names': [s.get('serviceName', 'Unknown') for s in services],
                'services': [
                    {
                        'name': s.get('serviceName', 'Unknown'),
                        'status': s.get('status', 'Unknown'),
                        'running': s.get('runningCount', 0),
                        'desired': s.get('desiredCount', 0)
                    } for s in services
                ]
            }
        except Exception as e:
            print(f"❌ Error getting cluster info: {e}")
            return {}

    def get_load_balancers_summary(self) -> List[Dict[str, Any]]:
        """Get load balancer summary."""
        try:
            lbs = self.elbv2.describe_load_balancers()
            return [
                {
                    'name': lb.get('LoadBalancerName', 'Unknown'),
                    'type': lb.get('Type', 'Unknown'),
                    'state': lb.get('State', {}).get('Code', 'Unknown'),
                    'scheme': lb.get('Scheme', 'Unknown'),
                    'dns': lb.get('DNSName', 'Unknown')
                } for lb in lbs['LoadBalancers']
            ]
        except Exception as e:
            print(f"❌ Error getting load balancers: {e}")
            return []

    def generate_fallback_analysis(self, cluster_data: Dict[str, Any], lbs: List[Dict[str, Any]]) -> str:
        """Generate fallback analysis when API is unavailable."""
        
        analysis = f"""
# AWS Infrastructure Analysis Report
**Generated:** {datetime.now().isoformat()}  
**Cluster:** {cluster_data.get('cluster_name', 'Unknown')}  
**Status:** {cluster_data.get('status', 'Unknown')}  

## 📊 Infrastructure Overview

### ECS Cluster Summary
- **Cluster Name:** {cluster_data.get('cluster_name', 'Unknown')}
- **Status:** {cluster_data.get('status', 'Unknown')}
- **Running Tasks:** {cluster_data.get('running_tasks', 0)}
- **Pending Tasks:** {cluster_data.get('pending_tasks', 0)}
- **Active Services:** {cluster_data.get('active_services', 0)}

### Services Details
"""
        
        for service in cluster_data.get('services', []):
            status_emoji = "✅" if service.get('running', 0) == service.get('desired', 0) else "⚠️"
            analysis += f"""
- **{service.get('name', 'Unknown')}** {status_emoji}
  - Status: {service.get('status', 'Unknown')}
  - Running: {service.get('running', 0)}/{service.get('desired', 0)} tasks
"""
        
        analysis += f"""
### Load Balancers
"""
        
        for lb in lbs:
            state_emoji = "✅" if lb.get('state') == 'active' else "❌"
            analysis += f"""
- **{lb.get('name', 'Unknown')}** {state_emoji}
  - Type: {lb.get('type', 'Unknown')}
  - Scheme: {lb.get('scheme', 'Unknown')}
  - DNS: {lb.get('dns', 'Unknown')}
"""
        
        analysis += """
## 🔍 Analysis & Recommendations

### Architecture Assessment
"""
        
        if cluster_data.get('running_tasks', 0) > 0:
            analysis += "✅ **Active Workload:** Cluster has running tasks and is processing work\n"
        else:
            analysis += "⚠️ **No Running Tasks:** Cluster may be idle or experiencing issues\n"
        
        if cluster_data.get('active_services', 0) > 0:
            analysis += f"✅ **Service Configuration:** {cluster_data.get('active_services', 0)} services configured\n"
        else:
            analysis += "⚠️ **No Services:** No services found in cluster\n"
        
        if len(lbs) > 0:
            analysis += f"✅ **Load Balancing:** {len(lbs)} load balancer(s) configured for traffic distribution\n"
        else:
            analysis += "⚠️ **No Load Balancer:** Consider adding load balancer for high availability\n"
        
        analysis += """
### Security Considerations
- 🔒 Review security group rules for least privilege
- 🔒 Ensure IAM roles follow principle of least privilege
- 🔒 Monitor VPC flow logs for unusual traffic

### Performance Optimization
- 📈 Monitor CloudWatch metrics for CPU/memory utilization
- 📈 Consider auto-scaling based on demand
- 📈 Review task definitions for resource allocation

### High Availability
- 🌐 Load balancers provide fault tolerance
- 🌐 Consider multi-AZ deployment for critical services
- 🌐 Implement health checks for service monitoring

### Next Steps
1. **Monitor:** Set up CloudWatch alerts for key metrics
2. **Security:** Conduct regular security audits
3. **Optimization:** Review resource utilization and rightsizing
4. **Documentation:** Keep architecture documentation updated

---
*This analysis was generated automatically using AWS API data. For AI-powered insights, ensure the Ollama API is accessible and responsive.*
"""
        
        return analysis

    def analyze_architecture(self, cluster_name: str) -> None:
        """Analyze architecture with fallback."""
        print(f"🏗️  Analyzing architecture for cluster: {cluster_name}")
        
        # Get infrastructure data
        cluster_data = self.get_cluster_summary(cluster_name)
        load_balancers = self.get_load_balancers_summary()
        
        if not cluster_data:
            print("❌ Could not retrieve cluster information")
            return
        
        # Try AI analysis first
        simple_prompt = f"""
        Briefly analyze this AWS ECS infrastructure:
        
        Cluster: {cluster_data.get('cluster_name')} ({cluster_data.get('status')})
        Services: {cluster_data.get('active_services')}
        Running tasks: {cluster_data.get('running_tasks')}
        Load balancers: {len(load_balancers)}
        
        Provide a concise architecture overview in 3-4 paragraphs.
        """
        
        ai_result = self.query_ollama_api(simple_prompt, "aws-architecture", timeout=30)
        
        print("\n" + "="*80)
        print("📋 ARCHITECTURE ANALYSIS")
        print("="*80)
        
        if ai_result:
            print("🤖 **AI-Powered Analysis:**")
            print(ai_result.get('response', 'No response received'))
            print(f"\n⏱️  Processing time: {ai_result.get('processing_time_ms', 0):.2f}ms")
            print(f"🤖 Model: {ai_result.get('model', 'unknown')}")
        else:
            print("📊 **Automated Analysis (AI API unavailable):**")
            fallback_analysis = self.generate_fallback_analysis(cluster_data, load_balancers)
            print(fallback_analysis)
        
        print("="*80)
        
        # Save analysis
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"architecture_analysis_{timestamp}.md"
        
        with open(filename, 'w', encoding='utf-8') as f:
            if ai_result:
                f.write(f"# AI-Powered Architecture Analysis - {cluster_name}\n\n")
                f.write(f"Generated: {datetime.now().isoformat()}\n\n")
                f.write(f"Processing time: {ai_result.get('processing_time_ms', 0):.2f}ms\n\n")
                f.write(f"Model: {ai_result.get('model', 'unknown')}\n\n")
                f.write(ai_result.get('response', 'No response received'))
            else:
                f.write(self.generate_fallback_analysis(cluster_data, load_balancers))
        
        print(f"💾 Analysis saved to: {filename}")

def main():
    parser = argparse.ArgumentParser(description='Simple AWS Infrastructure Analyzer')
    parser.add_argument('--cluster', required=True, help='ECS cluster name')
    parser.add_argument('--api-url', default='http://ollama-alb-427582956.us-east-1.elb.amazonaws.com',
                       help='Ollama API URL')
    
    args = parser.parse_args()
    
    analyzer = SimpleAWSAnalyzer(args.api_url)
    
    try:
        analyzer.analyze_architecture(args.cluster)
    except KeyboardInterrupt:
        print("\n⚠️  Analysis interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
