#!/usr/bin/env python3
"""
Render Deployment Automation Script
Run this to set all required environment variables on Render via their API.

Usage:
  export RENDER_API_KEY="your-api-key"
  python scripts/render_deploy_setup.py

Get your API key from: https://dashboard.render.com/u/settings#api-keys
"""

import json
import os
import sys
import urllib.request
import urllib.error
import secrets
import string

RENDER_API_BASE = "https://api.render.com/v1"


def generate_secret_key(length=50):
    chars = string.ascii_letters + string.digits + "!@#$%^&*(-_=+)"
    return "".join(secrets.choice(chars) for _ in range(length))


def generate_password(length=16):
    chars = string.ascii_letters + string.digits + "!@#$%"
    return "".join(secrets.choice(chars) for _ in range(length))


def api_request(method, path, data=None):
    api_key = os.environ.get("RENDER_API_KEY")
    if not api_key:
        print("ERROR: Set RENDER_API_KEY environment variable first.")
        print("Get it from: https://dashboard.render.com/u/settings#api-keys")
        sys.exit(1)

    url = f"{RENDER_API_BASE}{path}"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }

    body = json.dumps(data).encode() if data else None
    req = urllib.request.Request(url, data=body, headers=headers, method=method)

    try:
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        error_body = e.read().decode()
        print(f"API Error {e.code}: {error_body}")
        return None


def get_services():
    resp = api_request("GET", "/services")
    if resp and "data" in resp:
        return {item["service"]["name"]: item["service"]["id"] for item in resp["data"]}
    return {}


def get_env_vars(service_id):
    resp = api_request("GET", f"/services/{service_id}/env-vars")
    if resp and "data" in resp:
        return {item["envVar"]["key"]: item["envVar"]["id"] for item in resp["data"]}
    return {}


def set_env_var(service_id, key, value):
    existing = get_env_vars(service_id)
    if key in existing:
        resp = api_request("PATCH", f"/services/{service_id}/env-vars/{existing[key]}", {"value": value})
        if resp:
            print(f"  Updated: {key}")
            return True
    else:
        resp = api_request("POST", f"/services/{service_id}/env-vars", {"key": key, "value": value})
        if resp:
            print(f"  Set: {key}")
            return True
    print(f"  Failed: {key}")
    return False


def setup_backend_service(service_id):
    print("\n--- Setting Backend Environment Variables ---")

    secrets_to_set = {
        "DJANGO_SECRET_KEY": generate_secret_key(),
        "ADMIN_PASSWORD": generate_password(),
        "TG_PASSWORD": generate_password(),
        "HEAD_OFFICE_PASSWORD": generate_password(),
        "SCHOOL_STAFF_PASSWORD": generate_password(),
        "TEACHER_PASSWORD": generate_password(),
        "STUDENT_PASSWORD": generate_password(),
    }

    for key, value in secrets_to_set.items():
        set_env_var(service_id, key, value)

    # Print credentials for reference
    print("\n--- Generated Credentials (SAVE THESE) ---")
    for key, value in secrets_to_set.items():
        print(f"  {key}: {value}")

    return secrets_to_set


def main():
    print("=== Render Deployment Automation ===\n")

    if "--help" in sys.argv or "-h" in sys.argv:
        print(__doc__)
        return

    services = get_services()
    if not services:
        print("Could not fetch services. Check your RENDER_API_KEY.")
        return

    print(f"Found services: {list(services.keys())}")

    backend_id = services.get("ediv-portal")
    if not backend_id:
        print("ERROR: Service 'ediv-portal' not found.")
        print("Create it first via Render dashboard or Blueprint from render.yaml")
        return

    creds = setup_backend_service(backend_id)

    print("\n=== Setup Complete ===")
    print("Next steps:")
    print("1. The service will auto-redeploy with new env vars")
    print("2. Check logs at: https://dashboard.render.com")
    print("3. Test health at: https://ediv-portal.onrender.com/health/")


if __name__ == "__main__":
    main()
