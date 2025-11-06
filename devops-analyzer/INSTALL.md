# Installation Guide

## What You Need

- Python 3.7 or higher
- AWS CLI (for AWS features)
- Access to your Ollama API (for AI features)

## Install in 2 Steps

### Step 1: Install Python Packages
```bash
cd devops-analyzer
pip install -r requirements.txt
```

### Step 2: Test It Works
```bash
# Basic URL test (no AWS needed)
python devops-analyzer.py url https://google.com --no-ai
```

## AWS Setup (Optional)

If you want to use AWS infrastructure features:

```bash
# Configure AWS
aws configure

# Test AWS access
aws sts get-caller-identity
```

## Verify Everything

```bash
# Test URL analysis
python devops-analyzer.py url https://google.com

# Test AWS analysis (if configured)
python devops-analyzer.py infrastructure --type architecture --cluster your-cluster --no-ai
```

## Problems?

**Python not found?** Install Python from python.org

**AWS errors?** Check your credentials: `aws configure list`

**Network issues?** Try: `python devops-analyzer.py url https://google.com --no-ai`

---

**Ready to go! 🚀 Check README.md for usage examples.**
