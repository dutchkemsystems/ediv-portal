import requests

API_KEY = "rnd_1uUl4n2tXxDl3lgVXfRnNNPECJlr"
HEADERS = {"Authorization": f"Bearer {API_KEY}", "Accept": "application/json"}

# Check deploy status
resp = requests.get(
    "https://api.render.com/v1/services/srv-da6u74gae00c73855d3g/deploys",
    headers=HEADERS
)
deploys = resp.json()
for d in deploys[:5]:
    deploy = d.get("deploy", d)
    print(f"Deploy {deploy.get('id', '?')}: status={deploy.get('status', '?')}")

# Try health
print("\nHealth check...")
try:
    h = requests.get("https://ediv-portal.onrender.com/health/", timeout=120)
    print(f"Health: {h.status_code} - {h.text[:200]}")
except Exception as e:
    print(f"Health: {e}")
