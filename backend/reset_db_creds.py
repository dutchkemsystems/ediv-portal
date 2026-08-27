import requests, json

API_KEY = "rnd_1uUl4n2tXxDl3lgVXfRnNNPECJlr"
H = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json", "Accept": "application/json"}

# Generate new credentials for the database
r = requests.post(
    "https://api.render.com/v1/postgres/dpg-da6utpq6iojc73ft0ip0-a/generate-credentials",
    headers=H,
    json={"type": "reset"}
)
print(f"Generate creds: {r.status_code}")
print(r.text[:500])

# Try another endpoint
r2 = requests.post(
    "https://api.render.com/v1/postgres/dpg-da6utpq6iojc73ft0ip0-a/credentials",
    headers=H,
    json={}
)
print(f"\nCredentials POST: {r2.status_code}")
print(r2.text[:500])

# Try to reset the password
r3 = requests.patch(
    "https://api.render.com/v1/postgres/dpg-da6utpq6iojc73ft0ip0-a",
    headers=H,
    json={"resetPassword": True}
)
print(f"\nReset password: {r3.status_code}")
print(r3.text[:500])
