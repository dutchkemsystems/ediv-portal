# Education District IV Portal - Complete Deployment Guide

## Quick Deploy (5 Minutes)

### Step 1: Go to Render Dashboard
Open: https://dashboard.render.com

### Step 2: Create Backend Service
1. Click **"New +"** → **"Web Service"**
2. Click **"Build and deploy from a Git repository"**
3. Connect your GitHub: `dutchkemsystems/ediv-portal`
4. Fill in:
   - **Name**: `ediv-portal`
   - **Region**: Oregon (US West)
   - **Runtime**: Python
   - **Build Command**:
     ```
     pip install -r backend/requirements/render.txt && cd backend && python manage.py collectstatic --noinput
     ```
   - **Start Command**:
     ```
     cd backend && python manage.py migrate --noinput && cd backend && gunicorn config.wsgi:application --bind 0.0.0.0:$PORT --workers 2 --threads 2 --timeout 120
     ```

### Step 3: Add Database
1. In the same service page, scroll to **"Add Database"**
2. Click **"Add Database"**
3. Select **PostgreSQL** → **Free** plan
4. Database name: `ediv-db`

### Step 4: Set Environment Variables
Click **"Environment"** tab and add:

| Key | Value |
|-----|-------|
| `DJANGO_SETTINGS_MODULE` | `config.settings.production` |
| `DJANGO_SECRET_KEY` | Click "Generate" |
| `DJANGO_DEBUG` | `False` |
| `DJANGO_ALLOWED_HOSTS` | `*.onrender.com,localhost,127.0.0.1` |
| `POSTGRES_HOST` | (auto-linked from database) |
| `POSTGRES_PORT` | (auto-linked from database) |
| `POSTGRES_DB` | (auto-linked from database) |
| `POSTGRES_USER` | (auto-linked from database) |
| `POSTGRES_PASSWORD` | (auto-linked from database) |
| `FRONTEND_URL` | `https://ediv-frontend-static.onrender.com` |

### Step 5: Deploy Backend
1. Click **"Create Web Service"**
2. Wait 5-10 minutes for first build

### Step 6: Create Frontend Service
1. Go back to Dashboard
2. Click **"New +"** → **"Static Site"**
3. Connect the same repo
4. Fill in:
   - **Name**: `ediv-frontend-static`
   - **Build Command**:
     ```
     cd frontend && npm install && npm run build
     ```
   - **Publish Directory**:
     ```
     frontend/dist
     ```

### Step 7: Add Route Rewrite
1. In frontend service, click **"Settings"**
2. Scroll to **"Routes"**
3. Click **"Add Route"**
4. Set:
   - **Source**: `/*`
   - **Destination**: `/index.html`

### Step 8: Set Frontend Environment Variables
| Key | Value |
|-----|-------|
| `VITE_API_URL` | `/api` |

### Step 9: Deploy Frontend
Click **"Create Static Site"** and wait 2-3 minutes.

---

## After Deployment

### 1. Seed the Database
1. Go to `ediv-portal` service
2. Click **"Shell"** tab
3. Run:
   ```bash
   python manage.py seed_departments
   python manage.py seed_users
   ```

### 2. Create Admin User
In the same shell:
```bash
python manage.py createsuperuser
```

### 3. Test the Application
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
- Check logs in Render dashboard
- Common issue: Missing `render.txt` requirements file (already fixed in code)

### 500 Error on Health Check
- Database not connected
- Check environment variables are set correctly

### Frontend Can't Connect to API
- Check `VITE_API_URL` is set to `/api`
- Check CORS settings in backend

### Login Fails
- Run `python manage.py seed_users` in shell
- Check `DJANGO_SECRET_KEY` is set

---

## Need Help?

If you encounter any issues:
1. Check Render build logs
2. Check Render runtime logs
3. Share the error message and I'll help troubleshoot
