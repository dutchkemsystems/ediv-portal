import requests
import json

API_KEY = "rnd_1uUl4n2tXxDl3lgVXfRnNNPECJlr"
SID = "srv-da6u74gae00c73855d3g"
H = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json", "Accept": "application/json"}

env_vars = [
    {"key": "DJANGO_SETTINGS_MODULE", "value": "config.settings.production"},
    {"key": "PYTHONPATH", "value": "/opt/render/project/src/backend"},
    {"key": "DJANGO_DEBUG", "value": "False"},
    {"key": "DJANGO_ALLOWED_HOSTS", "value": "ediv-portal.onrender.com,localhost,127.0.0.1"},
    {"key": "DJANGO_SECRET_KEY", "value": "django-insecure-eDiv-Pr0d-S3cr3t-K3y-2026-xK9mN2pQ7rT4wY6z"},
    {"key": "ADMIN_PASSWORD", "value": "Admin@12345678"},
    {"key": "TG_PASSWORD", "value": "TutorGen@12345"},
    {"key": "HEAD_OFFICE_PASSWORD", "value": "HeadOffice@123"},
    {"key": "SCHOOL_STAFF_PASSWORD", "value": "SchoolStaff@12345"},
    {"key": "TEACHER_PASSWORD", "value": "Teacher@12345"},
    {"key": "STUDENT_PASSWORD", "value": "Student@12345"},
    {"key": "DEFAULT_FROM_EMAIL", "value": "EDIV Portal <noreply@ediv.gov.ng>"},
    {"key": "EMAIL_HOST", "value": "smtp.gmail.com"},
    {"key": "EMAIL_PORT", "value": "587"},
    {"key": "EMAIL_USE_TLS", "value": "True"},
    {"key": "FRONTEND_URL", "value": "https://ediv-frontend-static.onrender.com"},
    {"key": "REDIS_URL", "value": ""},
    {"key": "CLOUDINARY_URL", "value": ""},
    {"key": "EMAIL_HOST_USER", "value": ""},
    {"key": "EMAIL_HOST_PASSWORD", "value": ""},
    {"key": "KORA_PAY_PUBLIC_KEY", "value": ""},
    {"key": "KORA_PAY_SECRET_KEY", "value": ""},
]

print(f"Setting {len(env_vars)} env vars via PUT...")
r = requests.put(
    f"https://api.render.com/v1/services/{SID}/env-vars",
    headers=H,
    json=env_vars
)
print(f"Status: {r.status_code}")
result = r.json()
print(f"Env vars set: {len(result)}")
for item in result:
    ev = item.get("envVar", item)
    val = ev.get("value", "")
    print(f"  {ev.get('key', '?')}: {val[:50]}")
