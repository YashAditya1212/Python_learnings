# 🐍 Python for DevOps — Complete Reference Guide

> **Scope:** Virtual Environments · Packages · Modules · Functions
> **Style:** Real-world DevOps examples · Beginner-friendly · GitHub-ready

---

## 📑 Table of Contents

- [Virtual Environments](#-virtual-environments)
  - [Why Virtual Environments](#why-virtual-environments)
  - [Creating and Activating](#creating-and-activating)
  - [Common Commands](#common-commands)
  - [In a DevOps Project](#in-a-devops-project)
- [Packages](#-packages)
  - [Installing Packages](#installing-packages)
  - [requirements.txt](#requirementstxt)
  - [Key DevOps Packages](#key-devops-packages)
- [Modules](#-modules)
  - [What is a Module](#what-is-a-module)
  - [Importing Modules](#importing-modules)
  - [Writing Your Own Module](#writing-your-own-module)
  - [Standard Library Modules for DevOps](#standard-library-modules-for-devops)
- [Functions](#-functions)
  - [Defining Functions](#defining-functions)
  - [Arguments and Parameters](#arguments-and-parameters)
  - [Return Values](#return-values)
  - [Default Arguments](#default-arguments)
  - [*args and **kwargs](#args-and-kwargs)
  - [Lambda Functions](#lambda-functions)
  - [Docstrings](#docstrings)
  - [Real DevOps Function Patterns](#real-devops-function-patterns)

---

## 🌐 Virtual Environments

### Why Virtual Environments

A virtual environment is an **isolated Python workspace**. Each project gets its own Python interpreter and its own set of packages — completely separate from every other project on your machine.

**The problem without virtual environments:**

```
Your Machine (Global Python)
├── Project A needs requests==2.20.0
├── Project B needs requests==2.28.0   ← CONFLICT
└── One install will break the other
```

**The solution with virtual environments:**

```
Your Machine
├── project-a/
│   └── venv/  ← has requests==2.20.0
└── project-b/
    └── venv/  ← has requests==2.28.0  ← No conflict
```

> **DevOps context:** Your server health-checker script uses `boto3==1.26` but your Slack alerting tool needs `boto3==1.34`. Without venvs, one will break the other on the same machine.

---

### Creating and Activating

```bash
# Step 1 — Create a virtual environment
python3 -m venv venv

# The folder structure it creates:
# venv/
# ├── bin/          ← Python interpreter + pip (Linux/macOS)
# ├── Scripts/      ← Python interpreter + pip (Windows)
# ├── lib/          ← All installed packages go here
# └── pyvenv.cfg    ← Config file
```

```bash
# Step 2 — Activate it

# Linux / macOS
source venv/bin/activate

# Windows (CMD)
venv\Scripts\activate.bat

# Windows (PowerShell)
venv\Scripts\Activate.ps1
```

```bash
# How you know it's active — prompt changes:
# Before: user@server:~/medisync$
# After:  (venv) user@server:~/medisync$
```

```bash
# Step 3 — Deactivate when done
deactivate
```

> ⚠️ **Rule:** Always activate your venv before running any Python script in that project. If you forget, packages installed globally may clash or be missing.

---

### Common Commands

```bash
# Check which Python is being used
which python3
# Should point to: /your/project/venv/bin/python3

# Check which pip is being used
which pip
# Should point to: /your/project/venv/bin/pip

# List all installed packages in current venv
pip list

# Show details of a specific package
pip show boto3

# Freeze current packages with exact versions
pip freeze
# Output: boto3==1.34.0
#         requests==2.31.0
#         PyYAML==6.0.1

# Upgrade pip itself (do this after creating venv)
pip install --upgrade pip
```

---

### In a DevOps Project

**Typical project layout with venv:**

```
medisync-devops/
├── venv/                  ← Never commit this to git
├── scripts/
│   ├── health_check.py
│   ├── deploy.py
│   └── cleanup_ecr.py
├── requirements.txt       ← Always commit this
├── .gitignore
└── README.md
```

**`.gitignore` — always add these:**

```gitignore
# Virtual Environment
venv/
env/
.venv/
ENV/

# Python cache
__pycache__/
*.pyc
*.pyo

# Environment variables
.env
*.env
```

**Setup script for a new team member (bootstrap.sh):**

```bash
#!/bin/bash
# bootstrap.sh — run this once after cloning the repo

echo "Setting up Python environment..."

python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

echo "Done! Run 'source venv/bin/activate' to start."
```

---

## 📦 Packages

### Installing Packages

```bash
# Install a single package
pip install requests

# Install a specific version (recommended for DevOps scripts)
pip install boto3==1.34.0

# Install minimum version
pip install "requests>=2.28.0"

# Install multiple packages at once
pip install requests boto3 PyYAML

# Install from requirements.txt
pip install -r requirements.txt

# Uninstall a package
pip uninstall requests

# Upgrade a package
pip install --upgrade boto3

# Install without internet (from local cache) — useful in air-gapped servers
pip install --no-index --find-links=/offline/packages boto3
```

---

### requirements.txt

This file records every package your project needs. Anyone who clones your repo runs `pip install -r requirements.txt` and gets the exact same environment.

**Generate it from your current venv:**

```bash
pip freeze > requirements.txt
```

**What it looks like:**

```txt
# requirements.txt
boto3==1.34.0
requests==2.31.0
PyYAML==6.0.1
python-dotenv==1.0.0
```

**Best practice — split into two files:**

```txt
# requirements.txt (production only)
boto3==1.34.0
requests==2.31.0
PyYAML==6.0.1
python-dotenv==1.0.0
```

```txt
# requirements-dev.txt (development + testing)
-r requirements.txt          ← includes everything from requirements.txt
pytest==7.4.0
pytest-cov==4.1.0
black==23.9.1
flake8==6.1.0
```

**In GitHub Actions CI pipeline:**

```yaml
# .github/workflows/ci.yml
- name: Install dependencies
  run: |
    python -m pip install --upgrade pip
    pip install -r requirements.txt
    pip install -r requirements-dev.txt

- name: Run tests
  run: pytest tests/ --cov=scripts/
```

---

### Key DevOps Packages

| Package | Install | What it does |
|---|---|---|
| `boto3` | `pip install boto3` | AWS SDK — control EC2, S3, CloudWatch from Python |
| `requests` | `pip install requests` | Make HTTP calls to REST APIs |
| `PyYAML` | `pip install PyYAML` | Read/write YAML files (K8s manifests, configs) |
| `python-dotenv` | `pip install python-dotenv` | Load `.env` file into environment variables |
| `paramiko` | `pip install paramiko` | SSH into servers from Python |
| `slack-sdk` | `pip install slack-sdk` | Send Slack alerts from scripts |
| `psutil` | `pip install psutil` | Read CPU, memory, disk usage |
| `schedule` | `pip install schedule` | Run functions on a timer (lightweight cron) |

---

## 🧩 Modules

### What is a Module

A **module** is simply a `.py` file containing Python code — functions, variables, or classes — that you can reuse in other scripts.

```
scripts/
├── deploy.py        ← your main script
├── aws_utils.py     ← a module you wrote
└── slack_utils.py   ← another module you wrote
```

> **DevOps context:** Instead of copy-pasting your `send_slack_alert()` function into every script, you write it once in `slack_utils.py` and import it anywhere.

---

### Importing Modules

```python
# ── Standard Library (built-in, no install needed) ──────────────────────────

import os                        # import entire module
import sys
import json
import subprocess

# Use with module name prefix
os.getcwd()
sys.exit(1)

# ── Import specific things from a module ────────────────────────────────────

from pathlib import Path         # import just one thing
from datetime import datetime
from subprocess import run, PIPE

# Use directly without prefix
Path("/var/log").exists()
datetime.now().strftime("%Y-%m-%d")

# ── Import with an alias (shorter name) ─────────────────────────────────────

import boto3                     # third-party package
import yaml                      # PyYAML package
import subprocess as sp          # alias

# ── Import your own module ──────────────────────────────────────────────────

import aws_utils                 # your file: aws_utils.py
from slack_utils import send_alert   # specific function from your file
```

---

### Writing Your Own Module

**`slack_utils.py`** — a reusable Slack module:

```python
# slack_utils.py
import requests
import os

SLACK_WEBHOOK = os.environ.get("SLACK_WEBHOOK_URL")

def send_alert(message: str, level: str = "info") -> bool:
    """
    Send a message to Slack via webhook.
    level: "info", "warning", "error"
    """
    icons = {"info": "ℹ️", "warning": "⚠️", "error": "🔴"}
    icon  = icons.get(level, "ℹ️")

    payload = {"text": f"{icon} {message}"}

    response = requests.post(SLACK_WEBHOOK, json=payload)
    return response.status_code == 200


def send_deploy_success(app: str, version: str, env: str) -> bool:
    """Send a formatted deploy success message."""
    msg = f"*Deploy Successful*\nApp: {app}\nVersion: {version}\nEnv: {env}"
    return send_alert(msg, level="info")
```

**`deploy.py`** — using the module:

```python
# deploy.py
from slack_utils import send_alert, send_deploy_success

# Use the functions from your module
send_alert("Starting deployment...", level="info")

# ... deployment logic ...

send_deploy_success(
    app="medisync",
    version="v2.1.0",
    env="production"
)
```

---

### Standard Library Modules for DevOps

These come with Python — no `pip install` needed.

#### `os` — Operating System Operations

```python
import os

# Read environment variables
db_host = os.environ.get("DB_HOST", "localhost")   # with default fallback
api_key = os.environ["API_KEY"]                    # raises error if missing

# File and directory operations
os.makedirs("/backup/2024-01-15", exist_ok=True)   # create folder safely
os.listdir("/var/log/nginx")                        # list files in a dir
os.remove("/tmp/old_backup.tar.gz")                # delete a file
os.rename("app.log.1", "app.log.bak")             # rename a file

# Check existence
os.path.exists("/etc/nginx/nginx.conf")            # True / False
os.path.isfile("/var/log/app.log")                 # is it a file?
os.path.isdir("/var/log")                          # is it a directory?

# Get file size
size = os.path.getsize("/var/log/app.log")
print(f"Log size: {size / 1024:.1f} KB")

# Join path parts safely (handles slashes automatically)
log_path = os.path.join("/var", "log", "nginx", "error.log")
# "/var/log/nginx/error.log"
```

#### `sys` — System and Script Control

```python
import sys

# Exit with a status code — critical for CI/CD pipelines
# Exit 0 = success, Exit 1 = failure
if not health_check_passed:
    print("Health check failed — aborting deployment")
    sys.exit(1)

# Read command line arguments
# Run as: python deploy.py production v2.1.0
env     = sys.argv[1]   # "production"
version = sys.argv[2]   # "v2.1.0"

# Print to stderr (errors) vs stdout (normal output)
# CI/CD systems use these differently
print("Deployment started", file=sys.stdout)
print("ERROR: config missing", file=sys.stderr)

# Check Python version in your script
if sys.version_info < (3, 8):
    print("Python 3.8+ required")
    sys.exit(1)
```

#### `subprocess` — Run Shell Commands

```python
import subprocess

# Run a command and get output
result = subprocess.run(
    ["docker", "ps", "--format", "{{.Names}}"],
    capture_output=True,   # capture stdout and stderr
    text=True,             # return strings, not bytes
    check=True             # raise exception if command fails
)

running_containers = result.stdout.strip().split("\n")
print(f"Running containers: {running_containers}")

# Run a command and check if it succeeds
result = subprocess.run(
    ["kubectl", "get", "pods", "-n", "production"],
    capture_output=True,
    text=True
)

if result.returncode != 0:
    print(f"kubectl failed: {result.stderr}")
else:
    print(result.stdout)

# Run a shell pipeline (use shell=True carefully)
result = subprocess.run(
    "docker images | grep medisync | awk '{print $2}'",
    shell=True,
    capture_output=True,
    text=True
)
print("MediSync versions:", result.stdout.strip())
```

#### `json` — Read and Write JSON

```python
import json

# Parse JSON string (from API response)
response_text = '{"status": "healthy", "uptime": 99.9}'
data = json.loads(response_text)
print(data["status"])    # "healthy"

# Read a JSON config file
with open("config.json") as f:
    config = json.load(f)

db_host = config["database"]["host"]

# Write JSON to a file (save state, reports)
report = {
    "timestamp": "2024-01-15T10:30:00",
    "servers_checked": 10,
    "healthy": 9,
    "unhealthy": 1
}

with open("health_report.json", "w") as f:
    json.dump(report, f, indent=2)   # indent=2 for readable output

# Pretty print JSON to terminal for debugging
print(json.dumps(config, indent=2))
```

#### `yaml` — Read YAML Files (PyYAML)

```python
import yaml   # pip install PyYAML

# Read a Kubernetes manifest
with open("deployment.yaml") as f:
    manifest = yaml.safe_load(f)

replicas = manifest["spec"]["replicas"]      # 3
image    = manifest["spec"]["template"]["spec"]["containers"][0]["image"]

# Read docker-compose.yml
with open("docker-compose.yml") as f:
    compose = yaml.safe_load(f)

services = list(compose["services"].keys())  # ["api", "db", "redis"]

# Write YAML
config = {
    "app": "medisync",
    "version": "2.1.0",
    "replicas": 3,
    "env": "production"
}

with open("app_config.yaml", "w") as f:
    yaml.dump(config, f, default_flow_style=False)
```

#### `logging` — Proper Log Output

```python
import logging

# Basic setup — do this once at the top of your script
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        logging.FileHandler("deploy.log"),   # write to file
        logging.StreamHandler()              # also print to terminal
    ]
)

logger = logging.getLogger(__name__)

# Use these levels in the right context
logger.debug("Connecting to DB_HOST=%s", db_host)      # verbose details
logger.info("Deployment started for version %s", ver)   # normal progress
logger.warning("Disk usage at %d%% — approaching limit", 85)
logger.error("Health check failed for server %s", host) # something broke
logger.critical("Database unreachable — rolling back")  # everything is down

# Output looks like:
# 2024-01-15 10:30:00 [INFO] Deployment started for version v2.1.0
# 2024-01-15 10:30:05 [ERROR] Health check failed for server web-03
```

#### `pathlib` — Modern File Paths

```python
from pathlib import Path

# Create path objects — cleaner than os.path
log_dir = Path("/var/log/medisync")
log_file = log_dir / "app.log"         # "/" joins paths — clean syntax!

# Check and create
if not log_dir.exists():
    log_dir.mkdir(parents=True)        # mkdir -p equivalent

# Find all log files recursively
for log in Path("/var/log").glob("**/*.log"):
    print(log)

# Find old logs — delete if over 50MB
for log in Path("/var/log/nginx").glob("*.log"):
    if log.stat().st_size > 50 * 1024 * 1024:
        log.unlink()
        print(f"Deleted large log: {log.name}")

# Read and write files cleanly
content = Path("config.txt").read_text()
Path("output.txt").write_text("deployment complete")

# Get parts of a path
path = Path("/var/log/nginx/error.log")
path.name      # "error.log"
path.stem      # "error"
path.suffix    # ".log"
path.parent    # Path("/var/log/nginx")
```

#### `datetime` — Timestamps

```python
from datetime import datetime, timedelta

# Get current timestamp — used in log names, S3 prefixes, reports
now = datetime.now()
today = now.strftime("%Y-%m-%d")           # "2024-01-15"
timestamp = now.strftime("%Y%m%d_%H%M%S")  # "20240115_103045"

# Create a backup filename with timestamp
backup_name = f"medisync-backup-{timestamp}.tar.gz"
# "medisync-backup-20240115_103045.tar.gz"

# S3 key prefix organized by date
s3_prefix = f"backups/{today}/"
# "backups/2024-01-15/"

# Calculate time differences — delete files older than 7 days
cutoff = datetime.now() - timedelta(days=7)

# Parse a timestamp from a log line
log_time = datetime.strptime("2024-01-15 10:30:00", "%Y-%m-%d %H:%M:%S")
age = datetime.now() - log_time
print(f"Log is {age.seconds // 3600} hours old")
```

---

## ⚙️ Functions

### Defining Functions

```python
# Basic function syntax
def function_name(parameters):
    """Docstring — explain what this does."""
    # body
    return result
```

```python
# Simple DevOps function
def restart_service(service_name):
    """Restart a systemd service and return success status."""
    import subprocess
    result = subprocess.run(
        ["systemctl", "restart", service_name],
        capture_output=True,
        text=True
    )
    return result.returncode == 0   # True if success


# Call it
success = restart_service("nginx")
if success:
    print("nginx restarted successfully")
else:
    print("nginx restart failed")
```

---

### Arguments and Parameters

```python
# Positional arguments — must be passed in order
def deploy(app, version, environment):
    print(f"Deploying {app} {version} to {environment}")

deploy("medisync", "v2.1.0", "production")   # correct
deploy("production", "medisync", "v2.1.0")   # wrong — order matters


# Keyword arguments — pass by name, order doesn't matter
deploy(environment="staging", app="medisync", version="v2.0.0")
```

---

### Return Values

```python
# Return a single value
def get_instance_count(region):
    """Return number of running EC2 instances in a region."""
    import boto3
    ec2 = boto3.client("ec2", region_name=region)
    response = ec2.describe_instances(
        Filters=[{"Name": "instance-state-name", "Values": ["running"]}]
    )
    return len(response["Reservations"])

count = get_instance_count("us-east-1")
print(f"Running instances: {count}")


# Return multiple values (as a tuple)
def check_server(host, port):
    """Check if a server is reachable. Returns (is_up, response_time)."""
    import socket, time
    start = time.time()
    try:
        socket.create_connection((host, port), timeout=3)
        return True, round(time.time() - start, 3)
    except (socket.timeout, ConnectionRefusedError):
        return False, None

is_up, response_time = check_server("10.0.0.5", 8080)

if is_up:
    print(f"Server up — responded in {response_time}s")
else:
    print("Server is DOWN")


# Return a dictionary — cleaner for multiple related values
def get_disk_info(path="/"):
    """Return disk usage info as a dictionary."""
    import shutil
    total, used, free = shutil.disk_usage(path)
    return {
        "total_gb": total // (2**30),
        "used_gb":  used  // (2**30),
        "free_gb":  free  // (2**30),
        "percent":  round(used / total * 100, 1)
    }

disk = get_disk_info("/")
print(f"Disk: {disk['used_gb']}GB used, {disk['percent']}% full")

if disk["percent"] > 85:
    send_alert(f"Disk at {disk['percent']}% — clean up needed", level="warning")
```

---

### Default Arguments

```python
# Default values — used when caller doesn't provide that argument
def send_alert(message, level="info", channel="#devops-alerts"):
    """Send alert to Slack with sensible defaults."""
    icons = {"info": "ℹ️", "warning": "⚠️", "error": "🔴"}
    icon = icons.get(level, "ℹ️")
    print(f"[{channel}] {icon} {message}")


# All three are valid calls:
send_alert("Deployment complete")                          # uses all defaults
send_alert("Disk at 90%", level="warning")               # custom level
send_alert("DB down", level="error", channel="#oncall")  # all custom


# Default for a list of regions
def check_all_regions(regions=None):
    """Check EC2 health across regions."""
    if regions is None:                  # ← never use [] as default — it's a Python gotcha
        regions = ["us-east-1", "ap-south-1"]

    for region in regions:
        print(f"Checking {region}...")


check_all_regions()                          # uses default regions
check_all_regions(["eu-west-1", "us-west-2"])  # custom regions
```

> ⚠️ **Python Gotcha:** Never use a mutable type (list, dict) as a default argument. Use `None` and set the default inside the function body.

---

### *args and **kwargs

```python
# *args — accept any number of positional arguments
def tag_resources(*resource_ids):
    """Tag multiple AWS resources at once."""
    for rid in resource_ids:
        print(f"Tagging: {rid}")

tag_resources("i-0abc123")                          # one resource
tag_resources("i-0abc123", "i-0def456", "i-0ghi789")  # three resources


# **kwargs — accept any number of keyword arguments
def create_tags(**tags):
    """Build an AWS tags list from keyword arguments."""
    return [{"Key": k, "Value": v} for k, v in tags.items()]

aws_tags = create_tags(
    Environment="production",
    Project="medisync",
    Owner="devops-team",
    ManagedBy="terraform"
)
# [{"Key": "Environment", "Value": "production"}, ...]


# Combining both — most flexible function signature
def deploy_service(app_name, *versions, **config):
    """
    Deploy a service with flexible options.

    app_name  — required positional
    *versions — any number of versions to deploy
    **config  — any keyword config options
    """
    print(f"App: {app_name}")
    print(f"Versions: {versions}")
    print(f"Config: {config}")


deploy_service(
    "medisync",
    "v2.0.0", "v2.1.0",          # *versions
    env="production",              # **config
    replicas=3,
    region="ap-south-1"
)

# Output:
# App: medisync
# Versions: ('v2.0.0', 'v2.1.0')
# Config: {'env': 'production', 'replicas': 3, 'region': 'ap-south-1'}
```

---

### Lambda Functions

Lambda is a **one-line anonymous function**. Use it for short, simple logic — not complex operations.

```python
# Syntax: lambda arguments: expression

# Sort servers by their number suffix
servers = ["web-03", "web-01", "web-04", "web-02"]
sorted_servers = sorted(servers, key=lambda s: int(s.split("-")[1]))
# ["web-01", "web-02", "web-03", "web-04"]


# Filter only ERROR lines from a log list
log_lines = [
    "INFO: service started",
    "ERROR: connection refused",
    "INFO: health check ok",
    "ERROR: timeout exceeded"
]

errors = list(filter(lambda line: "ERROR" in line, log_lines))
# ["ERROR: connection refused", "ERROR: timeout exceeded"]


# Extract just the IP from each log entry
logs = ["2024-01-15 10.0.0.1 GET /health", "2024-01-15 10.0.0.2 POST /api"]
ips = list(map(lambda line: line.split()[1], logs))
# ["10.0.0.1", "10.0.0.2"]


# Sort EC2 instances by launch time (newest first)
instances.sort(key=lambda i: i["LaunchTime"], reverse=True)
```

> 💡 **When to use lambda:** Sorting, filtering, or mapping short logic inline. If the logic is more than one expression — write a proper named function instead.

---

### Docstrings

A docstring explains what a function does. Python reads it as `function.__doc__`.

```python
def backup_s3(bucket, prefix, local_dir, dry_run=False):
    """
    Upload all files from a local directory to an S3 bucket.

    Args:
        bucket   (str):  Name of the S3 bucket.
        prefix   (str):  S3 key prefix (e.g., 'backups/2024-01-15/').
        local_dir(str):  Local directory path to upload.
        dry_run  (bool): If True, print actions without uploading.

    Returns:
        int: Number of files uploaded (0 if dry_run=True).

    Raises:
        FileNotFoundError: If local_dir does not exist.
        boto3.exceptions.S3UploadFailedError: If S3 upload fails.

    Example:
        >>> count = backup_s3("medisync-backups", "daily/", "/var/data")
        >>> print(f"Uploaded {count} files")
    """
    from pathlib import Path
    import boto3

    path = Path(local_dir)
    if not path.exists():
        raise FileNotFoundError(f"Directory not found: {local_dir}")

    s3 = boto3.client("s3")
    uploaded = 0

    for file in path.rglob("*"):
        if file.is_file():
            key = f"{prefix}{file.name}"
            if dry_run:
                print(f"[DRY RUN] Would upload {file} → s3://{bucket}/{key}")
            else:
                s3.upload_file(str(file), bucket, key)
                uploaded += 1

    return uploaded


# Read the docstring
help(backup_s3)      # full formatted output
print(backup_s3.__doc__)  # raw docstring text
```

---

### Real DevOps Function Patterns

#### Pattern 1 — Health Check Function

```python
import requests
import logging

logger = logging.getLogger(__name__)

def check_endpoint(url, expected_status=200, timeout=5):
    """
    Check if an HTTP endpoint is healthy.

    Returns True if reachable and returns expected status code.
    """
    try:
        response = requests.get(url, timeout=timeout)
        if response.status_code == expected_status:
            logger.info("HEALTHY: %s (%dms)", url, response.elapsed.microseconds // 1000)
            return True
        else:
            logger.warning("UNHEALTHY: %s returned %d", url, response.status_code)
            return False

    except requests.exceptions.ConnectionError:
        logger.error("UNREACHABLE: %s", url)
        return False

    except requests.exceptions.Timeout:
        logger.error("TIMEOUT: %s did not respond in %ds", url, timeout)
        return False


# Usage
services = {
    "API":      "http://10.0.0.5:8080/health",
    "Frontend": "http://10.0.0.5:3000/",
    "Metrics":  "http://10.0.0.5:9090/-/healthy"
}

for name, url in services.items():
    if not check_endpoint(url):
        send_alert(f"{name} is DOWN at {url}", level="error")
```

---

#### Pattern 2 — Retry Wrapper Function

```python
import time
import logging

logger = logging.getLogger(__name__)

def retry(func, retries=3, delay=5, backoff=2):
    """
    Retry a function on failure with exponential backoff.

    Args:
        func    : The function to call (no arguments).
        retries : Max number of attempts.
        delay   : Initial wait in seconds between attempts.
        backoff : Multiply delay by this after each failure.

    Returns:
        The return value of func on success.

    Raises:
        Exception: Re-raises the last exception after all retries fail.
    """
    current_delay = delay

    for attempt in range(1, retries + 1):
        try:
            return func()

        except Exception as e:
            if attempt == retries:
                logger.error("All %d attempts failed: %s", retries, e)
                raise

            logger.warning("Attempt %d/%d failed: %s — retrying in %ds",
                           attempt, retries, e, current_delay)
            time.sleep(current_delay)
            current_delay *= backoff


# Usage — wrap any failing operation
import boto3

def get_ec2_instances():
    ec2 = boto3.client("ec2", region_name="us-east-1")
    return ec2.describe_instances()

result = retry(get_ec2_instances, retries=3, delay=5)
```

---

#### Pattern 3 — Config Loader Function

```python
import os
import yaml
import json
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

def load_config(config_path, required_keys=None):
    """
    Load configuration from a YAML or JSON file.
    Override values with environment variables if they exist.

    Args:
        config_path   (str) : Path to config file (.yaml or .json).
        required_keys (list): Keys that must be present. Raises if missing.

    Returns:
        dict: Merged configuration (file + env overrides).
    """
    path = Path(config_path)

    if not path.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")

    # Parse based on file extension
    if path.suffix in (".yaml", ".yml"):
        with open(path) as f:
            config = yaml.safe_load(f)
    elif path.suffix == ".json":
        with open(path) as f:
            config = json.load(f)
    else:
        raise ValueError(f"Unsupported config format: {path.suffix}")

    # Override with environment variables (env always wins)
    for key in config:
        env_val = os.environ.get(key.upper())
        if env_val:
            logger.info("Config key '%s' overridden by environment variable", key)
            config[key] = env_val

    # Validate required keys are present
    if required_keys:
        missing = [k for k in required_keys if k not in config]
        if missing:
            raise KeyError(f"Missing required config keys: {missing}")

    return config


# Usage
config = load_config(
    "config.yaml",
    required_keys=["db_host", "db_port", "api_key"]
)

db_host = config["db_host"]
```

---

#### Pattern 4 — Decorator Function (Advanced but Useful)

```python
import time
import logging
import functools

logger = logging.getLogger(__name__)

def log_execution(func):
    """
    Decorator: log when a function starts, finishes, and how long it took.
    Apply with @log_execution above any function definition.
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        logger.info("Starting: %s", func.__name__)
        start = time.time()

        result = func(*args, **kwargs)

        duration = round(time.time() - start, 2)
        logger.info("Finished: %s in %ss", func.__name__, duration)
        return result

    return wrapper


# Apply to any function with @
@log_execution
def run_backup():
    """Run the nightly backup job."""
    time.sleep(2)   # simulate work
    return "backup complete"


@log_execution
def sync_s3():
    """Sync local files to S3."""
    time.sleep(1)
    return "sync complete"


# When called, they automatically log start/finish/duration:
run_backup()
# INFO: Starting: run_backup
# INFO: Finished: run_backup in 2.0s
```

---

## 📌 Quick Reference — Function Syntax Cheatsheet

```python
# Basic function
def greet(name):
    return f"Hello, {name}"

# Default arguments
def deploy(app, env="staging"):
    pass

# Multiple return values
def ping(host):
    return True, 23.4        # is_up, latency_ms

# Accept any positional args
def tag(*resource_ids):
    for rid in resource_ids:
        print(rid)

# Accept any keyword args
def configure(**settings):
    for key, val in settings.items():
        print(f"{key} = {val}")

# Lambda (one-liner)
get_level = lambda log: log.split()[1]

# Decorator
def my_decorator(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # before
        result = func(*args, **kwargs)
        # after
        return result
    return wrapper
```

---

## 🔑 Key Takeaways

| Concept | When to Use |
|---|---|
| **Virtual Environment** | Always — one per project, never use global Python |
| **`requirements.txt`** | Always commit this, never commit `venv/` folder |
| **Standard modules** | `os`, `sys`, `subprocess`, `json`, `logging`, `pathlib`, `datetime` — no install needed |
| **Third-party packages** | `boto3`, `requests`, `PyYAML`, `python-dotenv` — install via pip |
| **Your own modules** | Write reusable functions in separate `.py` files, import them |
| **Default arguments** | Use `None` not `[]` or `{}` as default for mutable types |
| **`*args`** | When number of positional inputs is unknown |
| **`**kwargs`** | When number of keyword inputs is unknown |
| **Lambda** | Inline sorting/filtering only — not for complex logic |
| **Docstrings** | Every function that will be reused by others |

---

*Last updated: 2026 · Python 3.11+ · DevOps track*
