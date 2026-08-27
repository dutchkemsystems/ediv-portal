import requests
import json

API_KEY = "rnd_1uUl4n2tXxDl3lgVXfRnNNPECJlr"
HEADERS = {"Authorization": f"Bearer {API_KEY}", "Accept": "application/json", "Content-Type": "application/json"}
SERVICE_ID = "srv-da6u74gae00c73855d3g"

# Check current service config
resp = requests.get(
    f"https://api.render.com/v1/services/{SERVICE_ID}",
    headers=HEADERS
)
svc = resp.json().get("service", resp.json())
details = svc.get("serviceDetails", {})
env_details = details.get("envSpecificDetails", {})

print("Current startCommand:", repr(env_details.get("startCommand", "N/A")))
print("Current buildCommand:", repr(env_details.get("buildCommand", "N/A")))
print("URL:", details.get("url", "N/A"))

# Also check env vars
resp2 = requests.get(
    f"https://api.render.com/v1/services/{SERVICE_ID}/env-vars",
    headers=HEADERS
)
env_vars = resp2.json()
print("\nEnv vars set:")
for ev in env_vars:
    e = ev.get("envVar", ev)
    print(f"  {e.get('key', '?')}: {e.get('value', '?')[:50]}")
