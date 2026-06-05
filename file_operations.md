# 🐍 Python for DevOps — File Operations

> **Scope:** Reading · Writing · Appending · File Modes · pathlib · os · shutil · JSON · YAML · CSV · Temp Files · File Watching
> **Style:** Real-world DevOps examples · Beginner-friendly · GitHub-ready

---

## 📑 Table of Contents

- [Core Concepts](#-core-concepts)
  - [Opening Files — open()](#opening-files--open)
  - [File Modes](#file-modes)
  - [The with Statement](#the-with-statement)
- [Reading Files](#-reading-files)
  - [read()](#read--entire-file-as-one-string)
  - [readline()](#readline--one-line-at-a-time)
  - [readlines()](#readlines--all-lines-as-a-list)
  - [Iterating Line by Line](#iterating-line-by-line)
- [Writing Files](#-writing-files)
  - [write()](#write)
  - [writelines()](#writelines)
  - [print() to a File](#print-to-a-file)
- [Appending to Files](#-appending-to-files)
- [File Modes — Complete Reference](#-file-modes--complete-reference)
- [pathlib — Modern File Paths](#-pathlib--modern-file-paths)
  - [Creating Paths](#creating-paths)
  - [Checking Files and Dirs](#checking-files-and-dirs)
  - [Reading and Writing](#reading-and-writing-with-pathlib)
  - [Directory Operations](#directory-operations)
  - [Glob — Find Files by Pattern](#glob--find-files-by-pattern)
- [os Module — File and Directory Ops](#-os-module--file-and-directory-ops)
- [shutil — Copy Move Delete](#-shutil--copy-move-delete)
- [Structured File Formats](#-structured-file-formats)
  - [JSON Files](#json-files)
  - [YAML Files](#yaml-files)
  - [CSV Files](#csv-files)
  - [.env Files](#env-files)
- [Temporary Files](#-temporary-files)
- [File Metadata](#-file-metadata)
- [Error Handling](#-error-handling)
- [Real DevOps Patterns](#-real-devops-patterns)
- [Quick Reference Cheatsheet](#-quick-reference-cheatsheet)

---

## 🔑 Core Concepts

### Opening Files — open()

Every file operation starts with `open()`. It returns a **file object**
that you use to read from or write to the file.

```python
# Syntax
file_object = open("path/to/file", mode, encoding="utf-8")

# Basic example
f = open("/var/log/app.log", "r")   # open for reading
content = f.read()                  # read the content
f.close()                           # MUST close — releases file handle
```

> ⚠️ **Always close files** after opening them. An unclosed file
> holds a system resource, can cause data corruption on write,
> and will eventually hit the OS file handle limit on long-running scripts.
> The `with` statement handles this automatically — use it always.

---

### File Modes

| Mode | Name | Description |
|---|---|---|
| `"r"` | Read | Default. Read only. Error if file missing. |
| `"w"` | Write | Write only. **Creates** file if missing. **Overwrites** if exists. |
| `"a"` | Append | Write only. **Creates** if missing. **Adds to end** if exists. |
| `"x"` | Exclusive | Create only. **Error if file already exists.** |
| `"r+"` | Read+Write | Read and write. Error if file missing. |
| `"w+"` | Write+Read | Read and write. Creates or overwrites. |
| `"b"` | Binary | Add to any mode: `"rb"`, `"wb"` — for non-text files. |
| `"t"` | Text | Default text mode. Usually omitted. |

```python
open("file.txt", "r")    # read text
open("file.txt", "w")    # write text — DANGER: overwrites existing content
open("file.txt", "a")    # append text — safe for logs
open("file.txt", "x")    # create new — fails if already exists
open("image.png", "rb")  # read binary — for images, zips, etc.
open("file.txt", "r+")   # read and write — pointer starts at beginning
```

---

### The with Statement

`with` is the **only correct way** to open files in Python.
It automatically closes the file when the block ends — even if an error occurs.

```python
# Without with — risky
f = open("/var/log/app.log", "r")
content = f.read()
f.close()   # if an exception happens above, this line never runs


# With 'with' — always safe
with open("/var/log/app.log", "r") as f:
    content = f.read()
# file is automatically closed here — guaranteed


# Open multiple files at once
with open("input.log", "r") as infile, open("errors.log", "w") as outfile:
    for line in infile:
        if "ERROR" in line:
            outfile.write(line)
# both files closed automatically
```

---

## 📖 Reading Files

### read() — Entire File as One String

```python
# Read the whole file into a single string
with open("/etc/nginx/nginx.conf", "r") as f:
    content = f.read()

print(content)          # entire file content
print(len(content))     # total character count


# ── DevOps use cases ──────────────────────────────────────────────────────────

# Check if a config file contains a specific directive
with open("/etc/nginx/nginx.conf", "r") as f:
    config = f.read()

if "worker_processes auto" not in config:
    print("WARNING: worker_processes not set to auto")

if "ssl_certificate" not in config:
    print("WARNING: SSL not configured in nginx")


# Read a shell script and validate it
with open("deploy.sh", "r") as f:
    script = f.read()

if "set -e" not in script:
    print("WARNING: deploy.sh missing 'set -e' — errors won't stop execution")

if "rm -rf /" in script:
    print("CRITICAL: Dangerous command found in deploy script!")


# Read and replace — swap environment placeholder
with open("config.template", "r") as f:
    template = f.read()

config = template.replace("{{ENV}}", "production")
config = config.replace("{{DB_HOST}}", "prod-db.internal")
config = config.replace("{{REPLICAS}}", "5")

with open("config.yaml", "w") as f:
    f.write(config)
```

---

### readline() — One Line at a Time

Reads one line per call. Useful for very large files where loading everything
into memory is not possible.

```python
with open("/var/log/app.log", "r") as f:
    first_line  = f.readline()   # "2024-01-15 10:30:00 INFO  service started\n"
    second_line = f.readline()   # "2024-01-15 10:30:01 ERROR connection refused\n"
    third_line  = f.readline()   # next line...

# Each readline() moves the pointer forward
# Returns empty string "" when end of file is reached


# ── Read until a condition is met ────────────────────────────────────────────
with open("/var/log/app.log", "r") as f:
    while True:
        line = f.readline()

        if not line:           # empty string = end of file
            break

        if "CRITICAL" in line:
            send_pagerduty_alert(line)
            break              # stop after first critical — don't flood


# ── Process a large log file without loading it all ──────────────────────────
error_count = 0

with open("/var/log/nginx/access.log", "r") as f:
    while line := f.readline():    # walrus operator — read and check in one go
        if " 500 " in line or " 502 " in line or " 503 " in line:
            error_count += 1

print(f"Total 5xx errors: {error_count}")
```

---

### readlines() — All Lines as a List

Returns a list where each element is one line (including `\n` at the end).

```python
with open("/var/log/app.log", "r") as f:
    lines = f.readlines()
# ["2024-01-15 INFO  started\n", "2024-01-15 ERROR timeout\n", ...]

# Access specific lines
print(lines[0])     # first line (with \n)
print(lines[-1])    # last line
print(len(lines))   # total number of lines


# ── Strip newline from each line ──────────────────────────────────────────────
with open("/etc/hosts", "r") as f:
    lines = [line.strip() for line in f.readlines()]
# ["127.0.0.1  localhost", "10.0.0.1  web-01", ...]


# ── Get the last N lines — like tail -n ──────────────────────────────────────
def tail(filepath, n=100):
    """Return the last n lines of a file."""
    with open(filepath, "r") as f:
        lines = f.readlines()
    return lines[-n:]

last_50 = tail("/var/log/app.log", 50)
for line in last_50:
    print(line, end="")   # end="" because lines already have \n


# ── Get the first N lines — like head -n ─────────────────────────────────────
def head(filepath, n=10):
    """Return the first n lines of a file."""
    with open(filepath, "r") as f:
        lines = f.readlines()
    return lines[:n]
```

---

### Iterating Line by Line

The most **memory-efficient** way to read large files.
Python reads one line at a time — never loads the whole file.

```python
# Iterating a file object reads one line per iteration
with open("/var/log/nginx/access.log", "r") as f:
    for line in f:
        # line includes \n at the end — use .strip() to remove
        process(line.strip())


# ── Parse a log file ─────────────────────────────────────────────────────────
error_lines  = []
total_lines  = 0

with open("/var/log/app.log", "r", encoding="utf-8") as f:
    for line in f:
        total_lines += 1
        line = line.strip()

        if not line:           # skip blank lines
            continue

        if "ERROR" in line or "CRITICAL" in line:
            error_lines.append(line)

print(f"Scanned {total_lines} lines — found {len(error_lines)} errors")


# ── Search for a keyword — return matching lines with line numbers ────────────
def grep(filepath, keyword, case_sensitive=True):
    """Return list of (line_number, line) tuples where keyword is found."""
    matches = []

    with open(filepath, "r") as f:
        for line_num, line in enumerate(f, start=1):
            search_line = line if case_sensitive else line.lower()
            search_key  = keyword if case_sensitive else keyword.lower()

            if search_key in search_line:
                matches.append((line_num, line.strip()))

    return matches


results = grep("/var/log/app.log", "connection refused")
for line_num, line in results:
    print(f"Line {line_num}: {line}")


# ── Count lines matching a pattern — like grep -c ────────────────────────────
with open("/var/log/nginx/access.log", "r") as f:
    count = sum(1 for line in f if "POST /api" in line)

print(f"POST /api requests: {count}")
```

---

## ✍️ Writing Files

### write()

```python
# "w" mode — creates the file or OVERWRITES existing content
with open("deploy_report.txt", "w") as f:
    f.write("Deployment Report\n")
    f.write("=================\n")
    f.write(f"Status: Success\n")
    f.write(f"Version: v2.1.0\n")

# write() does NOT add newlines automatically — you must add \n yourself
# Returns the number of characters written


# ── Write a generated config file ────────────────────────────────────────────
def write_nginx_config(server_name, port, upstream_host):
    config = f"""
server {{
    listen {port};
    server_name {server_name};

    location / {{
        proxy_pass http://{upstream_host};
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }}
}}
""".strip()

    config_path = f"/etc/nginx/sites-available/{server_name}"
    with open(config_path, "w") as f:
        f.write(config)

    print(f"Config written to {config_path}")


write_nginx_config("api.medisync.io", 80, "10.0.0.5:8080")


# ── Write a deployment summary ────────────────────────────────────────────────
from datetime import datetime

def write_deploy_summary(app, version, env, status, details):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    filename  = f"deploy_{app}_{env}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"

    with open(filename, "w", encoding="utf-8") as f:
        f.write(f"DEPLOYMENT SUMMARY\n")
        f.write(f"{'=' * 40}\n")
        f.write(f"Timestamp:   {timestamp}\n")
        f.write(f"Application: {app}\n")
        f.write(f"Version:     {version}\n")
        f.write(f"Environment: {env}\n")
        f.write(f"Status:      {status}\n")
        f.write(f"{'=' * 40}\n")
        f.write(f"Details:\n{details}\n")

    return filename
```

---

### writelines()

Write a list of strings at once. Like `write()`, does NOT add newlines automatically.

```python
# writelines() takes any iterable of strings
lines = [
    "web-01: healthy\n",
    "web-02: healthy\n",
    "web-03: unhealthy\n",
    "web-04: healthy\n",
]

with open("health_report.txt", "w") as f:
    f.writelines(lines)   # writes all lines in one call


# ── Write a list of servers to a hosts file ───────────────────────────────────
servers = [
    ("10.0.0.1", "web-01"),
    ("10.0.0.2", "web-02"),
    ("10.0.0.3", "db-primary"),
]

with open("/tmp/new_hosts", "w") as f:
    f.writelines(f"{ip}\t{hostname}\n" for ip, hostname in servers)
# 10.0.0.1    web-01
# 10.0.0.2    web-02
# 10.0.0.3    db-primary


# ── Filter a file — keep only non-error lines ─────────────────────────────────
with open("app.log", "r") as infile:
    clean_lines = [l for l in infile if "ERROR" not in l]

with open("app_clean.log", "w") as outfile:
    outfile.writelines(clean_lines)
```

---

### print() to a File

A convenient alternative to `write()` — adds newlines automatically.

```python
with open("report.txt", "w") as f:
    print("Deployment Report", file=f)        # auto adds \n
    print("=" * 40,           file=f)
    print(f"App:     medisync",   file=f)
    print(f"Version: v2.1.0",     file=f)
    print(f"Status:  Success",    file=f)

# print() to file is cleaner than f.write() + "\n"
# especially for formatted reports
```

---

## ➕ Appending to Files

`"a"` mode adds content to the **end** of the file without touching existing content.
If the file doesn't exist, it creates it. Safe for logs.

```python
# "a" mode — safe for logs and audit trails
with open("/var/log/deploy.log", "a") as f:
    f.write(f"2024-01-15 10:30:00 INFO  Deployment started\n")

# File pointer starts at the end — cannot read in "a" mode


# ── Append-only log writer ────────────────────────────────────────────────────
from datetime import datetime

def log(message, level="INFO", log_file="/var/log/medisync/deploy.log"):
    """Append a structured log line to a file."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line      = f"{timestamp} [{level:<8}] {message}\n"

    with open(log_file, "a", encoding="utf-8") as f:
        f.write(line)


log("Deployment pipeline started")
log("Running tests...",        level="INFO")
log("2 tests failed",          level="WARNING")
log("Deployment blocked",      level="ERROR")


# ── Append to a CSV audit trail ───────────────────────────────────────────────
import csv
from datetime import datetime

def record_deployment(app, version, env, status, user):
    """Record deployment details in a CSV audit file."""
    row = [
        datetime.now().isoformat(),
        app,
        version,
        env,
        status,
        user,
    ]

    with open("deployments_audit.csv", "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(row)


record_deployment("medisync", "v2.1.0", "production", "success", "rahul")
```

---

## 📁 pathlib — Modern File Paths

`pathlib` is the modern, object-oriented way to work with file paths.
Always prefer it over `os.path` for new scripts.

```python
from pathlib import Path
```

---

### Creating Paths

```python
# Create a Path object — no file system call yet
log_dir  = Path("/var/log/medisync")
log_file = Path("/var/log/medisync/app.log")

# Join paths with / operator — cleaner than os.path.join
log_dir  = Path("/var/log")
app_log  = log_dir / "medisync" / "app.log"
# Path("/var/log/medisync/app.log")

# Current directory and relative paths
here       = Path(".")               # current directory
config     = Path("config") / "app.yaml"
script_dir = Path(__file__).parent   # directory of the current script

# Home directory
home    = Path.home()                # Path("/home/ubuntu")
ssh_dir = Path.home() / ".ssh"
ssh_key = Path.home() / ".ssh" / "id_rsa"

# Get path parts
path = Path("/var/log/nginx/error.log")

path.name       # "error.log"      — filename with extension
path.stem       # "error"          — filename without extension
path.suffix     # ".log"           — extension only
path.suffixes   # [".log"]         — all extensions (e.g. [".tar", ".gz"])
path.parent     # Path("/var/log/nginx")
path.parts      # ("/", "var", "log", "nginx", "error.log")
str(path)       # "/var/log/nginx/error.log" — convert to string
```

---

### Checking Files and Dirs

```python
path = Path("/var/log/medisync/app.log")

path.exists()     # True if file or dir exists
path.is_file()    # True if it's a file (not dir)
path.is_dir()     # True if it's a directory
path.is_symlink() # True if it's a symbolic link


# ── Guard checks before file operations ──────────────────────────────────────
config_path = Path("/etc/medisync/config.yaml")

if not config_path.exists():
    print(f"ERROR: Config not found at {config_path}")
    sys.exit(1)

if not config_path.is_file():
    print(f"ERROR: {config_path} is not a file")
    sys.exit(1)

if config_path.stat().st_size == 0:
    print(f"ERROR: Config file is empty")
    sys.exit(1)

# Safe to open now
with open(config_path) as f:
    config = yaml.safe_load(f)
```

---

### Reading and Writing with pathlib

```python
path = Path("/var/log/medisync/app.log")

# Read entire file as string
content = path.read_text(encoding="utf-8")

# Read as bytes
raw = path.read_bytes()

# Write (overwrites)
path.write_text("new content\n", encoding="utf-8")

# Append — pathlib has no native append, use open()
with path.open("a") as f:
    f.write("appended line\n")


# ── Clean one-liners ──────────────────────────────────────────────────────────

# Read a config template and fill placeholders
template = Path("nginx.conf.template").read_text()
rendered = template.replace("{{HOST}}", "api.medisync.io")
Path("/etc/nginx/sites-available/medisync").write_text(rendered)

# Copy file content (read one, write another)
source = Path("config.prod.yaml")
dest   = Path("/etc/medisync/config.yaml")
dest.write_text(source.read_text())
```

---

### Directory Operations

```python
from pathlib import Path

log_dir    = Path("/var/log/medisync")
backup_dir = Path("/backup/2024-01-15")

# ── Create directories ────────────────────────────────────────────────────────
log_dir.mkdir()                          # create — fails if parent missing
log_dir.mkdir(parents=True)             # like mkdir -p — creates all parents
log_dir.mkdir(parents=True, exist_ok=True)  # no error if already exists

# ── Delete ────────────────────────────────────────────────────────────────────
Path("old_file.log").unlink()            # delete a file
Path("old_file.log").unlink(missing_ok=True)  # no error if already gone
log_dir.rmdir()                          # delete empty directory

# ── Rename / Move ─────────────────────────────────────────────────────────────
Path("app.log").rename("app.log.bak")    # rename (same directory)
Path("app.log").replace("archive/app.log") # move (overwrites destination)

# ── List directory contents ───────────────────────────────────────────────────
log_dir = Path("/var/log/nginx")

# All items (files + dirs)
for item in log_dir.iterdir():
    print(item.name)

# Only files
for item in log_dir.iterdir():
    if item.is_file():
        print(item.name)

# Only directories
for item in log_dir.iterdir():
    if item.is_dir():
        print(item.name)
```

---

### Glob — Find Files by Pattern

```python
from pathlib import Path

log_dir = Path("/var/log")

# ── glob — search in one directory ───────────────────────────────────────────
list(log_dir.glob("*.log"))           # all .log files in /var/log
list(log_dir.glob("nginx-*.log"))     # nginx-access.log, nginx-error.log, etc.
list(log_dir.glob("access.log*"))     # access.log, access.log.1, access.log.2.gz


# ── rglob — recursive, searches all subdirectories ───────────────────────────
list(log_dir.rglob("*.log"))          # ALL .log files anywhere under /var/log
list(log_dir.rglob("error.log"))      # any error.log at any depth
list(log_dir.rglob("*.yaml"))         # all YAML files recursively


# ── DevOps use cases ──────────────────────────────────────────────────────────

# Find all log files larger than 100MB
large_logs = [
    f for f in Path("/var/log").rglob("*.log")
    if f.stat().st_size > 100 * 1024 * 1024
]

for log in large_logs:
    size_mb = log.stat().st_size / (1024 * 1024)
    print(f"{log} — {size_mb:.1f} MB")


# Find all Kubernetes YAML manifests
manifests = list(Path("k8s/").rglob("*.yaml"))
print(f"Found {len(manifests)} Kubernetes manifests")


# Find all Python files that import boto3
boto3_files = []
for py_file in Path(".").rglob("*.py"):
    if "import boto3" in py_file.read_text():
        boto3_files.append(py_file)

print(f"Files using boto3: {boto3_files}")


# Find and delete old backup files (older than 7 days)
import time

cutoff = time.time() - (7 * 24 * 60 * 60)   # 7 days ago

for backup in Path("/backup").glob("*.tar.gz"):
    if backup.stat().st_mtime < cutoff:
        print(f"Deleting old backup: {backup.name}")
        backup.unlink()
```

---

## 🖥️ os Module — File and Directory Ops

```python
import os

# ── Path operations ───────────────────────────────────────────────────────────
os.getcwd()                              # current working directory
os.chdir("/var/log")                     # change directory

os.path.exists("/etc/nginx/nginx.conf")  # True / False
os.path.isfile("/etc/hosts")             # True if file
os.path.isdir("/var/log")               # True if directory

os.path.join("/var", "log", "app.log")  # "/var/log/app.log"  — safe join
os.path.basename("/var/log/app.log")    # "app.log"
os.path.dirname("/var/log/app.log")     # "/var/log"
os.path.splitext("app.log")             # ("app", ".log")
os.path.getsize("/var/log/app.log")     # file size in bytes
os.path.abspath("config.yaml")         # full absolute path


# ── Directory operations ──────────────────────────────────────────────────────
os.mkdir("/var/log/medisync")            # create one directory
os.makedirs("/var/log/medisync/api", exist_ok=True)  # like mkdir -p

os.listdir("/var/log")                   # list directory contents
os.remove("/tmp/old.log")               # delete a file
os.rmdir("/tmp/empty_dir")              # delete empty directory
os.rename("old.log", "archive.log")     # rename/move


# ── Walk — recursively traverse directory tree ────────────────────────────────
# os.walk yields (dirpath, subdirs, files) for every directory
for dirpath, subdirs, files in os.walk("/var/log"):
    for filename in files:
        full_path = os.path.join(dirpath, filename)
        size      = os.path.getsize(full_path)
        print(f"{full_path} — {size} bytes")


# ── DevOps use cases ──────────────────────────────────────────────────────────

# Calculate total size of a directory (like du -sh)
def get_dir_size(path):
    total = 0
    for dirpath, _, files in os.walk(path):
        for f in files:
            fp    = os.path.join(dirpath, f)
            total += os.path.getsize(fp)
    return total

size_bytes = get_dir_size("/var/log")
size_mb    = size_bytes / (1024 * 1024)
print(f"/var/log total size: {size_mb:.1f} MB")


# List only .log files in a directory
log_files = [
    f for f in os.listdir("/var/log/nginx")
    if f.endswith(".log")
]


# Ensure output directory exists before writing
output_dir = "/opt/medisync/reports"
os.makedirs(output_dir, exist_ok=True)

output_file = os.path.join(output_dir, "health_report.json")
with open(output_file, "w") as f:
    json.dump(report, f, indent=2)
```

---

## 📦 shutil — Copy Move Delete

`shutil` handles **higher-level** file operations — copying entire directories,
moving files across filesystems, and creating archives.

```python
import shutil


# ── Copy ──────────────────────────────────────────────────────────────────────
shutil.copy("config.yaml", "/backup/config.yaml")
# copies file — destination can be a file path or directory

shutil.copy2("config.yaml", "/backup/config.yaml")
# same as copy but also preserves metadata (timestamps, permissions)

shutil.copytree("/etc/nginx", "/backup/nginx_config")
# copy ENTIRE directory tree — destination must not exist


# ── Move ──────────────────────────────────────────────────────────────────────
shutil.move("app.log", "/archive/app.log")
# move file or directory — works across filesystems (unlike os.rename)


# ── Delete ────────────────────────────────────────────────────────────────────
shutil.rmtree("/tmp/build_artifacts")
# delete directory and ALL its contents — like rm -rf
# WARNING: no confirmation, no recycle bin — gone permanently


# ── Disk usage ────────────────────────────────────────────────────────────────
total, used, free = shutil.disk_usage("/")
print(f"Total: {total // (2**30)} GB")
print(f"Used:  {used  // (2**30)} GB")
print(f"Free:  {free  // (2**30)} GB")
print(f"Usage: {used / total * 100:.1f}%")


# ── Create archives ───────────────────────────────────────────────────────────
# shutil.make_archive(output_name, format, root_dir, base_dir)

shutil.make_archive("/backup/medisync-2024-01-15", "gztar", "/opt", "medisync")
# creates: /backup/medisync-2024-01-15.tar.gz
# containing the contents of /opt/medisync

shutil.make_archive("/backup/logs-2024-01-15", "zip", "/var/log")
# creates: /backup/logs-2024-01-15.zip


# ── Extract archives ──────────────────────────────────────────────────────────
shutil.unpack_archive("medisync.tar.gz", "/opt/medisync")
shutil.unpack_archive("config-backup.zip", "/tmp/restore")


# ── DevOps use case — rotate and archive logs ─────────────────────────────────
from datetime import datetime
from pathlib import Path

def rotate_logs(log_dir, archive_dir, keep_days=7):
    """Archive and compress log files older than keep_days."""
    import time

    log_dir_path     = Path(log_dir)
    archive_dir_path = Path(archive_dir)
    archive_dir_path.mkdir(parents=True, exist_ok=True)

    cutoff = time.time() - (keep_days * 86400)
    rotated = 0

    for log_file in log_dir_path.glob("*.log"):
        if log_file.stat().st_mtime < cutoff:
            dest = archive_dir_path / log_file.name
            shutil.move(str(log_file), str(dest))
            rotated += 1
            print(f"Rotated: {log_file.name}")

    if rotated > 0:
        date_str     = datetime.now().strftime("%Y%m%d")
        archive_name = str(archive_dir_path / f"logs-{date_str}")
        shutil.make_archive(archive_name, "gztar", archive_dir)
        shutil.rmtree(archive_dir)
        print(f"Compressed to {archive_name}.tar.gz")

    print(f"Rotated {rotated} log files")


rotate_logs("/var/log/medisync", "/var/log/medisync/archive")
```

---

## 🗂️ Structured File Formats

### JSON Files

```python
import json


# ── Read JSON ─────────────────────────────────────────────────────────────────
with open("config.json", "r") as f:
    config = json.load(f)          # parse JSON file → Python dict/list

# Parse a JSON string (from API response, subprocess output, etc.)
raw_json = '{"status": "healthy", "version": "v2.1.0", "uptime": 99.9}'
data     = json.loads(raw_json)    # string → dict

print(config["db"]["host"])
print(data["status"])


# ── Write JSON ────────────────────────────────────────────────────────────────
report = {
    "timestamp":   "2024-01-15T10:30:00",
    "environment": "production",
    "services": [
        {"name": "api",      "status": "healthy",   "uptime": 99.9},
        {"name": "database", "status": "healthy",   "uptime": 100.0},
        {"name": "cache",    "status": "unhealthy", "uptime": 87.3},
    ],
    "overall": "degraded",
}

with open("health_report.json", "w") as f:
    json.dump(report, f, indent=2)        # write dict → JSON file

# Convert to JSON string (for API calls, logging)
json_str = json.dumps(report, indent=2)   # dict → string


# ── Update a JSON file ────────────────────────────────────────────────────────
config_path = "deploy_config.json"

with open(config_path, "r") as f:
    config = json.load(f)

config["version"]    = "v2.2.0"          # update a value
config["replicas"]   = 5
config["updated_at"] = "2024-01-15"

with open(config_path, "w") as f:
    json.dump(config, f, indent=2)        # write back


# ── Pretty print JSON to terminal ────────────────────────────────────────────
print(json.dumps(report, indent=2))


# ── Handle non-serialisable types ────────────────────────────────────────────
from datetime import datetime

report["timestamp"] = datetime.now()

# This will fail — datetime is not JSON-serialisable
# json.dumps(report)   # TypeError

# Fix — convert datetime to string
json.dumps(report, default=str)   # converts any unknown type to str
```

---

### YAML Files

```python
import yaml   # pip install PyYAML


# ── Read YAML ─────────────────────────────────────────────────────────────────
with open("deployment.yaml", "r") as f:
    manifest = yaml.safe_load(f)      # safe_load — prevents code execution
    # NEVER use yaml.load() without Loader=yaml.SafeLoader — security risk

# Read multiple YAML docs from one file (separated by ---)
with open("k8s_resources.yaml", "r") as f:
    resources = list(yaml.safe_load_all(f))   # list of dicts


# ── Write YAML ────────────────────────────────────────────────────────────────
config = {
    "app":      "medisync",
    "version":  "v2.1.0",
    "replicas": 3,
    "database": {
        "host": "prod-db.internal",
        "port": 5432,
        "name": "medisync",
    },
    "ports": [8080, 9090],
}

with open("app_config.yaml", "w") as f:
    yaml.dump(config, f, default_flow_style=False, indent=2)
# default_flow_style=False — use block style (readable) not inline style


# ── Update a Kubernetes manifest ──────────────────────────────────────────────
def update_k8s_image(manifest_path, new_image):
    """Update the container image in a Kubernetes Deployment manifest."""
    with open(manifest_path, "r") as f:
        manifest = yaml.safe_load(f)

    containers = manifest["spec"]["template"]["spec"]["containers"]
    for container in containers:
        if container["name"] == "api":
            container["image"] = new_image

    with open(manifest_path, "w") as f:
        yaml.dump(manifest, f, default_flow_style=False)

    print(f"Updated image to {new_image} in {manifest_path}")


update_k8s_image("k8s/deployment.yaml", "medisync:v2.2.0")


# ── Generate a docker-compose.yml ────────────────────────────────────────────
def generate_compose(app_name, image, env_vars, ports):
    compose = {
        "version": "3.8",
        "services": {
            app_name: {
                "image":       image,
                "environment": env_vars,
                "ports":       ports,
                "restart":     "unless-stopped",
            }
        }
    }

    with open("docker-compose.yml", "w") as f:
        yaml.dump(compose, f, default_flow_style=False)


generate_compose(
    app_name  = "medisync-api",
    image     = "medisync:v2.1.0",
    env_vars  = ["APP_ENV=production", "LOG_LEVEL=INFO"],
    ports     = ["8080:8080"],
)
```

---

### CSV Files

```python
import csv


# ── Read CSV ──────────────────────────────────────────────────────────────────
# As rows (list of lists)
with open("servers.csv", "r", newline="") as f:
    reader = csv.reader(f)
    header = next(reader)         # read header row separately
    for row in reader:
        hostname, ip, port, env = row
        print(f"{hostname} → {ip}:{port} [{env}]")


# As dicts (DictReader — uses header row as keys)
with open("servers.csv", "r", newline="") as f:
    reader = csv.DictReader(f)
    for row in reader:
        print(row["hostname"], row["ip"], row["port"])
        # row is an OrderedDict with column names as keys


# ── Write CSV ─────────────────────────────────────────────────────────────────
servers = [
    ["web-01", "10.0.0.1", "8080", "production"],
    ["web-02", "10.0.0.2", "8080", "production"],
    ["db-01",  "10.0.0.3", "5432", "production"],
]

with open("inventory.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["hostname", "ip", "port", "environment"])  # header
    writer.writerows(servers)    # write all rows at once


# DictWriter — write from list of dicts
instances = [
    {"id": "i-001", "type": "t3.medium", "state": "running",  "region": "ap-south-1"},
    {"id": "i-002", "type": "t3.small",  "state": "stopped",  "region": "us-east-1"},
]

with open("ec2_report.csv", "w", newline="") as f:
    fieldnames = ["id", "type", "state", "region"]
    writer     = csv.DictWriter(f, fieldnames=fieldnames)

    writer.writeheader()         # write column names
    writer.writerows(instances)  # write all rows


# ── Append to CSV audit log ───────────────────────────────────────────────────
from datetime import datetime

def log_deployment(app, version, env, status):
    with open("deploy_audit.csv", "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([
            datetime.now().isoformat(),
            app,
            version,
            env,
            status,
        ])
```

---

### .env Files

```python
# ── Read .env manually (without dotenv library) ───────────────────────────────
def load_env_file(filepath=".env"):
    """
    Parse a .env file and return a dict of key-value pairs.
    Handles comments, blank lines, and quoted values.
    """
    env = {}

    with open(filepath, "r") as f:
        for line in f:
            line = line.strip()

            # Skip blank lines and comments
            if not line or line.startswith("#"):
                continue

            # Skip lines without =
            if "=" not in line:
                continue

            key, _, value = line.partition("=")
            key   = key.strip()
            value = value.strip().strip('"').strip("'")   # remove quotes

            env[key] = value

    return env


config = load_env_file(".env")
print(config["DB_HOST"])
print(config["APP_ENV"])


# ── Write a .env file ──────────────────────────────────────────────────────────
def write_env_file(env_dict, filepath=".env"):
    """Write a dict as a .env file."""
    with open(filepath, "w") as f:
        f.write("# Auto-generated — do not commit\n\n")
        for key, value in env_dict.items():
            f.write(f"{key}={value}\n")


write_env_file({
    "APP_ENV":     "staging",
    "DB_HOST":     "staging-db.internal",
    "DB_PORT":     "5432",
    "LOG_LEVEL":   "INFO",
})
```

---

## 🕐 Temporary Files

Used for intermediate processing — automatically deleted when done.

```python
import tempfile
import os


# ── Named temporary file ──────────────────────────────────────────────────────
with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml",
                                  delete=True, encoding="utf-8") as tmp:
    tmp.write("app: medisync\nenv: production\n")
    tmp_path = tmp.name
    print(f"Temp file: {tmp_path}")
    # file exists here — you can pass tmp_path to other processes

# file is automatically deleted after the with block


# ── Temporary directory ───────────────────────────────────────────────────────
with tempfile.TemporaryDirectory() as tmp_dir:
    build_path   = os.path.join(tmp_dir, "build")
    os.makedirs(build_path)

    # Do build work in the temp directory
    # e.g., clone repo, run tests, build Docker image

    print(f"Working in: {tmp_dir}")
# entire directory tree is deleted after the block


# ── DevOps use case — render and apply a K8s manifest ────────────────────────
import subprocess
import tempfile
import yaml

def apply_manifest(manifest_dict):
    """Render a dict as YAML and apply it to the cluster via kubectl."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml",
                                      delete=False, encoding="utf-8") as tmp:
        yaml.dump(manifest_dict, tmp, default_flow_style=False)
        tmp_path = tmp.name

    try:
        result = subprocess.run(
            ["kubectl", "apply", "-f", tmp_path],
            capture_output=True, text=True, check=True
        )
        print(result.stdout)
    finally:
        os.unlink(tmp_path)   # always clean up


manifest = {
    "apiVersion": "v1",
    "kind": "ConfigMap",
    "metadata": {"name": "app-config", "namespace": "production"},
    "data": {"LOG_LEVEL": "INFO", "APP_ENV": "production"},
}

apply_manifest(manifest)
```

---

## 📊 File Metadata

```python
import os
from pathlib import Path
from datetime import datetime


# ── Using os.stat() ───────────────────────────────────────────────────────────
stat = os.stat("/var/log/app.log")

stat.st_size    # file size in bytes
stat.st_mtime   # last modified time (Unix timestamp)
stat.st_atime   # last accessed time
stat.st_ctime   # metadata changed time (Linux) / created time (Windows)
stat.st_mode    # permissions as a bitmask


# ── Using pathlib ─────────────────────────────────────────────────────────────
path = Path("/var/log/app.log")
stat = path.stat()

# Size
size_bytes = stat.st_size
size_mb    = size_bytes / (1024 * 1024)
print(f"Size: {size_mb:.2f} MB")

# Last modified — human-readable
modified = datetime.fromtimestamp(stat.st_mtime)
print(f"Modified: {modified.strftime('%Y-%m-%d %H:%M:%S')}")

# Age in hours
age_hours = (datetime.now() - modified).total_seconds() / 3600
print(f"Age: {age_hours:.1f} hours")


# ── DevOps use cases ──────────────────────────────────────────────────────────

# Find all log files modified in the last hour
import time

one_hour_ago = time.time() - 3600

recent_logs = [
    f for f in Path("/var/log").rglob("*.log")
    if f.stat().st_mtime > one_hour_ago
]

print(f"Logs modified in the last hour: {len(recent_logs)}")


# Report top 5 largest files in a directory
log_files = list(Path("/var/log").rglob("*.log"))
log_files.sort(key=lambda f: f.stat().st_size, reverse=True)

print("Top 5 largest logs:")
for log in log_files[:5]:
    size_mb = log.stat().st_size / (1024 * 1024)
    print(f"  {size_mb:8.2f} MB  {log}")


# Alert if a file hasn't been updated in 30 minutes (stuck process?)
def check_file_freshness(filepath, max_age_minutes=30):
    path = Path(filepath)
    if not path.exists():
        return False, "file does not exist"

    age_minutes = (time.time() - path.stat().st_mtime) / 60
    if age_minutes > max_age_minutes:
        return False, f"not updated in {age_minutes:.0f} minutes"

    return True, f"updated {age_minutes:.0f} minutes ago"

fresh, msg = check_file_freshness("/var/log/medisync/app.log")
if not fresh:
    print(f"WARNING: Log file stale — {msg}")
```

---

## ⚠️ Error Handling

```python
import errno


# ── Common file exceptions ────────────────────────────────────────────────────

# FileNotFoundError — file or directory does not exist
try:
    with open("/etc/nonexistent.conf", "r") as f:
        content = f.read()
except FileNotFoundError as e:
    print(f"ERROR: File not found — {e.filename}")


# PermissionError — not allowed to read/write
try:
    with open("/etc/shadow", "r") as f:
        content = f.read()
except PermissionError as e:
    print(f"ERROR: Permission denied — {e.filename}")


# IsADirectoryError — tried to open a dir as a file
try:
    with open("/var/log", "r") as f:
        content = f.read()
except IsADirectoryError:
    print("ERROR: That's a directory, not a file")


# FileExistsError — "x" mode, file already exists
try:
    with open("config.yaml", "x") as f:
        f.write("new content")
except FileExistsError:
    print("ERROR: config.yaml already exists — refusing to overwrite")


# OSError — parent directory of the catch-all for OS errors
try:
    with open("/nonexistent_dir/file.txt", "w") as f:
        f.write("content")
except OSError as e:
    print(f"ERROR: {e.strerror} — {e.filename}")


# ── Production-grade file read ────────────────────────────────────────────────
def safe_read(filepath, default=None, encoding="utf-8"):
    """
    Safely read a file. Returns content or default on any error.
    Logs the error but does not crash the script.
    """
    import logging
    logger = logging.getLogger(__name__)

    try:
        with open(filepath, "r", encoding=encoding) as f:
            return f.read()

    except FileNotFoundError:
        logger.warning("File not found: %s", filepath)
        return default

    except PermissionError:
        logger.error("Permission denied reading: %s", filepath)
        return default

    except UnicodeDecodeError as e:
        logger.error("Encoding error in %s: %s", filepath, e)
        return default

    except OSError as e:
        logger.error("OS error reading %s: %s", filepath, e)
        return default


# Usage
content = safe_read("/etc/app/config.yaml", default="")
if not content:
    print("Using defaults — config file unavailable")


# ── Atomic write — prevent partial writes from corrupting a file ──────────────
import tempfile
import os

def atomic_write(filepath, content):
    """
    Write content to a file atomically.
    Writes to a temp file first, then renames — prevents
    partial writes if the script crashes mid-write.
    """
    dir_path = os.path.dirname(os.path.abspath(filepath))

    with tempfile.NamedTemporaryFile(
        mode="w",
        dir=dir_path,
        delete=False,
        encoding="utf-8"
    ) as tmp:
        tmp.write(content)
        tmp_path = tmp.name

    os.replace(tmp_path, filepath)   # atomic on POSIX systems
    print(f"Written: {filepath}")


atomic_write("/etc/medisync/config.yaml", yaml_content)
```

---

## 🛠️ Real DevOps Patterns

### Pattern 1 — Log Scanner and Reporter

```python
from pathlib import Path
from datetime import datetime
from collections import defaultdict
import json


def scan_logs(log_dir, output_report):
    """
    Scan all .log files in a directory.
    Count errors per service.
    Write a JSON report.
    """
    log_dir = Path(log_dir)

    if not log_dir.is_dir():
        raise NotADirectoryError(f"Not a directory: {log_dir}")

    summary = {
        "scan_time":    datetime.now().isoformat(),
        "log_dir":      str(log_dir),
        "files_scanned":0,
        "total_lines":  0,
        "error_count":  0,
        "by_level":     defaultdict(int),
        "by_file":      {},
        "critical_lines": [],
    }

    for log_file in sorted(log_dir.rglob("*.log")):
        file_errors  = 0
        file_lines   = 0

        try:
            with log_file.open("r", encoding="utf-8", errors="replace") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue

                    file_lines             += 1
                    summary["total_lines"] += 1

                    for level in ("CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG"):
                        if level in line:
                            summary["by_level"][level] += 1
                            break

                    if "ERROR" in line or "CRITICAL" in line:
                        file_errors            += 1
                        summary["error_count"] += 1

                    if "CRITICAL" in line:
                        summary["critical_lines"].append({
                            "file": log_file.name,
                            "line": line[:200],    # cap at 200 chars
                        })

        except PermissionError:
            print(f"Skipping (permission denied): {log_file}")
            continue

        summary["files_scanned"] += 1
        summary["by_file"][log_file.name] = {
            "lines":  file_lines,
            "errors": file_errors,
            "size_kb": round(log_file.stat().st_size / 1024, 1),
        }

    # Convert defaultdict to regular dict for JSON serialisation
    summary["by_level"] = dict(summary["by_level"])

    # Write report
    output_path = Path(output_report)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with output_path.open("w") as f:
        json.dump(summary, f, indent=2)

    print(f"Scanned {summary['files_scanned']} files")
    print(f"Total errors:    {summary['error_count']}")
    print(f"Critical alerts: {len(summary['critical_lines'])}")
    print(f"Report written:  {output_report}")

    return summary


scan_logs("/var/log/medisync", "/opt/reports/log_scan.json")
```

---

### Pattern 2 — Config File Manager

```python
import json
import yaml
import shutil
from pathlib import Path
from datetime import datetime


class ConfigManager:
    """
    Manage application config files safely.
    Supports JSON and YAML. Auto-backups before every write.
    """

    def __init__(self, config_path):
        self.path       = Path(config_path)
        self.backup_dir = self.path.parent / "backups"
        self.backup_dir.mkdir(exist_ok=True)

    def _detect_format(self):
        if self.path.suffix in (".yaml", ".yml"):
            return "yaml"
        elif self.path.suffix == ".json":
            return "json"
        else:
            raise ValueError(f"Unsupported format: {self.path.suffix}")

    def read(self):
        """Read and parse the config file."""
        if not self.path.exists():
            raise FileNotFoundError(f"Config not found: {self.path}")

        with self.path.open("r", encoding="utf-8") as f:
            if self._detect_format() == "yaml":
                return yaml.safe_load(f)
            else:
                return json.load(f)

    def write(self, data):
        """Write data to config file. Creates backup first."""
        self._backup()

        with self.path.open("w", encoding="utf-8") as f:
            if self._detect_format() == "yaml":
                yaml.dump(data, f, default_flow_style=False, indent=2)
            else:
                json.dump(data, f, indent=2)

        print(f"Config written: {self.path}")

    def update(self, updates):
        """Read, merge updates, and write back."""
        config = self.read()
        config.update(updates)
        self.write(config)
        return config

    def _backup(self):
        """Copy current config to backups/ with timestamp."""
        if self.path.exists():
            timestamp   = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"{self.path.stem}_{timestamp}{self.path.suffix}"
            backup_path = self.backup_dir / backup_name
            shutil.copy2(self.path, backup_path)
            print(f"Backup created: {backup_path}")

    def list_backups(self):
        """Return list of backup files sorted newest first."""
        pattern  = f"{self.path.stem}_*{self.path.suffix}"
        backups  = sorted(
            self.backup_dir.glob(pattern),
            key=lambda f: f.stat().st_mtime,
            reverse=True,
        )
        return backups

    def restore(self, backup_path):
        """Restore config from a backup file."""
        self._backup()   # backup current before restoring
        shutil.copy2(backup_path, self.path)
        print(f"Restored from: {backup_path}")


# Usage
cm = ConfigManager("/etc/medisync/config.yaml")

# Read current config
config = cm.read()
print(f"Current version: {config.get('version')}")

# Update specific keys
cm.update({"version": "v2.2.0", "replicas": 5})

# List backups
for backup in cm.list_backups():
    print(f"  {backup.name}")
```

---

### Pattern 3 — Cleanup Script

```python
from pathlib import Path
from datetime import datetime
import time
import shutil
import logging

logging.basicConfig(
    format="%(asctime)s [%(levelname)s] %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)


def cleanup_old_files(
    directory,
    pattern     = "*.log",
    max_age_days= 7,
    max_size_mb = None,
    dry_run     = False,
):
    """
    Delete files matching pattern that are older than max_age_days.
    Optionally skip files under max_size_mb.

    Args:
        directory:    Directory to clean
        pattern:      Glob pattern (default: *.log)
        max_age_days: Delete files older than this
        max_size_mb:  Only delete if file is larger than this (optional)
        dry_run:      If True, print actions without deleting

    Returns:
        dict: Summary of files deleted and space freed
    """
    dir_path = Path(directory)

    if not dir_path.is_dir():
        logger.error("Not a directory: %s", directory)
        return {}

    cutoff      = time.time() - (max_age_days * 86400)
    deleted     = []
    skipped     = []
    freed_bytes = 0

    for file in dir_path.rglob(pattern):
        if not file.is_file():
            continue

        stat    = file.stat()
        age_days= (time.time() - stat.st_mtime) / 86400

        # Skip if not old enough
        if stat.st_mtime >= cutoff:
            continue

        # Skip if below size threshold
        if max_size_mb and stat.st_size < max_size_mb * 1024 * 1024:
            skipped.append(file.name)
            continue

        if dry_run:
            logger.info("[DRY RUN] Would delete: %s (%.1f days old, %.1f MB)",
                        file.name, age_days, stat.st_size / (1024*1024))
        else:
            logger.info("Deleting: %s (%.1f days old)", file.name, age_days)
            freed_bytes += stat.st_size
            file.unlink()
            deleted.append(file.name)

    summary = {
        "deleted":    len(deleted),
        "skipped":    len(skipped),
        "freed_mb":   round(freed_bytes / (1024 * 1024), 2),
        "files":      deleted,
    }

    logger.info(
        "Cleanup complete — deleted %d files, freed %.1f MB",
        summary["deleted"], summary["freed_mb"]
    )

    return summary


# Usage
result = cleanup_old_files(
    directory    = "/var/log/medisync",
    pattern      = "*.log",
    max_age_days = 14,
    dry_run      = True,    # test first
)

# Run for real
result = cleanup_old_files(
    directory    = "/var/log/medisync",
    pattern      = "*.log",
    max_age_days = 14,
    max_size_mb  = 10,      # only delete files over 10MB
    dry_run      = False,
)
```

---

## 📌 Quick Reference Cheatsheet

### Reading

```python
# Entire file
with open("file.txt", "r") as f:
    content = f.read()          # one big string

# All lines as list
with open("file.txt", "r") as f:
    lines = f.readlines()       # ["line1\n", "line2\n"]

# Line by line — most memory-efficient
with open("file.txt", "r") as f:
    for line in f:
        process(line.strip())

# One line at a time manually
with open("file.txt", "r") as f:
    line = f.readline()         # moves pointer forward each call
```

### Writing

```python
# Write (overwrite)
with open("file.txt", "w") as f:
    f.write("content\n")

# Write multiple lines
with open("file.txt", "w") as f:
    f.writelines(["line1\n", "line2\n"])

# Append
with open("file.txt", "a") as f:
    f.write("new line\n")

# print() to file
with open("file.txt", "w") as f:
    print("content", file=f)   # auto-adds \n
```

### pathlib

```python
from pathlib import Path

p = Path("/var/log/app.log")

p.exists()              # True/False
p.is_file()             # True/False
p.is_dir()              # True/False

p.name                  # "app.log"
p.stem                  # "app"
p.suffix                # ".log"
p.parent                # Path("/var/log")

p.read_text()           # read entire file
p.write_text("...")     # write entire file
p.unlink()              # delete file

p.mkdir(parents=True, exist_ok=True)   # create dir
p.stat().st_size        # file size in bytes
p.stat().st_mtime       # last modified timestamp

Path("/var") / "log" / "app.log"       # join with /
list(Path(".").glob("*.yaml"))          # find files
list(Path(".").rglob("*.log"))          # recursive find
```

### Structured Formats

```python
# JSON
import json
with open("f.json") as f: data = json.load(f)       # read
with open("f.json", "w") as f: json.dump(data, f, indent=2)  # write
json.loads(string)           # string → dict
json.dumps(data, indent=2)   # dict → string

# YAML
import yaml
with open("f.yaml") as f: data = yaml.safe_load(f)  # read
with open("f.yaml", "w") as f: yaml.dump(data, f, default_flow_style=False)  # write

# CSV
import csv
with open("f.csv") as f: reader = csv.DictReader(f)  # read as dicts
with open("f.csv", "w") as f:                         # write
    w = csv.DictWriter(f, fieldnames=["a","b"])
    w.writeheader()
    w.writerows(rows)
```

### shutil

```python
import shutil

shutil.copy("src", "dst")           # copy file
shutil.copy2("src", "dst")          # copy with metadata
shutil.copytree("src_dir", "dst_dir")  # copy directory
shutil.move("src", "dst")           # move file or dir
shutil.rmtree("dir")                # delete directory recursively
shutil.disk_usage("/")              # (total, used, free) in bytes
shutil.make_archive("out", "gztar", "dir")  # create .tar.gz
shutil.unpack_archive("file.tar.gz", "dst") # extract
```

---

| Task | Use |
|---|---|
| Read entire small file | `path.read_text()` or `f.read()` |
| Read large file efficiently | `for line in f:` — line by line |
| Write/overwrite a file | `open("f", "w")` + `f.write()` |
| Add to end of file (logs) | `open("f", "a")` + `f.write()` |
| Create only if not exists | `open("f", "x")` |
| Work with paths | `pathlib.Path` — always prefer over `os.path` |
| Find files by pattern | `Path.glob()` or `Path.rglob()` |
| Copy / move / delete dirs | `shutil.copy()`, `shutil.move()`, `shutil.rmtree()` |
| Read/write JSON | `json.load()` / `json.dump()` |
| Read/write YAML | `yaml.safe_load()` / `yaml.dump()` |
| Read/write CSV | `csv.DictReader` / `csv.DictWriter` |
| Temp files for processing | `tempfile.NamedTemporaryFile()` |
| Prevent partial writes | Atomic write — write to temp, then `os.replace()` |
| Check file age | `Path.stat().st_mtime` + `time.time()` |

---

*Last updated: 2026 · Python 3.11+ · DevOps track*
