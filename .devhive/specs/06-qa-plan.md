# QA Plan: Enterprise Staff Dashboard

## Test Coverage
- Backend endpoint: Python syntax verified, AST parsed successfully
- Frontend build: Vite build completed with 0 errors
- Component imports: All MUI icons verified against available exports

## Manual Verification
- [x] Backend views.py compiles without syntax errors
- [x] Frontend builds without errors (Vite production build)
- [x] Recharts library installed and importable
- [x] StaffEnterpriseDashboard component exported correctly
- [x] Dashboard.jsx lazy import and role mapping configured

## Areas for Future Testing
1. Unit tests for `staff_profile` view (mock Staff, User, StaffLeave, StaffPerformance)
2. Integration test: GET `/api/analytics/stats/staff-profile/{id}/` with auth
3. E2E test: Login as staff user, verify dashboard renders
4. Visual regression test: Dashboard layout on mobile/tablet/desktop
