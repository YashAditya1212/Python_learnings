# 🐍 Python for DevOps — Lists, Tuples & Dictionaries

> **Scope:** Lists · Tuples · Dictionaries · Differences · Use Cases
> **Style:** Real-world DevOps examples · Beginner-friendly · GitHub-ready

---

## 📑 Table of Contents

- [Lists](#-lists)
  - [Creating Lists](#creating-lists)
  - [Accessing Elements](#accessing-elements)
  - [Slicing](#slicing)
  - [Modifying Lists](#modifying-lists)
  - [List Methods](#list-methods)
  - [Iterating Lists](#iterating-lists)
  - [List Comprehension](#list-comprehension)
- [Tuples](#-tuples)
  - [Creating Tuples](#creating-tuples)
  - [Accessing Elements](#accessing-tuple-elements)
  - [Tuple Methods](#tuple-methods)
  - [Tuple Unpacking](#tuple-unpacking)
  - [Named Tuples](#named-tuples)
- [Dictionaries](#-dictionaries)
  - [Creating Dictionaries](#creating-dictionaries)
  - [Accessing Values](#accessing-values)
  - [Modifying Dictionaries](#modifying-dictionaries)
  - [Dictionary Methods](#dictionary-methods)
  - [Iterating Dictionaries](#iterating-dictionaries)
  - [Nested Dictionaries](#nested-dictionaries)
  - [Dict Comprehension](#dict-comprehension)
- [Differences & When to Use Which](#-differences--when-to-use-which)
- [Real DevOps Patterns](#-real-devops-patterns)
- [Quick Reference Cheatsheet](#-quick-reference-cheatsheet)

---

## 📋 Lists

A list is an **ordered, mutable** collection.
- **Ordered** — items stay in the order you put them
- **Mutable** — you can add, remove, and change items after creation
- **Allows duplicates** — same value can appear multiple times
- **Mixed types** — can hold strings, integers, dicts, even other lists

---

### Creating Lists

```python
# Empty list
servers = []
servers = list()

# List of strings
servers = ["web-01", "web-02", "web-03"]

# List of integers
ports = [22, 80, 443, 8080, 8443]

# Mixed types — valid but avoid unless needed
mixed = ["web-01", 8080, True, None]

# List of dicts — very common in DevOps
instances = [
    {"id": "i-0abc123", "state": "running",  "type": "t3.medium"},
    {"id": "i-0def456", "state": "stopped",  "type": "t3.small"},
    {"id": "i-0ghi789", "state": "running",  "type": "t3.large"},
]

# list() from another iterable
open_ports = list(range(8000, 8010))   # [8000, 8001, ..., 8009]
log_chars  = list("ERROR")             # ['E', 'R', 'R', 'O', 'R']
```

---

### Accessing Elements

```python
servers = ["web-01", "web-02", "web-03", "web-04", "web-05"]

# Positive index — from the front (starts at 0)
servers[0]    # "web-01"  — first
servers[1]    # "web-02"  — second
servers[4]    # "web-05"  — fifth

# Negative index — from the back
servers[-1]   # "web-05"  — last
servers[-2]   # "web-04"  — second from last

# Length
len(servers)  # 5


# ── DevOps use cases ──────────────────────────────────────────────────────────

log_lines = [
    "INFO:  service started",
    "ERROR: connection refused",
    "ERROR: timeout exceeded",
    "INFO:  retrying...",
]

first_line = log_lines[0]    # "INFO:  service started"
last_line  = log_lines[-1]   # "INFO:  retrying..."

# Check if list has items before accessing
if log_lines:
    print(f"First log: {log_lines[0]}")
    print(f"Last log:  {log_lines[-1]}")
```

---

### Slicing

Slicing extracts a **portion** of a list. Syntax: `list[start:stop:step]`
- `start` — index to begin from (inclusive, default 0)
- `stop`  — index to stop at (exclusive, default end)
- `step`  — how many to skip (default 1)

```python
servers = ["web-01", "web-02", "web-03", "web-04", "web-05"]

servers[1:3]    # ["web-02", "web-03"]  — index 1 and 2 (stop=3 excluded)
servers[:3]     # ["web-01", "web-02", "web-03"]  — first 3
servers[2:]     # ["web-03", "web-04", "web-05"]  — from index 2 to end
servers[-2:]    # ["web-04", "web-05"]  — last 2
servers[::2]    # ["web-01", "web-03", "web-05"]  — every other one
servers[::-1]   # ["web-05", "web-04", "web-03", "web-02", "web-01"]  — reversed


# ── DevOps use cases ──────────────────────────────────────────────────────────

# Get the last 100 lines of a log file (like tail -n 100)
with open("/var/log/app.log") as f:
    all_lines = f.readlines()

last_100 = all_lines[-100:]


# Process logs in batches of 50
batch_size = 50
for i in range(0, len(all_lines), batch_size):
    batch = all_lines[i : i + batch_size]
    upload_batch_to_s3(batch)


# Get all servers except the primary (index 0)
all_servers = ["primary-db", "replica-1", "replica-2", "replica-3"]
replicas    = all_servers[1:]   # ["replica-1", "replica-2", "replica-3"]


# Preview first 5 items without processing all
first_five = instances[:5]
print(f"Showing {len(first_five)} of {len(instances)} instances")
```

---

### Modifying Lists

```python
servers = ["web-01", "web-02", "web-03"]

# ── Add items ─────────────────────────────────────────────────────────────────
servers.append("web-04")            # add one item to the END
# ["web-01", "web-02", "web-03", "web-04"]

servers.insert(0, "web-00")         # insert at specific index
# ["web-00", "web-01", "web-02", "web-03", "web-04"]

servers.extend(["web-05", "web-06"])# add multiple items from another list
# ["web-00", ..., "web-04", "web-05", "web-06"]

combined = servers + ["web-07"]     # merge two lists into a new one (doesn't modify original)


# ── Remove items ──────────────────────────────────────────────────────────────
servers.remove("web-00")            # remove by VALUE — raises ValueError if not found
popped  = servers.pop()             # remove and return LAST item
popped  = servers.pop(1)            # remove and return item at index 1
del servers[0]                      # delete by index — no return value
servers.clear()                     # remove ALL items


# ── Update items ──────────────────────────────────────────────────────────────
servers = ["web-01", "web-02", "web-03"]
servers[1] = "web-02-new"           # replace by index
# ["web-01", "web-02-new", "web-03"]


# ── DevOps use cases ──────────────────────────────────────────────────────────

# Build a list of failed servers dynamically
failed_servers = []

for server in all_servers:
    if not ping(server):
        failed_servers.append(server)   # collect failures

print(f"Failed servers: {failed_servers}")


# Remove a decommissioned server from rotation
active_servers = ["web-01", "web-02", "web-03", "web-04"]

decommissioned = "web-02"
if decommissioned in active_servers:           # check before removing
    active_servers.remove(decommissioned)


# Pop the next task from a queue
task_queue = ["backup-db", "sync-s3", "restart-nginx", "check-ssl"]
next_task  = task_queue.pop(0)    # "backup-db" — process first item
print(f"Running: {next_task}")
print(f"Remaining: {task_queue}")
```

---

### List Methods

```python
servers   = ["web-03", "web-01", "web-02", "web-01"]
log_lines = ["ERROR: timeout", "INFO: started", "ERROR: refused"]


# ── Searching ─────────────────────────────────────────────────────────────────
"web-01" in servers           # True  — membership check
servers.index("web-01")       # 1     — first occurrence index (raises ValueError if missing)
servers.count("web-01")       # 2     — how many times it appears


# ── Sorting ───────────────────────────────────────────────────────────────────
servers.sort()                # sort IN PLACE — modifies original list (ascending)
servers.sort(reverse=True)    # sort descending IN PLACE

sorted_servers = sorted(servers)          # returns NEW sorted list — original unchanged
sorted_servers = sorted(servers, reverse=True)

# Sort by a specific field — sort instances by instance type
instances.sort(key=lambda i: i["type"])

# Sort log entries by timestamp (assuming format "2024-01-15 10:30:00 MESSAGE")
log_lines.sort(key=lambda line: line[:19])   # sort by first 19 chars (timestamp)


# ── Reversing ─────────────────────────────────────────────────────────────────
servers.reverse()             # reverse IN PLACE
servers[::-1]                 # reversed copy — original unchanged


# ── Copying ───────────────────────────────────────────────────────────────────
original = ["web-01", "web-02", "web-03"]

# Shallow copy — new list, same string objects (safe for simple values)
copy_1 = original.copy()
copy_2 = original[:]
copy_3 = list(original)

# Why copy matters
a = ["web-01", "web-02"]
b = a           # NOT a copy — b points to the SAME list
b.append("web-03")
print(a)        # ["web-01", "web-02", "web-03"] — a was also modified!

a = ["web-01", "web-02"]
b = a.copy()    # proper copy
b.append("web-03")
print(a)        # ["web-01", "web-02"] — a is untouched


# ── Other useful methods ──────────────────────────────────────────────────────
ports = [443, 80, 8080, 22, 443, 8080]

len(ports)      # 6    — number of items
min(ports)      # 22   — smallest value
max(ports)      # 8080 — largest value
sum(ports)      # 9556 — total (useful for summing file sizes, counts)
```

---

### Iterating Lists

```python
servers = ["web-01", "web-02", "web-03"]


# ── Basic for loop ────────────────────────────────────────────────────────────
for server in servers:
    print(f"Checking {server}...")


# ── enumerate — when you need the index too ───────────────────────────────────
for index, server in enumerate(servers):
    print(f"{index + 1}. {server}")
# 1. web-01
# 2. web-02
# 3. web-03


# ── zip — iterate two lists in parallel ──────────────────────────────────────
ips      = ["10.0.0.1", "10.0.0.2", "10.0.0.3"]
hostnames= ["web-01",   "web-02",   "web-03"]

for ip, hostname in zip(ips, hostnames):
    print(f"{hostname} → {ip}")
# web-01 → 10.0.0.1
# web-02 → 10.0.0.2
# web-03 → 10.0.0.3


# ── Filtering with conditions ─────────────────────────────────────────────────
instances = [
    {"id": "i-001", "state": "running"},
    {"id": "i-002", "state": "stopped"},
    {"id": "i-003", "state": "running"},
]

# Collect only running instances
running = []
for inst in instances:
    if inst["state"] == "running":
        running.append(inst)


# ── any() and all() — check conditions across the whole list ─────────────────
statuses = [True, True, False, True]

any(statuses)   # True  — at least one is True
all(statuses)   # False — not all are True

# Are ANY servers down?
server_health = [check_health(s) for s in servers]
if not all(server_health):
    print("WARNING: Some servers are unhealthy")

# Are ALL tests passing?
test_results = [run_test(t) for t in test_suite]
if all(test_results):
    deploy()
```

---

### List Comprehension

A concise one-line way to create a list from another iterable.
Syntax: `[expression for item in iterable if condition]`

```python
# ── Basic — transform every item ─────────────────────────────────────────────
servers = ["web-01", "web-02", "web-03"]

# Without comprehension
upper_servers = []
for s in servers:
    upper_servers.append(s.upper())

# With comprehension — same result, one line
upper_servers = [s.upper() for s in servers]
# ["WEB-01", "WEB-02", "WEB-03"]


# ── With filter — transform only matching items ───────────────────────────────
log_lines = [
    "INFO:  service started",
    "ERROR: connection refused",
    "INFO:  health check ok",
    "ERROR: timeout exceeded",
]

# Extract only error lines
errors = [line for line in log_lines if "ERROR" in line]
# ["ERROR: connection refused", "ERROR: timeout exceeded"]

# Extract error messages (strip the "ERROR: " prefix)
messages = [line.replace("ERROR: ", "") for line in log_lines if "ERROR" in line]
# ["connection refused", "timeout exceeded"]


# ── Real DevOps examples ──────────────────────────────────────────────────────

# Get IDs of all running instances
instances = [
    {"id": "i-001", "state": "running"},
    {"id": "i-002", "state": "stopped"},
    {"id": "i-003", "state": "running"},
]
running_ids = [i["id"] for i in instances if i["state"] == "running"]
# ["i-001", "i-003"]


# Build Docker image tags from a list of versions
versions  = ["1.0.0", "1.1.0", "2.0.0"]
image_tag = [f"medisync:{v}" for v in versions]
# ["medisync:1.0.0", "medisync:1.1.0", "medisync:2.0.0"]


# Filter ports above 1024 (non-privileged)
all_ports     = [22, 80, 443, 3000, 5432, 8080, 9090]
app_ports     = [p for p in all_ports if p > 1024]
# [3000, 5432, 8080, 9090]


# Extract unique log levels from a log file
import re
lines      = open("/var/log/app.log").readlines()
levels     = [line.split()[1] for line in lines if len(line.split()) > 1]
# ["INFO", "ERROR", "WARNING", "INFO", ...]

unique_levels = list(set(levels))   # set removes duplicates
# ["INFO", "ERROR", "WARNING"]


# Flatten list of lists — all ports from all servers
server_ports = [[80, 443], [8080, 8443], [22, 9090]]
all_ports    = [port for server in server_ports for port in server]
# [80, 443, 8080, 8443, 22, 9090]
```

---

## 🔒 Tuples

A tuple is an **ordered, immutable** collection.
- **Ordered** — items stay in the order you put them
- **Immutable** — cannot be changed after creation (no add/remove/modify)
- **Allows duplicates** — same value can appear multiple times
- **Faster** than lists — less memory, faster iteration

---

### Creating Tuples

```python
# Empty tuple
empty = ()
empty = tuple()

# Single item — the trailing comma is REQUIRED
single = ("web-01",)    # tuple
not_tuple = ("web-01")  # just a string — no comma = not a tuple!

# Multiple items — parentheses optional but recommended for clarity
server = ("web-01", "10.0.0.1", 8080)
server = "web-01", "10.0.0.1", 8080    # same result — parentheses optional

# Common DevOps tuples
aws_regions   = ("us-east-1", "ap-south-1", "eu-west-1")
http_methods  = ("GET", "POST", "PUT", "DELETE", "PATCH")
valid_envs    = ("dev", "staging", "production")
log_levels    = ("DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL")

# Convert a list to tuple
ports_list  = [22, 80, 443]
ports_tuple = tuple(ports_list)   # (22, 80, 443)
```

---

### Accessing Tuple Elements

Exactly like lists — same index and slicing syntax.

```python
server = ("web-01", "10.0.0.1", 8080, "running")

server[0]     # "web-01"    — first
server[-1]    # "running"   — last
server[1:3]   # ("10.0.0.1", 8080)  — slice
len(server)   # 4

# Membership
"web-01" in server    # True
9090    in server     # False
```

---

### Tuple Methods

Tuples have only two methods — they're immutable so most list methods don't apply.

```python
regions = ("us-east-1", "ap-south-1", "us-east-1", "eu-west-1")

regions.count("us-east-1")   # 2 — how many times it appears
regions.index("ap-south-1")  # 1 — first occurrence index

# Tuples support all read operations
len(regions)                  # 4
min(regions)                  # "ap-south-1" (alphabetical)
max(regions)                  # "us-west-2"
sorted(regions)               # returns a new sorted LIST (not tuple)
```

---

### Tuple Unpacking

Assign each element of a tuple to a separate variable in one line.
This is where tuples truly shine in DevOps scripts.

```python
# ── Basic unpacking ───────────────────────────────────────────────────────────
server = ("web-01", "10.0.0.1", 8080)

hostname, ip, port = server   # unpack all three
print(hostname)   # "web-01"
print(ip)         # "10.0.0.1"
print(port)       # 8080


# ── Swap two variables — no temp variable needed ──────────────────────────────
primary  = "db-01"
standby  = "db-02"

primary, standby = standby, primary   # swap in one line
print(primary)   # "db-02"
print(standby)   # "db-01"


# ── Unpack function return values ─────────────────────────────────────────────
def check_server(host):
    """Returns (is_up, response_time_ms, status_code)."""
    # ...
    return True, 42, 200

is_up, response_ms, status = check_server("10.0.0.5")

if is_up:
    print(f"Up — {response_ms}ms — HTTP {status}")


# ── * operator — capture remaining items ─────────────────────────────────────
servers = ("primary", "replica-1", "replica-2", "replica-3")

primary, *replicas = servers
print(primary)    # "primary"
print(replicas)   # ["replica-1", "replica-2", "replica-3"]

first, *middle, last = servers
print(first)      # "primary"
print(middle)     # ["replica-1", "replica-2"]
print(last)       # "replica-3"


# ── Unpack in loops — iterate list of tuples ──────────────────────────────────
server_list = [
    ("web-01", "10.0.0.1", 8080),
    ("web-02", "10.0.0.2", 8080),
    ("web-03", "10.0.0.3", 9090),
]

for hostname, ip, port in server_list:
    print(f"Checking {hostname} at {ip}:{port}")


# ── Ignore values with _ ──────────────────────────────────────────────────────
server = ("web-01", "10.0.0.1", 8080, "us-east-1", "running")

hostname, _, port, *_ = server   # only care about name and port
print(f"Connecting to {hostname} on port {port}")
```

---

### Named Tuples

A named tuple gives **names** to each position — making code more readable
than accessing `server[0]`, `server[1]` etc.

```python
from collections import namedtuple

# Define a named tuple type
Server   = namedtuple("Server",   ["hostname", "ip", "port", "state"])
Instance = namedtuple("Instance", ["id", "type", "region", "state"])

# Create instances
web01 = Server(hostname="web-01", ip="10.0.0.1", port=8080, state="running")
ec2   = Instance(id="i-0abc123", type="t3.medium", region="ap-south-1", state="running")

# Access by name — much clearer than [0], [1], [2]
print(web01.hostname)   # "web-01"
print(web01.port)       # 8080
print(ec2.region)       # "ap-south-1"

# Still works as a regular tuple
hostname, ip, port, state = web01   # unpacking works
web01[0]                            # "web-01" — index access works

# Immutable like a regular tuple
web01.port = 9090   # AttributeError — cannot modify


# ── Real use — parsing log lines ─────────────────────────────────────────────
LogEntry = namedtuple("LogEntry", ["timestamp", "level", "service", "message"])

def parse_log_line(line):
    # "2024-01-15 10:30:00 ERROR nginx connection refused"
    parts = line.strip().split(" ", 4)
    return LogEntry(
        timestamp = f"{parts[0]} {parts[1]}",
        level     = parts[2],
        service   = parts[3],
        message   = parts[4],
    )

entry = parse_log_line("2024-01-15 10:30:00 ERROR nginx connection refused")

print(entry.level)     # "ERROR"
print(entry.service)   # "nginx"
print(entry.message)   # "connection refused"

# Filter only errors — readable
if entry.level == "ERROR":
    send_slack_alert(f"[{entry.service}] {entry.message}")
```

---

## 📚 Dictionaries

A dictionary is an **unordered, mutable** collection of **key-value pairs**.
- **Key-value pairs** — every item has a name (key) and a value
- **Keys are unique** — no duplicate keys allowed (value is overwritten)
- **Mutable** — add, remove, and update after creation
- **Ordered by insertion** — since Python 3.7, maintains insertion order

---

### Creating Dictionaries

```python
# Empty dict
config = {}
config = dict()

# Direct definition
server = {
    "hostname": "web-01",
    "ip":       "10.0.0.1",
    "port":     8080,
    "running":  True,
    "tags":     ["web", "nginx", "production"],
}

# dict() constructor
config = dict(host="localhost", port=5432, name="medisync_db")

# From two lists using zip
keys   = ["host", "port", "user"]
values = ["localhost", 5432, "admin"]
config = dict(zip(keys, values))
# {"host": "localhost", "port": 5432, "user": "admin"}

# From list of tuples
env_vars = [("DB_HOST", "localhost"), ("DB_PORT", "5432")]
config   = dict(env_vars)

# Keys can be strings, integers, or tuples — not lists
valid_keys   = {"name": "web", 8080: "http-alt", ("us", "east"): "region"}
invalid_keys = {["list", "key"]: "value"}   # TypeError — lists are not hashable
```

---

### Accessing Values

```python
config = {
    "host":     "prod-db.internal",
    "port":     5432,
    "db_name":  "medisync",
    "user":     "admin",
    "ssl":      True,
}

# ── Direct access — raises KeyError if key missing ────────────────────────────
config["host"]       # "prod-db.internal"
config["port"]       # 5432

config["password"]   # KeyError — key doesn't exist!

# ── .get() — safe access, returns None or default if missing ─────────────────
config.get("host")              # "prod-db.internal"
config.get("password")          # None — no error
config.get("password", "")      # "" — custom default
config.get("timeout", 30)       # 30 — default if not in config
config.get("ssl", False)        # True — found in dict, returns actual value

# ── Check key exists before accessing ────────────────────────────────────────
if "host" in config:
    print(f"Connecting to {config['host']}")

if "password" not in config:
    print("WARNING: No password set — using passwordless auth")


# ── Nested access ─────────────────────────────────────────────────────────────
server = {
    "name": "web-01",
    "network": {
        "ip":      "10.0.0.1",
        "subnet":  "10.0.0.0/24",
        "gateway": "10.0.0.254",
    },
    "ports": [80, 443, 8080],
}

server["network"]["ip"]       # "10.0.0.1"
server["ports"][0]            # 80

# Safe nested access — avoid KeyError at each level
ip = server.get("network", {}).get("ip", "unknown")
# If "network" key missing, get({}) returns {}, then .get("ip") returns "unknown"
```

---

### Modifying Dictionaries

```python
config = {"host": "localhost", "port": 5432}

# ── Add or update ─────────────────────────────────────────────────────────────
config["db_name"] = "medisync"      # add new key
config["port"]    = 5433            # update existing key (overwritten)

# .update() — add/overwrite multiple keys at once
config.update({"user": "admin", "ssl": True})
config.update(user="admin", ssl=True)   # keyword syntax


# ── Remove items ──────────────────────────────────────────────────────────────
del config["ssl"]                   # delete key — KeyError if missing

value = config.pop("port")          # remove and return value — KeyError if missing
value = config.pop("port", None)    # safe pop — returns None if missing

config.clear()                      # remove ALL keys


# ── setdefault — add key only if it doesn't already exist ────────────────────
config = {"host": "localhost"}

config.setdefault("port",    5432)   # adds port=5432 — key was missing
config.setdefault("host", "remote")  # does NOT change host — key already exists

print(config)   # {"host": "localhost", "port": 5432}


# ── DevOps use cases ──────────────────────────────────────────────────────────

# Build a tags dict for an EC2 instance
tags = {}
tags["Name"]        = "medisync-api"
tags["Environment"] = "production"
tags["ManagedBy"]   = "terraform"
tags["Project"]     = "medisync"

# Merge two dicts — Python 3.9+ uses | operator
base_tags  = {"Project": "medisync", "ManagedBy": "terraform"}
extra_tags = {"Environment": "prod",  "Owner": "devops-team"}

all_tags = base_tags | extra_tags      # Python 3.9+
all_tags = {**base_tags, **extra_tags} # Works on Python 3.5+
# {"Project": "medisync", "ManagedBy": "terraform",
#  "Environment": "prod", "Owner": "devops-team"}

# If same key in both, the RIGHT dict wins
{"port": 80} | {"port": 443}   # {"port": 443}
```

---

### Dictionary Methods

```python
config = {
    "host":    "localhost",
    "port":    5432,
    "db_name": "medisync",
    "user":    "admin",
    "ssl":     True,
}

# ── View objects — live windows into the dict ─────────────────────────────────
config.keys()     # dict_keys(["host", "port", "db_name", "user", "ssl"])
config.values()   # dict_values(["localhost", 5432, "medisync", "admin", True])
config.items()    # dict_items([("host", "localhost"), ("port", 5432), ...])

# Convert to list if you need list operations
list(config.keys())     # ["host", "port", "db_name", "user", "ssl"]
list(config.values())   # ["localhost", 5432, "medisync", "admin", True]


# ── Check membership — always checks KEYS ────────────────────────────────────
"host"     in config    # True
"password" in config    # False
"password" not in config# True

# Check VALUES — use .values()
"localhost" in config.values()   # True
5433        in config.values()   # False


# ── Copy ──────────────────────────────────────────────────────────────────────
copy_1 = config.copy()      # shallow copy
copy_2 = dict(config)       # also shallow copy

import copy
deep = copy.deepcopy(config) # deep copy — needed if dict contains dicts/lists


# ── fromkeys — create a dict with default values ─────────────────────────────
servers    = ["web-01", "web-02", "web-03"]
health_map = dict.fromkeys(servers, "unknown")
# {"web-01": "unknown", "web-02": "unknown", "web-03": "unknown"}

# Then update as you check
health_map["web-01"] = "healthy"
health_map["web-02"] = "unhealthy"
```

---

### Iterating Dictionaries

```python
config = {"host": "localhost", "port": 5432, "db_name": "medisync"}


# ── Iterate keys (default) ────────────────────────────────────────────────────
for key in config:
    print(key)
# host
# port
# db_name


# ── Iterate values ────────────────────────────────────────────────────────────
for value in config.values():
    print(value)
# localhost
# 5432
# medisync


# ── Iterate key-value pairs — most common ────────────────────────────────────
for key, value in config.items():
    print(f"{key} = {value}")
# host = localhost
# port = 5432
# db_name = medisync


# ── DevOps use cases ──────────────────────────────────────────────────────────

# Print all environment variables that start with DB_
import os
for key, value in os.environ.items():
    if key.startswith("DB_"):
        print(f"{key} = {value}")


# Validate all required config keys have non-empty values
required_keys = ["host", "port", "db_name", "user"]

for key in required_keys:
    if not config.get(key):
        print(f"ERROR: Config key '{key}' is missing or empty")


# Build AWS tags list format from a plain dict
tags_dict = {"Environment": "prod", "Project": "medisync", "Owner": "devops"}

aws_tags  = [{"Key": k, "Value": v} for k, v in tags_dict.items()]
# [{"Key": "Environment", "Value": "prod"}, ...]


# Count occurrences — frequency map of log levels
log_lines  = ["ERROR: ...", "INFO: ...", "ERROR: ...", "WARNING: ...", "INFO: ..."]
level_count = {}

for line in log_lines:
    level = line.split(":")[0]
    level_count[level] = level_count.get(level, 0) + 1
    # level_count.get(level, 0) returns 0 if level not yet seen

print(level_count)   # {"ERROR": 2, "INFO": 2, "WARNING": 1}

# Cleaner way using setdefault
for line in log_lines:
    level = line.split(":")[0]
    level_count.setdefault(level, 0)
    level_count[level] += 1
```

---

### Nested Dictionaries

Dicts inside dicts — extremely common when working with AWS API responses,
Kubernetes manifests, and JSON config files.

```python
# ── Server inventory ──────────────────────────────────────────────────────────
inventory = {
    "web-01": {
        "ip":    "10.0.0.1",
        "port":  8080,
        "tags":  ["nginx", "production"],
        "health": {"status": "healthy", "last_check": "2024-01-15 10:30:00"},
    },
    "web-02": {
        "ip":    "10.0.0.2",
        "port":  8080,
        "tags":  ["nginx", "production"],
        "health": {"status": "unhealthy", "last_check": "2024-01-15 10:31:00"},
    },
}

# Access nested values
inventory["web-01"]["ip"]                    # "10.0.0.1"
inventory["web-01"]["health"]["status"]      # "healthy"
inventory["web-01"]["tags"][0]               # "nginx"

# Safe nested access using .get() chaining
status = inventory.get("web-03", {}).get("health", {}).get("status", "unknown")
# "unknown" — web-03 doesn't exist, no KeyError

# Iterate and check health
for server, details in inventory.items():
    status = details["health"]["status"]
    if status != "healthy":
        print(f"ALERT: {server} is {status}")


# ── K8s-style manifest as nested dict ────────────────────────────────────────
deployment = {
    "apiVersion": "apps/v1",
    "kind":       "Deployment",
    "metadata": {
        "name":      "medisync-api",
        "namespace": "production",
        "labels":    {"app": "medisync", "version": "v2.1.0"},
    },
    "spec": {
        "replicas": 3,
        "selector": {"matchLabels": {"app": "medisync"}},
        "template": {
            "spec": {
                "containers": [
                    {
                        "name":  "api",
                        "image": "medisync:v2.1.0",
                        "ports": [{"containerPort": 8080}],
                    }
                ]
            }
        },
    },
}

# Navigate deep structures
name      = deployment["metadata"]["name"]          # "medisync-api"
replicas  = deployment["spec"]["replicas"]          # 3
image     = deployment["spec"]["template"]["spec"]["containers"][0]["image"]
# "medisync:v2.1.0"

# Update a nested value
deployment["spec"]["replicas"] = 5
deployment["metadata"]["labels"]["version"] = "v2.2.0"
```

---

### Dict Comprehension

Build a dictionary in one line — same idea as list comprehension.
Syntax: `{key_expr: value_expr for item in iterable if condition}`

```python
# ── Basic ─────────────────────────────────────────────────────────────────────
servers = ["web-01", "web-02", "web-03"]

# Map each server to a default status
status_map = {server: "unknown" for server in servers}
# {"web-01": "unknown", "web-02": "unknown", "web-03": "unknown"}


# ── With condition ────────────────────────────────────────────────────────────
instances = [
    {"id": "i-001", "state": "running",  "type": "t3.medium"},
    {"id": "i-002", "state": "stopped",  "type": "t3.small"},
    {"id": "i-003", "state": "running",  "type": "t3.large"},
]

# Map ID → type for only running instances
running_map = {
    i["id"]: i["type"]
    for i in instances
    if i["state"] == "running"
}
# {"i-001": "t3.medium", "i-003": "t3.large"}


# ── Transform keys or values ──────────────────────────────────────────────────
env_vars = {"db_host": "localhost", "db_port": "5432", "log_level": "info"}

# Uppercase all keys
upper_env = {k.upper(): v for k, v in env_vars.items()}
# {"DB_HOST": "localhost", "DB_PORT": "5432", "LOG_LEVEL": "info"}

# Uppercase keys AND values
upper_all = {k.upper(): v.upper() for k, v in env_vars.items()}


# ── Invert a dict — swap keys and values ─────────────────────────────────────
port_service = {80: "http", 443: "https", 22: "ssh", 5432: "postgres"}

service_port = {v: k for k, v in port_service.items()}
# {"http": 80, "https": 443, "ssh": 22, "postgres": 5432}

print(service_port["https"])   # 443


# ── Filter a dict ─────────────────────────────────────────────────────────────
all_config = {
    "DB_HOST":     "localhost",
    "DB_PORT":     "5432",
    "LOG_LEVEL":   "INFO",
    "APP_ENV":     "production",
    "SECRET_KEY":  "abc123",
}

# Extract only DB-related config
db_config = {k: v for k, v in all_config.items() if k.startswith("DB_")}
# {"DB_HOST": "localhost", "DB_PORT": "5432"}
```

---

## ⚖️ Differences & When to Use Which

### Side-by-Side Comparison

```
┌─────────────────┬──────────────────┬──────────────────┬──────────────────────┐
│   Property      │      List        │      Tuple       │     Dictionary       │
├─────────────────┼──────────────────┼──────────────────┼──────────────────────┤
│ Syntax          │ [a, b, c]        │ (a, b, c)        │ {"k": v, "k2": v2}   │
│ Ordered         │ ✓ Yes            │ ✓ Yes            │ ✓ Yes (Python 3.7+)  │
│ Mutable         │ ✓ Yes            │ ✗ No             │ ✓ Yes                │
│ Duplicates      │ ✓ Allowed        │ ✓ Allowed        │ Keys: No, Values: Yes│
│ Access by       │ Index [0]        │ Index [0]        │ Key ["name"]         │
│ Use for         │ Collections      │ Fixed records    │ Labelled data        │
│ Speed           │ Moderate         │ Fastest          │ Fast (O(1) lookup)   │
│ Memory          │ More             │ Less             │ More                 │
│ Hashable        │ ✗ No             │ ✓ Yes            │ ✗ No                 │
│ Can be dict key │ ✗ No             │ ✓ Yes            │ ✗ No                 │
└─────────────────┴──────────────────┴──────────────────┴──────────────────────┘
```

---

### When to Use Each

#### ✅ Use a List when:

```python
# 1 — Collection that changes over time
active_servers = ["web-01", "web-02"]
active_servers.append("web-03")    # grows
active_servers.remove("web-01")    # shrinks

# 2 — Order matters and may be re-sorted
task_queue = ["backup", "deploy", "test", "notify"]
task_queue.sort()

# 3 — You need to iterate and collect results
failed = [s for s in servers if not ping(s)]

# 4 — Duplicate values are meaningful
log_levels = ["ERROR", "INFO", "ERROR", "ERROR", "INFO"]
error_count = log_levels.count("ERROR")   # 3 — duplicates matter here
```

#### ✅ Use a Tuple when:

```python
# 1 — Fixed, unchanging data — constants in your script
VALID_ENVS   = ("dev", "staging", "production")   # never changes
HTTP_METHODS = ("GET", "POST", "PUT", "DELETE")

if env not in VALID_ENVS:
    raise ValueError(f"Invalid env: {env}")


# 2 — Returning multiple values from a function
def get_server_info(hostname):
    return hostname, "10.0.0.1", 8080   # returns a tuple

host, ip, port = get_server_info("web-01")   # unpack cleanly


# 3 — As a dictionary key (lists cannot be dict keys)
location_config = {
    ("us-east-1", "production"): {"replicas": 5, "instance": "c5.2xlarge"},
    ("ap-south-1", "staging"):   {"replicas": 2, "instance": "t3.medium"},
}
config = location_config[("ap-south-1", "staging")]


# 4 — Structured records with fixed fields
ServerRecord = namedtuple("ServerRecord", ["hostname", "ip", "port"])
web01 = ServerRecord("web-01", "10.0.0.1", 8080)
print(web01.hostname)   # clear and readable
```

#### ✅ Use a Dictionary when:

```python
# 1 — Data has meaningful labels (key-value structure)
instance = {
    "id":     "i-0abc123",
    "type":   "t3.medium",
    "region": "ap-south-1",
    "state":  "running",
}
print(instance["state"])   # "running" — clear what you're accessing


# 2 — Fast lookups by key — O(1) — not O(n) like searching a list
port_to_service = {22: "ssh", 80: "http", 443: "https", 5432: "postgres"}
print(port_to_service[443])    # instant lookup — no loop needed


# 3 — Counting / grouping
level_counts = {}
for line in log_lines:
    level = line.split(":")[0]
    level_counts[level] = level_counts.get(level, 0) + 1


# 4 — Config and settings — anywhere you'd use a .env or yaml file
db_config = {
    "host":     os.environ.get("DB_HOST", "localhost"),
    "port":     int(os.environ.get("DB_PORT", "5432")),
    "name":     os.environ.get("DB_NAME", "medisync"),
    "user":     os.environ.get("DB_USER", "admin"),
    "password": os.environ.get("DB_PASSWORD"),
}


# 5 — JSON API responses — already come as dicts
response = requests.get("https://api.github.com/repos/org/repo").json()
stars    = response["stargazers_count"]
language = response["language"]
```

---

### Common Mistake — List vs Tuple

```python
# ── Mistake: using a list for constants ───────────────────────────────────────
# Bad — list signals "this will change"
VALID_ENVS = ["dev", "staging", "production"]

# Good — tuple signals "this is fixed"
VALID_ENVS = ("dev", "staging", "production")


# ── Mistake: using a list as a dict key ───────────────────────────────────────
# Bad — TypeError: unhashable type: 'list'
cache = {["us-east-1", "prod"]: "value"}

# Good — tuple is hashable, can be a key
cache = {("us-east-1", "prod"): "value"}


# ── Mistake: accessing dict without .get() ────────────────────────────────────
# Bad — crashes if "timeout" key missing
timeout = config["timeout"]

# Good — safe with default
timeout = config.get("timeout", 30)


# ── Mistake: searching a list for O(n) lookups ───────────────────────────────
# Bad — O(n) search every time
critical_servers = ["web-01", "db-primary", "api-gateway"]
if "db-primary" in critical_servers:    # searches linearly

# Good — O(1) lookup with a set
critical_servers = {"web-01", "db-primary", "api-gateway"}   # set, not list
if "db-primary" in critical_servers:    # instant hash lookup
```

---

## 🛠️ Real DevOps Patterns

### Pattern 1 — Server Inventory Manager

```python
def build_server_inventory(raw_instances):
    """
    Convert a raw AWS API response into a clean inventory dict.
    Key: instance_id, Value: structured server info dict.
    """
    inventory = {}

    for reservation in raw_instances["Reservations"]:
        for inst in reservation["Instances"]:

            # Get name from tags (list of dicts)
            name = next(
                (t["Value"] for t in inst.get("Tags", []) if t["Key"] == "Name"),
                inst["InstanceId"]   # fallback to ID if no Name tag
            )

            inventory[inst["InstanceId"]] = {
                "name":       name,
                "type":       inst["InstanceType"],
                "state":      inst["State"]["Name"],
                "private_ip": inst.get("PrivateIpAddress", "N/A"),
                "public_ip":  inst.get("PublicIpAddress",  "N/A"),
                "az":         inst["Placement"]["AvailabilityZone"],
                "tags":       {t["Key"]: t["Value"] for t in inst.get("Tags", [])},
            }

    return inventory


def find_stopped_instances(inventory):
    """Return list of (id, name) tuples for all stopped instances."""
    return [
        (inst_id, details["name"])
        for inst_id, details in inventory.items()
        if details["state"] == "stopped"
    ]


def get_instances_by_env(inventory, env):
    """Return dict of instances filtered by Environment tag."""
    return {
        inst_id: details
        for inst_id, details in inventory.items()
        if details["tags"].get("Environment") == env
    }


# Usage
import boto3
ec2 = boto3.client("ec2", region_name="ap-south-1")
raw = ec2.describe_instances()

inventory = build_server_inventory(raw)
stopped   = find_stopped_instances(inventory)
prod_only = get_instances_by_env(inventory, "production")

print(f"Total instances:      {len(inventory)}")
print(f"Stopped instances:    {len(stopped)}")
print(f"Production instances: {len(prod_only)}")

for inst_id, name in stopped:
    print(f"  Stopped: {name} ({inst_id})")
```

---

### Pattern 2 — Log Analyser

```python
from collections import defaultdict
from pathlib import Path

def analyse_logs(log_file_path):
    """
    Parse a log file and return structured analysis.

    Returns a dict with:
      - level_counts: how many lines per level
      - errors:       list of error messages
      - services:     dict of service → error count
    """
    lines = Path(log_file_path).read_text().splitlines()

    # defaultdict — like a dict but auto-creates missing keys
    level_counts  = defaultdict(int)     # missing key returns 0
    service_errors= defaultdict(int)
    errors        = []

    for line in lines:
        if not line.strip():
            continue

        parts = line.split(" ", 4)
        if len(parts) < 4:
            continue

        # Unpack with tuple unpacking
        timestamp, time_, level, service, *message_parts = parts
        message = message_parts[0] if message_parts else ""

        level_counts[level] += 1     # auto-initialised to 0

        if level in ("ERROR", "CRITICAL"):
            errors.append({
                "timestamp": f"{timestamp} {time_}",
                "level":     level,
                "service":   service,
                "message":   message,
            })
            service_errors[service] += 1

    return {
        "total_lines":    len(lines),
        "level_counts":   dict(level_counts),
        "error_count":    len(errors),
        "errors":         errors[-10:],   # last 10 errors
        "services":       dict(service_errors),
        "top_offender":   max(service_errors, key=service_errors.get)
                          if service_errors else None,
    }


# Usage
result = analyse_logs("/var/log/medisync/app.log")

print(f"Total lines:   {result['total_lines']}")
print(f"Error count:   {result['error_count']}")
print(f"Top offender:  {result['top_offender']}")
print(f"Level summary: {result['level_counts']}")
```

---

### Pattern 3 — Config Merger (Dev/Staging/Prod)

```python
def get_config(env):
    """
    Return merged config for a given environment.
    Base config is overridden by environment-specific values.
    """

    # Immutable base — use dict for named access, tuple for fixed options
    BASE_CONFIG = {
        "app_name":   "medisync",
        "log_level":  "INFO",
        "timeout":    30,
        "retries":    3,
        "db_port":    5432,
        "replicas":   2,
    }

    # Environment overrides — only what changes
    ENV_OVERRIDES = {
        "dev": {
            "log_level":  "DEBUG",
            "db_host":    "localhost",
            "replicas":   1,
            "debug":      True,
        },
        "staging": {
            "log_level":  "INFO",
            "db_host":    "staging-db.internal",
            "replicas":   2,
            "debug":      False,
        },
        "production": {
            "log_level":  "WARNING",
            "db_host":    "prod-db.internal",
            "replicas":   5,
            "debug":      False,
            "timeout":    60,    # longer timeout in prod
            "retries":    5,
        },
    }

    VALID_ENVS = ("dev", "staging", "production")   # tuple — fixed constants

    if env not in VALID_ENVS:
        raise ValueError(f"Invalid environment: {env}. Choose from {VALID_ENVS}")

    # Merge: base + env overrides (env wins on conflict)
    config = {**BASE_CONFIG, **ENV_OVERRIDES[env]}

    # Inject secrets from environment variables — never hardcode
    config["db_password"] = os.environ.get("DB_PASSWORD")
    config["api_key"]     = os.environ.get("API_KEY")

    return config


# Usage
import os
config = get_config("production")

print(f"App:      {config['app_name']}")
print(f"DB Host:  {config['db_host']}")
print(f"Replicas: {config['replicas']}")
print(f"Log:      {config['log_level']}")
```

---

## 📌 Quick Reference Cheatsheet

### Lists

```python
# Create
servers = ["web-01", "web-02"]
servers = list()

# Access
servers[0]       # first
servers[-1]      # last
servers[1:3]     # slice
len(servers)     # length

# Modify
servers.append("web-03")          # add to end
servers.insert(0, "web-00")       # add at index
servers.extend(["web-04", "web-05"]) # add multiple
servers.remove("web-00")          # remove by value
servers.pop()                     # remove last, return it
servers.pop(0)                    # remove by index, return it
servers[1] = "web-02-new"         # update

# Info
"web-01" in servers               # membership
servers.index("web-01")           # find index
servers.count("web-01")           # count occurrences

# Operations
servers.sort()                    # sort in place
sorted(servers)                   # new sorted list
servers.reverse()                 # reverse in place
servers.copy()                    # shallow copy

# Comprehension
errors = [l for l in lines if "ERROR" in l]
```

### Tuples

```python
# Create
region = ("us-east-1", "ap-south-1")
single = ("only-one",)    # trailing comma required for single item

# Access — same as list
region[0]        # "us-east-1"
region[-1]       # "ap-south-1"

# Methods
region.count("us-east-1")   # occurrences
region.index("ap-south-1")  # find index

# Unpack
host, ip, port = ("web-01", "10.0.0.1", 8080)
first, *rest   = ("web-01", "web-02", "web-03")

# Use as dict key
cache = {("us-east-1", "prod"): config}
```

### Dictionaries

```python
# Create
config = {"host": "localhost", "port": 5432}
config = dict(host="localhost", port=5432)

# Access
config["host"]                  # direct — KeyError if missing
config.get("host")              # safe — None if missing
config.get("host", "fallback")  # safe with default

# Modify
config["key"]   = "value"       # add or update
config.update({"a": 1, "b": 2}) # update multiple
del config["key"]               # delete — KeyError if missing
config.pop("key", None)         # safe delete

# Info
config.keys()                   # all keys
config.values()                 # all values
config.items()                  # key-value pairs
"key" in config                 # check key exists

# Merge
merged = base | override        # Python 3.9+
merged = {**base, **override}   # Python 3.5+

# Comprehension
upper = {k.upper(): v for k, v in config.items()}
```

---

| When you need... | Use |
|---|---|
| Ordered, changeable collection | **List** |
| Fixed constants that never change | **Tuple** |
| Labelled data / named access | **Dictionary** |
| Return multiple values from function | **Tuple** |
| Fast key-based lookup | **Dictionary** |
| Collect matching items in a loop | **List** |
| Dict key that's a multi-part key | **Tuple** |
| Count occurrences of items | **Dictionary** (with `.get(k, 0) + 1`) |
| Membership check with performance | **Set** (then convert to list if needed) |

---

*Last updated: 2026 · Python 3.11+ · DevOps track*
