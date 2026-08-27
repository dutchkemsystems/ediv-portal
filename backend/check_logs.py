import requests

API_KEY = "rnd_1uUl4n2tXxDl3lgVXfRnNNPECJlr"
HEADERS = {"Authorization": f"Bearer {API_KEY}", "Accept": "application/json"}

# Get deploy details for the failed deploy
deploy_id = "dep-da6u750ae00c73855e70"
resp = requests.get(
    f"https://api.render.com/v1/services/srv-da6u74gae00c73855d3g/deploys/{deploy_id}",
    headers=HEADERS
)
print(f"Status: {resp.status_code}")
import json
print(json.dumps(resp.json(), indent=2)[:3000])

# Also check the in-progress one
deploy_id2 = "dep-da6u8mbbptlc73f1gh3g"
resp2 = requests.get(
    f"https://api.render.com/v1/services/srv-da6u74gae00c73855d3g/deploys/{deploy_id2}",
    headers=HEADERS
)
print(f"\nIn-progress deploy status: {resp2.status_code}")
print(json.dumps(resp2.json(), indent=2)[:2000])
