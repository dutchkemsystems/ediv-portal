# Proposal: Enterprise Staff Dashboard

## Scope
### In Scope
1. Backend API endpoint for staff profile data
2. Frontend StaffEnterpriseDashboard component
3. Dashboard routing integration
4. recharts installation

### Out of Scope
- Leave application workflow
- Performance review workflow
- Salary editing
- Profile photo upload

## Technical Approach
1. Add `staff_profile` action to `DashboardStatsViewSet` in analytics views
2. Create `StaffEnterpriseDashboard.jsx` with Material UI + Recharts
3. Add lazy import and role mapping in `Dashboard.jsx`

## Risk Assessment
- Low risk: Extending existing patterns
- No database migrations needed
- No new models required
