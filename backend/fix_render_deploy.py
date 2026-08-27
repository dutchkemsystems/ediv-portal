import requests
import json

API_KEY = "rnd_1uUl4n2tXxDl3lgVXfRnNNPECJlr"
SERVICE_ID = "srv-da6u74gae00c73855d3g"
BASE = "https://api.render.com/v1"
HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json",
    "Accept": "application/json"
}

start_cmd = (
    "cd /opt/render/project/src/backend && "
    "python manage.py migrate --noinput && "
    "python manage.py ensure_admin && "
    "python manage.py seed_departments && "
    "python manage.py seed_schools && "
    "python manage.py seed_users && "
    "gunicorn config.wsgi:application --bind 0.0.0.0:$PORT --workers 2 --threads 2 --timeout 180"
)

print("Fixing startCommand...")
resp = requests.patch(
    f"{BASE}/services/{SERVICE_ID}",
    headers=HEADERS,
    json={
        "serviceDetails": {
            "envSpecificDetails": {
                "buildCommand": "cd /opt/render/project/src && pip install --no-cache-dir -r requirements.txt && cd backend && python manage.py collectstatic --noinput",
                "startCommand": start_cmd
            }
        }
    }
)
print(f"Status: {resp.status_code}")
result = resp.json()
sc = result.get("service", result).get("serviceDetails", {}).get("envSpecificDetails", {}).get("startCommand", "NOT FOUND")
print(f"Updated startCommand: {sc}")

# Now trigger a manual deploy
print("\nTriggering manual deploy...")
resp2 = requests.post(
    f"{BASE}/services/{SERVICE_ID}/deploys",
    headers=HEADERS,
    json={"clearCache": "do_not_clear"}
)
print(f"Deploy status: {resp2.status_code}")
if resp2.status_code in (200, 201):
    deploy = resp2.json()
    deploy_id = deploy.get("deploy", {}).get("id", "unknown")
    print(f"Deploy ID: {deploy_id}")
    print(f"Deploy URL: https://dashboard.render.com/web/{SERVICE_ID}")
else:
    print(f"Deploy response: {resp2.text[:500]}")
