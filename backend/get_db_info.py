import requests, json

API_KEY = "rnd_1uUl4n2tXxDl3lgVXfRnNNPECJlr"
H = {"Authorization": f"Bearer {API_KEY}", "Accept": "application/json"}

r = requests.get(
    "https://api.render.com/v1/postgres/dpg-da6utpq6iojc73ft0ip0-a",
    headers=H
)
db = r.json()
print(json.dumps(db, indent=2))

# The Render internal hostname for PG is typically:
# <db-id>.internal.db.render.com
# External is: <db-id>.<region>.postgres.render.com
host_internal = "dpg-da6utpq6iojc73ft0ip0-a.internal.db.render.com"
host_external = "dpg-da6utpq6iojc73ft0ip0-a.oregon-postgres.render.com"
db_user = db.get("databaseUser", "")
db_name = db.get("databaseName", "")

print(f"\nInternal: postgresql://{db_user}:PASSWORD@{host_internal}:5432/{db_name}")
print(f"External: postgresql://{db_user}:PASSWORD@{host_external}:5432/{db_name}")

# Set DATABASE_URL using internal host (Render services can reach internal hosts)
# Note: We don't have the password from the API. The password is only shown on dashboard.
# For same-account services, Render can auto-inject DATABASE_URL when linked via blueprint.
# Since we created via API, we need to construct it manually.
# The DATABASE_URL on Render internal uses the password from the credentials endpoint.
