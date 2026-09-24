# Architecture: Enterprise Staff Dashboard

## Backend
- **Endpoint**: `GET /api/analytics/stats/staff-profile/{user_id}/`
- **ViewSet**: `DashboardStatsViewSet` (existing) with new `@action`
- **Pattern**: Inline imports, computed properties, DRF Response

## Frontend
- **Component**: `StaffEnterpriseDashboard.jsx` (lazy-loaded)
- **State**: Local useState/useEffect with axios fetch
- **Charts**: Recharts (RadarChart, RadialBarChart)
- **Layout**: MUI Grid with responsive breakpoints

## Data Flow
1. Frontend calls `/api/analytics/stats/staff-profile/{user_id}/`
2. Backend queries Staff, StaffLeave, StaffPerformance
3. Backend computes derived fields (age, years_of_service, etc.)
4. Frontend renders profile banner, cards, and charts
