import requests
import json
import time

API_KEY = "rnd_1uUl4n2tXxDl3lgVXfRnNNPECJlr"
HEADERS = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json", "Accept": "application/json"}

# Trigger frontend redeploy
print("Triggering frontend redeploy...")
resp = requests.post(
    "https://api.render.com/v1/services/srv-d9gmjfrbc2fs738sdvag/deploys",
    headers=HEADERS,
    json={"clearCache": "do_not_clear"}
)
print(f"Frontend deploy: {resp.status_code}")

# Check backend deploy status
print("\nChecking backend deploy status...")
resp2 = requests.get(
    "https://api.render.com/v1/services/srv-da6u74gae00c73855d3g/deploys",
    headers=HEADERS
)
deploys = resp2.json()
for d in deploys[:3]:
    deploy = d.get("deploy", d)
    did = deploy.get("id", "?")
    status = deploy.get("status", "?")
    finish = deploy.get("finishTime", "in progress")
    print(f"  Deploy {did}: status={status}, finishTime={finish}")

# Wait 60s and check health
print("\nWaiting 60s for build to progress...")
time.sleep(60)

print("\nChecking backend health...")
try:
    resp3 = requests.get("https://ediv-portal.onrender.com/health/", timeout=30)
    print(f"Health: {resp3.status_code} - {resp3.text[:200]}")
except Exception as e:
    print(f"Health check failed (expected during build): {e}")

print("\nChecking deploy status again...")
resp4 = requests.get(
    "https://api.render.com/v1/services/srv-da6u74gae00c73855d3g/deploys",
    headers=HEADERS
)
deploys = resp4.json()
for d in deploys[:2]:
    deploy = d.get("deploy", d)
    did = deploy.get("id", "?")
    status = deploy.get("status", "?")
    print(f"  Deploy {did}: status={status}")
