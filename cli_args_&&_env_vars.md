# 🐍 Python for DevOps — CLI Arguments & Environment Variables

> **Scope:** `sys.argv` · `argparse` · `os.environ` · `python-dotenv` · Real patterns
> **Style:** Real-world DevOps examples · Beginner-friendly · GitHub-ready

---

## 📑 Table of Contents

- [Why These Matter in DevOps](#-why-these-matter-in-devops)
- [Command Line Arguments](#-command-line-arguments)
  - [sys.argv — The Raw Way](#sysargv--the-raw-way)
  - [argparse — The Right Way](#argparse--the-right-way)
  - [Positional Arguments](#positional-arguments)
  - [Optional Arguments (Flags)](#optional-arguments-flags)
  - [Argument Types](#argument-types)
  - [Default Values](#default-values)
  - [Choices — Restrict Valid Values](#choices--restrict-valid-values)
  - [Boolean Flags](#boolean-flags)
  - [Mutually Exclusive Arguments](#mutually-exclusive-arguments)
  - [Subcommands](#subcommands)
  - [Argument Groups](#argument-groups)
- [Environment Variables](#-environment-variables)
  - [What Are Environment Variables](#what-are-environment-variables)
  - [Reading with os.environ](#reading-with-osenviron)
  - [Setting and Unsetting](#setting-and-unsetting)
  - [The .env File](#the-env-file)
  - [python-dotenv](#python-dotenv)
  - [Validating Required Variables](#validating-required-variables)
- [CLI vs Environment Variables — When to Use Which](#-cli-vs-environment-variables--when-to-use-which)
- [Real DevOps Script Patterns](#-real-devops-script-patterns)
  - [Pattern 1 — Deployment Script](#pattern-1--deployment-script)
  - [Pattern 2 — Health Check CLI Tool](#pattern-2--health-check-cli-tool)
  - [Pattern 3 — EC2 Manager CLI](#pattern-3--ec2-manager-cli)
  - [Pattern 4 — Config Validator](#pattern-4--config-validator)
- [Quick Reference Cheatsheet](#-quick-reference-cheatsheet)

---

## 💡 Why These Matter in DevOps

DevOps scripts almost never run interactively. They run:

- Inside **GitHub Actions** pipelines — triggered automatically
- Inside **Docker containers** — no human at the keyboard
- On a **cron schedule** — at 2 AM with no one watching
- By **other team members** — who need to pass different values

You need two mechanisms to get values into your scripts without hardcoding them:

```
┌─────────────────────────────────────────────────────────────────┐
│                   Ways to Pass Values to a Script               │
├──────────────────────────────┬──────────────────────────────────┤
│   Command Line Arguments     │     Environment Variables        │
├──────────────────────────────┼──────────────────────────────────┤
│  python deploy.py prod v2.1  │  ENV=prod VERSION=v2.1 python..  │
│  Visible in terminal         │  Hidden — not in shell history   │
│  For runtime options         │  For secrets and config          │
│  Changes per invocation      │  Set once, used everywhere       │
└──────────────────────────────┴──────────────────────────────────┘
```

---

## ⌨️ Command Line Arguments

### sys.argv — The Raw Way

`sys.argv` is a **list** of everything typed after `python` in the terminal.

```python
# script.py
import sys

print(sys.argv)

# Run: python script.py hello world 123
# Output: ['script.py', 'hello', 'world', '123']
#          ↑ index 0      ↑ [1]    ↑ [2]    ↑ [3]
# Index 0 is always the script name itself
```

```python
# deploy.py — basic sys.argv usage
import sys

# Check correct number of arguments were passed
if len(sys.argv) != 3:
    print("Usage: python deploy.py <environment> <version>")
    print("Example: python deploy.py production v2.1.0")
    sys.exit(1)

environment = sys.argv[1]   # "production"
version     = sys.argv[2]   # "v2.1.0"

print(f"Deploying {version} to {environment}...")
```

```bash
# Terminal usage
python deploy.py production v2.1.0
# Deploying v2.1.0 to production...

python deploy.py
# Usage: python deploy.py <environment> <version>
```

> ⚠️ **Limitation of sys.argv:** No automatic help text, no type validation,
> no default values, no named flags. Use it only for the simplest scripts.
> For anything real — use `argparse`.

---

### argparse — The Right Way

`argparse` is Python's built-in CLI framework. It gives you:

- Named flags (`--env production`)
- Automatic `--help` generation
- Type validation
- Default values
- Required vs optional arguments

```python
# Basic argparse structure — always follows this pattern
import argparse

# Step 1 — Create the parser with a description
parser = argparse.ArgumentParser(
    description="Deploy MediSync to a target environment"
)

# Step 2 — Add arguments
parser.add_argument("--env", help="Target environment")

# Step 3 — Parse the arguments
args = parser.parse_args()

# Step 4 — Use the values
print(args.env)
```

```bash
# --help is generated automatically — for free
python deploy.py --help

# Output:
# usage: deploy.py [-h] [--env ENV]
#
# Deploy MediSync to a target environment
#
# options:
#   -h, --help   show this help message and exit
#   --env ENV    Target environment
```

---

### Positional Arguments

Positional arguments are **required** and passed by position, not by name.

```python
import argparse

parser = argparse.ArgumentParser(description="Manage Docker containers")

# Positional — required, no -- prefix
parser.add_argument("action",     help="Action to perform: start, stop, restart")
parser.add_argument("container",  help="Container name or ID")

args = parser.parse_args()

print(f"Action:    {args.action}")
print(f"Container: {args.container}")
```

```bash
# Usage — values passed by position
python manage.py restart nginx
# Action:    restart
# Container: nginx

python manage.py stop medisync-api
# Action:    stop
# Container: medisync-api

# Missing argument — argparse catches it automatically
python manage.py restart
# error: the following arguments are required: container
```

---

### Optional Arguments (Flags)

Optional arguments use `--name` prefix. They are not required by default.

```python
import argparse

parser = argparse.ArgumentParser(description="Deploy application")

# Long form only
parser.add_argument("--env",     help="Target environment")
parser.add_argument("--version", help="App version to deploy")
parser.add_argument("--region",  help="AWS region")

# Long AND short form — -e is shortcut for --env
parser.add_argument("-e", "--env",     help="Target environment")
parser.add_argument("-v", "--version", help="App version to deploy")
parser.add_argument("-r", "--region",  help="AWS region")

args = parser.parse_args()

# Access using the long name (without --)
print(args.env)
print(args.version)
print(args.region)
```

```bash
# Both of these work
python deploy.py --env production --version v2.1.0 --region ap-south-1
python deploy.py -e production -v v2.1.0 -r ap-south-1
```

---

### Argument Types

By default, all arguments are strings. Use `type=` to auto-convert and validate.

```python
import argparse

parser = argparse.ArgumentParser(description="Scale a service")

# type=int — auto-converts "3" to 3, rejects "abc"
parser.add_argument("--replicas", type=int,   help="Number of replicas")

# type=float — auto-converts "85.5" to 85.5
parser.add_argument("--threshold", type=float, help="CPU threshold percentage")

# type=str — default, explicit for clarity
parser.add_argument("--service",  type=str,   help="Service name")

args = parser.parse_args()

# args.replicas is already an int — no need for int() conversion
if args.replicas > 10:
    print("Warning: scaling beyond 10 replicas requires approval")

if args.threshold > 90.0:
    print("Threshold too high — defaulting to 85%")
```

```bash
python scale.py --replicas 5 --threshold 75.5 --service api
# args.replicas  → 5      (int)
# args.threshold → 75.5   (float)
# args.service   → "api"  (str)

# Type validation — argparse rejects wrong types automatically
python scale.py --replicas abc
# error: argument --replicas: invalid int value: 'abc'
```

```python
# type= with a custom validation function
def valid_port(value):
    """Validate port is a number between 1 and 65535."""
    port = int(value)
    if not (1 <= port <= 65535):
        raise argparse.ArgumentTypeError(
            f"Port must be between 1 and 65535, got {port}"
        )
    return port


parser.add_argument("--port", type=valid_port, help="Port number (1-65535)")
```

```bash
python server.py --port 8080    # valid → args.port = 8080
python server.py --port 99999   # error: Port must be between 1 and 65535
python server.py --port abc     # error: invalid int value: 'abc'
```

---

### Default Values

```python
import argparse

parser = argparse.ArgumentParser(description="Deploy with sensible defaults")

# default= sets the value when flag is not provided
parser.add_argument(
    "--env",
    default="staging",
    help="Target environment (default: staging)"
)

parser.add_argument(
    "--replicas",
    type=int,
    default=2,
    help="Number of replicas (default: 2)"
)

parser.add_argument(
    "--region",
    default="ap-south-1",
    help="AWS region (default: ap-south-1)"
)

args = parser.parse_args()

# If not passed, uses default
print(args.env)      # "staging"  if --env not provided
print(args.replicas) # 2          if --replicas not provided
print(args.region)   # "ap-south-1" if --region not provided
```

```bash
# No flags — all defaults apply
python deploy.py
# env=staging, replicas=2, region=ap-south-1

# Override specific ones
python deploy.py --env production --replicas 5
# env=production, replicas=5, region=ap-south-1  ← region still default
```

---

### Choices — Restrict Valid Values

Reject any value not in your approved list — argparse handles the error automatically.

```python
import argparse

parser = argparse.ArgumentParser(description="Deploy to a controlled environment")

parser.add_argument(
    "--env",
    choices=["dev", "staging", "production"],
    required=True,
    help="Target environment — must be dev, staging, or production"
)

parser.add_argument(
    "--log-level",
    choices=["DEBUG", "INFO", "WARNING", "ERROR"],
    default="INFO",
    help="Logging level (default: INFO)"
)

parser.add_argument(
    "--strategy",
    choices=["rolling", "blue-green", "canary"],
    default="rolling",
    help="Deployment strategy (default: rolling)"
)

args = parser.parse_args()
print(f"Deploying to {args.env} using {args.strategy} strategy")
```

```bash
python deploy.py --env production --strategy blue-green
# Deploying to production using blue-green strategy

# Invalid value — argparse rejects it cleanly
python deploy.py --env uat
# error: argument --env: invalid choice: 'uat'
# (choose from 'dev', 'staging', 'production')
```

---

### Boolean Flags

Boolean flags are switches — either present (`True`) or absent (`False`). No value needed.

```python
import argparse

parser = argparse.ArgumentParser(description="Run deployment tasks")

# store_true — flag presence = True, absence = False
parser.add_argument(
    "--dry-run",
    action="store_true",
    help="Print actions without executing them"
)

parser.add_argument(
    "--verbose",
    action="store_true",
    help="Enable detailed output"
)

parser.add_argument(
    "--force",
    action="store_true",
    help="Skip confirmation prompts"
)

# store_false — opposite: flag presence = False
parser.add_argument(
    "--no-backup",
    action="store_false",
    dest="backup",          # stores result in args.backup
    help="Skip backup before deployment"
)

args = parser.parse_args()

if args.dry_run:
    print("[DRY RUN] No changes will be made")

if args.verbose:
    print(f"Verbose mode on — logging level set to DEBUG")

if not args.backup:
    print("Warning: skipping pre-deployment backup")

# Use in conditions throughout your script
def delete_old_images(dry_run=False):
    images = get_old_docker_images()
    for image in images:
        if dry_run:
            print(f"[DRY RUN] Would delete: {image}")
        else:
            delete_image(image)
            print(f"Deleted: {image}")

delete_old_images(dry_run=args.dry_run)
```

```bash
python deploy.py --dry-run --verbose
# [DRY RUN] No changes will be made
# Verbose mode on

python deploy.py --force --no-backup
# Warning: skipping pre-deployment backup

# Note: dashes in flag names become underscores in args
# --dry-run  → args.dry_run
# --no-backup → args.backup
```

> 💡 **Note:** Dashes in flag names (`--dry-run`) become underscores
> in `args` (`args.dry_run`). This is automatic.

---

### Mutually Exclusive Arguments

Force the user to pick exactly one option from a group — not both, not neither.

```python
import argparse

parser = argparse.ArgumentParser(description="EC2 power management")
parser.add_argument("--instance-id", required=True, help="EC2 instance ID")

# Only one of start/stop/restart can be used at a time
group = parser.add_mutually_exclusive_group(required=True)
group.add_argument("--start",   action="store_true", help="Start the instance")
group.add_argument("--stop",    action="store_true", help="Stop the instance")
group.add_argument("--restart", action="store_true", help="Restart the instance")

args = parser.parse_args()

if args.start:
    print(f"Starting instance {args.instance_id}")
elif args.stop:
    print(f"Stopping instance {args.instance_id}")
elif args.restart:
    print(f"Restarting instance {args.instance_id}")
```

```bash
# Valid — one action
python ec2.py --instance-id i-0abc123 --start
# Starting instance i-0abc123

# Invalid — two actions at once
python ec2.py --instance-id i-0abc123 --start --stop
# error: argument --stop: not allowed with argument --start

# Invalid — no action (required=True)
python ec2.py --instance-id i-0abc123
# error: one of the arguments --start --stop --restart is required
```

---

### Subcommands

Subcommands let you build a multi-purpose CLI tool — like `docker` (which has
`docker run`, `docker build`, `docker ps`) or `kubectl`.

```python
import argparse

parser = argparse.ArgumentParser(
    description="MediSync DevOps CLI — manage deployments, infra, and monitoring"
)

# Create subparsers — each subcommand gets its own parser
subparsers = parser.add_subparsers(
    dest="command",        # args.command will hold the subcommand name
    help="Available commands"
)

# ── Subcommand: deploy ───────────────────────────────────────────────────────
deploy_parser = subparsers.add_parser("deploy", help="Deploy the application")
deploy_parser.add_argument("--env",     required=True, choices=["dev","staging","prod"])
deploy_parser.add_argument("--version", required=True, help="Version tag to deploy")
deploy_parser.add_argument("--dry-run", action="store_true")

# ── Subcommand: scale ────────────────────────────────────────────────────────
scale_parser = subparsers.add_parser("scale", help="Scale a service")
scale_parser.add_argument("service",    help="Service name")
scale_parser.add_argument("--replicas", type=int, required=True)

# ── Subcommand: logs ─────────────────────────────────────────────────────────
logs_parser = subparsers.add_parser("logs", help="Fetch application logs")
logs_parser.add_argument("service",   help="Service name")
logs_parser.add_argument("--lines",   type=int, default=100, help="Number of lines")
logs_parser.add_argument("--follow",  action="store_true",   help="Follow log output")

# ── Subcommand: healthcheck ──────────────────────────────────────────────────
health_parser = subparsers.add_parser("healthcheck", help="Check service health")
health_parser.add_argument("--url",     required=True, help="Endpoint URL to check")
health_parser.add_argument("--timeout", type=int, default=5)

# ── Route to the right function ─────────────────────────────────────────────
args = parser.parse_args()

if args.command == "deploy":
    print(f"Deploying {args.version} to {args.env} (dry_run={args.dry_run})")

elif args.command == "scale":
    print(f"Scaling {args.service} to {args.replicas} replicas")

elif args.command == "logs":
    print(f"Fetching last {args.lines} lines from {args.service}")

elif args.command == "healthcheck":
    print(f"Checking {args.url} with timeout={args.timeout}s")

else:
    parser.print_help()
```

```bash
# Each subcommand has its own --help
python medisync.py --help
# usage: medisync.py [-h] {deploy,scale,logs,healthcheck} ...
# MediSync DevOps CLI
#
# positional arguments:
#   {deploy,scale,logs,healthcheck}
#                         Available commands

python medisync.py deploy --help
# usage: medisync.py deploy [-h] --env {dev,staging,prod} --version VERSION [--dry-run]

# Real usage
python medisync.py deploy --env staging --version v2.1.0
python medisync.py scale api --replicas 5
python medisync.py logs api --lines 200 --follow
python medisync.py healthcheck --url http://10.0.0.5:8080/health
```

---

### Argument Groups

Group related arguments together for a cleaner `--help` output.

```python
import argparse

parser = argparse.ArgumentParser(description="Deploy with grouped options")

# Group 1 — required deployment settings
required = parser.add_argument_group("Required — Deployment")
required.add_argument("--env",     required=True, help="Target environment")
required.add_argument("--version", required=True, help="Version to deploy")

# Group 2 — AWS settings
aws = parser.add_argument_group("AWS Configuration")
aws.add_argument("--region",  default="ap-south-1", help="AWS region")
aws.add_argument("--profile", default="default",    help="AWS CLI profile")

# Group 3 — optional behavior
options = parser.add_argument_group("Options")
options.add_argument("--dry-run", action="store_true", help="Simulate only")
options.add_argument("--verbose", action="store_true", help="Verbose output")
options.add_argument("--timeout", type=int, default=300, help="Timeout in seconds")

args = parser.parse_args()
```

```bash
python deploy.py --help

# Output is neatly grouped:
# Required — Deployment:
#   --env ENV          Target environment
#   --version VERSION  Version to deploy
#
# AWS Configuration:
#   --region REGION    AWS region
#   --profile PROFILE  AWS CLI profile
#
# Options:
#   --dry-run          Simulate only
#   --verbose          Verbose output
#   --timeout TIMEOUT  Timeout in seconds
```

---

## 🔐 Environment Variables

### What Are Environment Variables

Environment variables are **key-value pairs** stored in the shell's environment.
Every process started from that shell **inherits** them automatically.

```bash
# Set in terminal
export DB_HOST="prod-db.internal"
export DB_PORT="5432"
export API_KEY="sk-abc123xyz"

# Your Python script reads them — no value in the source code
python app.py
```

```
Your Shell Environment
├── DB_HOST  = "prod-db.internal"
├── DB_PORT  = "5432"
├── API_KEY  = "sk-abc123xyz"
├── PATH     = "/usr/bin:/usr/local/bin:..."
└── HOME     = "/home/ubuntu"
          ↓ inherited by ↓
     python app.py        docker run ...       subprocess.run(...)
```

> **Why not just hardcode values?**
>
> - Secrets in source code get committed to git — catastrophic
> - Different environments (dev/staging/prod) need different values
> - Docker containers and CI/CD systems inject config via env vars by default

---

### Reading with os.environ

```python
import os

# ── Method 1: os.environ["KEY"] ─────────────────────────────────────────────
# Raises KeyError if variable is not set — use when the value is mandatory
db_host = os.environ["DB_HOST"]
api_key = os.environ["API_KEY"]

# ── Method 2: os.environ.get("KEY") ─────────────────────────────────────────
# Returns None if not set — use when variable is optional
debug_mode = os.environ.get("DEBUG")    # None if not set

# ── Method 3: os.environ.get("KEY", "default") ──────────────────────────────
# Returns the default if not set — most common pattern
db_host   = os.environ.get("DB_HOST",  "localhost")
db_port   = os.environ.get("DB_PORT",  "5432")
log_level = os.environ.get("LOG_LEVEL","INFO")
region    = os.environ.get("AWS_REGION","ap-south-1")

# ── Type conversion — env vars are always strings ────────────────────────────
db_port    = int(os.environ.get("DB_PORT", "5432"))
max_retry  = int(os.environ.get("MAX_RETRIES", "3"))
debug      = os.environ.get("DEBUG", "false").lower() == "true"
timeout    = float(os.environ.get("TIMEOUT_SECONDS", "30.0"))

# ── Check if a variable exists ───────────────────────────────────────────────
if "API_KEY" in os.environ:
    print("API key is configured")
else:
    print("Warning: API_KEY not set")

# ── List all environment variables (useful for debugging) ────────────────────
for key, value in os.environ.items():
    print(f"{key} = {value}")

# ── Get all env vars as a regular dictionary ─────────────────────────────────
env_dict = dict(os.environ)
```

---

### Setting and Unsetting

```python
import os

# Set an environment variable from within Python
# Only affects the current process and its children — not the parent shell
os.environ["MY_VAR"] = "hello"

# Unset / remove a variable
del os.environ["MY_VAR"]

# Safe unset — doesn't raise error if variable doesn't exist
os.environ.pop("MY_VAR", None)

# Pass custom env vars to a subprocess
import subprocess

result = subprocess.run(
    ["python", "child_script.py"],
    env={
        **os.environ,              # inherit current environment
        "CUSTOM_VAR": "my_value",  # add or override specific vars
        "LOG_LEVEL": "DEBUG"
    },
    capture_output=True,
    text=True
)
```

```bash
# Setting env vars before running a script in the terminal
DB_HOST=localhost DB_PORT=5432 python app.py

# Setting for the whole session
export DB_HOST="prod-db.internal"
python app.py    # DB_HOST is now available inside the script

# Check what's set
echo $DB_HOST
printenv DB_HOST
env | grep DB_
```

---

### The .env File

A `.env` file stores your environment variables locally so you don't have to
`export` them every time. It lives in your project root.

```bash
# .env — local development config
# Never commit this file to git

APP_ENV=development
DB_HOST=localhost
DB_PORT=5432
DB_NAME=medisync_dev
DB_USER=admin
DB_PASSWORD=localpassword123

AWS_REGION=ap-south-1
AWS_PROFILE=default

SLACK_WEBHOOK_URL=https://hooks.slack.com/services/T00000/B00000/XXXX
LOG_LEVEL=DEBUG
MAX_RETRIES=3
TIMEOUT_SECONDS=30
```

```gitignore
# .gitignore — always add this
.env
*.env
.env.local
.env.production

# Provide a template instead
# .env.example — commit this one (with fake values)
```

```bash
# .env.example — safe to commit, shows team what vars are needed
APP_ENV=development
DB_HOST=localhost
DB_PORT=5432
DB_NAME=your_db_name
DB_USER=your_db_user
DB_PASSWORD=your_db_password_here    # ← placeholder, not real value

AWS_REGION=ap-south-1
SLACK_WEBHOOK_URL=https://hooks.slack.com/your-webhook-here
LOG_LEVEL=INFO
```

---

### python-dotenv

`python-dotenv` loads your `.env` file into `os.environ` automatically.

```bash
pip install python-dotenv
```

```python
# Basic usage — call this at the top of your script
from dotenv import load_dotenv
import os

load_dotenv()   # reads .env file in current directory

# Now all .env variables are in os.environ
db_host = os.environ.get("DB_HOST")
api_key = os.environ.get("API_KEY")
```

```python
# Load a specific .env file (not default .env)
load_dotenv("/etc/medisync/production.env")
load_dotenv(".env.staging")
```

```python
# override=True — env file values override existing shell variables
# override=False (default) — shell variables take priority over .env
load_dotenv(override=True)   # .env wins
load_dotenv(override=False)  # shell export wins (safer for prod)
```

```python
# verbose=True — print which file was loaded (useful for debugging)
load_dotenv(verbose=True)
# Loading .env
```

```python
# Complete pattern used in almost every DevOps script
from dotenv import load_dotenv
import os
import logging

# Load .env before anything else
load_dotenv()

# Now read your config
DB_HOST  = os.environ.get("DB_HOST",  "localhost")
DB_PORT  = int(os.environ.get("DB_PORT", "5432"))
LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO")

logging.basicConfig(level=getattr(logging, LOG_LEVEL))
logger = logging.getLogger(__name__)

logger.info("Connecting to %s:%d", DB_HOST, DB_PORT)
```

```python
# dotenv_values() — load .env as a dict without touching os.environ
# Useful when you want the values but not to pollute the environment
from dotenv import dotenv_values

config = dotenv_values(".env")
print(config["DB_HOST"])    # reads from .env but doesn't set os.environ
```

---

### Validating Required Variables

Always validate that required environment variables exist before your script
does any real work. Fail fast with a clear message.

```python
import os
import sys

def require_env(*variable_names):
    """
    Check that all required environment variables are set.
    Exits with a clear error message if any are missing.

    Usage:
        require_env("DB_HOST", "DB_PORT", "API_KEY")
    """
    missing = [var for var in variable_names if not os.environ.get(var)]

    if missing:
        print("ERROR: The following required environment variables are not set:")
        for var in missing:
            print(f"  - {var}")
        print("\nSet them in your .env file or export them before running.")
        sys.exit(1)


# Call at the very top of your script — before any logic
require_env(
    "DB_HOST",
    "DB_PORT",
    "DB_PASSWORD",
    "AWS_REGION",
    "SLACK_WEBHOOK_URL"
)

# If any are missing, output is clean:
# ERROR: The following required environment variables are not set:
#   - DB_PASSWORD
#   - SLACK_WEBHOOK_URL
#
# Set them in your .env file or export them before running.
```

```python
# More detailed validator — checks type and value constraints
def load_and_validate_env():
    """
    Load all environment config with type conversion and validation.
    Returns a config dict. Raises on any invalid value.
    """
    from dotenv import load_dotenv
    load_dotenv()

    errors = []

    # Helper — read or record error
    def get(key, default=None, required=False, cast=str, allowed=None):
        value = os.environ.get(key, default)

        if required and not value:
            errors.append(f"{key} is required but not set")
            return None

        if value is not None:
            try:
                value = cast(value)
            except (ValueError, TypeError):
                errors.append(f"{key} must be of type {cast.__name__}, got '{value}'")
                return None

        if allowed and value not in allowed:
            errors.append(f"{key} must be one of {allowed}, got '{value}'")
            return None

        return value

    config = {
        "env":         get("APP_ENV", required=True,
                           allowed=["development", "staging", "production"]),
        "db_host":     get("DB_HOST",    default="localhost"),
        "db_port":     get("DB_PORT",    default="5432",  cast=int),
        "db_password": get("DB_PASSWORD",required=True),
        "log_level":   get("LOG_LEVEL",  default="INFO",
                           allowed=["DEBUG","INFO","WARNING","ERROR"]),
        "max_retries": get("MAX_RETRIES",default="3", cast=int),
    }

    if errors:
        print("Configuration errors:")
        for err in errors:
            print(f"  ✗ {err}")
        sys.exit(1)

    return config


config = load_and_validate_env()
print(f"Running in {config['env']} mode")
```

---

## 🔀 CLI vs Environment Variables — When to Use Which

```
┌────────────────────────────┬─────────────────────────────────────────────┐
│  Use CLI Arguments for...  │  Use Environment Variables for...           │
├────────────────────────────┼─────────────────────────────────────────────┤
│  --env production          │  DB_PASSWORD=secret123                      │
│  --version v2.1.0          │  API_KEY=sk-abc123                          │
│  --replicas 5              │  AWS_ACCESS_KEY_ID=AKIA...                  │
│  --dry-run                 │  SLACK_WEBHOOK_URL=https://...              │
│  --region ap-south-1       │  APP_ENV=production                         │
│  --verbose                 │  DB_HOST=prod-db.internal                   │
│                            │  LOG_LEVEL=INFO                             │
├────────────────────────────┼─────────────────────────────────────────────┤
│  Runtime options           │  Secrets and credentials                    │
│  Changes per invocation    │  Infrastructure config                      │
│  Visible in shell history  │  Hidden from shell history                  │
│  Documented in --help      │  Set by CI/CD system or ops team            │
│  User-facing controls      │  Docker / Kubernetes config injection       │
└────────────────────────────┴─────────────────────────────────────────────┘
```

**Real-world example — both used together:**

```python
# deploy.py
import argparse
import os
import sys
from dotenv import load_dotenv

load_dotenv()

# CLI args — what to deploy and how
parser = argparse.ArgumentParser(description="Deploy MediSync")
parser.add_argument("--env",      required=True, choices=["dev","staging","prod"])
parser.add_argument("--version",  required=True)
parser.add_argument("--dry-run",  action="store_true")
parser.add_argument("--replicas", type=int, default=2)
args = parser.parse_args()

# Env vars — secrets and infrastructure config (never on CLI)
db_password      = os.environ.get("DB_PASSWORD")
slack_webhook    = os.environ.get("SLACK_WEBHOOK_URL")
aws_region       = os.environ.get("AWS_REGION", "ap-south-1")

if not db_password:
    print("ERROR: DB_PASSWORD environment variable not set")
    sys.exit(1)

print(f"Deploying {args.version} to {args.env}")
print(f"Replicas: {args.replicas} | Region: {aws_region}")

if args.dry_run:
    print("[DRY RUN] No actual deployment performed")
```

```bash
# Terminal usage — secrets come from .env, options come from CLI
python deploy.py --env production --version v2.1.0 --replicas 3

# In GitHub Actions — secrets injected as env vars by the pipeline
env:
  DB_PASSWORD:   ${{ secrets.DB_PASSWORD }}
  SLACK_WEBHOOK: ${{ secrets.SLACK_WEBHOOK }}
```

---

## 🛠️ Real DevOps Script Patterns

### Pattern 1 — Deployment Script

```python
#!/usr/bin/env python3
"""
deploy.py — Deploy MediSync to a target environment.

Usage:
    python deploy.py --env staging --version v2.1.0
    python deploy.py --env production --version v2.1.0 --dry-run
"""

import argparse
import os
import sys
import subprocess
import logging
from dotenv import load_dotenv

load_dotenv()

# ── Logging setup ────────────────────────────────────────────────────────────
logging.basicConfig(
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
    level=logging.INFO
)
logger = logging.getLogger(__name__)


# ── Argument parsing ─────────────────────────────────────────────────────────
def parse_args():
    parser = argparse.ArgumentParser(
        description="Deploy MediSync application",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python deploy.py --env staging --version v2.1.0
  python deploy.py --env production --version v2.1.0 --dry-run
  python deploy.py --env dev --version latest --replicas 1 --verbose
        """
    )

    parser.add_argument("--env",
        required=True,
        choices=["dev", "staging", "production"],
        help="Target environment"
    )
    parser.add_argument("--version",
        required=True,
        help="Docker image version tag (e.g. v2.1.0, latest)"
    )
    parser.add_argument("--replicas",
        type=int,
        default=2,
        help="Number of replicas (default: 2)"
    )
    parser.add_argument("--dry-run",
        action="store_true",
        help="Print commands without executing"
    )
    parser.add_argument("--verbose",
        action="store_true",
        help="Enable debug logging"
    )

    return parser.parse_args()


# ── Main logic ───────────────────────────────────────────────────────────────
def run_command(cmd, dry_run=False):
    """Run a shell command, or print it if dry_run=True."""
    cmd_str = " ".join(cmd)
    if dry_run:
        logger.info("[DRY RUN] %s", cmd_str)
        return True

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        logger.error("Command failed: %s\n%s", cmd_str, result.stderr)
        return False

    logger.debug(result.stdout)
    return True


def main():
    args = parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    # Read secrets from environment
    registry = os.environ.get("DOCKER_REGISTRY", "docker.io/medisync")

    logger.info("Starting deployment")
    logger.info("Environment : %s", args.env)
    logger.info("Version     : %s", args.version)
    logger.info("Replicas    : %d", args.replicas)

    image = f"{registry}/api:{args.version}"

    # Pull the image
    if not run_command(["docker", "pull", image], args.dry_run):
        sys.exit(1)

    # Deploy
    if not run_command([
        "kubectl", "set", "image",
        f"deployment/medisync-{args.env}",
        f"api={image}",
        "-n", args.env
    ], args.dry_run):
        sys.exit(1)

    # Scale
    if not run_command([
        "kubectl", "scale", "deployment",
        f"medisync-{args.env}",
        f"--replicas={args.replicas}",
        "-n", args.env
    ], args.dry_run):
        sys.exit(1)

    logger.info("Deployment complete ✓")


if __name__ == "__main__":
    main()
```

---

### Pattern 2 — Health Check CLI Tool

```python
#!/usr/bin/env python3
"""
healthcheck.py — Check if one or more HTTP endpoints are healthy.

Usage:
    python healthcheck.py --urls http://10.0.0.5:8080/health
    python healthcheck.py --urls http://api:8080/health http://db:5432
    python healthcheck.py --urls http://api/health --retries 5 --timeout 10
"""

import argparse
import os
import sys
import requests
import time
import logging
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(
    format="%(asctime)s [%(levelname)s] %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)


def parse_args():
    parser = argparse.ArgumentParser(description="HTTP endpoint health checker")

    parser.add_argument(
        "--urls",
        nargs="+",           # accepts one or more values
        required=True,
        metavar="URL",
        help="One or more URLs to check (space-separated)"
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=int(os.environ.get("HEALTH_TIMEOUT", "5")),
        help="Request timeout in seconds (default: 5, or HEALTH_TIMEOUT env var)"
    )
    parser.add_argument(
        "--retries",
        type=int,
        default=3,
        help="Number of retries per URL (default: 3)"
    )
    parser.add_argument(
        "--interval",
        type=int,
        default=5,
        help="Seconds between retries (default: 5)"
    )
    parser.add_argument(
        "--expected-status",
        type=int,
        default=200,
        help="Expected HTTP status code (default: 200)"
    )

    return parser.parse_args()


def check_url(url, timeout, expected_status, retries, interval):
    """Check a URL with retries. Returns True if healthy."""
    for attempt in range(1, retries + 1):
        try:
            resp = requests.get(url, timeout=timeout)
            if resp.status_code == expected_status:
                logger.info("✓ HEALTHY %s (attempt %d/%d)", url, attempt, retries)
                return True
            else:
                logger.warning("✗ Status %d at %s (attempt %d/%d)",
                               resp.status_code, url, attempt, retries)

        except requests.exceptions.ConnectionError:
            logger.warning("✗ Unreachable %s (attempt %d/%d)", url, attempt, retries)

        except requests.exceptions.Timeout:
            logger.warning("✗ Timeout %s (attempt %d/%d)", url, attempt, retries)

        if attempt < retries:
            time.sleep(interval)

    logger.error("✗ UNHEALTHY %s — all %d attempts failed", url, retries)
    return False


def main():
    args = parse_args()
    results = {}

    for url in args.urls:
        results[url] = check_url(
            url, args.timeout, args.expected_status,
            args.retries, args.interval
        )

    # Summary
    print("\n── Health Check Summary ──")
    all_healthy = True
    for url, healthy in results.items():
        status = "✓ UP  " if healthy else "✗ DOWN"
        print(f"  {status}  {url}")
        if not healthy:
            all_healthy = False

    sys.exit(0 if all_healthy else 1)


if __name__ == "__main__":
    main()
```

```bash
# Usage examples
python healthcheck.py --urls http://10.0.0.5:8080/health

python healthcheck.py \
  --urls http://api:8080/health http://frontend:3000 \
  --retries 5 \
  --interval 10 \
  --timeout 3

# Output:
# 10:30:01 [INFO] ✓ HEALTHY http://api:8080/health (attempt 1/5)
# 10:30:01 [WARNING] ✗ Unreachable http://frontend:3000 (attempt 1/5)
# 10:30:11 [WARNING] ✗ Unreachable http://frontend:3000 (attempt 2/5)
# ...
# ── Health Check Summary ──
#   ✓ UP    http://api:8080/health
#   ✗ DOWN  http://frontend:3000
```

---

### Pattern 3 — EC2 Manager CLI

```python
#!/usr/bin/env python3
"""
ec2_manager.py — Start, stop, or list EC2 instances.

Usage:
    python ec2_manager.py list
    python ec2_manager.py list --state running --region ap-south-1
    python ec2_manager.py stop  --instance-id i-0abc123def456
    python ec2_manager.py start --instance-id i-0abc123def456
"""

import argparse
import os
import sys
import logging
import boto3
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(format="%(asctime)s [%(levelname)s] %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)


def parse_args():
    parser = argparse.ArgumentParser(description="EC2 instance manager")

    subparsers = parser.add_subparsers(dest="command", required=True)

    # -- list subcommand
    list_p = subparsers.add_parser("list", help="List EC2 instances")
    list_p.add_argument(
        "--state",
        choices=["running", "stopped", "pending", "all"],
        default="all",
        help="Filter by instance state (default: all)"
    )
    list_p.add_argument(
        "--region",
        default=os.environ.get("AWS_REGION", "ap-south-1"),
        help="AWS region (default: AWS_REGION env var or ap-south-1)"
    )

    # -- start subcommand
    start_p = subparsers.add_parser("start", help="Start a stopped instance")
    start_p.add_argument("--instance-id", required=True, help="EC2 instance ID")
    start_p.add_argument(
        "--region",
        default=os.environ.get("AWS_REGION", "ap-south-1")
    )

    # -- stop subcommand
    stop_p = subparsers.add_parser("stop", help="Stop a running instance")
    stop_p.add_argument("--instance-id", required=True, help="EC2 instance ID")
    stop_p.add_argument(
        "--region",
        default=os.environ.get("AWS_REGION", "ap-south-1")
    )
    stop_p.add_argument(
        "--force",
        action="store_true",
        help="Skip confirmation prompt"
    )

    return parser.parse_args()


def get_client(region):
    return boto3.client("ec2", region_name=region)


def cmd_list(args):
    ec2 = get_client(args.region)
    filters = [] if args.state == "all" else [
        {"Name": "instance-state-name", "Values": [args.state]}
    ]

    response = ec2.describe_instances(Filters=filters)

    print(f"\n{'ID':<22} {'State':<12} {'Type':<14} {'Name'}")
    print("-" * 70)

    for reservation in response["Reservations"]:
        for inst in reservation["Instances"]:
            name = next(
                (t["Value"] for t in inst.get("Tags", []) if t["Key"] == "Name"),
                "—"
            )
            print(f"{inst['InstanceId']:<22} "
                  f"{inst['State']['Name']:<12} "
                  f"{inst['InstanceType']:<14} "
                  f"{name}")


def cmd_start(args):
    ec2 = get_client(args.region)
    logger.info("Starting instance %s...", args.instance_id)
    ec2.start_instances(InstanceIds=[args.instance_id])
    logger.info("Start request sent ✓")


def cmd_stop(args):
    if not args.force:
        confirm = input(f"Stop instance {args.instance_id}? [y/N]: ")
        if confirm.lower() != "y":
            print("Aborted.")
            sys.exit(0)

    ec2 = get_client(args.region)
    logger.info("Stopping instance %s...", args.instance_id)
    ec2.stop_instances(InstanceIds=[args.instance_id])
    logger.info("Stop request sent ✓")


def main():
    args = parse_args()

    if args.command == "list":
        cmd_list(args)
    elif args.command == "start":
        cmd_start(args)
    elif args.command == "stop":
        cmd_stop(args)


if __name__ == "__main__":
    main()
```

```bash
python ec2_manager.py list
python ec2_manager.py list --state running --region us-east-1
python ec2_manager.py stop  --instance-id i-0abc123def456
python ec2_manager.py stop  --instance-id i-0abc123def456 --force
python ec2_manager.py start --instance-id i-0abc123def456
```

---

### Pattern 4 — Config Validator

```python
#!/usr/bin/env python3
"""
validate_config.py — Validate environment config before deployment.
Exits 0 if valid, exits 1 with errors listed if not.

Usage:
    python validate_config.py
    python validate_config.py --env-file .env.production
    python validate_config.py --env-file .env.staging --strict
"""

import argparse
import os
import sys
import re
from dotenv import load_dotenv


def parse_args():
    parser = argparse.ArgumentParser(
        description="Validate environment config before deployment"
    )
    parser.add_argument(
        "--env-file",
        default=".env",
        help="Path to .env file (default: .env)"
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Treat warnings as errors"
    )
    return parser.parse_args()


def main():
    args = parse_args()
    load_dotenv(args.env_file, override=True)

    errors   = []
    warnings = []

    # Required variables
    required = ["DB_HOST", "DB_PORT", "DB_PASSWORD", "APP_ENV", "AWS_REGION"]
    for var in required:
        if not os.environ.get(var):
            errors.append(f"{var} is required but not set")

    # Type validation
    db_port = os.environ.get("DB_PORT", "")
    if db_port and not db_port.isdigit():
        errors.append(f"DB_PORT must be a number, got '{db_port}'")

    # Value validation
    app_env = os.environ.get("APP_ENV", "")
    if app_env and app_env not in ["development", "staging", "production"]:
        errors.append(f"APP_ENV must be development/staging/production, got '{app_env}'")

    # Security warnings
    db_password = os.environ.get("DB_PASSWORD", "")
    if db_password and len(db_password) < 12:
        warnings.append("DB_PASSWORD is shorter than 12 characters — use a stronger password")

    slack_url = os.environ.get("SLACK_WEBHOOK_URL", "")
    if slack_url and not slack_url.startswith("https://"):
        warnings.append("SLACK_WEBHOOK_URL should use HTTPS")

    # Report
    if warnings:
        print("⚠ Warnings:")
        for w in warnings:
            print(f"  - {w}")

    if errors:
        print("\n✗ Errors:")
        for e in errors:
            print(f"  - {e}")
        sys.exit(1)

    if args.strict and warnings:
        print("\nStrict mode: warnings treated as errors")
        sys.exit(1)

    print("✓ Config is valid")
    sys.exit(0)


if __name__ == "__main__":
    main()
```

```bash
python validate_config.py
# ✓ Config is valid

python validate_config.py --env-file .env.production --strict
# ⚠ Warnings:
#   - DB_PASSWORD is shorter than 12 characters
# Strict mode: warnings treated as errors
```

---

## 📌 Quick Reference Cheatsheet

### argparse

```python
import argparse

parser = argparse.ArgumentParser(description="My script")

# Positional — required, by position
parser.add_argument("name")

# Optional — by flag name
parser.add_argument("--env", default="staging")

# Short + long flag
parser.add_argument("-v", "--verbose", action="store_true")

# Type conversion
parser.add_argument("--port",     type=int)
parser.add_argument("--rate",     type=float)

# Restrict to valid values
parser.add_argument("--level", choices=["low","mid","high"])

# Required optional
parser.add_argument("--token", required=True)

# Multiple values
parser.add_argument("--urls", nargs="+")   # one or more
parser.add_argument("--tags", nargs="*")   # zero or more
parser.add_argument("--hosts",nargs=3)     # exactly 3

# Boolean switches
parser.add_argument("--dry-run",  action="store_true")
parser.add_argument("--no-cache", action="store_false", dest="cache")

# Subcommands
subs = parser.add_subparsers(dest="command")
deploy = subs.add_parser("deploy")

args = parser.parse_args()
```

### os.environ

```python
import os

os.environ["KEY"]                      # read — KeyError if missing
os.environ.get("KEY")                  # read — None if missing
os.environ.get("KEY", "default")       # read — fallback if missing
"KEY" in os.environ                    # check existence
os.environ["KEY"] = "value"            # set
del os.environ["KEY"]                  # unset — KeyError if missing
os.environ.pop("KEY", None)            # safe unset

int(os.environ.get("PORT", "8080"))         # cast to int
os.environ.get("DEBUG","false") == "true"   # cast to bool
```

### python-dotenv

```python
from dotenv import load_dotenv, dotenv_values

load_dotenv()                          # load .env into os.environ
load_dotenv(".env.staging")            # load specific file
load_dotenv(override=True)             # .env overrides shell exports
load_dotenv(verbose=True)              # print which file loaded

config = dotenv_values(".env")         # load as dict, don't touch os.environ
```

---

| Concept | Key Point |
|---|---|
| `sys.argv` | Raw list of CLI inputs — use only for trivial scripts |
| `argparse` | Always use this for real scripts — free `--help`, validation, types |
| `required=True` | Makes an optional `--flag` mandatory |
| `action="store_true"` | Boolean flag — present = True, absent = False |
| `nargs="+"` | Accept one or more values for a single flag |
| `subparsers` | Build multi-command tools like docker or kubectl |
| `os.environ.get()` | Always prefer over `os.environ[]` to avoid KeyError |
| `.env` file | Never commit — commit `.env.example` instead |
| `load_dotenv()` | Call at top of script before reading any env var |
| `require_env()` | Custom validator — fail fast with clear messages |

---

*Last updated: 2026 · Python 3.11+ · DevOps track*
