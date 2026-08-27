# Education District IV Portal — Environment Setup Checklist

Follow this checklist in order. Each step has a verification check.

---

## STEP 1: Cloudinary (File Storage)

- [ ] Go to https://cloudinary.com → Sign up (free)
- [ ] Copy your **Cloudinary URL** from the Dashboard
  - Format: `cloudinary://123456789012345:xAbCdEfGhIjKlMnOpQrStUvWxYz@di8shift`
- [ ] Go to Render Dashboard → ediv-portal → **Environment** tab
- [ ] Find `CLOUDINARY_URL` → Click edit → Paste your URL → Save
- [ ] **Verify:** Redeploy, then upload a test file — it should persist after restart

---

## STEP 2: Redis (Background Tasks)

- [ ] Go to Render Dashboard → **New +** → **Redis**
- [ ] Name: `ediv-redis` → Plan: **Free** → Create Database
- [ ] Wait ~2 minutes for it to spin up
- [ ] Click `ediv-redis` → Copy the **Internal Redis URL**
  - Format: `rediss://red-xxxxx:6379`
- [ ] Go to ediv-portal → **Environment** tab
- [ ] Find `REDIS_URL` → Paste the Redis URL → Save
- [ ] Find `CELERY_BROKER_URL` → Paste the same Redis URL → Save
- [ ] **Verify:** Check Render → ediv-celery-worker → Logs → Should show "connected to redis"

---

## STEP 3: Email (SMTP Notifications)

- [ ] Go to https://myaccount.google.com/apppasswords
- [ ] Create an app password (select "Mail" and your device)
- [ ] Copy the 16-character password (e.g., `abcd efgh ijkl mnop`)
- [ ] Go to ediv-portal → **Environment** tab
- [ ] Find `EMAIL_HOST_USER` → Enter your Gmail address → Save
- [ ] Find `EMAIL_HOST_PASSWORD` → Paste the app password → Save
- [ ] **Verify:** Assign a mail to someone → They should receive an email notification

---

## STEP 4: Deployment Secrets (Already Set)

These should already be set via `generateValue: true` or `sync: false`:

| Variable | Status | Notes |
|---|---|---|
| `DJANGO_SECRET_KEY` | Auto-generated | Render creates this automatically |
| `DATABASE_URL` | Auto-linked | Connected to ediv-db automatically |
| `ADMIN_PASSWORD` | Manual | Set in Render dashboard |
| `TG_PASSWORD` | Manual | Set in Render dashboard |
| `KORA_PAY_PUBLIC_KEY` | Manual | For payment integration |
| `KORA_PAY_SECRET_KEY` | Manual | For payment integration |

---

## STEP 5: Post-Deploy Verification

After all variables are set and the service redeploys:

- [ ] **Health check:** `https://ediv-portal.onrender.com/health/`
  - Expected: `{"status": "healthy", "database": "connected"}`
- [ ] **API root:** `https://ediv-portal.onrender.com/api/`
  - Expected: JSON with all available endpoints
- [ ] **Admin login:** `https://ediv-portal.onrender.com/api/users/login/`
  - POST with `{"email": "admin@ediv.gov.ng", "password": "your-admin-password"}`
  - Expected: JWT access + refresh tokens
- [ ] **Frontend:** `https://ediv-frontend-static.onrender.com`
  - Expected: Login page loads

---

## Default Login Credentials

After running `seed_users`, these accounts are available:

| Role | Email | Password |
|---|---|---|
| System Admin | admin@ediv.gov.ng | Set via `ADMIN_PASSWORD` env var |
| TG/PS | tg.ps@ediv.gov.ng | Set via `TG_PASSWORD` env var |
| HR Head | hr.head@ediv.gov.ng | Set via `HEAD_OFFICE_PASSWORD` |
| School Principal | school.pri@school.edu.ng | Set via `SCHOOL_STAFF_PASSWORD` |
| Teacher | teacher@school.edu.ng | Set via `TEACHER_PASSWORD` |
| Student | student@school.edu.ng | Set via `STUDENT_PASSWORD` |

---

## Troubleshooting

### Login fails with "Invalid credentials"
1. Check that `seed_users` ran successfully (check Render build logs)
2. Verify the password env var is set correctly
3. Check: `https://ediv-portal.onrender.com/api/users/` (requires admin token)

### Files not persisting
1. Check `CLOUDINARY_URL` is set (not empty)
2. Check Render logs for "CLOUDINARY_URL not set" warning

### Emails not sending
1. Check `EMAIL_HOST_USER` and `EMAIL_HOST_PASSWORD` are set
2. Check Gmail app password is still valid (Google may revoke after 30 days)
3. Check Render logs for email-related warnings

### Celery worker not running
1. Check Render → ediv-celery-worker → Logs
2. If "Redis not connected" → Check REDIS_URL is set correctly
3. If worker shows "CELERY_TASK_ALWAYS_EAGER" → REDIS_URL is empty

### Database migration errors
1. Check Render → ediv-portal → Logs for migration errors
2. If new migration needed: run `python manage.py makemigrations` locally, commit, push

---

## Cost Summary (Free Tier)

| Service | Plan | Cost |
|---|---|---|
| ediv-portal (web) | Free | $0/month |
| ediv-celery-worker | Free | $0/month |
| ediv-redis | Free | $0/month |
| ediv-db (PostgreSQL) | Free | $0/month |
| ediv-frontend-static | Free | $0/month |
| Cloudinary | Free (25GB) | $0/month |
| **Total** | | **$0/month** |

Note: Free tier services spin down after inactivity. First request after idle takes ~30-60 seconds.
