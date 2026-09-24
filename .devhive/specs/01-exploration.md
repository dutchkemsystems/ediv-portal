# Exploration: Enterprise Staff Dashboard

## Existing Code Analysis
- **Staff Model** (`backend/apps/staff/models.py`): Has all required fields including computed `years_of_service` property
- **Analytics Views** (`backend/apps/analytics/views.py`): `DashboardStatsViewSet` pattern with `@action` decorators
- **Analytics URLs** (`backend/apps/analytics/urls.py`): Router registered at `stats/` basename
- **Dashboard.jsx**: Uses `roleDashboards` mapping for role-based routing
- **Existing Dashboards**: 7 role-based components in `frontend/src/components/dashboard/`

## Dependencies
- **recharts**: Not installed — needs `npm install recharts`
- **MUI Icons**: Already installed (`@mui/icons-material`)
- **Axios client**: Available at `frontend/src/api/client.js`

## Key Observations
- Staff model has `years_of_service` property already
- User model has `first_name`, `last_name`, `email`, `phone_number`
- StaffLeave and StaffPerformance models exist with all needed fields
- No `STAFF` role in User.Role — need to check if staff users use TCH/PRI/VP roles
