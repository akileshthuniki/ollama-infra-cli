# DevOps Analyzer

A simple command-line tool to check URLs and AWS infrastructure. Uses your private AI for smart analysis.

## 🚀 Quick Start

### Install
```bash
pip install -r requirements.txt
```

### Use
```bash
# Check a website
python devops-analyzer.py url https://google.com

# Ask a specific question
python devops-analyzer.py url https://your-alb.amazonaws.com --question "Why is this slow?"

# Check AWS infrastructure
python devops-analyzer.py infrastructure --type architecture --cluster my-cluster

# Check deployment health
python devops-analyzer.py deploy --action pre-check --cluster production
```

## 📁 What's Inside

```
devops-analyzer/
├── devops-analyzer.py    # Main tool
├── requirements.txt      # Dependencies
├── README.md            # This file
├── INSTALL.md           # Setup help
├── DEVOPS_DAILY_SCENARIOS.md  # Real-world scenarios
├── url-analyzer/        # Old web stuff (optional)
└── docs/                # Your saved reports
```

## 🎯 What It Does

### 🔍 URL Analysis
- Checks if websites and services are working
- Tests DNS, SSL, and response times
- Answers your specific questions about issues
- Works with any URL (websites, APIs, load balancers)

### 🏗️ Infrastructure Analysis  
- Documents your AWS setup
- Checks service health
- Finds security and performance issues

### 🚀 Deployment Checks
- Pre-deployment health checks
- Post-deployment verification
- Service monitoring

## 📖 Commands

### URL Commands
```bash
python devops-analyzer.py url <URL> [--question "your question"] [--output file.md]
```

**Examples:**
```bash
# Basic check
python devops-analyzer.py url https://google.com

# Ask about performance
python devops-analyzer.py url https://slow-site.com --question "Why is this slow?"

# Security check
python devops-analyzer.py url https://api.example.com --question "Is this secure?" --output security.md
```

### Infrastructure Commands
```bash
python devops-analyzer.py infrastructure --type architecture|health --cluster <name>
```

**Examples:**
```bash
# Document infrastructure
python devops-analyzer.py infrastructure --type architecture --cluster production

# Check service health
python devops-analyzer.py infrastructure --type health --cluster production
```

### Deployment Commands
```bash
python devops-analyzer.py deploy --action pre-check|post-check --cluster <name>
```

**Examples:**
```bash
# Before deployment
python devops-analyzer.py deploy --action pre-check --cluster production

# After deployment
python devops-analyzer.py deploy --action post-check --cluster production
```

## 🔒 Privacy

✅ All analysis happens on your infrastructure  
✅ No data sent to external services  
✅ Your information stays private  

## 🆘 Need Help?

### Common Problems

**Tool not working?**
```bash
# Use without AI for faster results
python devops-analyzer.py url https://google.com --no-ai
```

**AWS permission errors?**
```bash
# Check your AWS setup
aws sts get-caller-identity
```

**Network issues?**
```bash
# Test basic connectivity
python devops-analyzer.py url https://google.com --no-ai
```

### More Examples

See **DEVOPS_DAILY_SCENARIOS.md** for real-world scenarios and scripts.

---

**That's it! Simple, private, and powerful DevOps analysis.** 🚀
