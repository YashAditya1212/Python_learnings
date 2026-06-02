# Python as React for Shell Scripting

**User:** React is an advantage of frontend for things which can be done using vanilla js. So can I say that python is the React.js of shell scripting?

---

## Python String Built-in Functions — DevOps Edition

### Case Manipulation
`.upper()` / `.lower()` / `.capitalize()` / `.title()`

```python
env = "production"
region = "US-EAST-1"

# Normalize env variable from config — always compare in lowercase
if env.lower() == "production":
    print("Warning: Deploying to PROD")

# Normalize region input from user — always store in uppercase
region_key = region.upper()          # "US-EAST-1"

# Format for display in reports
"aws prod server".title()            # "Aws Prod Server"
"restarting nginx".capitalize()      # "Restarting nginx"
```

### Whitespace Cleaning
`.strip()` / `.lstrip()` / `.rstrip()`

```python
# Reading config values from a file — users often add accidental spaces
host = "   10.0.0.1   \n"
host.strip()     # "10.0.0.1"   — removes both sides
host.lstrip()    # "10.0.0.1   \n" — removes left only
host.rstrip()    # "   10.0.0.1"  — removes right only

# Common pattern when reading a .env file line by line
with open(".env") as f:
    for line in f:
        key, value = line.strip().split("=")
        # Without strip(), value would have "\n" at the end
```

### Splitting
`.split()` / `.rsplit()`

```python
# Parse a server log line
log = "2024-01-15 ERROR nginx: connection refused to 10.0.0.5:5432"
parts = log.split(" ", 2)
# ["2024-01-15", "ERROR", "nginx: connection refused to 10.0.0.5:5432"]

date    = parts[0]   # "2024-01-15"
level   = parts[1]   # "ERROR"
message = parts[2]   # rest of the line

# Split a file path — get just the filename
path = "/var/log/nginx/access.log"
filename = path.split("/")[-1]     # "access.log"

# rsplit — split from the right, useful for paths with dots
"my-app.v2.tar.gz".rsplit(".", 1)  # ["my-app.v2.tar", "gz"]
```

### Joining
`.join()`

```python
# Build a file path from parts — cleaner than string concatenation
parts = ["var", "log", "nginx", "error.log"]
path = "/".join(parts)             # "var/log/nginx/error.log"

# Build a comma-separated list of servers for a report
servers = ["web-01", "web-02", "web-03"]
print("Restarting: " + ", ".join(servers))
# "Restarting: web-01, web-02, web-03"

# Build a shell command from a list of arguments
cmd = ["docker", "run", "-d", "--name", "myapp", "myapp:latest"]
print(" ".join(cmd))
# "docker run -d --name myapp myapp:latest"
```

### Replacing
`.replace()`

```python
# Swap environment in a config template
template = "Host: db.dev.internal\nPort: 5432"
prod_config = template.replace("dev", "prod")
# "Host: db.prod.internal\nPort: 5432"

# Sanitize a branch name for use as a Docker tag
# Branch names can have slashes — Docker tags can't
branch = "feature/user-auth"
tag = branch.replace("/", "-")     # "feature-user-auth"
# docker build -t myapp:feature-user-auth .

# Remove unwanted characters from log output
raw = "Memory usage: [42%]\n"
clean = raw.replace("[", "").replace("]", "").strip()  # "Memory usage: 42%"
```

### Searching
`.find()` / `.index()`

```python
log = "2024-01-15 ERROR: disk usage at 95% on /dev/sda1"

# find() returns -1 if not found — safe to use in conditions
if log.find("ERROR") != -1:
    print("Alert: Error found in logs")

# index() raises ValueError if not found — use in try/except
try:
    pos = log.index("disk")
    print(log[pos:])               # "disk usage at 95% on /dev/sda1"
except ValueError:
    print("Keyword not found")

# Find position to extract a substring
url = "[https://s3.amazonaws.com/my-bucket/backup.tar.gz](https://s3.amazonaws.com/my-bucket/backup.tar.gz)"
bucket_start = url.find("my-bucket")
print(url[bucket_start:])          # "my-bucket/backup.tar.gz"
```

### Checking Start / End
`.startswith()` / `.endswith()`

```python
filename = "backup-2024-01-15.tar.gz"

# Filter only backup files in a directory listing
if filename.startswith("backup-"):
    print("Found backup:", filename)

# Filter by file extension
if filename.endswith(".tar.gz"):
    print("Compressed archive — safe to upload to S3")

# Accept a tuple of values — very useful for multi-check
log_file = "app.log"
if log_file.endswith((".log", ".txt", ".out")):
    print("Text log file — parse it")

# Check if a URL is HTTPS before making requests
endpoint = "[https://api.github.com](https://api.github.com)"
if not endpoint.startswith("https://"):
    raise ValueError("Only HTTPS endpoints allowed in production")
```

### Membership Check
`in` operator

```python
log_line = "CRITICAL: CPU usage exceeded 90% threshold"

# The simplest way to check for keywords in logs
if "CRITICAL" in log_line:
    send_slack_alert(log_line)

if "ERROR" in log_line or "CRITICAL" in log_line:
    trigger_pagerduty()

# Check if a required env variable is set
required_vars = ["DB_HOST", "DB_PORT", "API_KEY"]
import os
for var in required_vars:
    if var not in os.environ:
        raise EnvironmentError(f"Missing required env variable: {var}")
```

### String Formatting
`f-strings` / `.format()`

```python
server = "web-03"
cpu = 87.4
env = "production"

# f-strings — use these, they're cleaner and faster
message = f"[{env.upper()}] Server {server} CPU at {cpu:.1f}%"
# "[PRODUCTION] Server web-03 CPU at 87.4%"

# Format a Docker image tag with version and git SHA
version = "1.4.2"
git_sha = "a3f9c12"
image_tag = f"myapp:{version}-{git_sha}"   # "myapp:1.4.2-a3f9c12"

# .format() — useful when template is stored in a variable
template = "Deploying {app} version {ver} to {env}"
msg = template.format(app="medisync", ver="2.1.0", env="staging")
```

### Counting Occurrences
`.count()`

```python
log_output = """ERROR: connection refused
INFO: retrying...
ERROR: connection refused
ERROR: timeout exceeded
INFO: giving up"""

error_count = log_output.count("ERROR")    # 3
if error_count > 2:
    print(f"Too many errors ({error_count}) — triggering rollback")

# Count how many times a server appears in a load balancer log
access_log = "10.0.0.1 10.0.0.2 10.0.0.1 10.0.0.3 10.0.0.1"
hits = access_log.count("10.0.0.1")       # 3
```

### Validation Checks
`.isdigit()` / `.isalpha()` / `.isalnum()`

```python
# Validate port number from user input or config file
port = "8080"
if not port.isdigit():
    raise ValueError(f"Invalid port: {port} — must be a number")
port = int(port)

# Validate environment name contains only letters
env_name = "production"
if not env_name.isalpha():
    raise ValueError("Environment name must contain only letters")

# Validate container name — only alphanumeric and hyphens allowed
def is_valid_container_name(name):
    return name.replace("-", "").isalnum()

is_valid_container_name("my-app-v2")    # True
is_valid_container_name("my app v2")    # False — has spaces
```

### Padding & Alignment
`.zfill()` / `.ljust()` / `.rjust()` / `.center()`

```python
# zfill — pad with zeros, useful for sequential naming
for i in range(1, 6):
    server = f"web-{str(i).zfill(3)}"
    print(server)
# web-001, web-002, web-003, web-004, web-005

# Consistent naming matters for sorted log output
# ljust / rjust — align columns in terminal reports
services = [("nginx", "running"), ("redis", "stopped"), ("postgres", "running")]
for name, status in services:
    print(name.ljust(15) + status.rjust(10))
# nginx              running
# redis              stopped
# postgres           running
```

### Partition
`.partition()`

```python
# Split on first occurrence only — great for key=value parsing
line = "DB_HOST=prod-db.internal"
key, sep, value = line.partition("=")
# key = "DB_HOST", sep = "=", value = "prod-db.internal"

# Parse HTTP header line
header = "Content-Type: application/json"
name, _, value = header.partition(": ")
# name = "Content-Type", value = "application/json"
```

---

### Quick Reference

| Method | One-line use case |
| :--- | :--- |
| `.lower()` / `.upper()` | Normalize env vars and config values |
| `.strip()` | Clean file/config input |
| `.split()` | Parse log lines and paths |
| `.join()` | Build paths and shell commands |
| `.replace()` | Swap env names, sanitize tags |
| `.find()` / `.index()` | Locate keywords in log output |
| `.startswith()` / `.endswith()` | Filter files by name or extension |
| `in` | Check for ERROR/CRITICAL in logs |
| `f-strings` | Build messages, tags, image names |
| `.count()` | Count errors in log output |
| `.isdigit()` | Validate ports and numeric config |
| `.zfill()` | Sequential server naming |
| `.partition()` | Parse key=value config lines |

> **The 80% Rule:** The pattern you'll use 80% of the time in DevOps scripting: read a line → `.strip()` → `.split()` or `.partition()` → check with `in` or `.startswith()` → format output with `f-string`. That chain covers log parsing, config reading, and report generation in one shot.
