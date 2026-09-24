# Semantic Memories

<!-- sem-001 -->
## Backend Stack
- **Framework**: Django 4.2 + DRF + SimpleJWT
- **Structure**: Apps under `backend/apps/` (staff, analytics, users, schools, students, finance, attendance, discipline, files, workflows, departments)
- **Database**: PostgreSQL (psycopg2-binary)
- **Tags**: backend, django, drf, architecture
- **Score**: 0.95

<!-- sem-002 -->
## Frontend Stack
- **Framework**: React 18 + Vite
- **UI**: Material UI 5 (@mui/material, @mui/icons-material, @mui/x-data-grid)
- **State**: Redux Toolkit + React Redux
- **Charts**: ApexCharts (react-apexcharts)
- **Routing**: React Router 6
- **Tags**: frontend, react, vite, mui, redux
- **Score**: 0.95

<!-- sem-003 -->
## Dashboard Routing Pattern
- Dashboard.jsx uses `roleDashboards` mapping: `{ ROLE: LazyComponent }`
- Each role has a dedicated lazy-loaded dashboard component
- Components stored in `frontend/src/components/dashboard/`
- **Tags**: frontend, dashboard, routing, pattern
- **Score**: 0.9

<!-- sem-004 -->
## Analytics API Pattern
- ViewSet at `backend/apps/analytics/views.py` with `DashboardStatsViewSet`
- Uses `@action(detail=False, methods=["get"])` for each dashboard endpoint
- Router registered at `/analytics/stats/`
- **Tags**: backend, analytics, api, pattern
- **Score**: 0.9

<!-- sem-005 -->
## Staff Model Fields
- Core: user, staff_id, employee_number, school, department
- Classification: category, designation, employment_type, qualification
- Personal: date_of_birth, gender, marital_status, state_of_origin, lga_of_origin
- Timeline: date_joined, date_of_first_appointment, date_of_retirement
- Compensation: grade_level, step, salary, pension_pin, tax_id
- Banking: bank_name, bank_account_number, bank_account_name
- Media: profile_photo
- **Tags**: backend, staff, model, fields
- **Score**: 0.95

<!-- sem-006 -->
## Lagos State Branding
- Red: #C8102E
- Green: #00843D
- Gold: #D4A017
- Used throughout dashboard components
- **Tags**: design, colors, branding
- **Score**: 0.95

<!-- sem-007 -->
## User Model
- Extends AbstractUser, no username field (email is USERNAME_FIELD)
- Role-based access via `Role` TextChoices
- Key roles: SYSADMIN, TG_PS, HR, FIN, PRI, VP, TCH, REG, PAR
- **Tags**: backend, users, auth, model
- **Score**: 0.9
