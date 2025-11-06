# DevOps Engineer Day-to-Day Scenarios

This document contains common questions and scenarios that DevOps engineers encounter in their daily work, along with example commands and expected outputs.

## Table of Contents
1. [Pre-Deployment Checks](#pre-deployment-checks)
2. [Post-Deployment Verification](#post-deployment-verification)
3. [Infrastructure Health Monitoring](#infrastructure-health-monitoring)
4. [Performance Analysis](#performance-analysis)
5. [Security Audits](#security-audits)
6. [CI/CD Pipeline Integration](#cicd-pipeline-integration)
7. [Troubleshooting Production Issues](#troubleshooting-production-issues)
8. [Load Balancer Analysis](#load-balancer-analysis)
9. [Service Availability Checks](#service-availability-checks)
10. [Architecture Documentation](#architecture-documentation)

---

## Pre-Deployment Checks

### Scenario 1: Pre-Deployment Validation
**Question:** "Is the infrastructure ready for deployment?"

**Command:**
```bash
python devops-analyzer.py deploy --action pre-check --cluster production --service api-service
```

**Expected Output:**
```
🔍 DevOps Analyzer - DEPLOY Analysis
============================================================
   Action: pre-check
   Cluster: production
   Service: api-service

📡 Running deployment checks...

🤖 Getting analysis...
⚠️  AI analysis failed, using fallback...

# Deployment Analysis

**Status:** ready
**Analyzed:** 2025-11-05T20:45:00.000000

## 📊 Deployment Results

**Recommendation:** Safe to deploy

## 🔧 Next Steps

✅ **Safe to Deploy**
- All services are healthy
- Infrastructure is ready for deployment
- Proceed with deployment plan

### Post-Deployment Actions
- Monitor service health
- Check application logs
- Verify functionality
- Set up monitoring alerts
```

---

## Post-Deployment Verification

### Scenario 2: Post-Deployment Health Check
**Question:** "Did the deployment succeed? Are all services healthy?"

**Command:**
```bash
python devops-analyzer.py deploy --action post-check --cluster production --service api-service
```

**Expected Output:**
```
🔍 DevOps Analyzer - DEPLOY Analysis
============================================================
   Action: post-check
   Cluster: production
   Service: api-service

📡 Running deployment checks...

🤖 Getting analysis...
⚠️  AI analysis failed, using fallback...

# Deployment Analysis

**Status:** success
**Analyzed:** 2025-11-05T20:50:00.000000

## 📊 Deployment Results

**Recommendation:** Deployment successful

## 🔧 Next Steps

✅ **Deployment Successful**
- All services are running correctly
- Health checks passing
- Monitor for stability

### Post-Deployment Monitoring
- Watch performance metrics
- Monitor error rates
- Check user experience
- Document deployment
```

---

## Infrastructure Health Monitoring

### Scenario 3: Daily Health Check
**Question:** "What's the current health status of all services in production?"

**Command:**
```bash
python devops-analyzer.py infrastructure --type health --cluster production
```

**Expected Output:**
```
🔍 DevOps Analyzer - INFRASTRUCTURE Analysis
============================================================
   Type: health
   Cluster: production

📡 Gathering infrastructure data...

🤖 Getting analysis...
⚠️  AI analysis failed, using fallback...

# AWS Service Health Analysis

**Cluster:** production
**Analyzed:** 2025-11-05T21:00:00.000000

## 🏥 Service Health Status

- **api-service**: ✅ Healthy (3/3 running)
- **web-service**: ✅ Healthy (2/2 running)
- **worker-service**: ✅ Healthy (5/5 running)

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
```

---

## Performance Analysis

### Scenario 4: API Performance Investigation
**Question:** "Why is the API endpoint slow? How can I improve performance?"

**Command:**
```bash
python devops-analyzer.py url https://api.production.com/api/v1/users --question "Why is this slow? How can I improve performance?"
```

**Expected Output:**
```
🔍 DevOps Analyzer - URL Analysis
============================================================
📡 Analyzing URL: https://api.production.com/api/v1/users
❓ Question: Why is this slow? How can I improve performance?

📊 Basic Results:
   ✅ DNS: 10.0.1.50
   ✅ Port 443: Open
   ✅ SSL: Valid
   ✅ HTTP: 200
   ⚠️ Response: 2150ms

🤖 Getting analysis...
⚠️  AI analysis failed, using fallback...

Your service is experiencing very slow response times (2150ms), which significantly impacts user experience. This could be due to high server load, inefficient database queries, or lack of caching. I recommend checking your server resource utilization (CPU, memory, and network), implementing caching at multiple levels (application cache, database query cache, and CDN), and considering a Content Delivery Network (CDN) to serve static content from locations closer to your users.
```

---

## Security Audits

### Scenario 5: SSL Certificate Check
**Question:** "Is this endpoint secure? Are there any security issues?"

**Command:**
```bash
python devops-analyzer.py url https://api.production.com --question "Is this secure? Are there any security issues?"
```

**Expected Output:**
```
🔍 DevOps Analyzer - URL Analysis
============================================================
📡 Analyzing URL: https://api.production.com
❓ Question: Is this secure? Are there any security issues?

📊 Basic Results:
   ✅ DNS: 10.0.1.50
   ✅ Port 443: Open
   ✅ SSL: Valid
   ✅ HTTP: 200
   ✅ Response: 245ms

🤖 Getting analysis...
⚠️  AI analysis failed, using fallback...

Your website is properly secured with a valid SSL certificate configured correctly. This means your connections are encrypted using HTTPS, which protects data in transit between clients and your server. Your SSL certificate is valid and properly configured, providing both security and trust for your users.
```

### Scenario 6: HTTP to HTTPS Migration Check
**Question:** "Is this service using HTTP? Should we upgrade to HTTPS?"

**Command:**
```bash
python devops-analyzer.py url http://legacy-service.internal.com --question "Is this secure? Should we upgrade to HTTPS?"
```

**Expected Output:**
```
🔍 DevOps Analyzer - URL Analysis
============================================================
📡 Analyzing URL: http://legacy-service.internal.com
❓ Question: Is this secure? Should we upgrade to HTTPS?

📊 Basic Results:
   ✅ DNS: 10.0.2.100
   ✅ Port 80: Open
   ⚪ SSL: Not applicable (HTTP)
   ✅ HTTP: 200
   ✅ Response: 180ms

🤖 Getting analysis...
⚠️  AI analysis failed, using fallback...

Your website is currently using HTTP, which is a critical security concern. All data transmitted between users and your server is unencrypted, making it vulnerable to interception and man-in-the-middle attacks. I strongly recommend upgrading to HTTPS immediately by obtaining an SSL certificate (you can use free certificates from Let's Encrypt). Additionally, implement HTTPS redirects to automatically send HTTP traffic to HTTPS, and add security headers like HSTS (HTTP Strict Transport Security) and CSP (Content Security Policy) to further enhance your security posture.
```

---

## CI/CD Pipeline Integration

### Scenario 7: Pre-Deployment Check in CI/CD
**Question:** "Is it safe to deploy? Are all services healthy?"

**Command (for CI/CD pipeline):**
```bash
python devops-analyzer.py deploy --action pre-check --cluster staging --service api-service
```

**Expected Output:**
```
🔍 DevOps Analyzer - DEPLOY Analysis
============================================================
   Action: pre-check
   Cluster: staging
   Service: api-service

📡 Running deployment checks...

🤖 Getting analysis...
⚠️  AI analysis failed, using fallback...

# Deployment Analysis

**Status:** ready
**Analyzed:** 2025-11-05T22:00:00.000000

## 📊 Deployment Results

**Recommendation:** Safe to deploy
```

**CI/CD Integration Example (GitHub Actions):**
```yaml
name: Pre-Deployment Check
on:
  push:
    branches: [main]

jobs:
  pre-deploy-check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Setup Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.9'
          
      - name: Install dependencies
        run: pip install -r requirements.txt
        
      - name: Pre-deployment check
        run: |
          python devops-analyzer.py deploy --action pre-check \
            --cluster ${{ env.CLUSTER }} \
            --service ${{ env.SERVICE }}
        env:
          CLUSTER: production
          SERVICE: api-service
```

---

## Troubleshooting Production Issues

### Scenario 8: Production Incident Investigation
**Question:** "Why are users getting 500 errors? What's the issue?"

**Command:**
```bash
python devops-analyzer.py url https://api.production.com/api/v1/orders --question "Why are we getting errors? What's the issue?"
```

**Expected Output:**
```
🔍 DevOps Analyzer - URL Analysis
============================================================
📡 Analyzing URL: https://api.production.com/api/v1/orders
❓ Question: Why are we getting errors? What's the issue?

📊 Basic Results:
   ✅ DNS: 10.0.1.50
   ✅ Port 443: Open
   ✅ SSL: Valid
   ❌ HTTP: 500
   ⚠️ Response: 3500ms

🤖 Getting analysis...
⚠️  AI analysis failed, using fallback...

During the connectivity analysis, I found several issues that need attention:
  - HTTP Error 500: Internal Server Error
  - Response time is very slow (3500ms)

These issues should be investigated and resolved to ensure your service operates correctly. Check your server logs, review your configuration, and verify that all required services are running properly. Additionally, there's an HTTP error (500) being returned, which indicates the service is encountering issues. You should check your service logs and application error handling to identify and resolve the root cause.
```

---

## Load Balancer Analysis

### Scenario 9: ALB Health Check
**Question:** "Is the load balancer working correctly? How can I improve availability?"

**Command:**
```bash
python devops-analyzer.py url http://my-alb-123456789.us-east-1.elb.amazonaws.com --question "How can I improve availability?"
```

**Expected Output:**
```
🔍 DevOps Analyzer - URL Analysis
============================================================
📡 Analyzing URL: http://my-alb-123456789.us-east-1.elb.amazonaws.com
❓ Question: How can I improve availability?

📊 Basic Results:
   ✅ DNS: 3.214.49.48
   ✅ Port 80: Open
   ⚪ SSL: Not applicable (HTTP)
   ✅ HTTP: 200
   ✅ Response: 145ms

🤖 Getting analysis...
⚠️  AI analysis failed, using fallback...

Your service is currently performing well with a response time of 145ms. However, you're currently using HTTP, which poses security risks and can impact availability. Upgrading to HTTPS is critical for both security and reliability, as it ensures encrypted connections and prevents potential man-in-the-middle attacks. The connectivity tests show no critical issues detected, indicating your service is stable. To further enhance availability, consider deploying across multiple Availability Zones (AZs) to ensure redundancy and fault tolerance. Setting up comprehensive health checks and monitoring alerts will help you proactively identify and resolve issues before they impact users. Implementing proper load balancing ensures traffic is distributed evenly across your infrastructure, and auto-scaling based on demand patterns will help maintain performance during traffic spikes.
```

---

## Service Availability Checks

### Scenario 10: Critical Service Monitoring
**Question:** "Is the payment service available? Are there any issues?"

**Command:**
```bash
python devops-analyzer.py url https://payment-api.production.com/health --question "Are there any issues with this service?"
```

**Expected Output:**
```
🔍 DevOps Analyzer - URL Analysis
============================================================
📡 Analyzing URL: https://payment-api.production.com/health
❓ Question: Are there any issues with this service?

📊 Basic Results:
   ✅ DNS: 10.0.3.25
   ✅ Port 443: Open
   ✅ SSL: Valid
   ✅ HTTP: 200
   ✅ Response: 98ms

🤖 Getting analysis...
⚠️  AI analysis failed, using fallback...

Based on the connectivity tests performed, no critical issues were detected with your service. The DNS resolution is working, the required ports are open, and the service is responding correctly. However, I recommend regularly monitoring your service and performing periodic checks to maintain this healthy state.
```

---

## Architecture Documentation

### Scenario 11: Infrastructure Documentation
**Question:** "What's the current architecture? Document the infrastructure."

**Command:**
```bash
python devops-analyzer.py infrastructure --type architecture --cluster production --output architecture-report.md
```

**Expected Output:**
```
🔍 DevOps Analyzer - INFRASTRUCTURE Analysis
============================================================
   Type: architecture
   Cluster: production

📡 Gathering infrastructure data...

🤖 Getting analysis...
⚠️  AI analysis failed, using fallback...

# AWS Architecture Analysis

**Cluster:** production
**Analyzed:** 2025-11-05T23:00:00.000000

## 📊 Infrastructure Overview

### ECS Cluster
- **Name:** production
- **Status:** ACTIVE
- **Services:** 5

### Services
- ✅ **api-service**: 3/3 running
- ✅ **web-service**: 2/2 running
- ✅ **worker-service**: 5/5 running
- ✅ **cache-service**: 2/2 running
- ✅ **db-service**: 1/1 running

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

💾 Analysis saved to: architecture-report.md
```

---

## Daily Workflow Examples

### Morning Routine: Health Check
```bash
# Check all production services
python devops-analyzer.py infrastructure --type health --cluster production

# Check critical endpoints
python devops-analyzer.py url https://api.production.com/health --question "Is everything working correctly?"
python devops-analyzer.py url https://payment-api.production.com/health --question "Are there any issues?"
```

### Before Deployment: Pre-Check
```bash
# Validate infrastructure is ready
python devops-analyzer.py deploy --action pre-check --cluster staging --service api-service

# Check target URL
python devops-analyzer.py url https://staging-api.example.com --question "Is this ready for deployment?"
```

### After Deployment: Post-Check
```bash
# Verify deployment success
python devops-analyzer.py deploy --action post-check --cluster production --service api-service

# Test new deployment
python devops-analyzer.py url https://api.production.com/api/v1/health --question "Did the deployment succeed?"
```

### Performance Investigation
```bash
# Check slow endpoints
python devops-analyzer.py url https://api.production.com/slow-endpoint --question "Why is this slow? How can I improve performance?"

# Analyze response times
python devops-analyzer.py url https://api.production.com --question "What's the performance status?"
```

### Security Audit
```bash
# Check SSL certificates
python devops-analyzer.py url https://api.production.com --question "Is this secure? Are there any security issues?"

# Verify HTTPS configuration
python devops-analyzer.py url https://www.production.com --question "Is the SSL certificate valid?"
```

---

## Integration with Monitoring Tools

### Prometheus Alert Integration
```bash
#!/bin/bash
# alert_handler.sh

ALERT_URL=$1
ALERT_NAME=$2

# Generate analysis for the alert
python devops-analyzer.py url $ALERT_URL \
  --question "What is causing this alert? How can I fix it?" \
  --output "alerts/$(date +%Y%m%d_%H%M%S)_${ALERT_NAME}_analysis.md"

# Send to Slack/Teams
# Add your notification logic here
```

### Scheduled Health Checks
```bash
#!/bin/bash
# daily_health_check.sh

DATE=$(date +%Y%m%d)
REPORT_DIR="daily_reports"
mkdir -p $REPORT_DIR

# Production cluster health
python devops-analyzer.py infrastructure --type health \
  --cluster production \
  --output "$REPORT_DIR/${DATE}_production_health.md"

# Critical endpoints
python devops-analyzer.py url https://api.production.com/health \
  --question "Is everything working correctly?" \
  --output "$REPORT_DIR/${DATE}_api_health.md"

python devops-analyzer.py url https://payment-api.production.com/health \
  --question "Are there any issues?" \
  --output "$REPORT_DIR/${DATE}_payment_health.md"
```

---

## Best Practices

1. **Regular Health Checks**: Run infrastructure health checks daily
2. **Pre-Deployment Validation**: Always check infrastructure before deployments
3. **Post-Deployment Verification**: Verify deployments immediately after completion
4. **Performance Monitoring**: Monitor response times and investigate slow endpoints
5. **Security Audits**: Regularly check SSL certificates and security configurations
6. **Documentation**: Generate architecture reports for documentation
7. **Automation**: Integrate into CI/CD pipelines for automated checks
8. **Alerting**: Use with monitoring tools for proactive issue detection

---

## Troubleshooting Common Issues

### Issue: Service Not Responding
```bash
python devops-analyzer.py url https://api.production.com --question "Why is this service not responding? What's the issue?"
```

### Issue: Slow Performance
```bash
python devops-analyzer.py url https://api.production.com/slow-endpoint --question "Why is this slow? How can I improve performance?"
```

### Issue: SSL Certificate Expired
```bash
python devops-analyzer.py url https://api.production.com --question "Is the SSL certificate valid? Are there any security issues?"
```

### Issue: Deployment Failed
```bash
python devops-analyzer.py deploy --action post-check --cluster production --service api-service
```

---

*This document provides examples of common DevOps scenarios. Adjust commands and questions based on your specific infrastructure and requirements.*

