# RBAC Implementation Tasks

## Feature: Role-Based Access Control (RBAC) for All API Endpoints

### Backend Tasks
- [ ] Create `backend/config/rbac.py` with centralized RBAC permission system
- [ ] Update `backend/config/permissions.py` to integrate with new RBAC system
- [ ] Update `backend/apps/finance/views.py` with RBAC permissions
- [ ] Update `backend/apps/hr/views.py` with RBAC permissions
- [ ] Update `backend/apps/academics/views.py` with RBAC permissions
- [ ] Update `backend/apps/attendance/views.py` with RBAC permissions
- [ ] Update `backend/apps/students/views.py` with RBAC permissions
- [ ] Update `backend/apps/staff/views.py` with RBAC permissions
- [ ] Update `backend/apps/files/views.py` with RBAC permissions
- [ ] Update `backend/apps/mail_workflow/views.py` with RBAC permissions
- [ ] Add school-scoped filtering for school-level users

### Data Tasks
- [ ] No new models needed (uses existing User.role, Privilege, RolePrivilege)

### Documentation Tasks
- [ ] N/A

### Release Tasks
- [ ] N/A
