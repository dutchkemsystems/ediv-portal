# PRD: Enterprise Staff Dashboard

## Overview
Build an Enterprise Staff Profile API endpoint and a professional 4K-quality Staff Dashboard component for the Education District IV Portal.

## Problem Statement
Staff members need a comprehensive personal dashboard showing their employment details, service timeline, performance metrics, and leave summary — all in one professional view.

## Target Users
- Staff members (TCH, PRI, VP roles)
- HR administrators
- System administrators

## Feature Requirements
1. **Backend API**: `GET /api/analytics/stats/staff-profile/{user_id}/` returning personal info, employment info, service timeline, school history, financial info, performance, and leave summary
2. **Frontend Dashboard**: `StaffEnterpriseDashboard.jsx` with profile banner, service timeline, key metrics, employment details, performance chart, leave summary, and Recharts visualizations

## Acceptance Criteria
- [ ] Backend endpoint returns all 7 data categories
- [ ] Frontend displays all sections with Lagos State branding
- [ ] Responsive grid layout works on all screen sizes
- [ ] Recharts radar chart shows performance scores
- [ ] Dashboard routes correctly from Dashboard.jsx for staff users
