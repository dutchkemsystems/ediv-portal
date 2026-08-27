import requests, json

API_KEY = "rnd_1uUl4n2tXxDl3lgVXfRnNNPECJlr"
H = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json", "Accept": "application/json"}

# Create new credentials with a specific username
r = requests.post(
    "https://api.render.com/v1/postgres/dpg-da6utpq6iojc73ft0ip0-a/credentials",
    headers=H,
    json={
        "username": "ediv_user"
    }
)
print(f"Status: {r.status_code}")
print(json.dumps(r.json(), indent=2)[:1000])
