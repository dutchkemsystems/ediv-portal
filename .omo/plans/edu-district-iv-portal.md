# edu-district-iv-portal - Work Plan

## TL;DR (For humans)

**What you'll get:** A fully production-ready Education District IV Portal serving 80,000+ students, 5,000+ staff across 95 schools with E-File Movement, E-Registry, HR, Finance, and all 5 Departments operational.

**Why this approach:** Build on the existing 35+ Django apps and 41 React pages already in the codebase. Complete, test, and harden rather than rebuild. Phase-by-phase delivery ensures each module is production-ready before moving to the next.

**What it will NOT do:** Will not add new modules beyond what's already scaffolded. Will not change the tech stack. Will not break backward compatibility.

**Effort:** XL
**Risk:** Medium - Scale requirements (80K+ students) demand careful performance optimization
**Decisions to sanity-check:** Frontend completion scope, test coverage targets, deployment environment

Your next move: I'll begin Phase 1 execution immediately.

---

> TL;DR (machine): XL effort, Medium risk, 10-phase build completing existing Education District IV Portal for 80K+ students/5K+ staff/95 schools

## Scope
### Must have
- Complete all 35+ Django backend apps with full CRUD, custom actions, and audit logging
- Complete all 41 React frontend pages with Material-UI components
- Comprehensive test suites (backend: 80%+ coverage, frontend: critical paths)
- API documentation (OpenAPI/Swagger)
- Performance optimization for scale (database indexing, query optimization, caching)
- Security hardening (RBAC, encryption, audit trails)
- Docker production configuration
- Deployment scripts and documentation

### Must NOT have (guardrails, anti-slop, scope boundaries)
- No new Django apps beyond the 35+ already created
- No tech stack changes (keep Django/React/PostgreSQL)
- No breaking API changes without versioning
- No placeholder or stub code — everything must be production-ready
- No skipping test coverage requirements
- No security shortcuts (MFA, RBAC, encryption must be complete)

## Verification strategy
> Zero human intervention - all verification is agent-executed.
- Test decision: tests-after + framework (Django test for backend, Vitest for frontend)
- Evidence: .omo/evidence/task-<N>-edu-district-iv-portal.<ext>
- Backend: `python manage.py test` with coverage report
- Frontend: `npm run test` with coverage report
- API: `python manage.py spectacular` for OpenAPI schema validation
- Performance: Query count assertions, response time benchmarks
- Security: RBAC permission tests, audit log verification

## Execution strategy
### Parallel execution waves
> Target 5-8 todos per wave. Fewer than 3 (except the final) means you under-split.

**Wave 1 (Foundation):** Core modules — Users, Schools, Staff, Students, Departments
**Wave 2 (Academics):** Academics, Attendance, Timetable
**Wave 3 (Admin):** HR, Finance, Departments enhancement
**Wave 4 (Documents):** E-File Movement, E-Registry, Workflows
**Wave 5 (Support):** Communication, Notifications, Reports, Analytics
**Wave 6 (Specialized):** Inspection, Library, Transport, CPD, Wellness, Alumni, etc.
**Wave 7 (Frontend):** Complete all 41 React pages
**Wave 8 (Testing):** Comprehensive test suites
**Wave 9 (Docs):** API docs, user manuals
**Wave 10 (Deploy):** Production hardening

### Dependency matrix
| Todo | Depends on | Blocks | Can parallelize with |
| --- | --- | --- | --- |
| 1-5 (Foundation) | None | All subsequent phases | Each other |
| 6-8 (Academics) | Foundation | Frontend, Tests | Each other |
| 9-11 (Admin) | Foundation | Frontend, Tests | Each other |
| 12-14 (Documents) | Foundation | Frontend, Tests | Each other |
| 15-18 (Support) | Foundation | Frontend, Tests | Each other |
| 19-24 (Specialized) | Foundation | Frontend, Tests | Each other |
| 25-41 (Frontend) | All backend complete | Tests | Each other |
| 42-50 (Testing) | All code complete | Deployment | Each other |
| 51-55 (Docs) | All code complete | Deployment | Each other |
| 56-60 (Deploy) | All above complete | None | Each other |

## Todos
> Implementation + Test = ONE todo. Never separate.

### Wave 1: Foundation & Core

- [ ] 1. Complete Users App — Authentication, roles, JWT tokens, MFA
  What to do / Must NOT do: Ensure User model has all 22+ roles, JWT auth works with refresh tokens, MFA is functional, password reset works. Add missing API endpoints if any. Must NOT break existing auth flow.
  Parallelization: Wave 1 | Blocked by: None | Blocks: All subsequent phases
  References: backend/apps/users/models.py, views.py, serializers.py, urls.py, backend/config/settings/base.py (JWT settings)
  Acceptance criteria (agent-executable): `python manage.py test apps.users` passes, `python manage.py shell -c "from apps.users.models import User; print(User.objects.count())"` works, JWT token generation/refresh endpoints functional
  QA scenarios: happy — login with valid credentials returns JWT; failure — invalid credentials return 401; MFA — enable/disable MFA works; Evidence .omo/evidence/task-1-edu-district-iv-portal.json
  Commit: Y | feat(users): complete authentication, roles, JWT, MFA

- [ ] 2. Complete Schools App — 95 schools across 3 LGAs
  What to do / Must NOT do: Ensure School model has all fields (name, code, LGA, address, contact, type), CRUD operations work, school hierarchy is correct. Must NOT modify existing school data structure.
  Parallelization: Wave 1 | Blocked by: None | Blocks: All modules referencing schools
  References: backend/apps/schools/models.py, views.py, serializers.py, urls.py
  Acceptance criteria (agent-executable): `python manage.py test apps.schools` passes, 95 schools queryable, school CRUD endpoints functional
  QA scenarios: happy — list all 95 schools; create new school; update school; Evidence .omo/evidence/task-2-edu-district-iv-portal.json
  Commit: Y | feat(schools): complete school management for 95 schools

- [ ] 3. Complete Staff App — 5,000+ staff management
  What to do / Must NOT do: Ensure Staff model links to User, has department/school assignments, qualification tracking, employment history. CRUD and search functional. Must NOT break HR module references.
  Parallelization: Wave 1 | Blocked by: None | Blocks: HR, Finance, Attendance
  References: backend/apps/staff/models.py, views.py, serializers.py, urls.py
  Acceptance criteria (agent-executable): `python manage.py test apps.staff` passes, staff CRUD functional, staff search by name/department works
  QA scenarios: happy — list staff with pagination; search staff; create/update staff; Evidence .omo/evidence/task-3-edu-district-iv-portal.json
  Commit: Y | feat(staff): complete staff management for 5000+ staff

- [ ] 4. Complete Students App — 80,000+ students enrollment
  What to do / Must NOT do: Ensure Student model has enrollment, class assignment, guardian info, medical info. Bulk import/export works. Must NOT break Finance/Attendance references.
  Parallelization: Wave 1 | Blocked by: None | Blocks: Finance, Attendance, Academics
  References: backend/apps/students/models.py, views.py, serializers.py, urls.py
  Acceptance criteria (agent-executable): `python manage.py test apps.students` passes, student CRUD functional, bulk import works, 80K+ student queries optimized
  QA scenarios: happy — list students with pagination; search by name/class; bulk import CSV; Evidence .omo/evidence/task-4-edu-district-iv-portal.json
  Commit: Y | feat(students): complete student management for 80K+ students

- [ ] 5. Complete Departments App — Department and unit hierarchy
  What to do / Must NOT do: Ensure Department model has CORE/SUPPORT categories, parent-child hierarchy, Unit sub-departments. Department head assignment works. Must NOT break Files/Registry references.
  Parallelization: Wave 1 | Blocked by: None | Blocks: Files, Registry, HR
  References: backend/apps/departments/models.py, views.py, serializers.py, urls.py
  Acceptance criteria (agent-executable): `python manage.py test apps.departments` passes, department hierarchy queryable, unit CRUD functional
  QA scenarios: happy — list departments with units; create department with sub-departments; assign department head; Evidence .omo/evidence/task-5-edu-district-iv-portal.json
  Commit: Y | feat(departments): complete department and unit hierarchy

### Wave 2: Academic Modules

- [ ] 6. Complete Academics App — Classes, subjects, exams, report cards
  What to do / Must NOT do: Ensure ClassLevel, Subject, ClassAssignment, Exam, ExamResult models are complete. Report card generation works. Must NOT break Attendance/Timetable references.
  Parallelization: Wave 2 | Blocked by: Wave 1 | Blocks: Frontend, Tests
  References: backend/apps/academics/models.py, views.py, serializers.py, urls.py
  Acceptance criteria (agent-executable): `python manage.py test apps.academics` passes, class/subject CRUD functional, exam creation and result entry works
  QA scenarios: happy — create class level; assign subjects; create exam; enter results; generate report card; Evidence .omo/evidence/task-6-edu-district-iv-portal.json
  Commit: Y | feat(academics): complete academic management

- [ ] 7. Complete Attendance App — Student and staff attendance
  What to do / Must NOT do: Ensure DailyAttendance model tracks student/staff attendance by date/class. Attendance summary reports work. PWA offline capability for attendance. Must NOT break Students/Staff references.
  Parallelization: Wave 2 | Blocked by: Wave 1 | Blocks: Frontend, Tests
  References: backend/apps/attendance/models.py, views.py, serializers.py, urls.py
  Acceptance criteria (agent-executable): `python manage.py test apps.attendance` passes, attendance marking works, attendance summary reports generate
  QA scenarios: happy — mark attendance for class; view attendance summary; export attendance report; Evidence .omo/evidence/task-7-edu-district-iv-portal.json
  Commit: Y | feat(attendance): complete attendance tracking

- [ ] 8. Complete Timetable App — Class and teacher scheduling
  What to do / Must NOT do: Ensure Timetable model handles class/teacher/subject/time slot scheduling. Conflict detection works. Must NOT break Academics/Attendance references.
  Parallelization: Wave 2 | Blocked by: Wave 1 | Blocks: Frontend, Tests
  References: backend/apps/timetable/models.py, views.py, serializers.py, urls.py
  Acceptance criteria (agent-executable): `python manage.py test apps.timetable` passes, timetable CRUD functional, conflict detection works
  QA scenarios: happy — create timetable entry; detect scheduling conflicts; view teacher timetable; Evidence .omo/evidence/task-8-edu-district-iv-portal.json
  Commit: Y | feat(timetable): complete timetable scheduling

### Wave 3: Administrative Modules

- [ ] 9. Complete HR App — Job postings, applications, payroll, payslips
  What to do / Must NOT do: Ensure JobPosting, JobApplication, PayrollPeriod, Payslip models are complete. Salary calculations correct. Must NOT break Staff/Finance references.
  Parallelization: Wave 3 | Blocked by: Wave 1 | Blocks: Frontend, Tests
  References: backend/apps/hr/models.py, views.py, serializers.py, urls.py (lines 1-123)
  Acceptance criteria (agent-executable): `python manage.py test apps.hr` passes, job posting CRUD works, payroll processing generates payslips
  QA scenarios: happy — create job posting; apply for job; process payroll; generate payslip; Evidence .omo/evidence/task-9-edu-district-iv-portal.json
  Commit: Y | feat(hr): complete HR module with payroll

- [ ] 10. Complete Finance App — Fees, payments, budgets, grants
  What to do / Must NOT do: Ensure FeeStructure, StudentFee, Payment, Budget, Grant models work. KoraPay integration functional. Payment confirmation workflow. Must NOT break HR/Students references.
  Parallelization: Wave 3 | Blocked by: Wave 1 | Blocks: Frontend, Tests
  References: backend/apps/finance/models.py, views.py, serializers.py, urls.py, payment_views.py (lines 1-264)
  Acceptance criteria (agent-executable): `python manage.py test apps.finance` passes, fee structure CRUD works, payment processing functional, budget tracking works
  QA scenarios: happy — create fee structure; assign fee to student; process payment; confirm payment; track budget; Evidence .omo/evidence/task-10-edu-district-iv-portal.json
  Commit: Y | feat(finance): complete finance module with KoraPay

- [ ] 11. Complete Infrastructure App — Facilities, maintenance, projects
  What to do / Must NOT do: Ensure Facility, MaintenanceRequest, Project models are complete. Maintenance workflow works. Must NOT break Schools references.
  Parallelization: Wave 3 | Blocked by: Wave 1 | Blocks: Frontend, Tests
  References: backend/apps/infrastructure/models.py, views.py, serializers.py, urls.py (lines 1-143)
  Acceptance criteria (agent-executable): `python manage.py test apps.infrastructure` passes, facility CRUD works, maintenance request workflow functional
  QA scenarios: happy — create facility; submit maintenance request; approve request; track project; Evidence .omo/evidence/task-11-edu-district-iv-portal.json
  Commit: Y | feat(infrastructure): complete facility and project management

### Wave 4: Document Management

- [ ] 12. Complete Files App — E-File Movement with tracking
  What to do / Must NOT do: Ensure File, FileMovement, FileAttachment, FileComment models work. File numbering, movement, approval, escalation, timeline all functional. Audit logging complete. Must NOT break Departments/Registry references.
  Parallelization: Wave 4 | Blocked by: Wave 1 | Blocks: Frontend, Tests
  References: backend/apps/files/models.py, views.py, serializers.py, urls.py (lines 1-462)
  Acceptance criteria (agent-executable): `python manage.py test apps.files` passes, file creation with auto-numbering works, file movement between holders works, approval workflow functional, audit trail complete
  QA scenarios: happy — create file; move file to another holder; receive file; approve file; escalate file; view timeline; Evidence .omo/evidence/task-12-edu-district-iv-portal.json
  Commit: Y | feat(files): complete E-File Movement system

- [ ] 13. Complete Registry App — E-Registry with document management
  What to do / Must NOT do: Ensure Document, Correspondence, Filing, DocumentVersion, MemoWorkflow, MemoApproval, MemoCirculation models work. Memo approval and circulation workflows functional. Must NOT break Files/Departments references.
  Parallelization: Wave 4 | Blocked by: Wave 1 | Blocks: Frontend, Tests
  References: backend/apps/registry/models.py, views.py, serializers.py, urls.py (lines 1-200)
  Acceptance criteria (agent-executable): `python manage.py test apps.registry` passes, document CRUD works, memo workflow with approval/circulation functional, version tracking works
  QA scenarios: happy — create document; start memo workflow; approve memo; circulate memo; track versions; Evidence .omo/evidence/task-13-edu-district-iv-portal.json
  Commit: Y | feat(registry): complete E-Registry system

- [ ] 14. Complete Workflows App — Task assignment, approval, escalation
  What to do / Must NOT do: Ensure Workflow, WorkflowStep, WorkflowInstance, Task models work. Workflow execution engine functional. Must NOT break Files/Registry references.
  Parallelization: Wave 4 | Blocked by: Wave 1 | Blocks: Frontend, Tests
  References: backend/apps/workflows/models.py, views.py, serializers.py, urls.py (lines 1-140)
  Acceptance criteria (agent-executable): `python manage.py test apps.workflows` passes, workflow creation works, step execution works, task assignment works
  QA scenarios: happy — create workflow; add steps; start workflow instance; complete tasks; Evidence .omo/evidence/task-14-edu-district-iv-portal.json
  Commit: Y | feat(workflows): complete workflow automation

### Wave 5: Support Modules

- [ ] 15. Complete Communication App — Internal messaging, circulars
  What to do / Must NOT do: Ensure Message, Conversation, Circular models work. Message threading, read receipts functional. Must NOT break Notifications references.
  Parallelization: Wave 5 | Blocked by: Wave 1 | Blocks: Frontend, Tests
  References: backend/apps/communication/models.py, views.py, serializers.py, urls.py
  Acceptance criteria (agent-executable): `python manage.py test apps.communication` passes, messaging works, circular creation/distribution works
  QA scenarios: happy — send message; create conversation; post circular; mark as read; Evidence .omo/evidence/task-15-edu-district-iv-portal.json
  Commit: Y | feat(communication): complete internal messaging

- [ ] 16. Complete Notifications App — Real-time notifications
  What to do / Must NOT do: Ensure Notification model with channels (in-app, email, SMS) works. Notification preferences work. Must NOT break Communication references.
  Parallelization: Wave 5 | Blocked by: Wave 1 | Blocks: Frontend, Tests
  References: backend/apps/notifications/models.py, views.py, serializers.py, urls.py
  Acceptance criteria (agent-executable): `python manage.py test apps.notifications` passes, notification creation works, notification preferences functional
  QA scenarios: happy — create notification; mark as read; set preferences; Evidence .omo/evidence/task-16-edu-district-iv-portal.json
  Commit: Y | feat(notifications): complete notification system

- [ ] 17. Complete Reports App — Reporting and analytics
  What to do / Must NOT do: Ensure ReportTemplate, GeneratedReport models work. Report generation with filters works. Must NOT break Analytics references.
  Parallelization: Wave 5 | Blocked by: Wave 1 | Blocks: Frontend, Tests
  References: backend/apps/reports/models.py, views.py, serializers.py, urls.py
  Acceptance criteria (agent-executable): `python manage.py test apps.reports` passes, report generation works, PDF/Excel export works
  QA scenarios: happy — create report template; generate report; export to PDF; Evidence .omo/evidence/task-17-edu-district-iv-portal.json
  Commit: Y | feat(reports): complete reporting system

- [ ] 18. Complete Analytics App — Dashboard statistics
  What to do / Must NOT do: Ensure analytics endpoints return correct aggregations for dashboard. Must NOT break Reports references.
  Parallelization: Wave 5 | Blocked by: Wave 1 | Blocks: Frontend, Tests
  References: backend/apps/analytics/models.py, views.py, serializers.py, urls.py
  Acceptance criteria (agent-executable): `python manage.py test apps.analytics` passes, dashboard stats endpoints return correct data
  QA scenarios: happy — get student count; get staff count; get attendance summary; get finance summary; Evidence .omo/evidence/task-18-edu-district-iv-portal.json
  Commit: Y | feat(analytics): complete analytics dashboard

### Wave 6: Specialized Modules

- [ ] 19. Complete Inspection App — School inspection tracking
  What to do / Must NOT do: Ensure Inspection, InspectionChecklist, InspectionReport models work. Inspection workflow functional. Must NOT break Schools references.
  Parallelization: Wave 6 | Blocked by: Wave 1 | Blocks: Frontend, Tests
  References: backend/apps/inspection/models.py, views.py, serializers.py, urls.py
  Acceptance criteria (agent-executable): `python manage.py test apps.inspection` passes, inspection CRUD works, checklist scoring works
  QA scenarios: happy — create inspection; fill checklist; submit report; Evidence .omo/evidence/task-19-edu-district-iv-portal.json
  Commit: Y | feat(inspection): complete inspection module

- [ ] 20. Complete Library App — Library management
  What to do / Must NOT do: Ensure Book, BookLoan, LibraryMember models work. Book catalog and loan tracking functional. Must NOT break Schools references.
  Parallelization: Wave 6 | Blocked by: Wave 1 | Blocks: Frontend, Tests
  References: backend/apps/library/models.py, views.py, serializers.py, urls.py
  Acceptance criteria (agent-executable): `python manage.py test apps.library` passes, book CRUD works, loan tracking works
  QA scenarios: happy — add book; checkout book; return book; Evidence .omo/evidence/task-20-edu-district-iv-portal.json
  Commit: Y | feat(library): complete library management

- [ ] 21. Complete Transport App — School transport management
  What to do / Must NOT do: Ensure Route, Vehicle, BusAssignment models work. Route optimization functional. Must NOT break Schools references.
  Parallelization: Wave 6 | Blocked by: Wave 1 | Blocks: Frontend, Tests
  References: backend/apps/transport/models.py, views.py, serializers.py, urls.py
  Acceptance criteria (agent-executable): `python manage.py test apps.transport` passes, route CRUD works, vehicle tracking works
  QA scenarios: happy — create route; assign vehicle; track bus; Evidence .omo/evidence/task-21-edu-district-iv-portal.json
  Commit: Y | feat(transport): complete transport management

- [ ] 22. Complete CPD App — Continuing professional development
  What to do / Must NOT do: Ensure Training, TrainingEnrollment, Certification models work. Training tracking functional. Must NOT break Staff references.
  Parallelization: Wave 6 | Blocked by: Wave 1 | Blocks: Frontend, Tests
  References: backend/apps/cpd/models.py, views.py, serializers.py, urls.py
  Acceptance criteria (agent-executable): `python manage.py test apps.cpd` passes, training CRUD works, enrollment tracking works
  QA scenarios: happy — create training; enroll staff; track completion; Evidence .omo/evidence/task-22-edu-district-iv-portal.json
  Commit: Y | feat(cpd): complete professional development module

- [ ] 23. Complete Wellness App — Student/staff wellness tracking
  What to do / Must NOT do: Ensure WellnessRecord, CounselingSession models work. Wellness tracking functional. Must NOT break Students/Staff references.
  Parallelization: Wave 6 | Blocked by: Wave 1 | Blocks: Frontend, Tests
  References: backend/apps/wellness/models.py, views.py, serializers.py, urls.py
  Acceptance criteria (agent-executable): `python manage.py test apps.wellness` passes, wellness records CRUD works, counseling sessions tracked
  QA scenarios: happy — create wellness record; schedule counseling; Evidence .omo/evidence/task-23-edu-district-iv-portal.json
  Commit: Y | feat(wellness): complete wellness module

- [ ] 24. Complete remaining specialized apps (Alumni, Assets, Discipline, CoCurricular, French, ELearning, ParentTeacher, DataImportExport, MailWorkflow, Audit)
  What to do / Must NOT do: Ensure all remaining apps have complete models, views, serializers, URLs. Each app must pass tests. Must NOT break core module references.
  Parallelization: Wave 6 | Blocked by: Wave 1 | Blocks: Frontend, Tests
  References: backend/apps/alumni/, backend/apps/assets/, backend/apps/discipline/, backend/apps/co_curricular/, backend/apps/french/, backend/apps/e_learning/, backend/apps/parent_teacher/, backend/apps/data_import_export/, backend/apps/mail_workflow/, backend/apps/audit/
  Acceptance criteria (agent-executable): `python manage.py test apps.alumni apps.assets apps.discipline apps.co_curricular apps.french apps.e_learning apps.parent_teacher apps.data_import_export apps.mail_workflow apps.audit` passes
  QA scenarios: happy — CRUD operations work for each app; Evidence .omo/evidence/task-24-edu-district-iv-portal.json
  Commit: Y | feat(specialized): complete all specialized modules

### Wave 7: Frontend Completion

- [ ] 25-41. Complete all 41 React frontend pages
  What to do / Must NOT do: Ensure all 41 pages (Dashboard, Login, Landing, Academics, Alumni, Assets, Attendance, Audit, CoCurricular, Communication, CPD, DataImportExport, Departments, Discipline, ELearning, Files, Finance, French, Grants, HR, Infrastructure, Inspection, Library, MailWorkflow, MemoWorkflow, Notifications, ParentTeacher, Privileges, Registry, Reports, Schools, Staff, Students, Timetable, Transport, Wellness, Workflows) are fully functional with Material-UI components, proper state management, API integration, error handling, and responsive design. Must NOT break backend API contracts.
  Parallelization: Wave 7 | Blocked by: Waves 1-6 | Blocks: Wave 8
  References: frontend/src/pages/, frontend/src/components/, frontend/src/store/, frontend/src/api/
  Acceptance criteria (agent-executable): `npm run test` passes, all pages render correctly, API integration works, responsive design verified
  QA scenarios: happy — navigate to each page; perform CRUD operations; verify responsive design; Evidence .omo/evidence/task-25-41-edu-district-iv-portal.json
  Commit: Y | feat(frontend): complete all 41 React pages

### Wave 8: Testing & QA

- [ ] 42-50. Comprehensive test suites
  What to do / Must NOT do: Backend: 80%+ test coverage for all apps. Frontend: critical path tests for all pages. Integration tests for API endpoints. Performance tests for scale. Must NOT skip any module.
  Parallelization: Wave 8 | Blocked by: Waves 1-7 | Blocks: Wave 9
  References: backend/apps/*/tests.py, frontend/src/__tests__/,
  Acceptance criteria (agent-executable): `python manage.py test --coverage` shows 80%+, `npm run test:coverage` shows critical paths covered
  QA scenarios: happy — all tests pass; coverage thresholds met; Evidence .omo/evidence/task-42-50-edu-district-iv-portal.json
  Commit: Y | test: comprehensive test suites for all modules

### Wave 9: Documentation

- [ ] 51-55. API docs, user manuals, deployment guides
  What to do / Must NOT do: Generate OpenAPI schema, write API documentation, create user manuals for each role, write deployment guide. Must NOT include sensitive information.
  Parallelization: Wave 9 | Blocked by: Waves 1-8 | Blocks: Wave 10
  References: docs/
  Acceptance criteria (agent-executable): `python manage.py spectacular` generates valid schema, docs/API_DOCS.md exists, docs/USER_MANUAL.md exists, docs/DEPLOYMENT.md exists
  QA scenarios: happy — API docs render correctly; user manuals cover all roles; deployment guide works; Evidence .omo/evidence/task-51-55-edu-district-iv-portal.json
  Commit: Y | docs: complete API and user documentation

### Wave 10: Deployment & Production

- [ ] 56-60. Production hardening and deployment
  What to do / Must NOT do: Docker production configuration, Nginx optimization, SSL setup, database optimization, caching strategy, monitoring setup, backup strategy. Must NOT expose secrets.
  Parallelization: Wave 10 | Blocked by: Waves 1-9 | Blocks: None
  References: docker/, scripts/, docker-compose.yml, nginx/
  Acceptance criteria (agent-executable): `docker-compose -f docker-compose.prod.yml up -d` works, health check passes, all services running
  QA scenarios: happy — deploy to staging; verify all services; run smoke tests; Evidence .omo/evidence/task-56-60-edu-district-iv-portal.json
  Commit: Y | deploy: production configuration and deployment

## Final verification wave
> Runs in parallel after ALL todos. ALL must APPROVE. Surface results and wait for the user's explicit okay before declaring complete.
- [ ] F1. Plan compliance audit — Verify all todos completed, all acceptance criteria met
- [ ] F2. Code quality review — Linting, type checking, code standards
- [ ] F3. Real manual QA — Test all critical user journeys end-to-end
- [ ] F4. Scope fidelity — Verify no scope creep, all Must NOT have respected

## Commit strategy
- Each todo results in a single atomic commit
- Commit message format: `feat(<scope>): <summary>` or `test(<scope>): <summary>` or `docs(<scope>): <summary>`
- All commits follow conventional commits standard
- No commits without passing tests

## Success criteria
- [ ] All 35+ backend apps pass tests with 80%+ coverage
- [ ] All 41 frontend pages functional and responsive
- [ ] API response time < 200ms for 95% of endpoints
- [ ] Page load time < 2.5s
- [ ] System handles 10,000+ concurrent users
- [ ] Zero critical security vulnerabilities
- [ ] Complete audit trail for all actions
- [ ] All documentation complete and accurate
- [ ] Production deployment successful
