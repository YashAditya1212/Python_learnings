# 🐍 Python for DevOps — boto3

> **Scope:** What is boto3 · Why boto3 over CLI/Terraform · Setup · Core Concepts · Service Examples · Project: Lambda Snapshot Cleanup
> **Style:** Real-world DevOps examples · Beginner-friendly · GitHub-ready

---

## 📑 Table of Contents

- [What is boto3](#-what-is-boto3)
- [Why boto3 — The Gaps it Fills](#-why-boto3--the-gaps-it-fills)
  - [AWS CLI vs boto3 vs Terraform](#aws-cli-vs-boto3-vs-terraform)
  - [What CLI Cannot Do](#what-cli-cannot-do)
  - [What Terraform Cannot Do](#what-terraform-cannot-do)
  - [What boto3 Does Best](#what-boto3-does-best)
- [Setup and Authentication](#-setup-and-authentication)
  - [Installing boto3](#installing-boto3)
  - [Authentication Methods](#authentication-methods)
  - [client vs resource](#client-vs-resource)
- [EC2 — Instances](#-ec2--instances)
- [EC2 — Volumes and Snapshots](#-ec2--volumes-and-snapshots)
- [S3 — Storage](#-s3--storage)
- [IAM — Identity](#-iam--identity)
- [CloudWatch — Monitoring](#-cloudwatch--monitoring)
- [Lambda — Functions](#-lambda--functions)
- [SSM — Parameter Store](#-ssm--parameter-store)
- [SNS — Notifications](#-sns--notifications)
- [Paginators](#-paginators--never-miss-results)
- [Waiters](#-waiters--wait-for-state-changes)
- [Error Handling](#-error-handling)
- [🚀 PROJECT — Lambda Snapshot Cleanup](#-project--lambda-snapshot-cleanup)
- [Quick Reference Cheatsheet](#-quick-reference-cheatsheet)

---

## 🤔 What is boto3

**boto3** is the official **AWS SDK for Python**. It lets you talk to every
AWS service — EC2, S3, IAM, Lambda, CloudWatch, RDS, EKS, and 200+ more —
directly from Python code.

```
Your Python Script
      ↓
   boto3 SDK
      ↓
AWS REST API (HTTPS)
      ↓
  AWS Services
(EC2, S3, IAM...)
```

```bash
pip install boto3
```

```python
import boto3

# That's it — you now have programmatic access to all of AWS
ec2 = boto3.client("ec2", region_name="ap-south-1")
```

> **Think of it this way:**
> The AWS Console is for humans clicking buttons.
> The AWS CLI is for humans typing commands.
> **boto3 is for code making decisions and taking actions automatically.**

---

## 🎯 Why boto3 — The Gaps it Fills

### AWS CLI vs boto3 vs Terraform

```
┌──────────────┬──────────────────────┬──────────────────────┬─────────────────────┐
│  Feature     │     AWS CLI          │     Terraform        │      boto3          │
├──────────────┼──────────────────────┼──────────────────────┼─────────────────────┤
│ Language     │ Shell commands       │ HCL config files     │ Python code         │
│ Purpose      │ One-off commands     │ Provision infra      │ Automate & logic    │
│ State        │ No state tracking    │ Tracks state file    │ No state tracking   │
│ Logic        │ Minimal (shell if)   │ Limited (count/for)  │ Full Python logic   │
│ Conditions   │ Shell conditionals   │ Conditional resources│ if/elif/for/while   │
│ Error handle │ Exit codes only      │ Plan/apply model     │ try/except, retry   │
│ Scheduling   │ With cron only       │ Not designed for it  │ Lambda + EventBridge│
│ Reactions    │ Not real-time        │ Not real-time        │ Responds to events  │
│ Data process │ Needs jq/awk         │ Very limited         │ Full Python stdlib  │
│ API results  │ JSON strings         │ Not accessible       │ Native Python dicts │
│ Best for     │ Quick manual tasks   │ Infra as code        │ Automation & logic  │
└──────────────┴──────────────────────┴──────────────────────┴─────────────────────┘
```

---

### What CLI Cannot Do

```bash
# CLI can list instances — but logic is extremely painful
aws ec2 describe-instances \
  --filters "Name=instance-state-name,Values=running" \
  --query "Reservations[].Instances[].InstanceId" \
  --output text | while read id; do
    # now what? complex logic in bash is ugly and error-prone
    echo $id
done

# What if you need to:
# - Check CPU utilisation from CloudWatch for EACH instance?
# - Compare launch time with a date 90 days ago?
# - Cross-reference with a list from a database?
# - Send a Slack message with a formatted table?
# - Retry if an API call fails?
# CLI becomes a mess of pipes, awk, and shell hacks
```

```python
# boto3 handles all of that cleanly
import boto3
from datetime import datetime, timezone, timedelta

ec2 = boto3.client("ec2")
cw  = boto3.client("cloudwatch")

instances = ec2.describe_instances(
    Filters=[{"Name": "instance-state-name", "Values": ["running"]}]
)

for r in instances["Reservations"]:
    for inst in r["Instances"]:
        instance_id  = inst["InstanceId"]
        launch_time  = inst["LaunchTime"]
        age_days     = (datetime.now(timezone.utc) - launch_time).days

        # Get CPU from CloudWatch — impossible cleanly in CLI
        cpu = get_average_cpu(cw, instance_id)

        if age_days > 90 and cpu < 5:
            print(f"IDLE: {instance_id} — {age_days} days old, {cpu}% CPU")
            # tag it, stop it, send a Slack alert — all in the same script
```

---

### What Terraform Cannot Do

```hcl
# Terraform is declarative — it describes WHAT should exist
# It cannot react to runtime conditions or events

# Terraform CAN:
resource "aws_instance" "web" {
  ami           = "ami-0abcdef1234567890"
  instance_type = "t3.medium"
}

# Terraform CANNOT:
# - "Delete all snapshots older than 30 days"           ← needs date logic
# - "Stop EC2 instances with CPU < 5% for 7 days"       ← needs CloudWatch data
# - "Send a Slack alert when disk > 85%"                ← needs event response
# - "Rotate IAM keys older than 90 days"                ← needs date comparison
# - "Resize an RDS instance if connections > 1000"      ← needs metric data
# - "Retry a failed deployment 3 times with backoff"    ← needs retry logic

# These are OPERATIONAL tasks — Terraform handles PROVISIONING
# boto3 handles OPERATIONS
```

---

### What boto3 Does Best

```
boto3 fills the gap between "infrastructure exists" and "infrastructure is managed"

Provisioning (Terraform)          Operations (boto3)
        ↓                                 ↓
   Create EC2             →     Monitor, scale, clean up, respond
   Create S3              →     Upload, download, lifecycle, alerts
   Create Lambda          →     Trigger, monitor, update code
   Create CloudWatch      →     Query metrics, set alarms, react
```

**Real situations where only boto3 works:**

```
✅  Scheduled cleanup — delete snapshots > 30 days old at midnight
✅  Event-driven — Lambda triggered when S3 file lands, processes it
✅  Conditional logic — stop dev instances after 6PM based on tags
✅  Cross-service data — query CloudWatch, compare, update DynamoDB
✅  Dynamic infrastructure — auto-scale based on custom business metrics
✅  Audit scripts — scan 500 IAM users, report non-compliant ones
✅  DR automation — detect AZ failure, reroute traffic, notify team
✅  Cost control — find and delete unused EBS volumes, EIPs, old AMIs
```

---

## 🔧 Setup and Authentication

### Installing boto3

```bash
pip install boto3

# With specific version (recommended for production)
pip install boto3==1.34.0

# Verify
python3 -c "import boto3; print(boto3.__version__)"
```

---

### Authentication Methods

boto3 checks for credentials in this order. First match wins.

```
1. Explicit in code (NEVER do this — keys end up in git)
2. Environment variables  ← good for CI/CD pipelines
3. AWS credentials file   ← good for local dev
4. IAM Instance Profile   ← best for EC2 instances
5. IAM Role for ECS/Lambda← best for containers and functions
```

```python
# ── Method 1: NEVER hardcode keys ────────────────────────────────────────────
# BAD — keys in source code get committed to git
ec2 = boto3.client(
    "ec2",
    aws_access_key_id     = "AKIAIOSFODNN7EXAMPLE",   # ← NEVER DO THIS
    aws_secret_access_key = "wJalrXUtnFEMI/K7MDENG"  # ← NEVER DO THIS
)


# ── Method 2: Environment variables ── for CI/CD pipelines ───────────────────
# Set in GitHub Actions secrets or pipeline config:
# AWS_ACCESS_KEY_ID=AKIA...
# AWS_SECRET_ACCESS_KEY=...
# AWS_DEFAULT_REGION=ap-south-1

# boto3 picks them up automatically — no code changes needed
ec2 = boto3.client("ec2")


# ── Method 3: AWS credentials file ── for local development ──────────────────
# ~/.aws/credentials
# [default]
# aws_access_key_id = AKIA...
# aws_secret_access_key = ...
#
# [production]
# aws_access_key_id = AKIA...
# aws_secret_access_key = ...

# Use default profile
ec2 = boto3.client("ec2")

# Use a specific named profile
session = boto3.Session(profile_name="production")
ec2     = session.client("ec2", region_name="ap-south-1")


# ── Method 4: IAM Instance Profile ── for EC2 instances ──────────────────────
# Attach an IAM role to your EC2 instance in the console or Terraform
# boto3 automatically uses the instance metadata service — no config needed
ec2 = boto3.client("ec2")   # just works on EC2 with an attached role


# ── Method 5: IAM Role ── for Lambda functions ────────────────────────────────
# Lambda execution role is attached in the function config
# boto3 automatically picks it up inside Lambda — no config needed
def lambda_handler(event, context):
    ec2 = boto3.client("ec2")   # uses Lambda execution role automatically


# ── Assume a role ── cross-account access ────────────────────────────────────
sts    = boto3.client("sts")
assumed= sts.assume_role(
    RoleArn         = "arn:aws:iam::123456789:role/CrossAccountRole",
    RoleSessionName = "my-session"
)

creds  = assumed["Credentials"]
ec2    = boto3.client(
    "ec2",
    aws_access_key_id     = creds["AccessKeyId"],
    aws_secret_access_key = creds["SecretAccessKey"],
    aws_session_token     = creds["SessionToken"],
)
```

---

### client vs resource

boto3 has two interfaces. Know when to use each.

```python
# ── client — low-level, mirrors AWS API exactly ───────────────────────────────
# Returns raw JSON-like dicts
# All AWS services have a client
# More verbose but more complete

ec2_client = boto3.client("ec2", region_name="ap-south-1")

response   = ec2_client.describe_instances()
# Returns: {"Reservations": [{"Instances": [{"InstanceId": "i-...", ...}]}]}
# You navigate the raw API response structure


# ── resource — high-level, object-oriented ────────────────────────────────────
# Returns Python objects with attributes and methods
# Only available for some services: EC2, S3, IAM, DynamoDB, SQS, SNS
# More readable for simple tasks

ec2_resource = boto3.resource("ec2", region_name="ap-south-1")

for instance in ec2_resource.instances.all():
    print(instance.instance_id)     # attribute access — cleaner
    print(instance.state["Name"])
    instance.stop()                 # method call directly on object


# ── When to use which ────────────────────────────────────────────────────────

# Use client when:
# - Service has no resource interface (Lambda, CloudWatch, SSM, RDS)
# - You need full control of the API parameters
# - Working with filters, paginators, waiters

# Use resource when:
# - Available for the service (EC2, S3, IAM)
# - Performing simple object-level operations
# - Code readability matters more than raw control

# ── Both for the same service ────────────────────────────────────────────────
session      = boto3.Session(region_name="ap-south-1")
ec2_client   = session.client("ec2")    # for describe/filter operations
ec2_resource = session.resource("ec2")  # for object-level operations
```

---

## 💻 EC2 — Instances

```python
import boto3
from datetime import datetime, timezone

ec2 = boto3.client("ec2", region_name="ap-south-1")


# ── List all instances ────────────────────────────────────────────────────────
response = ec2.describe_instances()

for reservation in response["Reservations"]:
    for inst in reservation["Instances"]:
        name = next(
            (t["Value"] for t in inst.get("Tags", []) if t["Key"] == "Name"),
            "unnamed"
        )
        print(f"{inst['InstanceId']}  {inst['InstanceType']}  "
              f"{inst['State']['Name']}  {name}")


# ── Filter instances by state and tag ────────────────────────────────────────
response = ec2.describe_instances(
    Filters=[
        {"Name": "instance-state-name",  "Values": ["running"]},
        {"Name": "tag:Environment",      "Values": ["production"]},
        {"Name": "instance-type",        "Values": ["t3.micro", "t3.small"]},
    ]
)


# ── Start and stop instances ──────────────────────────────────────────────────
ec2.start_instances(InstanceIds=["i-0abc123def456789a"])
ec2.stop_instances( InstanceIds=["i-0abc123def456789a"])

# Stop multiple at once
ec2.stop_instances(
    InstanceIds=["i-0abc123", "i-0def456", "i-0ghi789"]
)


# ── Tag an instance ───────────────────────────────────────────────────────────
ec2.create_tags(
    Resources=["i-0abc123def456789a"],
    Tags=[
        {"Key": "Environment", "Value": "staging"},
        {"Key": "ManagedBy",   "Value": "boto3-script"},
        {"Key": "StopAfter",   "Value": "2024-01-31"},
    ]
)


# ── Get instance age and flag old dev instances ───────────────────────────────
response = ec2.describe_instances(
    Filters=[
        {"Name": "instance-state-name", "Values": ["running"]},
        {"Name": "tag:Environment",     "Values": ["dev"]},
    ]
)

old_instances = []

for r in response["Reservations"]:
    for inst in r["Instances"]:
        launch_time = inst["LaunchTime"]   # already a datetime object
        age_days    = (datetime.now(timezone.utc) - launch_time).days

        name = next(
            (t["Value"] for t in inst.get("Tags", []) if t["Key"] == "Name"),
            inst["InstanceId"]
        )

        if age_days > 7:
            old_instances.append({
                "id":       inst["InstanceId"],
                "name":     name,
                "age_days": age_days,
                "type":     inst["InstanceType"],
            })

print(f"Dev instances running over 7 days: {len(old_instances)}")
for inst in old_instances:
    print(f"  {inst['name']} ({inst['id']}) — {inst['age_days']} days old")
```

---

## 💾 EC2 — Volumes and Snapshots

```python
ec2 = boto3.client("ec2", region_name="ap-south-1")


# ── List all EBS volumes ──────────────────────────────────────────────────────
volumes = ec2.describe_volumes()

for vol in volumes["Volumes"]:
    state      = vol["State"]             # available, in-use
    size_gb    = vol["Size"]
    vol_type   = vol["VolumeType"]        # gp3, io2, etc.
    attachments= vol["Attachments"]

    if attachments:
        instance_id = attachments[0]["InstanceId"]
        print(f"{vol['VolumeId']}  {size_gb}GB  attached to {instance_id}")
    else:
        print(f"{vol['VolumeId']}  {size_gb}GB  UNATTACHED ← candidate for deletion")


# ── Find unattached volumes — cost saving ────────────────────────────────────
unattached = ec2.describe_volumes(
    Filters=[{"Name": "status", "Values": ["available"]}]
)

total_gb = sum(v["Size"] for v in unattached["Volumes"])
print(f"Unattached volumes: {len(unattached['Volumes'])} ({total_gb} GB)")


# ── Create a snapshot ────────────────────────────────────────────────────────
response = ec2.create_snapshot(
    VolumeId    = "vol-0abc123def456789a",
    Description = "Pre-deployment backup — medisync api — 2024-01-15",
    TagSpecifications=[{
        "ResourceType": "snapshot",
        "Tags": [
            {"Key": "Name",        "Value": "medisync-api-backup"},
            {"Key": "Environment", "Value": "production"},
            {"Key": "CreatedBy",   "Value": "boto3-backup-script"},
        ]
    }]
)
snapshot_id = response["SnapshotId"]
print(f"Snapshot created: {snapshot_id}")


# ── List all snapshots owned by your account ─────────────────────────────────
snapshots = ec2.describe_snapshots(OwnerIds=["self"])

for snap in snapshots["Snapshots"]:
    age_days = (datetime.now(timezone.utc) - snap["StartTime"]).days
    name     = next(
        (t["Value"] for t in snap.get("Tags", []) if t["Key"] == "Name"),
        "unnamed"
    )
    print(f"{snap['SnapshotId']}  {snap['VolumeId']}  "
          f"{snap['VolumeSize']}GB  {age_days} days old  {name}")


# ── Delete a snapshot ────────────────────────────────────────────────────────
ec2.delete_snapshot(SnapshotId="snap-0abc123def456789a")
print("Snapshot deleted")
```

---

## 🪣 S3 — Storage

```python
import boto3
import os

s3 = boto3.client("s3", region_name="ap-south-1")


# ── List buckets ──────────────────────────────────────────────────────────────
response = s3.list_buckets()
for bucket in response["Buckets"]:
    print(f"{bucket['Name']}  created: {bucket['CreationDate'].date()}")


# ── Create a bucket ───────────────────────────────────────────────────────────
s3.create_bucket(
    Bucket                    = "medisync-backups-prod",
    CreateBucketConfiguration = {"LocationConstraint": "ap-south-1"},
)
# Note: us-east-1 does NOT use CreateBucketConfiguration


# ── Upload a file ─────────────────────────────────────────────────────────────
s3.upload_file(
    Filename = "/var/log/app.log",         # local file path
    Bucket   = "medisync-backups-prod",    # S3 bucket name
    Key      = "logs/2024-01-15/app.log",  # S3 object key (path inside bucket)
)

# Upload with metadata
s3.upload_file(
    Filename    = "/backup/db.tar.gz",
    Bucket      = "medisync-backups-prod",
    Key         = "db/backup-2024-01-15.tar.gz",
    ExtraArgs   = {
        "ServerSideEncryption": "AES256",
        "Metadata": {
            "uploaded-by": "backup-script",
            "environment": "production",
        }
    }
)


# ── Download a file ───────────────────────────────────────────────────────────
s3.download_file(
    Bucket   = "medisync-backups-prod",
    Key      = "logs/2024-01-15/app.log",
    Filename = "/tmp/restored_app.log",
)


# ── List objects in a bucket ──────────────────────────────────────────────────
response = s3.list_objects_v2(
    Bucket = "medisync-backups-prod",
    Prefix = "logs/2024-01-15/",       # filter by prefix (like a folder)
)

for obj in response.get("Contents", []):
    size_kb = obj["Size"] / 1024
    print(f"{obj['Key']}  {size_kb:.1f} KB  {obj['LastModified'].date()}")


# ── Delete an object ──────────────────────────────────────────────────────────
s3.delete_object(
    Bucket = "medisync-backups-prod",
    Key    = "logs/2024-01-14/app.log",
)

# Delete multiple objects at once (more efficient)
s3.delete_objects(
    Bucket = "medisync-backups-prod",
    Delete = {
        "Objects": [
            {"Key": "logs/2024-01-10/app.log"},
            {"Key": "logs/2024-01-11/app.log"},
            {"Key": "logs/2024-01-12/app.log"},
        ]
    }
)


# ── Generate a presigned URL — temporary access link ─────────────────────────
url = s3.generate_presigned_url(
    ClientMethod = "get_object",
    Params       = {
        "Bucket": "medisync-backups-prod",
        "Key":    "reports/health_report.pdf",
    },
    ExpiresIn    = 3600,    # URL valid for 1 hour
)
print(f"Share this URL (expires in 1 hour):\n{url}")


# ── Check if an object exists ─────────────────────────────────────────────────
def s3_object_exists(bucket, key):
    try:
        s3.head_object(Bucket=bucket, Key=key)
        return True
    except s3.exceptions.ClientError as e:
        if e.response["Error"]["Code"] == "404":
            return False
        raise   # re-raise unexpected errors


if s3_object_exists("medisync-backups-prod", "config/app.yaml"):
    print("Config exists in S3")
```

---

## 🔐 IAM — Identity

```python
iam = boto3.client("iam")


# ── List all IAM users ────────────────────────────────────────────────────────
response = iam.list_users()

for user in response["Users"]:
    print(f"{user['UserName']}  created: {user['CreateDate'].date()}")


# ── Check last login — find inactive users ───────────────────────────────────
from datetime import datetime, timezone, timedelta

response   = iam.list_users()
cutoff     = datetime.now(timezone.utc) - timedelta(days=90)
inactive   = []

for user in response["Users"]:
    username = user["UserName"]

    try:
        login_profile = iam.get_login_profile(UserName=username)
        # Has console access — check last login
        password_last  = user.get("PasswordLastUsed")

        if password_last and password_last < cutoff:
            inactive.append(username)
        elif not password_last:
            inactive.append(username)   # never logged in

    except iam.exceptions.NoSuchEntityException:
        pass   # no console access — skip

print(f"Inactive users (90+ days): {inactive}")


# ── List attached policies for a user ────────────────────────────────────────
response = iam.list_attached_user_policies(UserName="rahul-dev")
for policy in response["AttachedPolicies"]:
    print(f"  {policy['PolicyName']}")


# ── Create an IAM role (for a Lambda function) ───────────────────────────────
import json

trust_policy = {
    "Version": "2012-10-17",
    "Statement": [{
        "Effect":    "Allow",
        "Principal": {"Service": "lambda.amazonaws.com"},
        "Action":    "sts:AssumeRole",
    }]
}

response = iam.create_role(
    RoleName                 = "medisync-lambda-snapshot-cleanup",
    AssumeRolePolicyDocument = json.dumps(trust_policy),
    Description              = "Role for snapshot cleanup Lambda function",
)

role_arn = response["Role"]["Arn"]
print(f"Role created: {role_arn}")

# Attach managed policy
iam.attach_role_policy(
    RoleName  = "medisync-lambda-snapshot-cleanup",
    PolicyArn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole",
)
```

---

## 📊 CloudWatch — Monitoring

```python
from datetime import datetime, timezone, timedelta

cw = boto3.client("cloudwatch", region_name="ap-south-1")


# ── Get CPU utilisation for an EC2 instance ───────────────────────────────────
response = cw.get_metric_statistics(
    Namespace  = "AWS/EC2",
    MetricName = "CPUUtilization",
    Dimensions = [{"Name": "InstanceId", "Value": "i-0abc123def456789a"}],
    StartTime  = datetime.now(timezone.utc) - timedelta(hours=1),
    EndTime    = datetime.now(timezone.utc),
    Period     = 300,           # 5-minute intervals
    Statistics = ["Average"],
)

if response["Datapoints"]:
    avg_cpu = sum(d["Average"] for d in response["Datapoints"]) / len(response["Datapoints"])
    print(f"Average CPU (last 1hr): {avg_cpu:.1f}%")
else:
    print("No CPU data — instance may be stopped")


# ── Put a custom metric ───────────────────────────────────────────────────────
# Push your own application metrics to CloudWatch
cw.put_metric_data(
    Namespace  = "MediSync/Application",
    MetricData = [
        {
            "MetricName": "ActiveUsers",
            "Value":      142,
            "Unit":       "Count",
            "Dimensions": [
                {"Name": "Environment", "Value": "production"},
                {"Name": "Service",     "Value": "api"},
            ]
        },
        {
            "MetricName": "RequestLatencyMs",
            "Value":      87.3,
            "Unit":       "Milliseconds",
        }
    ]
)


# ── Create a CloudWatch alarm ─────────────────────────────────────────────────
cw.put_metric_alarm(
    AlarmName          = "medisync-api-high-cpu",
    AlarmDescription   = "Alert when API server CPU exceeds 85%",
    MetricName         = "CPUUtilization",
    Namespace          = "AWS/EC2",
    Dimensions         = [{"Name": "InstanceId", "Value": "i-0abc123"}],
    Statistic          = "Average",
    Period             = 300,
    EvaluationPeriods  = 2,          # must breach for 2 consecutive periods
    Threshold          = 85.0,
    ComparisonOperator = "GreaterThanThreshold",
    AlarmActions       = ["arn:aws:sns:ap-south-1:123456789:devops-alerts"],
    TreatMissingData   = "notBreaching",
)
print("Alarm created")
```

---

## ⚡ Lambda — Functions

```python
import boto3
import json

lam = boto3.client("lambda", region_name="ap-south-1")


# ── List Lambda functions ─────────────────────────────────────────────────────
response = lam.list_functions()
for func in response["Functions"]:
    print(f"{func['FunctionName']}  "
          f"{func['Runtime']}  "
          f"{func['MemorySize']}MB  "
          f"modified: {func['LastModified'][:10]}")


# ── Invoke a Lambda function synchronously ────────────────────────────────────
response = lam.invoke(
    FunctionName   = "medisync-health-checker",
    InvocationType = "RequestResponse",      # synchronous — wait for result
    Payload        = json.dumps({
        "environment": "production",
        "check_type":  "full",
    })
)

result   = json.loads(response["Payload"].read())
status   = response["StatusCode"]            # HTTP-like: 200 = success

print(f"Lambda returned: {result}")


# ── Invoke asynchronously — fire and forget ───────────────────────────────────
lam.invoke(
    FunctionName   = "medisync-send-report",
    InvocationType = "Event",                # async — returns immediately
    Payload        = json.dumps({"report_date": "2024-01-15"}),
)
print("Report generation triggered asynchronously")


# ── Update function code ──────────────────────────────────────────────────────
with open("function.zip", "rb") as f:
    zip_bytes = f.read()

lam.update_function_code(
    FunctionName = "medisync-snapshot-cleanup",
    ZipFile      = zip_bytes,
    Publish      = True,
)
print("Lambda code updated")


# ── Update environment variables ─────────────────────────────────────────────
lam.update_function_configuration(
    FunctionName = "medisync-snapshot-cleanup",
    Environment  = {
        "Variables": {
            "RETENTION_DAYS": "30",
            "DRY_RUN":        "false",
            "SNS_TOPIC_ARN":  "arn:aws:sns:ap-south-1:123456789:devops-alerts",
        }
    },
    Timeout      = 300,     # 5 minutes
    MemorySize   = 256,
)
```

---

## 🔑 SSM — Parameter Store

```python
ssm = boto3.client("ssm", region_name="ap-south-1")


# ── Store a secret parameter ──────────────────────────────────────────────────
ssm.put_parameter(
    Name        = "/medisync/production/db_password",
    Value       = "super-secret-password-123",
    Type        = "SecureString",    # encrypted with KMS
    Overwrite   = True,
    Description = "MediSync production database password",
)


# ── Read a parameter ──────────────────────────────────────────────────────────
response = ssm.get_parameter(
    Name            = "/medisync/production/db_password",
    WithDecryption  = True,    # decrypt SecureString
)
db_password = response["Parameter"]["Value"]


# ── Read multiple parameters at once ─────────────────────────────────────────
response = ssm.get_parameters(
    Names           = [
        "/medisync/production/db_host",
        "/medisync/production/db_port",
        "/medisync/production/db_password",
    ],
    WithDecryption  = True,
)

config = {p["Name"].split("/")[-1]: p["Value"] for p in response["Parameters"]}
# {"db_host": "...", "db_port": "5432", "db_password": "..."}


# ── Get all parameters under a path ──────────────────────────────────────────
response = ssm.get_parameters_by_path(
    Path            = "/medisync/production/",
    WithDecryption  = True,
    Recursive       = True,
)

for param in response["Parameters"]:
    print(f"{param['Name']} = {param['Value']}")
```

---

## 📢 SNS — Notifications

```python
sns = boto3.client("sns", region_name="ap-south-1")


# ── Publish a message to a topic ──────────────────────────────────────────────
sns.publish(
    TopicArn = "arn:aws:sns:ap-south-1:123456789012:devops-alerts",
    Subject  = "MediSync Snapshot Cleanup Complete",
    Message  = (
        "Snapshot cleanup completed.\n"
        "Deleted: 14 snapshots\n"
        "Space freed: ~280 GB\n"
        "Environment: production"
    ),
)
print("SNS notification sent")


# ── Publish with structured message (different format per protocol) ───────────
import json

message = {
    "default": "Snapshot cleanup complete — 14 snapshots deleted",
    "email":   "Dear team,\n\nSnapshot cleanup completed...\n\nRegards,\nDevOps Bot",
    "sqs":     json.dumps({"event": "snapshot_cleanup", "deleted": 14}),
}

sns.publish(
    TopicArn         = "arn:aws:sns:ap-south-1:123456789012:devops-alerts",
    MessageStructure = "json",
    Message          = json.dumps(message),
    Subject          = "Snapshot Cleanup Report",
)
```

---

## 📄 Paginators — Never Miss Results

AWS APIs return results in pages. Without paginators you only get the first
page (typically 100-1000 results). **Always use paginators** for listing operations.

```python
ec2 = boto3.client("ec2")

# ── Without paginator — WRONG — misses results beyond first page ───────────────
response  = ec2.describe_snapshots(OwnerIds=["self"])
snapshots = response["Snapshots"]   # only first page — might miss thousands!


# ── With paginator — CORRECT — gets ALL results ───────────────────────────────
paginator = ec2.get_paginator("describe_snapshots")

all_snapshots = []
for page in paginator.paginate(OwnerIds=["self"]):
    all_snapshots.extend(page["Snapshots"])

print(f"Total snapshots: {len(all_snapshots)}")


# ── With filter in the paginator ──────────────────────────────────────────────
paginator = ec2.get_paginator("describe_instances")

all_instances = []
for page in paginator.paginate(
    Filters=[{"Name": "instance-state-name", "Values": ["running"]}]
):
    for reservation in page["Reservations"]:
        all_instances.extend(reservation["Instances"])


# ── S3 paginator — for buckets with thousands of objects ─────────────────────
s3        = boto3.client("s3")
paginator = s3.get_paginator("list_objects_v2")

all_objects = []
for page in paginator.paginate(Bucket="medisync-backups-prod", Prefix="logs/"):
    all_objects.extend(page.get("Contents", []))

print(f"Total objects: {len(all_objects)}")


# ── IAM paginator — list all users ───────────────────────────────────────────
iam       = boto3.client("iam")
paginator = iam.get_paginator("list_users")

all_users = []
for page in paginator.paginate():
    all_users.extend(page["Users"])
```

---

## ⏳ Waiters — Wait for State Changes

Waiters poll AWS until a resource reaches the expected state.
Cleaner than writing your own polling loop.

```python
ec2 = boto3.client("ec2")


# ── Wait for an instance to be running ───────────────────────────────────────
print("Starting instance...")
ec2.start_instances(InstanceIds=["i-0abc123def456789a"])

waiter = ec2.get_waiter("instance_running")
waiter.wait(
    InstanceIds = ["i-0abc123def456789a"],
    WaiterConfig = {
        "Delay":       15,    # check every 15 seconds
        "MaxAttempts": 40,    # give up after 40 attempts (10 minutes)
    }
)
print("Instance is running ✓")


# ── Wait for a snapshot to complete ─────────────────────────────────────────
print("Creating snapshot...")
snap = ec2.create_snapshot(VolumeId="vol-0abc123")

waiter = ec2.get_waiter("snapshot_completed")
waiter.wait(
    SnapshotIds  = [snap["SnapshotId"]],
    WaiterConfig = {"Delay": 30, "MaxAttempts": 60},
)
print(f"Snapshot {snap['SnapshotId']} completed ✓")


# ── Available waiters for EC2 ────────────────────────────────────────────────
# instance_running, instance_stopped, instance_terminated
# snapshot_completed, image_available
# volume_available, volume_in_use, volume_deleted
# system_status_ok, instance_status_ok
```

---

## 🚨 Error Handling

```python
from botocore.exceptions import ClientError, NoCredentialsError, EndpointConnectionError


# ── ClientError — most common — returned by AWS API ──────────────────────────
def delete_snapshot(snapshot_id):
    try:
        ec2.delete_snapshot(SnapshotId=snapshot_id)
        print(f"Deleted: {snapshot_id}")

    except ClientError as e:
        error_code = e.response["Error"]["Code"]
        error_msg  = e.response["Error"]["Message"]

        if error_code == "InvalidSnapshot.InUse":
            print(f"SKIP: {snapshot_id} is currently in use")

        elif error_code == "InvalidSnapshot.NotFound":
            print(f"SKIP: {snapshot_id} does not exist")

        elif error_code == "UnauthorizedOperation":
            print(f"ERROR: No permission to delete snapshot {snapshot_id}")
            raise   # re-raise — this is a config problem, not expected

        else:
            print(f"ERROR {error_code}: {error_msg}")
            raise


# ── NoCredentialsError — no AWS credentials found ────────────────────────────
try:
    ec2 = boto3.client("ec2")
    ec2.describe_instances()

except NoCredentialsError:
    print("ERROR: No AWS credentials configured")
    print("Run 'aws configure' or set AWS_ACCESS_KEY_ID environment variable")
    sys.exit(1)


# ── EndpointConnectionError — no internet / wrong region ─────────────────────
try:
    ec2 = boto3.client("ec2", region_name="ap-south-1")
    ec2.describe_instances()

except EndpointConnectionError as e:
    print(f"ERROR: Cannot connect to AWS endpoint — {e}")


# ── Throttling — handle API rate limits with retry ───────────────────────────
import time
from botocore.exceptions import ClientError

def describe_with_retry(ec2, max_retries=5):
    for attempt in range(1, max_retries + 1):
        try:
            return ec2.describe_instances()

        except ClientError as e:
            if e.response["Error"]["Code"] in ("RequestLimitExceeded", "Throttling"):
                wait = 2 ** attempt           # exponential backoff: 2,4,8,16,32
                print(f"Throttled — retrying in {wait}s (attempt {attempt})")
                time.sleep(wait)
            else:
                raise   # not a throttling error — don't retry

    raise Exception("Max retries exceeded")
```

---

## 🚀 PROJECT — Lambda Snapshot Cleanup

### What This Does

```
EventBridge Rule (runs every Sunday at midnight)
              ↓
    Lambda Function triggered
              ↓
    1. Get all EC2 instance IDs (running + stopped)
    2. Get all EBS volume IDs attached to any instance
    3. Get ALL snapshots owned by this account
    4. For each snapshot:
         - Is the source volume NOT attached to any instance?
         - Is the snapshot older than 30 days?
         - If YES to both → DELETE IT
    5. Publish summary report to SNS
```

---

### Architecture

```
EventBridge (Cron)
      ↓  triggers
  Lambda Function
      ↓  calls
  ┌───────────────────────────────────────────┐
  │  1. ec2.describe_instances()              │
  │     → collect all attached volume IDs    │
  │                                           │
  │  2. ec2.describe_snapshots()              │
  │     → all snapshots older than 30 days   │
  │                                           │
  │  3. For each old snapshot:               │
  │     if volume NOT in attached_volumes:   │
  │         ec2.delete_snapshot()            │
  │                                           │
  │  4. sns.publish() → summary report       │
  └───────────────────────────────────────────┘
```

---

### IAM Policy Required

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "EC2ReadAccess",
      "Effect": "Allow",
      "Action": [
        "ec2:DescribeInstances",
        "ec2:DescribeVolumes",
        "ec2:DescribeSnapshots"
      ],
      "Resource": "*"
    },
    {
      "Sid": "SnapshotDeleteAccess",
      "Effect": "Allow",
      "Action": [
        "ec2:DeleteSnapshot"
      ],
      "Resource": "*"
    },
    {
      "Sid": "SNSPublishAccess",
      "Effect": "Allow",
      "Action": [
        "sns:Publish"
      ],
      "Resource": "arn:aws:sns:*:*:devops-alerts"
    },
    {
      "Sid": "LambdaLogs",
      "Effect": "Allow",
      "Action": [
        "logs:CreateLogGroup",
        "logs:CreateLogStream",
        "logs:PutLogEvents"
      ],
      "Resource": "arn:aws:logs:*:*:*"
    }
  ]
}
```

---

### Lambda Function Code

```python
"""
snapshot_cleanup.py

Lambda function that:
1. Finds all EBS volumes currently attached to EC2 instances
2. Finds all snapshots older than RETENTION_DAYS (default: 30)
3. Deletes snapshots whose source volume is NOT attached to any instance
4. Publishes a summary report to SNS

Environment Variables:
    RETENTION_DAYS  : Days to keep snapshots (default: 30)
    DRY_RUN         : "true" to simulate without deleting (default: "false")
    SNS_TOPIC_ARN   : SNS topic ARN for reports (optional)
    AWS_REGION      : AWS region (set automatically by Lambda)
"""

import boto3
import os
import logging
from datetime import datetime, timezone, timedelta
from botocore.exceptions import ClientError

# ── Logging setup ─────────────────────────────────────────────────────────────
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# ── Configuration from environment variables ──────────────────────────────────
RETENTION_DAYS = int(os.environ.get("RETENTION_DAYS", "30"))
DRY_RUN        = os.environ.get("DRY_RUN", "false").lower() == "true"
SNS_TOPIC_ARN  = os.environ.get("SNS_TOPIC_ARN", "")
REGION         = os.environ.get("AWS_REGION", "ap-south-1")


def get_attached_volume_ids(ec2_client):
    """
    Return a set of all EBS volume IDs that are currently
    attached to any EC2 instance (running OR stopped).

    We include stopped instances because their volumes
    are still "in use" — detaching and deleting snapshots
    for them could break recovery.
    """
    attached_volume_ids = set()

    paginator = ec2_client.get_paginator("describe_instances")

    # Get ALL instances — running and stopped
    for page in paginator.paginate(
        Filters=[{
            "Name":   "instance-state-name",
            "Values": ["running", "stopped", "stopping", "pending"],
        }]
    ):
        for reservation in page["Reservations"]:
            for instance in reservation["Instances"]:
                for mapping in instance.get("BlockDeviceMappings", []):
                    vol_id = mapping.get("Ebs", {}).get("VolumeId")
                    if vol_id:
                        attached_volume_ids.add(vol_id)

    logger.info("Found %d volumes attached to instances", len(attached_volume_ids))
    return attached_volume_ids


def get_old_snapshots(ec2_client, retention_days):
    """
    Return all snapshots owned by this account
    that are older than retention_days.
    """
    cutoff    = datetime.now(timezone.utc) - timedelta(days=retention_days)
    paginator = ec2_client.get_paginator("describe_snapshots")

    old_snapshots = []

    for page in paginator.paginate(OwnerIds=["self"]):
        for snap in page["Snapshots"]:
            if snap["StartTime"] < cutoff:
                old_snapshots.append(snap)

    logger.info(
        "Found %d snapshots older than %d days",
        len(old_snapshots), retention_days
    )
    return old_snapshots


def get_snapshot_name(snapshot):
    """Extract the Name tag from a snapshot, or return its ID."""
    return next(
        (t["Value"] for t in snapshot.get("Tags", []) if t["Key"] == "Name"),
        snapshot["SnapshotId"]
    )


def delete_snapshot_safe(ec2_client, snapshot_id, dry_run=False):
    """
    Delete a snapshot. Returns True on success, False on expected errors.
    Re-raises unexpected errors.
    """
    if dry_run:
        logger.info("[DRY RUN] Would delete snapshot: %s", snapshot_id)
        return True

    try:
        ec2_client.delete_snapshot(SnapshotId=snapshot_id)
        logger.info("Deleted snapshot: %s", snapshot_id)
        return True

    except ClientError as e:
        code = e.response["Error"]["Code"]

        if code == "InvalidSnapshot.InUse":
            # Snapshot is being used to create an AMI or volume — skip
            logger.warning("SKIP %s — currently in use", snapshot_id)
            return False

        elif code == "InvalidSnapshot.NotFound":
            # Already deleted (race condition) — not an error
            logger.warning("SKIP %s — not found (already deleted?)", snapshot_id)
            return False

        elif code == "UnauthorizedOperation":
            # Permission denied — this is a config problem, raise it
            logger.error("Permission denied deleting %s", snapshot_id)
            raise

        else:
            logger.error(
                "Unexpected error deleting %s: %s — %s",
                snapshot_id, code, e.response["Error"]["Message"]
            )
            raise


def publish_report(sns_client, topic_arn, report):
    """Publish the cleanup summary to SNS."""
    if not topic_arn:
        logger.info("No SNS_TOPIC_ARN set — skipping notification")
        return

    lines = [
        "EBS Snapshot Cleanup Report",
        "=" * 40,
        f"Run date:         {report['run_date']}",
        f"Region:           {report['region']}",
        f"Retention policy: {report['retention_days']} days",
        f"Dry run:          {report['dry_run']}",
        "",
        f"Snapshots scanned:   {report['total_scanned']}",
        f"Eligible for delete: {report['eligible']}",
        f"Successfully deleted:{report['deleted']}",
        f"Skipped (in use):    {report['skipped']}",
        f"Errors:              {report['errors']}",
        f"Est. space freed:    {report['freed_gb']:.1f} GB",
        "",
    ]

    if report["deleted_snapshots"]:
        lines.append("Deleted snapshots:")
        for snap in report["deleted_snapshots"][:20]:    # cap at 20 in message
            lines.append(
                f"  {snap['id']}  vol:{snap['volume_id']}  "
                f"{snap['size_gb']}GB  {snap['age_days']}d old  {snap['name']}"
            )
        if len(report["deleted_snapshots"]) > 20:
            lines.append(f"  ... and {len(report['deleted_snapshots']) - 20} more")

    message = "\n".join(lines)

    try:
        sns_client.publish(
            TopicArn = topic_arn,
            Subject  = (
                f"[{'DRY RUN ' if report['dry_run'] else ''}Snapshot Cleanup] "
                f"{report['deleted']} deleted, "
                f"{report['freed_gb']:.1f} GB freed — {report['region']}"
            ),
            Message  = message,
        )
        logger.info("SNS report published to %s", topic_arn)

    except ClientError as e:
        logger.error("Failed to publish SNS report: %s", e)


# ── Main Lambda handler ────────────────────────────────────────────────────────

def lambda_handler(event, context):
    """
    Main entry point for the Lambda function.

    event: dict passed by EventBridge (mostly unused here)
    context: Lambda context object (has remaining_time_in_millis, etc.)
    """

    logger.info(
        "Starting snapshot cleanup | region=%s | retention=%dd | dry_run=%s",
        REGION, RETENTION_DAYS, DRY_RUN
    )

    if DRY_RUN:
        logger.info("DRY RUN MODE — no snapshots will be deleted")

    # Initialise clients
    ec2 = boto3.client("ec2", region_name=REGION)
    sns = boto3.client("sns", region_name=REGION)

    # ── Step 1: Collect all volume IDs attached to instances ──────────────────
    try:
        attached_volume_ids = get_attached_volume_ids(ec2)
    except Exception as e:
        logger.error("Failed to get attached volumes: %s", e)
        raise

    # ── Step 2: Get all snapshots older than RETENTION_DAYS ───────────────────
    try:
        old_snapshots = get_old_snapshots(ec2, RETENTION_DAYS)
    except Exception as e:
        logger.error("Failed to get old snapshots: %s", e)
        raise

    # ── Step 3: Filter — keep only snapshots whose volume is NOT attached ──────
    candidates = [
        snap for snap in old_snapshots
        if snap.get("VolumeId") not in attached_volume_ids
    ]

    logger.info(
        "%d of %d old snapshots are candidates for deletion "
        "(source volume not attached to any instance)",
        len(candidates), len(old_snapshots)
    )

    # ── Step 4: Delete eligible snapshots ────────────────────────────────────
    report = {
        "run_date":          datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
        "region":            REGION,
        "retention_days":    RETENTION_DAYS,
        "dry_run":           DRY_RUN,
        "total_scanned":     len(old_snapshots),
        "eligible":          len(candidates),
        "deleted":           0,
        "skipped":           0,
        "errors":            0,
        "freed_gb":          0.0,
        "deleted_snapshots": [],
    }

    for snap in candidates:
        snapshot_id = snap["SnapshotId"]
        volume_id   = snap.get("VolumeId", "unknown")
        size_gb     = snap.get("VolumeSize", 0)
        age_days    = (datetime.now(timezone.utc) - snap["StartTime"]).days
        name        = get_snapshot_name(snap)

        try:
            success = delete_snapshot_safe(ec2, snapshot_id, dry_run=DRY_RUN)

            if success:
                report["deleted"]    += 1
                report["freed_gb"]   += size_gb
                report["deleted_snapshots"].append({
                    "id":        snapshot_id,
                    "volume_id": volume_id,
                    "size_gb":   size_gb,
                    "age_days":  age_days,
                    "name":      name,
                })
            else:
                report["skipped"] += 1

        except Exception as e:
            report["errors"] += 1
            logger.error("Error processing snapshot %s: %s", snapshot_id, e)
            # Continue with next snapshot — don't abort the whole run

    # ── Step 5: Publish report ────────────────────────────────────────────────
    logger.info(
        "Cleanup complete | deleted=%d | skipped=%d | errors=%d | freed=%.1fGB",
        report["deleted"], report["skipped"], report["errors"], report["freed_gb"]
    )

    publish_report(sns, SNS_TOPIC_ARN, report)

    return {
        "statusCode": 200,
        "body": {
            "message":  "Snapshot cleanup complete",
            "deleted":  report["deleted"],
            "freed_gb": round(report["freed_gb"], 2),
            "errors":   report["errors"],
            "dry_run":  DRY_RUN,
        }
    }
```

---

### Deploy This Lambda Using boto3

```python
"""
deploy_lambda.py

Script to package and deploy the snapshot cleanup Lambda function.
Run this once to create the function, then update it on code changes.
"""

import boto3
import json
import zipfile
import io
import os
import time

FUNCTION_NAME  = "medisync-snapshot-cleanup"
HANDLER        = "snapshot_cleanup.lambda_handler"
RUNTIME        = "python3.12"
TIMEOUT        = 300              # 5 minutes — may have many snapshots
MEMORY         = 256              # MB
REGION         = "ap-south-1"
ROLE_NAME      = "medisync-lambda-snapshot-cleanup"


def create_deployment_package(source_file="snapshot_cleanup.py"):
    """Zip the Lambda source file into bytes for upload."""
    buffer = io.BytesIO()

    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.write(source_file, arcname=source_file)

    buffer.seek(0)
    return buffer.read()


def ensure_iam_role(iam_client):
    """Create the Lambda execution role if it doesn't exist."""

    trust_policy = {
        "Version": "2012-10-17",
        "Statement": [{
            "Effect":    "Allow",
            "Principal": {"Service": "lambda.amazonaws.com"},
            "Action":    "sts:AssumeRole",
        }]
    }

    inline_policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Sid":      "EC2Access",
                "Effect":   "Allow",
                "Action":   [
                    "ec2:DescribeInstances",
                    "ec2:DescribeVolumes",
                    "ec2:DescribeSnapshots",
                    "ec2:DeleteSnapshot",
                ],
                "Resource": "*",
            },
            {
                "Sid":      "SNSAccess",
                "Effect":   "Allow",
                "Action":   ["sns:Publish"],
                "Resource": "*",
            },
            {
                "Sid":      "LogsAccess",
                "Effect":   "Allow",
                "Action":   [
                    "logs:CreateLogGroup",
                    "logs:CreateLogStream",
                    "logs:PutLogEvents",
                ],
                "Resource": "arn:aws:logs:*:*:*",
            },
        ]
    }

    try:
        role = iam_client.get_role(RoleName=ROLE_NAME)
        role_arn = role["Role"]["Arn"]
        print(f"Using existing IAM role: {role_arn}")

    except iam_client.exceptions.NoSuchEntityException:
        print(f"Creating IAM role: {ROLE_NAME}")

        role = iam_client.create_role(
            RoleName                 = ROLE_NAME,
            AssumeRolePolicyDocument = json.dumps(trust_policy),
            Description              = "Execution role for snapshot cleanup Lambda",
        )
        role_arn = role["Role"]["Arn"]

        iam_client.put_role_policy(
            RoleName       = ROLE_NAME,
            PolicyName     = "SnapshotCleanupPolicy",
            PolicyDocument = json.dumps(inline_policy),
        )

        print(f"IAM role created: {role_arn}")
        print("Waiting 15s for role to propagate...")
        time.sleep(15)   # IAM changes take a moment to propagate

    return role_arn


def deploy_lambda(lam_client, role_arn, zip_bytes):
    """Create or update the Lambda function."""
    try:
        # Try to get existing function
        lam_client.get_function(FunctionName=FUNCTION_NAME)

        # Function exists — update code and config
        print(f"Updating existing Lambda: {FUNCTION_NAME}")

        lam_client.update_function_code(
            FunctionName = FUNCTION_NAME,
            ZipFile      = zip_bytes,
            Publish      = True,
        )

        # Wait for update to complete
        waiter = lam_client.get_waiter("function_updated")
        waiter.wait(FunctionName=FUNCTION_NAME)

        lam_client.update_function_configuration(
            FunctionName = FUNCTION_NAME,
            Timeout      = TIMEOUT,
            MemorySize   = MEMORY,
            Environment  = {
                "Variables": {
                    "RETENTION_DAYS": "30",
                    "DRY_RUN":        "true",     # start with dry run!
                    "SNS_TOPIC_ARN":  "",         # add your ARN here
                }
            },
        )
        print(f"Lambda updated ✓")

    except lam_client.exceptions.ResourceNotFoundException:
        # Function doesn't exist — create it
        print(f"Creating new Lambda: {FUNCTION_NAME}")

        lam_client.create_function(
            FunctionName  = FUNCTION_NAME,
            Runtime       = RUNTIME,
            Role          = role_arn,
            Handler       = HANDLER,
            Code          = {"ZipFile": zip_bytes},
            Timeout       = TIMEOUT,
            MemorySize    = MEMORY,
            Description   = "Deletes EBS snapshots older than 30 days for unattached volumes",
            Environment   = {
                "Variables": {
                    "RETENTION_DAYS": "30",
                    "DRY_RUN":        "true",
                    "SNS_TOPIC_ARN":  "",
                }
            },
            Tags = {
                "Project":     "medisync",
                "ManagedBy":   "boto3-deploy-script",
                "Environment": "production",
            },
        )

        # Wait for function to be active
        waiter = lam_client.get_waiter("function_active")
        waiter.wait(FunctionName=FUNCTION_NAME)

        print(f"Lambda created ✓")


def create_eventbridge_schedule(events_client, lam_client, function_arn):
    """Schedule the Lambda to run every Sunday at midnight UTC."""
    rule_name = f"{FUNCTION_NAME}-weekly-schedule"

    # Create the schedule rule
    rule = events_client.put_rule(
        Name                = rule_name,
        ScheduleExpression  = "cron(0 0 ? * SUN *)",    # every Sunday midnight UTC
        State               = "ENABLED",
        Description         = "Trigger snapshot cleanup Lambda every Sunday at midnight",
    )

    rule_arn = rule["RuleArn"]

    # Add Lambda as the target
    events_client.put_targets(
        Rule    = rule_name,
        Targets = [{
            "Id":  "SnapshotCleanupTarget",
            "Arn": function_arn,
        }]
    )

    # Grant EventBridge permission to invoke the Lambda
    try:
        lam_client.add_permission(
            FunctionName = FUNCTION_NAME,
            StatementId  = f"allow-eventbridge-{rule_name}",
            Action       = "lambda:InvokeFunction",
            Principal    = "events.amazonaws.com",
            SourceArn    = rule_arn,
        )
    except lam_client.exceptions.ResourceConflictException:
        pass   # permission already exists

    print(f"EventBridge schedule created: {rule_arn}")
    print("Function will run every Sunday at midnight UTC")


def main():
    print(f"Deploying {FUNCTION_NAME} to {REGION}\n")

    iam    = boto3.client("iam")
    lam    = boto3.client("lambda",        region_name=REGION)
    events = boto3.client("events",        region_name=REGION)

    # Step 1 — Ensure IAM role exists
    role_arn = ensure_iam_role(iam)

    # Step 2 — Package the function code
    print("Packaging Lambda code...")
    zip_bytes = create_deployment_package("snapshot_cleanup.py")
    print(f"Package size: {len(zip_bytes) / 1024:.1f} KB")

    # Step 3 — Deploy the function
    deploy_lambda(lam, role_arn, zip_bytes)

    # Step 4 — Get function ARN for EventBridge
    func_config  = lam.get_function_configuration(FunctionName=FUNCTION_NAME)
    function_arn = func_config["FunctionArn"]

    # Step 5 — Create schedule
    create_eventbridge_schedule(events, lam, function_arn)

    # Step 6 — Test with dry run
    print("\nRunning test invocation (dry run)...")
    lam_client = boto3.client("lambda", region_name=REGION)
    response   = lam_client.invoke(
        FunctionName   = FUNCTION_NAME,
        InvocationType = "RequestResponse",
        Payload        = json.dumps({}),
    )

    import json as _json
    result = _json.loads(response["Payload"].read())
    print(f"Test result: {result}")

    print(f"\n✓ Deployment complete!")
    print(f"  Function: {FUNCTION_NAME}")
    print(f"  Region:   {REGION}")
    print(f"  Schedule: Every Sunday at midnight UTC")
    print(f"\n  Next step: Set DRY_RUN=false once you've verified the dry run output")


if __name__ == "__main__":
    main()
```

---

### How to Run the Project

```bash
# 1 — Set up virtual environment
python3 -m venv venv
source venv/bin/activate

# 2 — Install dependencies
pip install boto3

# 3 — Configure AWS credentials
aws configure
# or
export AWS_ACCESS_KEY_ID=AKIA...
export AWS_SECRET_ACCESS_KEY=...
export AWS_DEFAULT_REGION=ap-south-1

# 4 — Deploy (dry run mode by default)
python deploy_lambda.py

# 5 — Check CloudWatch Logs for dry run output
aws logs tail /aws/lambda/medisync-snapshot-cleanup --follow

# 6 — Once satisfied with dry run output, disable dry run
aws lambda update-function-configuration \
  --function-name medisync-snapshot-cleanup \
  --environment "Variables={RETENTION_DAYS=30,DRY_RUN=false,SNS_TOPIC_ARN=arn:aws:sns:...}"

# 7 — Trigger manually to verify
aws lambda invoke \
  --function-name medisync-snapshot-cleanup \
  --payload '{}' \
  --cli-binary-format raw-in-base64-out \
  response.json && cat response.json
```

---

## 📌 Quick Reference Cheatsheet

### Client Setup

```python
import boto3

# Simple client
ec2 = boto3.client("ec2", region_name="ap-south-1")

# With profile
session = boto3.Session(profile_name="production")
ec2     = session.client("ec2", region_name="ap-south-1")

# Resource interface
ec2_r = boto3.resource("ec2", region_name="ap-south-1")
```

### Common Patterns

```python
# Always paginate for list operations
paginator = client.get_paginator("describe_snapshots")
for page in paginator.paginate(OwnerIds=["self"]):
    for snap in page["Snapshots"]:
        process(snap)

# Get Name tag safely
name = next(
    (t["Value"] for t in resource.get("Tags", []) if t["Key"] == "Name"),
    "unnamed"
)

# Date comparison
from datetime import datetime, timezone, timedelta
cutoff   = datetime.now(timezone.utc) - timedelta(days=30)
is_old   = resource["StartTime"] < cutoff

# Safe error handling
from botocore.exceptions import ClientError
try:
    ec2.delete_snapshot(SnapshotId=snap_id)
except ClientError as e:
    if e.response["Error"]["Code"] == "InvalidSnapshot.InUse":
        pass   # expected — skip
    else:
        raise  # unexpected — re-raise

# Wait for state change
waiter = ec2.get_waiter("instance_running")
waiter.wait(InstanceIds=["i-0abc123"])
```

### Services Quick Reference

```python
ec2 = boto3.client("ec2")          # instances, volumes, snapshots, AMIs
s3  = boto3.client("s3")           # buckets, objects, presigned URLs
iam = boto3.client("iam")          # users, roles, policies
lam = boto3.client("lambda")       # functions, invocations
cw  = boto3.client("cloudwatch")   # metrics, alarms, dashboards
ssm = boto3.client("ssm")          # parameter store, session manager
sns = boto3.client("sns")          # topics, subscriptions, publish
rds = boto3.client("rds")          # databases, snapshots, clusters
eks = boto3.client("eks")          # Kubernetes clusters, node groups
sts = boto3.client("sts")          # assume role, caller identity
```

---

| Task | Do This |
|---|---|
| List resources | Always use `get_paginator()` |
| Get Name tag | `next((t["Value"] for t in r.get("Tags",[]) if t["Key"]=="Name"), "unnamed")` |
| Compare dates | Use `datetime.now(timezone.utc)` — AWS times are UTC-aware |
| Handle expected errors | `except ClientError as e: e.response["Error"]["Code"]` |
| Wait for state | `client.get_waiter("state").wait(...)` |
| Never hardcode keys | Use env vars, IAM roles, or `~/.aws/credentials` |
| Test safely | Set `DRY_RUN=true` — verify before deleting anything |
| Cross-region | `boto3.client("ec2", region_name="us-east-1")` |
| Cross-account | `sts.assume_role()` → create client with temp creds |

---

*Last updated: 2026 · boto3 1.34+ · Python 3.11+ · DevOps track*
