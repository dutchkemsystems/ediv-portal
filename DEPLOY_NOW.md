# Education District IV Portal - Complete Deployment Guide

## Quick Deploy (5 Minutes)

### Prerequisites
- GitHub repo: `dutchkemsystems/ediv-portal`
- Render account: https://dashboard.render.com

### Step 1: Use render.yaml (Recommended)

The `render.yaml` in the repo root auto-provisions everything:

1. Go to https://dashboard.render.com
2. Click **"New +"** → **"Blueprint"**
3. Connect your GitHub repo
4. Render reads `render.yaml` and creates:
   - `ediv-portal` (web service)
   - `ediv-frontend-static` (static site)
   - `ediv-db` (PostgreSQL database)
   - `wake-up` (cron job)

### Step 2: Set Required Secrets

In the `ediv-portal` service → **Environment** tab, set these secrets:

| Key | Value |
|-----|-------|
| `ADMIN_PASSWORD` | Your admin password |
| `TG_PASSWORD` | Tutor General password |
| `HEAD_OFFICE_PASSWORD` | Head Office password |
| `SCHOOL_STAFF_PASSWORD` | School Staff password |
| `TEACHER_PASSWORD` | Teacher password |
| `STUDENT_PASSWORD` | Student password |
| `EMAIL_HOST_USER` | Your Gmail address |
| `EMAIL_HOST_PASSWORD` | Gmail app password |
| `KORA_PAY_PUBLIC_KEY` | KoraPay public key |
| `KORA_PAY_SECRET_KEY` | KoraPay secret key |

### Step 3: Deploy

1. Click **"Manual Deploy"** → **"Deploy latest commit"**
2. Wait 5-10 minutes for first build

---

## Manual Setup (Without render.yaml)

If you prefer manual setup instead of using `render.yaml`:

### Step 1: Create Backend Service
1. Click **"New +"** → **"Web Service"**
2. Connect your GitHub repo
3. Fill in:
   - **Name**: `ediv-portal`
   - **Runtime**: Python
   - **Build Command**:
     ```
     cd /opt/render/project/src && pip install --no-cache-dir -r requirements.txt && cd backend && python manage.py collectstatic --noinput
     ```
   - **Start Command**:
     ```
     cd /opt/render/project/src/backend && python manage.py migrate --noinput && python manage.py ensure_admin && python manage.py seed_departments && python manage.py seed_schools && python manage.py seed_users && gunicorn config.wsgi:application --bind 0.0.0.0:$PORT --workers 2 --threads 2 --timeout 180
     ```

### Step 2: Add Database
1. In the service page, click **"Add Database"**
2. Select **PostgreSQL** → **Free** plan
3. Database name: `ediv-db`

### Step 3: Set Environment Variables

| Key | Value |
|-----|-------|
| `DJANGO_SETTINGS_MODULE` | `config.settings.production` |
| `PYTHONPATH` | `/opt/render/project/src/backend` |
| `DJANGO_SECRET_KEY` | Click "Generate" |
| `DJANGO_DEBUG` | `False` |
| `DJANGO_ALLOWED_HOSTS` | `ediv-portal.onrender.com,localhost,127.0.0.1` |
| `DATABASE_URL` | Auto-linked from `ediv-db` database |
| `FRONTEND_URL` | `https://ediv-frontend-static.onrender.com` |
| `EMAIL_HOST` | `smtp.gmail.com` |
| `EMAIL_PORT` | `587` |
| `EMAIL_USE_TLS` | `True` |
| `DEFAULT_FROM_EMAIL` | `EDIV Portal <noreply@ediv.gov.ng>` |

**Secrets** (set manually):
| Key | Value |
|-----|-------|
| `ADMIN_PASSWORD` | Your admin password |
| `TG_PASSWORD` | Tutor General password |
| `HEAD_OFFICE_PASSWORD` | Head Office password |
| `SCHOOL_STAFF_PASSWORD` | School Staff password |
| `TEACHER_PASSWORD` | Teacher password |
| `STUDENT_PASSWORD` | Student password |
| `EMAIL_HOST_USER` | Your Gmail address |
| `EMAIL_HOST_PASSWORD` | Gmail app password |

### Step 4: Create Frontend Service
1. Click **"New +"** → **"Static Site"**
2. Connect the same repo
3. Fill in:
   - **Name**: `ediv-frontend-static`
   - **Build Command**: `cd frontend && npm install && npm run build`
   - **Publish Directory**: `frontend/dist`
4. Add route rewrite: `/**` → `/index.html`
5. Set env var: `VITE_API_URL` = `https://ediv-portal.onrender.com/api`

---

## After Deployment

### Test the Application
- **Backend API**: https://ediv-portal.onrender.com/health/
- **Frontend**: https://ediv-frontend-static.onrender.com
- **Login**: https://ediv-frontend-static.onrender.com/login

### Default Credentials
| Role | Email | Password |
|------|-------|----------|
| System Admin | admin@ediv.gov.ng | Admin@12345678 |
| Tutor General | tg@ediv.gov.ng | TutorGen@12345 |

---

## Troubleshooting

### Build Fails
- Check Render build logs for missing dependencies
- Ensure `requirements.txt` (root) is up to date

### 500 Error on Health Check
- `DATABASE_URL` not set — ensure `ediv-db` database is linked
- `DJANGO_SECRET_KEY` missing — generate one in env vars

### Frontend Can't Connect to API
- Check `VITE_API_URL` is set correctly
- Check CORS settings in `backend/config/settings/base.py`

### Login Fails
- Ensure seed passwords are set as env vars
- Check `DJANGO_SECRET_KEY` is set

---

## Need Help?

If you encounter any issues:
1. Check Render build logs
2. Check Render runtime logs
3. Share the error message for troubleshooting
