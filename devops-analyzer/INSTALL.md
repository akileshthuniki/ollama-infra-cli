# Installation Guide

Quick installation guide for DevOps Analyzer.

---

## Requirements

- **Python 3.7+** (Python 3.9+ recommended)
- **pip** (Python package manager)
- **AWS CLI** (optional, for AWS features)
- **Ollama API access** (optional, for AI features)

---

## Quick Installation

### Step 1: Install Dependencies

```bash
cd devops-analyzer
pip install -r requirements.txt
```

### Step 2: Verify Installation

```bash
python devops-analyzer.py --help
```

### Step 3: Test It Works

```bash
# Basic test (no AI or AWS required)
python devops-analyzer.py url https://google.com --no-ai
```

---

## Installation with Virtual Environment (Recommended)

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# Linux/macOS:
source venv/bin/activate
# Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Verify
python devops-analyzer.py --help
```

---

## Optional: AWS Configuration

For AWS infrastructure analysis:

```bash
# Configure AWS CLI
aws configure

# Verify access
aws sts get-caller-identity
```

---

## Troubleshooting

### Python not found?
```bash
# Try python3 instead
python3 --version
python3 -m pip install -r requirements.txt
```

### Permission errors?
```bash
# Use virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate    # Windows
pip install -r requirements.txt
```

### Module not found?
```bash
# Reinstall dependencies
pip install -r requirements.txt --upgrade

# Verify installation
pip list | grep requests
```

### Windows encoding errors?
```powershell
# Set encoding
$env:PYTHONIOENCODING="utf-8"
python devops-analyzer.py url https://google.com --no-ai
```

---

## Next Steps

- Read [README.md](./README.md) for usage guide
- Check [DEVOPS_DAILY_SCENARIOS.md](./DEVOPS_DAILY_SCENARIOS.md) for examples
- Configure AWS credentials for infrastructure analysis

---

**That's it! You're ready to go.** 🚀
