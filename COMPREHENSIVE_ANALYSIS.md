# Education District IV Portal — Full System Analysis & Optimization Report

**Date:** August 25, 2026
**Scope:** Complete analysis from System Admin/Tutor General/PS down to the least person across 95 schools

---

## TABLE OF CONTENTS

1. [Deployment Automation](#1-deployment-automation)
2. [System Architecture Overview](#2-system-architecture-overview)
3. [User Hierarchy & Role Analysis](#3-user-hierarchy--role-analysis)
4. [School Management (95 Schools)](#4-school-management-95-schools)
5. [Mail Workflow & Communication](#5-mail-workflow--communication)
6. [Registry & Document Management](#6-registry--document-management)
7. [Academics, Attendance & Timetable](#7-academics-attendance--timetable)
8. [Finance & HR Systems](#8-finance--hr-systems)
9. [Cross-Cutting Concerns](#9-cross-cutting-concerns)
10. [International Standards Compliance](#10-international-standards-compliance)
11. [Error Analysis & Gaps](#11-error-analysis--gaps)
12. [Recommendations for Optimal Performance](#12-recommendations-for-optimal-performance)

---

## 1. DEPLOYMENT AUTOMATION

### What Was Fixed
- `render.yaml`: Seed commands now run sequentially (was parallel with `&`, causing race conditions)
- `requirements.txt`: Added `dj-database-url`, `cloudinary`; removed `channels-redis` (Render-free-tier incompatible)
- `backend/requirements/render.txt`: Added missing `dj-database-url` and `cloudinary`
- `Dockerfile`: Changed `;` to `&&` in CMD (app now stops on migration/seeding failure)
- `DEPLOY_NOW.md`: Corrected build/start commands and env var references

### Render Automation Script Created
**File:** `scripts/render_deploy_setup.py`
- Auto-generates `DJANGO_SECRET_KEY` and all 6 seed passwords
- Sets them via Render API
- Usage: `export RENDER_API_KEY="..." && python scripts/render_deploy_setup.py`

### Required Manual Secrets on Render
| Secret | Purpose |
|--------|---------|
| `ADMIN_PASSWORD` | System admin login |
| `TG_PASSWORD` | Tutor General login |
| `HEAD_OFFICE_PASSWORD` | Department heads login |
| `SCHOOL_STAFF_PASSWORD` | Principals/VPs login |
| `TEACHER_PASSWORD` | Teachers login |
| `STUDENT_PASSWORD` | Students login |
| `EMAIL_HOST_USER` | Gmail SMTP username |
| `EMAIL_HOST_PASSWORD` | Gmail app password |
| `KORA_PAY_PUBLIC_KEY` | Payment gateway |
| `KORA_PAY_SECRET_KEY` | Payment gateway |

---

## 2. SYSTEM ARCHITECTURE OVERVIEW

### Technology Stack
| Layer | Technology |
|-------|-----------|
| Backend | Django 4.2 + DRF + SimpleJWT |
| Frontend | React 18 + Vite + Material UI + Redux |
| Database | PostgreSQL (Render free tier) |
| Cache/Queue | Redis (optional) |
| Deployment | Render (web service + static site) |
| Payments | KoraPay |
| Email | Gmail SMTP (port 587, TLS) |

### Application Count
**30+ Django apps** across these categories:

| Category | Apps |
|----------|------|
| Core | users, schools, departments, staff, students |
| Academic | academics, attendance, timetable, e_learning |
| Administrative | finance, hr, registry, files, workflows |
| Communication | communication, mail_workflow, notifications, push_notifications |
| Analytics | analytics, predictive_analytics, benchmarking, iot_dashboard |
| Specialized | report_card_gen, parent_teacher, discipline, inspection |
| Modern | chatbot, blockchain_cert, gamification, multilingual |
| Infrastructure | infrastructure, transport, library, assets, wellness, alumni, cpd, co_curricular, french |

### API Endpoint Count
Approximately **400+ REST endpoints** across all apps.

---

## 3. USER HIERARCHY & ROLE ANALYSIS

### Complete Role Hierarchy (22 Roles)

```
LEVEL 1 — SYSTEM ADMINISTRATION
├── SYSADMIN    System Administrator (superuser, full access)
└── TG_PS       Tutor General / Permanent Secretary (full access)

LEVEL 2 — DEPARTMENT HEADS (Head Office, 13 roles)
├── HR          Admin & HR Head
├── FIN         Finance Director
├── AUDIT       Internal Audit Head
├── QA          Quality Assurance Head
├── CC          Co-Curricular Head
├── EMIS        EMIS Head
├── PLAN        Planning Head
├── PROC        Procurement Head
├── PA          Public Affairs Head
├── SA          Schools Admin Head
├── FRENCH      French Unit Head
├── REG         Registry Head
└── SPD         Special Duties Head

LEVEL 3 — SCHOOL MANAGEMENT (per school)
├── PRI         Principal
└── VP          Vice Principal

LEVEL 4 — SCHOOL STAFF (per school)
├── TCH         Teacher
├── SA_OFF      School Admin Officer
└── REG_OFF     Registry Officer

LEVEL 5 — END USERS
├── STD         Student
└── PAR         Parent
```

### Authentication & Security
- **JWT tokens** with 30-min access / 7-day refresh
- **MFA support** via TOTP (pyotp)
- **Account lockout** after 5 failed attempts (30-min lock)
- **Password policy**: 12-char minimum, complexity requirements
- **Session management**: 30-min idle, 8-hr absolute, role-based concurrency limits
- **Rate limiting**: 100/hr anonymous, 1000/hr authenticated

### Module Access Matrix
| Role | Dashboard | Students | Staff | Academics | Attendance | Finance | Reports | Mail |
|------|-----------|----------|-------|-----------|------------|---------|---------|------|
| SYSADMIN | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| TG_PS | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| HR | ✓ | — | ✓ | — | — | — | ✓ | ✓ |
| FIN | ✓ | — | — | — | — | ✓ | ✓ | ✓ |
| PRI | ✓ | ✓ | ✓ | ✓ | ✓ | — | ✓ | ✓ |
| VP | ✓ | ✓ | ✓ | ✓ | ✓ | — | ✓ | ✓ |
| TCH | ✓ | ✓* | ✓* | ✓ | ✓ | — | ✓ | ✓ |
| STD | ✓ | ✓* | — | ✓ | ✓* | — | ✓ | ✓ |
| PAR | ✓ | ✓* | — | — | — | ✓* | ✓ | ✓ |

*Limited to own scope

---

## 4. SCHOOL MANAGEMENT (95 SCHOOLS)

### Distribution
| LGA | Junior | Senior | Total | Code Range |
|-----|--------|--------|-------|------------|
| APAPA | 15 | 15 | 30 | APU001-APU030 |
| MAINLAND | 18 | 17 | 35 | MLA001-MLA035 |
| SURULERE | 15 | 15 | 30 | SUR001-SUR030 |

### School Model Fields
22 fields including: name, code, school_type (JUNIOR/SENIOR), lga, address, phone, email, website, principal (FK→User), vice_principal (FK→User), student_capacity, current_enrollment, number_of_classrooms, number_of_staff, 4 facility booleans, GPS coordinates, is_active.

### Department Structure (9 Departments + 5 Units)

**Departments:**
1. Administration & Human Resources (ADMIN_HR)
2. Finance (FIN)
3. Quality Assurance (QA)
4. Co-Curricular Activities (CC)
5. Schools Administration (SA)
6. Registry (REG)
7. Special Duties (SPD)
8. School Support Services (SSS)
9. French Language (FRENCH)

**Independent Units:**
1. Internal Audit Unit (AUDIT)
2. EMIS Unit (EMIS)
3. Planning, Research & Statistics (PLAN)
4. Procurement Unit (PROC)
5. Public Affairs Unit (PA)

### Data Issues Found
- Duplicate school names across LGAs (Lawanson, Ojuelegba)
- Naming errors (APU005 "Apapa Senior Junior Secondary School")
- Geographic errors (MLA015/016 "Lagos Island" in Mainland LGA)
- Unbalanced school pairs (MLA035 has no Senior counterpart)
- Phone/email/GPS fields empty in seed data
- No SchoolAcademicYear records seeded

---

## 5. MAIL WORKFLOW & COMMUNICATION

### Dual-App Architecture
| App | Purpose | Models |
|-----|---------|--------|
| `mail_workflow` | Physical mail tracking (11 models) | IncomingMail, OutgoingMail, SchoolHQCorrespondence, MailCorrespondence + movements |
| `communication` | In-app messaging + email sending (3 models) | Message, UserNotification, Circular |

### Mail Reference Number Formats
| Type | Format | Example |
|------|--------|---------|
| Incoming | `EDIV/MAIL/{YYYY}/{SEQ}` | EDIV/MAIL/2026/0001 |
| Outgoing | `EDIV/OUT/{YYYY}/{SEQ}` | EDIV/OUT/2026/0001 |
| School→HQ | `EDIV/S2H/{YYYY}/{SEQ}` | EDIV/S2H/2026/0001 |
| HQ→School | `EDIV/H2S/{YYYY}/{SEQ}` | EDIV/H2S/2026/0001 |
| Correspondence | `EDIV/CORR/{TYPE}/{YYYY}/{SEQ}` | EDIV/CORR/INT/2026/0001 |

### Incoming Mail Lifecycle
```
RECEIVED → SCANNED → CLASSIFIED → ASSIGNED → UNDER_REVIEW → IN_ACTION → RESPONDED → DISPATCHED → ARCHIVED
```

### Outgoing Mail Lifecycle
```
DRAFT → PENDING_APPROVAL → APPROVED → DISPATCHED → DELIVERED → ARCHIVED
                                        ↓ (rejected)
                                      REJECTED
```

### School-HQ Correspondence Lifecycle
```
DRAFT → SUBMITTED → RECEIVED_AT_HQ → UNDER_REVIEW → APPROVED/REJECTED/ACTION_REQUIRED → COMPLETED → ARCHIVED
```

### Critical Mail Issues Found
1. **Email notifications never fire** — Celery tasks exist but are never called from views
2. **`send_mail_status_change_notification` references `mail.created_by`** — field doesn't exist (should be `received_by`)
3. **`send_mail_assignment_notification` references `assignment.incoming_mail`** — FK is named `mail`
4. **`check_overdue_mails` filters for `PENDING` status** — should be `ASSIGNED`
5. **Sequence number race condition** — `.count()` not atomic, concurrent requests can produce duplicates
6. **No integration between mail_workflow and communication apps**
7. **No email sending for outgoing mail dispatch**

---

## 6. REGISTRY & DOCUMENT MANAGEMENT

### Three Overlapping Systems

| System | Model | Reference Format | Purpose |
|--------|-------|-----------------|---------|
| Registry | `Document` | `EDIV/{YYYY}/{DEPT}/{SEQ}` | Official documents, memos, filing |
| Files | `File` | `EDIV-{YYYY}-{DEPT}-{SEQ}` | Enterprise document management with workflows |
| Mail | `IncomingMail` etc. | `EDIV/MAIL/{YYYY}/{SEQ}` | Physical mail tracking |

### Registry Models (7)
Document, Correspondence, Filing, DocumentVersion, MemoWorkflow, MemoApproval, MemoCirculation

### Files App — Enterprise Features (8 models + 9 services)
**Models:** File, FileMovement, FileAttachment, FileComment, WorkflowConfig, FileTemplate, FileClassification (AI), OfflineQueue

**Services:**
- FileMovementService — 11-step incoming / 7-step outgoing workflows
- ClassificationService — AI-powered keyword-based department routing (14 depts)
- ImportExportService — Multi-format (doc/docx/xls/xlsx/pdf/image/csv/txt)
- SearchService — Elasticsearch with database fallback
- TemplateService — Reusable file templates with field substitution
- NotificationService — Multi-channel (in-app, email, SMS, WhatsApp)
- OfflineSyncService — Mobile offline queue with retry
- OCRService — Tesseract OCR for scanned documents

### Memo Workflow
```
DRAFT → UNDER_APPROVAL → CIRCULATING → ACKNOWLEDGED → IN_ACTION → REPORTED → ARCHIVED
```

### Registry Issues Found
1. **Two overlapping document systems** (Registry Document vs Files File)
2. **Race condition in reference number generation** (same `.count()` issue)
3. **Memo workflow only creates ONE approval record** (no multi-level approval)
4. **No data retention policies enforced**
5. **No digital signatures**

---

## 7. ACADEMICS, ATTENDANCE & TIMETABLE

### Academic Models (8+)
ClassLevel, Class, Subject, ClassSubject, ExamType, Exam, ExamResult, ReportCard, AcademicCalendar, StudentEnrollment

### Nigerian 6-3-3-4 System Alignment
- **JSS1, JSS2, JSS3** (Junior Secondary)
- **SS1, SS2, SS3** (Senior Secondary)
- **Exam Types:** CA1, CA2, CA3, MIDTERM, FINAL

### Subject Categories
SCIENCE, ARTS, COMMERCIAL, TECHNICAL, GENERAL

### Attendance Models
- **StudentAttendance** — per student per day (PRESENT/ABSENT/LATE/EXCUSED/ON_LEAVE)
- **StaffAttendance** — per staff per day (with overtime tracking)
- **AttendanceSummary** — per school per term (aggregated)

### Timetable Structure
- **Period** — time slots per school
- **Timetable** — per class per year/term
- **TimetableEntry** — day + period + subject + teacher + room
- **TeacherTimetable** — links teachers to timetables

### Academic Issues Found
1. **No RBAC on academics endpoints** — students can delete exam results
2. **No automated grade calculation** — grades are free-text, no grading rubric
3. **No automated report card aggregation** — manual process only
4. **Duplicate report card systems** — `academics.ReportCard` vs `report_card_gen.GeneratedReportCard`
5. **No bulk mark entry** — teachers enter results one student at a time
6. **No constraint on marks vs total** — marks can exceed exam total
7. **academic_year is free-text** — no FK to SchoolAcademicYear
8. **No student promotion automation** — no class advancement mechanism
9. **No timetable-attendance link** — no auto-generation of attendance from timetable

---

## 8. FINANCE & HR SYSTEMS

### Finance Models (5)
FeeStructure, StudentFee, Payment, Budget, Grant

### Payment Flow (KoraPay)
```
1. Frontend → POST /api/finance/payments/initialize/ → creates pending Payment
2. Frontend → KoraPay widget → completes payment
3. KoraPay → POST /api/finance/payments/webhook/ → confirms payment → updates StudentFee
```

### Fee Types (13)
TUITION, DEVELOPMENT, SPORTS, LIBRARY, LABORATORY, EXAMINATION, ICT, PTA, INSURANCE, MEDICAL, TRANSPORT, UNIFORM, OTHER

### HR Models (4 in hr app + 3 in staff app)
**HR App:** JobPosting, JobApplication, PayrollPeriod, Payslip
**Staff App:** Staff, StaffLeave, StaffPerformance

### Staff Model — Comprehensive Fields
Personal: name, gender, DOB, phone, address, photo
Employment: employee_id, department, school, designation, grade_level (1-17), step, employment_type, date_of_first_appointment
Financial: bank_name, bank_account_number, bank_account_name, pension_pin, tax_id, salary
Emergency: emergency_contact_name, emergency_contact_phone

### Payroll Calculation
```
net_salary = basic_salary + allowances - deductions - tax - pension
```

### Finance Issues Found
1. **No RBAC** — students can view payslips and create budgets
2. **Payment confirmation race condition** — concurrent writes can corrupt totals
3. **Webhook endpoint open** — no rate limiting, optional signature verification
4. **No refund/void mechanism**
5. **No financial reports or dashboards**
6. **Grant model not in Django admin**
7. **Budget spent_amount is manual** — never auto-updated
8. **No receipt generation**
9. **HR and Staff apps split** — confusing separation of concerns

---

## 9. CROSS-CUTTING CONCERNS

### Security Analysis

| Area | Status | Risk |
|------|--------|------|
| Authentication | JWT + MFA | ✅ Strong |
| Password Policy | 12-char minimum | ✅ Good |
| Account Lockout | 5 attempts / 30 min | ✅ Good |
| Session Management | Role-based limits | ✅ Good |
| RBAC | Not enforced at API level | 🔴 Critical |
| Audit Logging | Comprehensive | ✅ Good |
| Rate Limiting | Basic (100/hr anon) | ⚠️ Adequate |
| Input Sanitization | Basic XSS filtering | ⚠️ Needs improvement |
| CSRF Protection | Bypassed on auth endpoints | ⚠️ Expected |
| API Versioning | None | ⚠️ Risky for upgrades |

### Celery/Async Status
- Celery only loads if `CELERY_BROKER_URL` is set
- On Render free tier without Redis: **NO async tasks work**
- Affected: email notifications, overdue mail checks, weekly digests, file escalation, Elasticsearch reindex

### Test Coverage
| App | Model Tests | API Tests | Coverage |
|-----|-------------|-----------|----------|
| Academics | 3 | 3 | Minimal |
| Attendance | 1 | 2 | Minimal |
| Timetable | 2 | 3 | Minimal |
| Finance | 3 | 3 | Minimal |
| HR | 3 | 3 | Minimal |
| Mail Workflow | — | 2 | Minimal |
| Schools | — | — | None |

---

## 10. INTERNATIONAL STANDARDS COMPLIANCE

### Education Standards
| Standard | Alignment | Notes |
|----------|-----------|-------|
| Nigerian 6-3-3-4 System | ✅ Full | JSS1-3, SS1-3 |
| WAEC/NECO Grading | ⚠️ Partial | Exam types aligned but no grading rubric |
| UNESCO ISCED | ⚠️ Partial | Custom categories instead of ISCED codes |
| Nigerian EMIS | ✅ Good | School census data covered |

### Financial Standards
| Standard | Alignment | Notes |
|----------|-----------|-------|
| NGN/Kobo Currency | ✅ Full | Kobo conversion for KoraPay |
| PENCOM Pension | ✅ Present | pension field on Payslip |
| PAYE Tax | ✅ Present | tax field on Payslip |
| Grade/Step Scale | ✅ Full | 17 grades with steps |
| Double-Entry Bookkeeping | ❌ Absent | No ledger system |
| Financial Reporting | ❌ Absent | No built-in reports |

### Document Management Standards
| Standard | Alignment | Notes |
|----------|-----------|-------|
| ISO 15489 (Records Mgmt) | ⚠️ Partial | Has classification, versioning, retention dates |
| MoReq | ⚠️ Partial | Has workflows, audit trails |
| GDPR/NDPR | ❌ Absent | No data retention, no right-to-erasure |
| FERPA | ⚠️ Partial | Audit exists but no consent model |

### Email Standards
| Standard | Alignment | Notes |
|----------|-----------|-------|
| RFC 2822/5322 | ❌ Absent | No email header generation |
| DKIM/SPF/DMARC | ❌ Absent | No email authentication |
| Email Threading | ❌ Absent | No References/In-Reply-To |

---

## 11. ERROR ANALYSIS & GAPS

### Critical Errors (Must Fix Before Production)

| # | Issue | Location | Impact |
|---|-------|----------|--------|
| 1 | **No RBAC on any API endpoint** | All views.py | Any user can access any data |
| 2 | **Email notifications broken** | mail_workflow/views.py | Tasks never called from views |
| 3 | **Celery tasks reference wrong fields** | communication/tasks.py | AttributeError at runtime |
| 4 | **Payment race condition** | finance/models.py | Corrupted payment totals |
| 5 | **Sequence number race condition** | Multiple apps | Duplicate reference numbers |

### High Priority Issues

| # | Issue | Impact |
|---|-------|--------|
| 6 | No automated grade calculation | Manual errors in grading |
| 7 | No automated report card aggregation | Manual process only |
| 8 | No bulk operations for mark entry | Teacher efficiency |
| 9 | No financial reports/dashboards | No visibility into finances |
| 10 | Webhook endpoint has no rate limiting | DDoS vulnerability |
| 11 | No student-level attendance summaries | No per-student tracking |
| 12 | Duplicate document systems (Registry + Files) | Data silos |
| 13 | No student promotion automation | Manual class advancement |
| 14 | Teachers created without Staff records | Incomplete data |
| 15 | Students created without Student profiles | Incomplete data |

### Medium Priority Issues

| # | Issue |
|---|-------|
| 16 | No email verification on user creation |
| 17 | No data retention policies |
| 18 | No soft deletes on financial records |
| 19 | No receipt/PDF generation |
| 20 | No API versioning |
| 21 | Grant model not in admin |
| 22 | Budget spent_amount is manual |
| 23 | No refund/void mechanism |
| 24 | HR and Staff app split confusing |
| 25 | No timetable-attendance link |

---

## 12. RECOMMENDATIONS FOR OPTIMAL PERFORMANCE

### Priority 1: Security (Immediate)

1. **Add RBAC to all ViewSets** — Create permission classes per role per app. The Privilege model exists but is not enforced at API level.

2. **Add rate limiting to webhook endpoints** — KoraPay webhook should have stricter rate limits and mandatory signature verification.

3. **Add email verification** — Users should confirm email before account activation.

### Priority 2: Core Functionality (Week 1-2)

4. **Fix mail notification integration** — Call Celery tasks from mail_workflow views. Fix the field name errors (`created_by` → `received_by`, `incoming_mail` → `mail`).

5. **Add automated grading** — Create a GradingScale model per school with grade boundaries (A1=75-100, B2=65-74, etc.).

6. **Add bulk mark entry** — Create endpoints for teachers to enter marks for an entire class at once.

7. **Add automated report card aggregation** — Create a management command or signal that aggregates ExamResults into ReportCards.

8. **Fix payment race condition** — Use `select_for_update()` in Payment.save() and wrap in transaction.

9. **Fix sequence number race condition** — Use database sequences or `F()` expressions instead of `.count()`.

### Priority 3: Data Quality (Week 2-3)

10. **Consolidate document systems** — Merge Registry Document and Files File into a single system, or clearly delineate responsibilities.

11. **Fix seed data issues** — Correct duplicate school names, naming errors, geographic errors.

12. **Seed SchoolAcademicYear records** — Every school needs at least one current academic year.

13. **Create Staff records for teachers** — Seed command should create Staff model entries, not just User objects.

14. **Create Student profiles** — Seed command should create Student model entries with admission numbers.

### Priority 4: Financial Systems (Week 3-4)

15. **Add financial reports** — Revenue summaries, outstanding balances, budget utilization, grant tracking.

16. **Add receipt generation** — Auto-generate receipt numbers and PDF receipts.

17. **Add refund/void mechanism** — Model and endpoint for payment reversals.

18. **Connect Budget.spent_amount to actual expenditures** — Auto-update from payments.

19. **Add Grant to Django admin** — Register the model.

### Priority 5: Academic Systems (Week 4-5)

20. **Add student promotion automation** — Management command to advance students to next class level.

21. **Add timetable-attendance link** — Auto-generate attendance records from timetable.

22. **Add per-student attendance summaries** — Track individual attendance rates.

23. **Add bulk attendance marking** — Mark entire class as present in one API call.

### Priority 6: Communication (Week 5-6)

24. **Integrate mail_workflow with communication app** — When mail is assigned, create a Message/Notification.

25. **Add outgoing mail email sending** — Send actual emails when outgoing mail is dispatched.

26. **Set up Celery with Redis** — Enable async email notifications, overdue checks, weekly digests.

27. **Add email threading** — Use References/In-Reply-To headers for correspondence chains.

### Priority 7: Infrastructure (Week 6-8)

28. **Add API versioning** — `/api/v1/` prefix for future-proofing.

29. **Increase test coverage** — Target 80% coverage for critical paths (auth, payments, mail, academics).

30. **Add Elasticsearch** — Enable full-text search across all entities.

31. **Add monitoring** — Set up Sentry error tracking, health check dashboards.

32. **Add backup strategy** — Automated daily database backups with retention policy.

---

## COMPLETE API ENDPOINT MAP

### Authentication (`/api/users/auth/`)
- `POST /api/users/auth/` — Login
- `POST /api/users/auth/refresh/` — Refresh token
- `POST /api/users/auth/logout/` — Logout
- `POST /api/users/auth/forgot_password/` — Forgot password
- `POST /api/users/auth/reset_password/` — Reset password
- `POST /api/users/auth/mfa_setup/` — MFA setup
- `POST /api/users/auth/mfa_enable/` — Enable MFA
- `POST /api/users/auth/mfa_disable/` — Disable MFA
- `POST /api/users/auth/mfa_verify/` — Verify MFA

### Users (`/api/users/`)
- `GET/POST /api/users/users/` — List/Create users
- `GET/PUT/PATCH/DELETE /api/users/users/{id}/` — User CRUD
- `GET /api/users/users/me/` — Current user profile
- `POST /api/users/users/change_password/` — Change password
- `POST /api/users/users/create-school-staff/` — Create school staff
- `GET /api/users/users/school-staff/` — List school staff

### Schools (`/api/schools/`)
- `GET/POST /api/schools/schools/` — List/Create schools
- `GET/PUT/PATCH/DELETE /api/schools/schools/{id}/` — School CRUD
- `GET/POST /api/schools/schools/{id}/academic-years/` — Academic years

### Departments (`/api/departments/`)
- `GET/POST /api/departments/departments/` — List/Create departments
- `GET/POST /api/departments/units/` — List/Create units

### Academics (`/api/academics/`)
- `GET/POST /api/academics/classes/` — Classes
- `GET/POST /api/academics/subjects/` — Subjects
- `GET/POST /api/academics/exams/` — Exams
- `GET/POST /api/academics/exam-results/` — Exam results
- `GET/POST /api/academics/report-cards/` — Report cards
- `GET/POST /api/academics/calendar/` — Academic calendar
- `GET/POST /api/academics/enrollments/` — Student enrollments

### Attendance (`/api/attendance/`)
- `GET/POST /api/attendance/student-attendance/` — Student attendance
- `GET/POST /api/attendance/staff-attendance/` — Staff attendance
- `GET/POST /api/attendance/summaries/` — Attendance summaries

### Timetable (`/api/timetable/`)
- `GET/POST /api/timetable/periods/` — Time periods
- `GET/POST /api/timetable/timetables/` — Timetables
- `GET/POST /api/timetable/entries/` — Timetable entries

### Finance (`/api/finance/`)
- `GET/POST /api/finance/fee-structures/` — Fee structures
- `GET/POST /api/finance/student-fees/` — Student fees
- `GET/POST /api/finance/payments/` — Payments
- `POST /api/finance/payments/initialize/` — Initialize KoraPay
- `POST /api/finance/payments/webhook/` — KoraPay webhook
- `GET /api/finance/payments/verify/{ref}/` — Verify payment
- `GET/POST /api/finance/budgets/` — Budgets
- `GET/POST /api/finance/grants/` — Grants

### HR (`/api/hr/`)
- `GET/POST /api/hr/job-postings/` — Job postings
- `GET/POST /api/hr/applications/` — Job applications
- `GET/POST /api/hr/payroll-periods/` — Payroll periods
- `GET/POST /api/hr/payslips/` — Payslips

### Mail Workflow (`/api/mail-workflow/`)
- `GET/POST /api/mail-workflow/incoming-mail/` — Incoming mail
- `POST /api/mail-workflow/incoming-mail/{id}/scan/` — Scan
- `POST /api/mail-workflow/incoming-mail/{id}/classify/` — Classify
- `POST /api/mail-workflow/incoming-mail/{id}/assign/` — Assign
- `POST /api/mail-workflow/incoming-mail/{id}/forward/` — Forward
- `POST /api/mail-workflow/incoming-mail/{id}/respond/` — Respond
- `POST /api/mail-workflow/incoming-mail/{id}/dispatch/` — Dispatch
- `GET/POST /api/mail-workflow/outgoing-mail/` — Outgoing mail
- `POST /api/mail-workflow/outgoing-mail/{id}/submit/` — Submit
- `POST /api/mail-workflow/outgoing-mail/{id}/approve/` — Approve
- `GET/POST /api/mail-workflow/school-hq/` — School-HQ correspondence
- `GET/POST /api/mail-workflow/correspondences/` — General correspondence

### Communication (`/api/communication/`)
- `GET/POST /api/communication/messages/` — Messages
- `GET/POST /api/communication/notifications/` — Notifications
- `GET/POST /api/communication/circulars/` — Circulars

### Registry (`/api/registry/`)
- `GET/POST /api/registry/documents/` — Documents
- `POST /api/registry/documents/{id}/approve/` — Approve
- `GET/POST /api/registry/correspondence/` — Correspondence
- `GET/POST /api/registry/filings/` — Physical filings
- `GET/POST /api/registry/memos/` — Memos
- `POST /api/registry/memos/{id}/submit/` — Submit memo
- `POST /api/registry/memos/{id}/approve/` — Approve memo
- `POST /api/registry/memos/{id}/circulate/` — Circulate memo

### Files (`/api/files/`)
- `GET/POST /api/files/files/` — Files
- `POST /api/files/files/{id}/move/` — Move file
- `POST /api/files/files/{id}/submit/` — Submit
- `POST /api/files/files/{id}/approve/` — Approve
- `GET/POST /api/files/movements/` — Movements
- `GET/POST /api/files/attachments/` — Attachments
- `GET /api/files/search/` — Search
- `GET /api/files/dashboard/` — Dashboard
- `GET/POST /api/files/overdue/` — Overdue files

### Data Import/Export (`/api/data-import-export/`)
- `GET/POST /api/data-import-export/jobs/` — Import jobs
- `POST /api/data-import-export/jobs/import/` — Import data
- `GET /api/data-import-export/jobs/export/` — Export data
- `GET/POST /api/data-import-export/access-databases/` — Access databases
- `POST /api/data-import-export/access-databases/{id}/sync-to-portal/` — Sync to portal

### Report Cards (`/api/report-card-gen/`)
- `GET/POST /api/report-card-gen/templates/` — Templates
- `GET/POST /api/report-card-gen/reports/` — Generated reports
- `POST /api/report-card-gen/reports/generate/` — Generate reports
- `GET /api/report-card-gen/reports/{id}/download/` — Download PDF
- `POST /api/report-card-gen/reports/{id}/share/` — Share reports

### Additional Apps (30+ endpoints each)
- `/api/analytics/` — Dashboard and school statistics
- `/api/benchmarking/` — School benchmarks and comparisons
- `/api/inspection/` — School inspections
- `/api/discipline/` — Student discipline
- `/api/library/` — Library management
- `/api/e-learning/` — E-learning courses
- `/api/chatbot/` — AI chatbot
- `/api/blockchain-certs/` — Blockchain certificates
- `/api/gamification/` — Gamification
- `/api/push-notifications/` — Push notifications
- `/api/iot/` — IoT dashboard
- `/api/multilingual/` — Multi-language support
- `/api/parent-teacher/` — Parent-teacher communication
- `/api/co-curricular/` — Co-curricular activities
- `/api/french/` — French language
- `/api/infrastructure/` — Infrastructure management
- `/api/transport/` — Transport management
- `/api/wellness/` — Student wellness
- `/api/alumni/` — Alumni management
- `/api/assets/` — Asset management
- `/api/cpd/` — Continuous professional development

---

## SUMMARY

| Metric | Value |
|--------|-------|
| Total Django Apps | 30+ |
| Total Models | 100+ |
| Total API Endpoints | 400+ |
| Schools | 95 (3 LGAs) |
| User Roles | 22 |
| Departments | 9 + 5 units |
| Mail Models | 14 |
| Critical Issues | 5 |
| High Priority Issues | 10 |
| Medium Priority Issues | 15 |

### Overall Assessment

**Strengths:**
- Comprehensive role hierarchy with fine-grained module access
- Strong authentication (JWT + MFA + lockout)
- Extensive audit logging
- Well-structured mail workflow with movement tracking
- Enterprise document management with AI classification
- KoraPay payment integration
- Nigerian education system alignment (6-3-3-4)

**Weaknesses:**
- No RBAC enforcement at API level (critical security gap)
- Broken email notification pipeline
- Multiple overlapping systems (Registry vs Files vs Mail)
- Minimal test coverage
- No financial reports or dashboards
- Celery dependency without guaranteed Redis
- Seed data quality issues

**Effort Estimate for Full Remediation:** 8-12 weeks (1 developer)

---

*Report generated by automated codebase analysis*
*For questions, review individual app analyses in the agents/ directory*
