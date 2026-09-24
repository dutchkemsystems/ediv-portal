# EDUCATION DISTRICT IV PORTAL — CREDENTIALS REGISTRY

> **CONFIDENTIAL** — Do NOT commit this file to a public repository.

---

## 1. DEFAULT SEED PASSWORDS (by role)

These are the initial passwords set when users are first created.
After first login, users MUST change their password via the Change Password page.

| Role Group | Env Var | Default Password | Who Gets It |
|---|---|---|---|
| **System Admin** | `ADMIN_PASSWORD` | `Admin@12345678` | `admin@ediv.gov.ng` |
| **Tutor General** | `TG_PASSWORD` | `TutorGen@12345` | `tg.ps@ediv.gov.ng`, `tg@ediv.gov.ng` |
| **Dept/Unit Heads** | `HEAD_OFFICE_PASSWORD` | `HeadOffice@123` | HR, FIN, QA, CC, SA, REG, FRENCH, AUDIT, EMIS, PLAN, PROC, PA heads |
| **Principals/VPs** | `SCHOOL_STAFF_PASSWORD` | `SchoolStaff@12345` | All principals and vice principals |
| **Teachers** | `TEACHER_PASSWORD` | `Teacher@12345` | All teachers |
| **Students** | `STUDENT_PASSWORD` | `Student@12345` | All students |

---

## 2. ALL SEEDED USER ACCOUNTS

### 2.1 Admin & Tutor General

| Email | Name | Role | Phone | Default Password |
|---|---|---|---|---|
| `admin@ediv.gov.ng` | System Administrator | SYSADMIN | +2348010000001 | `Admin@12345678` |
| `tg.ps@ediv.gov.ng` | Abimbola Adesanya | TG_PS | +2348010000002 | `TutorGen@12345` |
| `tg@ediv.gov.ng` | Abimbola Adesanya | TG_PS | +2348010000002 | `TutorGen@12345` |

### 2.2 Department Heads

| Email | Name | Role | Dept | Phone | Default Password |
|---|---|---|---|---|---|
| `hr.head@ediv.gov.ng` | Funmilayo Ogundimu | HR | Admin & HR | +2348010000003 | `HeadOffice@123` |
| `finance.head@ediv.gov.ng` | Adewale Bakare | FIN | Finance | +2348010000004 | `HeadOffice@123` |
| `qa.head@ediv.gov.ng` | Oluwaseun Ajayi | QA | Quality Assurance | +2348010000005 | `HeadOffice@123` |
| `cc.head@ediv.gov.ng` | Chinedu Eze | CC | Co-Curricular | +2348010000006 | `HeadOffice@123` |
| `sa.head@ediv.gov.ng` | Adewale Lawal | SA | Schools Admin | +2348010000007 | `HeadOffice@123` |
| `registry.head@ediv.gov.ng` | Folake Okafor | REG | Registry | +2348010000008 | `HeadOffice@123` |
| `spd.head@ediv.gov.ng` | Ibrahim Abubakar | SA | School Planning | +2348010000009 | `HeadOffice@123` |
| `sss.head@ediv.gov.ng` | Ngozi Nwosu | QA | School Standards | +2348010000010 | `HeadOffice@123` |
| `french.head@ediv.gov.ng` | Amina Mohammed | FRENCH | French Unit | +2348010000011 | `HeadOffice@123` |

### 2.3 Major Unit Heads

| Email | Name | Role | Unit | Phone | Default Password |
|---|---|---|---|---|---|
| `audit.head@ediv.gov.ng` | Tunde Fashola | AUDIT | Internal Audit | +2348010000012 | `HeadOffice@123` |
| `emis.head@ediv.gov.ng` | Kolade Akande | EMIS | EMIS | +2348010000013 | `HeadOffice@123` |
| `plan.head@ediv.gov.ng` | Babatunde Olumide | PLAN | Planning | +2348010000014 | `HeadOffice@123` |
| `procurement.head@ediv.gov.ng` | Emeka Chukwu | PROC | Procurement | +2348010000015 | `HeadOffice@123` |
| `pa.head@ediv.gov.ng` | Funke Bakare | PA | Public Affairs | +2348010000016 | `HeadOffice@123` |

### 2.4 School Staff (Dynamically Generated)

| Email Pattern | Role | School | Default Password |
|---|---|---|---|
| `principal_{school_code}@ediv.gov.ng` | PRI | School | `SchoolStaff@12345` |
| `vp_{school_code}@ediv.gov.ng` | VP | School | `SchoolStaff@12345` |
| `teacher_{NNNN}@ediv.gov.ng` | TCH | Various | `Teacher@12345` |
| `student_{NNNN}@student.ediv.gov.ng` | STD | Various | `Student@12345` |

---

## 3. PASSWORD CHANGE MECHANISM

### How It Works

1. **Initial login**: User logs in with the default password from this registry.
2. **Password change**: User is required to change password via `POST /api/users/auth/change_password/`.
3. **Seed safety**: After the initial seed, `seed_users` and `ensure_admin` NO LONGER reset passwords for existing users. This was fixed on 2026-08-25.
4. **Admin unlock**: Admin can reset any user's password via `POST /api/users/auth/unlock/` (requires `X-Unlock-Token` header).
5. **Forgot password**: Users can self-reset via `POST /api/users/auth/forgot_password/` → email link → `POST /api/users/auth/reset_password/`.

### Password Policy

- Minimum 12 characters
- Must contain: uppercase, lowercase, digit, and special character
- Common passwords rejected: `password`, `1234567890`, `qwertyuiop`, `educationdistrict`, `admin123`, `welcome123`

---

## 4. SYNCING PASSWORD CHANGES TO RENDER

When a user changes their password via the API, the change is stored in the PostgreSQL database (which is persistent on Render). The seed env vars (`ADMIN_PASSWORD`, `TG_PASSWORD`, etc.) are only used during initial user creation and are **no longer reset on redeploy**.

### If You Need to Reset a User's Password

**Option A — Via API (recommended):**
```bash
# Admin unlock (requires X-Unlock-Token = UNLOCK_TOKEN env var)
curl -X POST https://ediv-portal.onrender.com/api/users/auth/unlock/ \
  -H "Content-Type: application/json" \
  -H "X-Unlock-Token: YOUR_UNLOCK_TOKEN" \
  -d '{"email": "admin@ediv.gov.ng", "password": "NewPassword@123"}'
```

**Option B — Via management command (on Render shell):**
```bash
python manage.py reset_password --email admin@ediv.gov.ng --password "NewPassword@123"
```

**Option C — Update Render env var and re-seed (last resort):**
```bash
python scripts/render_deploy_setup.py --render-api-key YOUR_KEY --project-id YOUR_ID
```
Then trigger a manual deploy. This only works for users whose passwords haven't been changed yet.

---

## 5. INFRASTRUCTURE CREDENTIALS

| Service | Variable | Value |
|---|---|---|
| PostgreSQL | `DATABASE_URL` | Set via `render.yaml` → `ediv-db` |
| Django Secret | `DJANGO_SECRET_KEY` | Set in Render env |
| Django Settings | `DJANGO_SETTINGS_MODULE` | `config.settings.production` |
| Email Host | `EMAIL_HOST_PASSWORD` | Set manually in Render |
| Frontend URL | `FRONTEND_URL` | `https://ediv-frontend-static.onrender.com` |
| Unlock Token | `UNLOCK_TOKEN` | Set manually in Render |

---

## 6. FILES WITH HARDCODED CREDENTIALS

These files contain default passwords in code. Handle with care:

| File | Contains |
|---|---|
| `backend/apps/users/management/commands/seed_users.py` | All default passwords + user seed data |
| `backend/apps/users/management/commands/ensure_admin.py` | Admin fallback passwords |
| `backend/apps/users/management/commands/print_credentials.py` | Reads passwords from env vars |
| `backend/apps/users/management/commands/diagnose_admin.py` | Admin unlock defaults |
| `backend/.env.example` | Seed password defaults |
| `.env.production` | Production placeholder passwords |
| `render.yaml` | Env var references (not actual passwords) |
| `scripts/render_deploy_setup.py` | Auto-generates random passwords |

---

*Last updated: 2026-08-25 — Passwords are now preserved across reseeds.*
