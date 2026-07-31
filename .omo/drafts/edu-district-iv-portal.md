---
slug: edu-district-iv-portal
status: drafting
intent: clear
pending-action: write .omo/plans/edu-district-iv-portal.md
approach: Complete the existing Education District IV Portal by implementing missing frontend pages, adding comprehensive tests, enhancing API endpoints, and ensuring all modules are production-ready for 80,000+ students and 5,000+ staff across 95 schools.
---

# Draft: edu-district-iv-portal

## Components (topology ledger)
<!-- Lock the SHAPE before depth. One row per top-level component that can succeed or fail independently. -->
<!-- id | outcome (one line) | status: active|deferred | evidence path -->

| ID | Component | Outcome | Status | Evidence Path |
|----|-----------|---------|--------|---------------|
| C1 | E-File Movement | Complete file tracking, movement, approval workflows with audit logging | active | backend/apps/files/models.py, views.py |
| C2 | E-Registry | Document management, correspondence, filing, memo workflows | active | backend/apps/registry/models.py |
| C3 | HR Module | Job postings, applications, payroll, payslips for 5,000+ staff | active | backend/apps/hr/models.py, views.py |
| C4 | Finance Module | Fee structures, student fees, payments, budgets, grants with KoraPay integration | active | backend/apps/finance/models.py, views.py |
| C5 | Departments | Department and unit management with hierarchy | active | backend/apps/departments/models.py |
| C6 | Frontend Pages | 41 React pages with Material-UI components | active | frontend/src/pages/ |
| C7 | API Backend | 30+ Django REST Framework endpoints with JWT auth | active | backend/config/urls.py |
| C8 | Infrastructure | Docker, Nginx, CI/CD, PostgreSQL, Redis | active | docker/, scripts/ |

## Open assumptions (announced defaults)
<!-- Record any default you adopt instead of asking, so the user can veto it at the gate. -->
<!-- assumption | adopted default | rationale | reversible? -->

| Assumption | Adopted Default | Rationale | Reversible? |
|------------|-----------------|-----------|-------------|
| Tech stack | Django 4.2+ / React 18+ / PostgreSQL 16+ | Already configured in codebase | No |
| Authentication | JWT with refresh tokens | Already implemented in settings | No |
| UI Framework | Material-UI 5 | Already in package.json | No |
| Payment Gateway | KoraPay | Already integrated in finance app | No |
| Testing Framework | Vitest (frontend) / Django test (backend) | Already configured | No |
| Deployment | Docker Compose | Already in project structure | No |

## Findings (cited - path:lines)

### Backend Structure (35+ Django apps)
- **Users**: Authentication, roles, JWT tokens
- **Schools**: 95 schools across 3 LGAs (Apapa, Mainland, Surulere)
- **Staff**: 5,000+ staff management
- **Students**: 80,000+ students with enrollment
- **Academics**: Classes, subjects, exams, report cards
- **Attendance**: Student and staff attendance tracking
- **Finance**: Fee structures, payments, budgets, grants (KoraPay integrated)
- **HR**: Job postings, applications, payroll, payslips
- **Files**: E-File Movement with tracking, approval workflows, audit logging
- **Registry**: E-Registry with document management, correspondence, memo workflows
- **Departments**: Department and unit hierarchy
- **Workflows**: Task assignment, approval, escalation
- **Notifications**: Real-time notifications
- **Analytics**: Dashboard statistics and reports
- **And 20+ more apps**: inspection, co_curricular, french, infrastructure, library, e_learning, wellness, alumni, assets, discipline, timetable, transport, cpd, audit, parent_teacher, data_import_export, mail_workflow

### Frontend Structure (41 React pages)
- Dashboard, Login, Landing, ForgotPassword, ResetPassword, MFASetup, MFAVerify
- All module pages: Academics, Alumni, Assets, Attendance, Audit, CoCurricular, Communication, CPD, DataImportExport, Departments, Discipline, ELearning, Files, Finance, French, Grants, HR, Infrastructure, Inspection, Library, MailWorkflow, MemoWorkflow, Notifications, ParentTeacher, Privileges, Registry, Reports, Schools, Staff, Students, Timetable, Transport, Wellness, Workflows

### API Endpoints (30+ routes)
- /api/users/ - Authentication and user management
- /api/schools/ - School management
- /api/staff/ - Staff management
- /api/students/ - Student management
- /api/academics/ - Academic management
- /api/attendance/ - Attendance tracking
- /api/finance/ - Finance management (with payment initialization, webhook, verification)
- /api/hr/ - HR management
- /api/files/ - E-File Movement
- /api/registry/ - E-Registry
- /api/departments/ - Department management
- /api/workflows/ - Workflow automation
- /api/notifications/ - Notifications
- /api/analytics/ - Analytics and reports
- And 15+ more endpoints

### Key Features Already Implemented
1. **E-File Movement**: Complete with file tracking, movement between holders, approval workflows, status timeline, audit logging
2. **E-Registry**: Document management, correspondence tracking, filing system, memo workflows with approval and circulation
3. **HR Module**: Job postings, applications, payroll periods, payslips with salary calculations
4. **Finance Module**: Fee structures, student fees, payment processing (KoraPay), budgets, grants
5. **Authentication**: JWT with refresh tokens, MFA support, role-based access control (22+ roles)
6. **Audit Logging**: Comprehensive audit trail for all actions
7. **Payment Integration**: KoraPay for online payments with webhook handling

## Decisions (with rationale)

| Decision | Rationale |
|----------|-----------|
| Use existing Django/React stack | Already configured and partially implemented |
| Maintain KoraPay integration | Already integrated and tested |
| Follow existing code patterns | Ensure consistency across modules |
| Use Material-UI 5 | Already in dependencies, consistent UI |
| Implement comprehensive tests | Production-ready quality for 80K+ students |

## Scope IN

### Must Complete
1. **Frontend Pages**: Ensure all 41 pages are fully functional with proper UI/UX
2. **API Endpoints**: Complete any missing CRUD operations and custom actions
3. **Tests**: Add comprehensive test suites for backend and frontend
4. **Documentation**: Update API docs, user manuals, deployment guides
5. **Performance**: Optimize queries for 80K+ students, 5K+ staff, 95 schools
6. **Security**: Ensure RBAC, audit logging, data encryption are complete
7. **Mobile**: Ensure responsive design works on all devices
8. **PWA**: Complete offline capability for attendance

### Must NOT Have (guardrails, anti-slop, scope boundaries)
1. **No new tech stacks**: Use existing Django/React/PostgreSQL
2. **No breaking changes**: Maintain backward compatibility
3. **No scope creep**: Focus on completing existing modules, not adding new ones
4. **No shortcuts**: Production-ready quality, no placeholder code
5. **No security compromises**: Maintain all security features

## Open questions

1. **Frontend Completion Status**: Are all 41 frontend pages fully implemented, or are some scaffolded/incomplete?
2. **Test Coverage**: What's the current test coverage for backend and frontend?
3. **Performance Issues**: Are there any known performance bottlenecks with the current implementation?
4. **Deployment Status**: Is the system currently deployed and in use, or still in development?
5. **User Feedback**: Have any users tested the system and provided feedback?

## Approval gate
status: awaiting-approval
pending-action: write .omo/plans/edu-district-iv-portal.md
approach: Complete the existing Education District IV Portal by implementing missing frontend pages, adding comprehensive tests, enhancing API endpoints, and ensuring all modules are production-ready for 80,000+ students and 5,000+ staff across 95 schools.
