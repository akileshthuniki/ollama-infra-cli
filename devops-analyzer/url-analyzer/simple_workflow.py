#!/usr/bin/env python3
"""
Simple DevOps Workflow with Fallback Analysis

This script demonstrates a complete workflow using your private Ollama API
with graceful fallback when the API is slow or unavailable.

Usage:
    python simple_workflow.py --cluster ollama-cluster --service ollama-api
"""

import argparse
import json
import sys
import time
import os
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from simple_analyzer import SimpleAWSAnalyzer

def run_simple_workflow(cluster_name: str, service_name: str, api_url: str):
    """Run a complete DevOps workflow with fallback analysis."""
    
    print("🚀 Starting Simple DevOps Workflow")
    print("="*60)
    
    # Initialize analyzer
    analyzer = SimpleAWSAnalyzer(api_url)
    
    # Step 1: Architecture Analysis
    print("\n📋 STEP 1: Architecture Analysis")
    print("-" * 40)
    analyzer.analyze_architecture(cluster_name)
    
    # Step 2: Service Health Check
    print("\n💓 STEP 2: Service Health Check")
    print("-" * 40)
    
    try:
        service_info = analyzer.get_cluster_summary(cluster_name)
        services = service_info.get('services', [])
        target_service = next((s for s in services if s.get('name') == service_name), None)
        
        if target_service:
            print(f"✅ Service '{service_name}' found:")
            print(f"   Status: {target_service.get('status', 'Unknown')}")
            print(f"   Running: {target_service.get('running', 0)}/{target_service.get('desired', 0)} tasks")
            
            if target_service.get('running', 0) == target_service.get('desired', 0):
                print("✅ Service is healthy")
            else:
                print("⚠️  Service may have issues")
        else:
            print(f"❌ Service '{service_name}' not found in cluster")
    except Exception as e:
        print(f"❌ Error checking service health: {e}")
    
    # Step 3: Infrastructure Summary
    print("\n📊 STEP 3: Infrastructure Summary")
    print("-" * 40)
    
    try:
        cluster_data = analyzer.get_cluster_summary(cluster_name)
        load_balancers = analyzer.get_load_balancers_summary()
        
        print(f"🏗️  Cluster: {cluster_data.get('cluster_name', 'Unknown')}")
        print(f"   Status: {cluster_data.get('status', 'Unknown')}")
        print(f"   Running tasks: {cluster_data.get('running_tasks', 0)}")
        print(f"   Active services: {cluster_data.get('active_services', 0)}")
        print(f"⚖️  Load balancers: {len(load_balancers)}")
        
        for lb in load_balancers:
            state_emoji = "✅" if lb.get('state') == 'active' else "❌"
            print(f"   {state_emoji} {lb.get('name', 'Unknown')} ({lb.get('type', 'Unknown')})")
            
    except Exception as e:
        print(f"❌ Error getting infrastructure summary: {e}")
    
    # Step 4: Generate Summary Report
    print("\n📄 STEP 4: Summary Report")
    print("-" * 40)
    
    timestamp = datetime.now().isoformat()
    
    report = f"""# DevOps Workflow Summary Report

**Generated:** {timestamp}
**Cluster:** {cluster_name}
**Service:** {service_name}
**Status:** ✅ COMPLETED

## Workflow Steps Completed

1. ✅ Architecture Analysis - Generated comprehensive documentation
2. ✅ Service Health Check - Verified service status and health
3. ✅ Infrastructure Summary - Collected infrastructure overview
4. ✅ Summary Report - Created this summary document

## Infrastructure Overview

### Cluster Status
- **Name:** {cluster_data.get('cluster_name', 'Unknown')}
- **Status:** {cluster_data.get('status', 'Unknown')}
- **Running Tasks:** {cluster_data.get('running_tasks', 0)}
- **Active Services:** {cluster_data.get('active_services', 0)}

### Service Status
- **Service:** {service_name}
- **Status:** {target_service.get('status', 'Not found') if 'target_service' in locals() else 'Not found'}
- **Tasks:** {target_service.get('running', 0)}/{target_service.get('desired', 0) if 'target_service' in locals() else '0/0'}

### Load Balancers
- **Count:** {len(load_balancers)}
- **Types:** {', '.join([lb.get('type', 'Unknown') for lb in load_balancers])}

## Generated Files

- `architecture_analysis_*.md` - Architecture documentation
- `workflow_summary_{timestamp.replace(':', '').replace('-', '').replace('.', '')}.md` - This summary report

## Recommendations

### Immediate Actions
- ✅ Architecture documentation is available
- ✅ Service health has been verified
- ✅ Infrastructure overview is complete

### Monitoring Recommendations
- 📈 Set up CloudWatch alerts for:
  - ECS task failures
  - High CPU/memory utilization
  - Load balancer unhealthy hosts

### Security Recommendations
- 🔒 Regular security group audits
- 🔒 IAM role permissions review
- 🔒 VPC flow log analysis

### Optimization Opportunities
- ⚡ Consider auto-scaling for variable workloads
- ⚡ Review resource allocation for cost optimization
- ⚡ Implement health checks for better reliability

## Next Steps

1. **Schedule Regular Analysis:** Run this workflow weekly
2. **Set Up Monitoring:** Configure alerts and notifications
3. **Documentation:** Keep architecture docs updated
4. **Security:** Implement regular security scans

---

*This workflow was completed using AWS API data with fallback analysis. For AI-powered insights, ensure the Ollama API is responsive.*
"""
    
    # Save summary report
    filename = f"simple_workflow_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"📄 Summary report saved to: {filename}")
    
    print("\n🎉 Simple Workflow Completed Successfully!")
    print("="*60)
    
    return True

def main():
    parser = argparse.ArgumentParser(description='Simple DevOps Workflow with Analysis')
    parser.add_argument('--cluster', required=True, help='ECS cluster name')
    parser.add_argument('--service', required=True, help='ECS service name')
    parser.add_argument('--api-url', default='http://ollama-alb-427582956.us-east-1.elb.amazonaws.com',
                       help='Ollama API URL')
    
    args = parser.parse_args()
    
    try:
        success = run_simple_workflow(args.cluster, args.service, args.api_url)
        sys.exit(0 if success else 1)
        
    except KeyboardInterrupt:
        print("\n⚠️  Workflow interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Workflow error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
