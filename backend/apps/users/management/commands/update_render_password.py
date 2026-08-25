"""Management command to update Render environment variables for a specific user's password.

Usage:
    python manage.py update_render_password --email admin@ediv.gov.ng --password "NewPass@123"
    python manage.py update_render_password --role SYSADMIN --password "NewPass@123"
    python manage.py update_render_password --email admin@ediv.gov.ng --generate

Requires:
    RENDER_API_KEY  — Render personal API key (https://dashboard.render.com/settings/api-keys)
    RENDER_SERVICE_ID — The service ID (e.g. srv-xxxxx) from render.yaml name: ediv-portal

Also updates the local database password so the user can log in immediately.
"""

import os
import secrets
import string

import requests
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

User = get_user_model()

ROLE_TO_ENV_VAR = {
    "SYSADMIN": "ADMIN_PASSWORD",
    "TG_PS": "TG_PASSWORD",
    "HR": "HEAD_OFFICE_PASSWORD",
    "FIN": "HEAD_OFFICE_PASSWORD",
    "AUDIT": "HEAD_OFFICE_PASSWORD",
    "QA": "HEAD_OFFICE_PASSWORD",
    "CC": "HEAD_OFFICE_PASSWORD",
    "EMIS": "HEAD_OFFICE_PASSWORD",
    "PLAN": "HEAD_OFFICE_PASSWORD",
    "PROC": "HEAD_OFFICE_PASSWORD",
    "PA": "HEAD_OFFICE_PASSWORD",
    "SA": "HEAD_OFFICE_PASSWORD",
    "FRENCH": "HEAD_OFFICE_PASSWORD",
    "REG": "HEAD_OFFICE_PASSWORD",
    "PRI": "SCHOOL_STAFF_PASSWORD",
    "VP": "SCHOOL_STAFF_PASSWORD",
    "TCH": "TEACHER_PASSWORD",
    "STD": "STUDENT_PASSWORD",
}


def _generate_password(length=16):
    alphabet = string.ascii_letters + string.digits + "!@#$%&*"
    while True:
        pw = "".join(secrets.choice(alphabet) for _ in range(length))
        if (
            any(c.islower() for c in pw)
            and any(c.isupper() for c in pw)
            and any(c.isdigit() for c in pw)
            and any(c in "!@#$%&*" for c in pw)
        ):
            return pw


class Command(BaseCommand):
    help = "Update a user's password in both the local DB and Render env vars"

    def add_arguments(self, parser):
        parser.add_argument("--email", help="User email address")
        parser.add_argument("--role", help="User role (updates env var for all users with this role)")
        parser.add_argument("--password", help="New password (required unless --generate is set)")
        parser.add_argument("--generate", action="store_true", help="Auto-generate a 16-char password")
        parser.add_argument(
            "--render-api-key",
            default=os.environ.get("RENDER_API_KEY"),
            help="Render API key (or set RENDER_API_KEY env var)",
        )
        parser.add_argument(
            "--render-service-id",
            default=os.environ.get("RENDER_SERVICE_ID"),
            help="Render service ID (or set RENDER_SERVICE_ID env var)",
        )
        parser.add_argument("--dry-run", action="store_true", help="Show what would be done without making changes")

    def handle(self, *args, **options):
        email = options.get("email")
        role = options.get("role")
        password = options.get("password")
        generate = options.get("generate")
        render_api_key = options.get("render_api_key")
        render_service_id = options.get("render_service_id")
        dry_run = options.get("dry_run")

        if not email and not role:
            self.stderr.write(self.style.ERROR("Provide --email or --role"))
            return

        if generate:
            password = _generate_password()
            self.stdout.write(f"Generated password: {password}")

        if not password:
            self.stderr.write(self.style.ERROR("Provide --password or --generate"))
            return

        # --- Step 1: Update local DB ---
        if email:
            try:
                user = User.objects.get(email=email)
                user.set_password(password)
                user.save()
                self.stdout.write(self.style.SUCCESS(f"DB updated: {user.email} ({user.role})"))
            except User.DoesNotExist:
                self.stderr.write(self.style.ERROR(f"User not found: {email}"))
                return

        # --- Step 2: Update Render env var ---
        env_var = ROLE_TO_ENV_VAR.get(role or (User.objects.get(email=email).role if email else None))
        if not env_var:
            self.stderr.write(self.style.ERROR(f"No env var mapping for role: {role}"))
            return

        if not render_api_key or not render_service_id:
            self.stdout.write(
                self.style.WARNING(
                    f"Render not configured. Set RENDER_API_KEY and RENDER_SERVICE_ID, "
                    f"or pass --render-api-key and --render-service-id.\n"
                    f"Local DB was updated. To update Render manually, set:\n"
                    f"  {env_var} = {password}"
                )
            )
            return

        if dry_run:
            self.stdout.write(f"DRY RUN: Would set {env_var} = {password} on Render service {render_service_id}")
            return

        # Fetch current env vars to find the variable ID
        self.stdout.write(f"Fetching Render env vars for service {render_service_id}...")
        resp = requests.get(
            f"https://api.render.com/v1/services/{render_service_id}/env-vars",
            headers={"Authorization": f"Bearer {render_api_key}"},
        )
        if resp.status_code != 200:
            self.stderr.write(self.style.ERROR(f"Render API error: {resp.status_code} {resp.text}"))
            return

        env_vars = resp.json().get("envVars", [])
        target_var = None
        for var in env_vars:
            if var.get("key") == env_var:
                target_var = var
                break

        if target_var:
            # Update existing
            var_id = target_var["id"]
            self.stdout.write(f"Updating {env_var} (id: {var_id})...")
            resp = requests.patch(
                f"https://api.render.com/v1/services/{render_service_id}/env-vars/{var_id}",
                headers={"Authorization": f"Bearer {render_api_key}", "Content-Type": "application/json"},
                json={"value": password},
            )
        else:
            # Create new
            self.stdout.write(f"Creating {env_var}...")
            resp = requests.post(
                f"https://api.render.com/v1/services/{render_service_id}/env-vars",
                headers={"Authorization": f"Bearer {render_api_key}", "Content-Type": "application/json"},
                json={"key": env_var, "value": password},
            )

        if resp.status_code in (200, 201):
            self.stdout.write(self.style.SUCCESS(f"Render updated: {env_var} = {password}"))
        else:
            self.stderr.write(self.style.ERROR(f"Render API error: {resp.status_code} {resp.text}"))
            return

        self.stdout.write(self.style.SUCCESS(f"\nDone. Password for {email or role} changed everywhere."))
        self.stdout.write(self.style.WARNING("Trigger a manual redeploy on Render for the change to take effect."))
