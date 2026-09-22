# Education District IV Portal — Codebase Map

> Read-only map generated from inspected source. All statements are grounded in code read during this pass; files not inspected are listed in **Scope Limits**.

---

## 1. One-Line Summary

This is a Django 4.2 + DRF backend (41 apps under `backend/apps/`, mounted under `config.urls`) with a React 18 (Vite) SPA served by that same backend, for managing a school district: registry/correspondence, file movement, mail workflow, workflows engine, import/export (incl. legacy Access databases), HR/students/staff/schools/finance, and a mobile companion app.

## 2. Backend App Inventory (41 apps)

Entry points: settings list in `backend/config/settings/base.py` (INSTALLED_APPS, lines 79–135); every app is also mounted in `backend/config/urls.py` under `api/v1/<name>/` (with a deprecated unversioned `/api/<name>/` twin).

| App | One-line description (evidence) |
|---|---|
| `apps.users` | Custom `User` model (`email` as USERNAME_FIELD, `role` field with 21 role choices), `RolePrivilege`/`Module`/`Privilege` RBAC models, `is_department_head`/`is_school_staff`/`is_head_office_staff`/`is_admin_level` properties, `can_access_module()` permission map. `AUTH_USER_MODEL = "users.User"`. |
| `apps.schools` | School entity; referenced by `File.school` and `IncomingMail.department`-style FKs. Router mounted `api/v1/schools/`. |
| `apps.staff` | Staff records module (roles: PRI/VP/TCH/SA_OFF per users serializers). |
| `apps.students` | Students module (export target in `data_import_export.EXPORTABLE_MODELS`). |
| `apps.academics` | Academic records (models grep: AcademicSession/AcademicTerm/Class/Grade across migrations). |
| `apps.attendance` | Attendance tracking module. |
| `apps.finance` | Finance; has `korapay.py` and `payment_views.py` (payment gateway integration). |
| `apps.communication` | Communications; has `tasks.py` (Celery tasks). |
| `apps.reports` | Reporting endpoints. |
| `apps.hr` | HR module (registry document approval grants HR role). |
| `apps.registry` | **E-Registry**: `Document`, `Correspondence`, `Filing`, `DocumentVersion`, `MemoWorkflow`, `MemoApproval`, `MemoCirculation`. Routers: `documents`, `correspondence`, `filings`, `versions`, `memos`, `memo-approvals`, `memo-circulations`. |
| `apps.departments` | `Department` model (FK target of `File.department`, `File.assigned_department`, mail models). |
| `apps.files` | **File movement engine**: `File`, `FileMovement`, `FileAttachment`, `FileComment`, `WorkflowConfig`, `FileTemplate`, `OfflineQueue`, `FileClassification`, `AuditLog`; 10 services (`file_movement_service`, `classification_service`, `import_export_service`, `search_service`, `notification_service`, `audit_service`, `offline_sync_service`, `ocr_service`, `template_service`); Celery `tasks.py`; import/export endpoints. |
| `apps.workflows` | **Workflow engine**: `Workflow`, `WorkflowStep`, `WorkflowInstance`, `Task`; `WorkflowService` (seed/start/advance/assign); `workflow_definitions.py` (7 workflows, 13-step incoming mail); `automation.py` (`AgenticRouter`, `MailDistributor`, `FileDistributor`, `DepartmentAgent`, `AutomationEngine`) with keyword-based auto-assignment; management commands `seed_workflows`, `run_automation`. |
| `apps.notifications` | Notifications module (referenced by registry/mail views). |
| `apps.inspection` | Inspection module (frontend page `Inspection.jsx`). |
| `apps.co_curricular` | Co-curricular activities module. |
| `apps.french` | French/FLS module (French Unit role exists in users). |
| `apps.infrastructure` | Infrastructure module. |
| `apps.library` | Library module (frontend `Library.jsx`). |
| `apps.e_learning` | E-learning module. |
| `apps.wellness` | Wellness module. |
| `apps.alumni` | Alumni module. |
| `apps.assets` | Assets module. |
| `apps.discipline` | Discipline module (registry approval grants AUDIT; discipline category in FileCategory). |
| `apps.timetable` | Timetable module. |
| `apps.transport` | Transport module. |
| `apps.cpd` | Continuous Professional Development module. |
| `apps.audit` | Audit module (router `api/v1/audit/`). |
| `apps.parent_teacher` | Parent-teacher association module. |
| `apps.analytics` | Analytics module. |
| `apps.data_import_export` | **Legacy import/export**: `ImportJob`, `ImportError`, `AccessDatabase`, `AccessTableData`, `AccessPrivilege`; `EXPORTABLE_MODELS = [students, staff, schools]`; parsers for CSV/XLSX/PDF/DOCX + Access mdb/accdb via subprocess; routers `data-import-export/` + `access-databases/`. |
| `apps.mail_workflow` | **Mail workflow**: `IncomingMail`, `MailScanRecord`, `MailAssignment`, `MailMovement`, `OutgoingMail`, `OutgoingMailApproval`, `OutgoingMailMovement`, `SchoolHQCorrespondence` (+movement), `MailCorrespondence` (+movement). Routers: `incoming-mail`, `assignments`, `incoming-movements`, `outgoing-mail`, `outgoing-movements`, `school-hq`, `school-hq-movements`, `correspondences`, `correspondence-movements`. |
| `apps.predictive_analytics` | Predictive analytics module. |
| `apps.chatbot` | Chatbot module. |
| `apps.blockchain_cert` | Blockchain certificate issuance module. |
| `apps.multilingual` | Multilingual/i18n module. |
| `apps.gamification` | Gamification module. |
| `apps.push_notifications` | Push notifications module. |
| `apps.iot_dashboard` | IoT dashboard module (frontend `IoT.jsx`). |
| `apps.benchmarking` | Benchmarking module. |
| `apps.report_card_gen` | Report card generation module. |

Not inspected (existence + INSTALLED_APPS only): academics, attendance, co_curricular, french, infrastructure, e_learning, wellness, alumni, assets, discipline, timetable, transport, cpd, analytics, predictive_analytics, chatbot, blockchain_cert, multilingual, gamification, push_notifications, iot_dashboard, benchmarking, report_card_gen, parent_teacher, inspection, library.

## 3. Import / Export — Current State

### File uploads / attachments
- `backend/apps/files/models.py` — `FileAttachment.file_format` choices: `doc, docx, xls, xlsx, pdf, jpeg, png, csv, txt, other` (lines 203–217). **No mdb/accdb, mp3, or mp4.**
- `backend/apps/registry/models.py` — `Document.attachment` FileField (`upload_to="registry/documents/"`); migration `0002_document_attachment` added it.
- `backend/apps/mail_workflow/models.py` — `IncomingMail.scanned_copy` (`mail/scans/`), `OutgoingMail.scanned_copy` (`mail/outgoing/scans/`).
- `backend/apps/files/services/import_export_service.py` — `ImportExportService`:
  - `SUPPORTED_IMPORT_FORMATS = ["doc", "docx", "xls", "xlsx", "pdf", "jpeg", "jpg", "png", "csv", "txt"]`
  - `SUPPORTED_EXPORT_FORMATS = ["xlsx", "csv", "pdf", "docx"]`
  - **Gap for extension (A)/file-type support: mdb/accdb (Access), mp3, mp4 are NOT in these lists** (and are not in `FileAttachment.file_format` choices).
- `backend/apps/files/urls.py` — import/export surface: `import/`, `export/`, `bulk-import/` plus `search/`, `search/suggestions/`, `notifications/`, `offline-queue/`, `OCRView`, `FileBulkImportView`, `FileDashboardView`.

### Legacy Access / HSG (data_import_export)
- `backend/apps/data_import_export/views.py` — `EXPORTABLE_MODELS = [students, staff, schools]` (ApprovedSchoolTable, StaffRecord, StudentRecord); `ImportJob`, `AccessDatabase`, `AccessTableData`, `AccessPrivilege` models; auto-sync of Access tables; `permission_classes` use `IsAdminOrTGOrDeptHead`; `AuditLogger.log_action` on imports; parser helpers for CSV/XLSX/PDF/DOCX (openpyxl/pdfplumber/python-docx family) and Access mdb/accdb via subprocess.
- Routers: `api/v1/data-import-export/` and `api/v1/access-databases/` (both versioned and unversioned).

## 4. E-Registry (apps/registry)

### Models (`models.py`)
- `Document` — unique `reference_number`, `title`, `document_type` (DocumentType: CORRESPONDENCE/MEMO/CIRCULAR/REPORT/MINUTES/POLICY/CONTRACT/LETTER/OTHER), `content`, `attachment` FileField, `created_by` FK, `department` FK, `status` (DRAFT/PENDING/APPROVED/REJECTED/ARCHIVED), `classification` (PUBLIC/INTERNAL/CONFIDENTIAL/RESTRICTED).
- `Correspondence`, `Filing`, `DocumentVersion`, `MemoWorkflow`, `MemoApproval`, `MemoCirculation`.

### Views (`views.py`) — all registered in `urls.py` DefaultRouter
- `DocumentViewSet` — `DocumentListSerializer` for list, `DocumentSerializer` for detail; filter (`document_type,status,classification,department`), search (`reference_number,title,content`), ordering; `perform_create` generates `EDIV/{year}/{dept_code}/{seq:04d}` via `config.sequence_utils.next_sequence_number`; custom actions `approve`, `reject` (role-gated: SYSADMIN/TG_PS/HR/FIN/AUDIT/QA/REG); every action logs through `AuditLogger`.
- `CorrespondenceViewSet`, `FilingViewSet`, `DocumentVersionViewSet` — ModelViewSets, `IsAdminOrTGOrDeptHead` permission; `Filing.perform_create` sets `filed_by`; `DocumentVersion.perform_create` bumps `Document.version`.
- `MemoWorkflowViewSet` — role-scoped queryset (SYSADMIN/TG_PS see all; others see created-by/approver/recipient) and state-machine actions: `submit` (DRAFT→UNDER_APPROVAL + creates MemoApproval for TG_PS/SYSADMIN), `approve`/`reject` (role-gated SYSADMIN/TG_PS/PRI/VP), `circulate` (creates MemoCirculation rows), `acknowledge` (SENT→ACKNOWLEDGED; all acked → memo ACKNOWLEDGED), `archive`.
- `MemoApprovalViewSet`, `MemoCirculationViewSet` — ReadOnly, `IsAuthenticated`, filtered.

### Serializers
`registry/serializers.py`: `DocumentVersionSerializer`, `CorrespondenceSerializer`, `FilingSerializer`, `DocumentSerializer`, `DocumentListSerializer`, `MemoWorkflowSerializer`, `MemoApprovalSerializer`, `MemoCirculationSerializer`.

## 5. Workflow Engine + Auto-Assignment

### Engine (`apps/workflows`)
- `models.py` — `Workflow` (status ACTIVE, `is_template`, `trigger_type` MANUAL/AUTOMATIC/SCHEDULED, `trigger_config` JSON), `WorkflowStep` (order, name, `step_type`, `assigned_role`, `is_required`), `WorkflowInstance` (status PENDING/IN_PROGRESS/COMPLETED/CANCELLED, `current_step`, `reference_number`, `data` JSON), `Task` (assigned_to, status PENDING/IN_PROGRESS/COMPLETED, `decision`, `comments`, `completed_at`).
- `services/workflow_service.py` — `WorkflowService`: `seed_all()` (creates Workflow+WorkflowStep from `ALL_WORKFLOWS`), `start_instance()` (assigns first step task), `advance()` (completes current task, moves to next step or COMPLETED), `_assign_task()` (assignee = first user with step role, fallback SYSADMIN, fallback initiator). `ROLE_MAPPING` translates definition roles (MAIL_ROOM→REG_OFF, REGISTRAR→REG_OFF, DEPT_HEAD→REG, PRINCIPAL→PRI, …). `APPROVAL_ACTIONS` set.
- `workflow_definitions.py` — 7 pre-configured workflows: Incoming Mail Processing (13 steps: Mail Receipt → Registration → Scanning → Classification → Sorting → Department Assignment → … incl. required_role MAIL_ROOM, approval actions), plus 6 others (outgoing mail, memo, circular, policy, correspondence, file-opened variants — names per definition file); exports `ALL_WORKFLOWS`, `DEPARTMENT_CODES`, `FILE_CATEGORIES`, `SECURITY_CLASSIFICATIONS`.
- `views.py` — `WorkflowViewSet`, `WorkflowStepViewSet`, `WorkflowInstanceViewSet` (with `start`/`advance` actions), `TaskViewSet`.
- Management commands: `seed_workflows` (calls `WorkflowService.seed_all`), `run_automation` (runs AutomationEngine).

### Auto-assignment (`apps/workflows/automation.py`)
- Classes: `AgenticRouter` (line 326), `MailDistributor` (600), `FileDistributor` (859), `DepartmentAgent` (1001), `AutomationEngine` (1320).
- `DEPARTMENT_KEYWORDS` content-keyword map → department; imports `FileMovementService`, `WorkflowService`, `NotificationService` and registry/mail_workflow models (`Correspondence`, `MemoWorkflow`, `MemoApproval`, `MemoCirculation`, `IncomingMail`, …).
- **This is the existing implementation of extension (B) auto-assignment**: incoming mail / files get an `assigned_department` (File model field, `help_text="Auto-assigned department based on AI classification"`) and workflow routing via keyword/agentic classification.

## 6. Frontend Structure (React 18 + Vite)

- Root: `frontend/` — Vite React SPA; build output `frontend/dist` is served by the Django backend `serve_frontend` catch-all (`backend/config/urls.py` line 226) for all non-`/api/` routes.
- Key pages (`frontend/src/pages/`): `Registry.jsx` (E-Registry UI), `Workflows.jsx` (workflow engine UI), `MailWorkflow.jsx` (incoming/outgoing mail UI), `MemoWorkflow.jsx` (memo approval/circulation UI), plus `Inspection.jsx`, `Reports.jsx`, `Library.jsx`, `IoT.jsx`, auth (Login/ResetPassword/MFA), checks pages.
- Tests: `frontend/src/__tests__/*.test.jsx` (Jest; e.g. `Login.test.jsx`, `Dashboard.test.jsx`).
- Mobile: `mobile/` directory exists (not inspected).
- The UI-independent directory list from earlier pass: components/hooks/lib/styles/services/api wrappers exist under `frontend/src/` (partially inspected).

## 7. Test Setup

- Backend: Django `manage.py test` (no pytest/conftest found at root or `backend/`; `pyproject.toml` has black/isort/flake8/ruff config only).
- Settings: `config/settings/test.py` — SQLite in-memory, MD5PasswordHasher, CORS open, `MIGRATION_MODULES` skipped for ~40 apps (incl. users, schools, files, workflows, registry, data_import_export, mail_workflow). Also `ediv_portal/test_settings.py` (imports `config.settings.base`).
- Run: `cd backend; $env:DJANGO_SETTINGS_MODULE='config.settings.test'; python manage.py test apps.<app> -v1` (command documented in plan docs).
- Test files present (note: at app root, **not** under `tests/` subdirs as the plan docs describe):
  - `apps/files/`: `tests_services.py`, `tests_file_movement_service.py`, `tests_classification_service.py`
  - `apps/workflows/`: `tests.py`, `test_workflow_api.py`, `test_workflow_service.py`
  - `apps/registry/`: `tests.py`, `test_memo_workflow_api.py`
  - `apps/mail_workflow/`: `tests.py`, `test_movement_api.py`
  - `apps/users/`: `tests.py`
- Frontend: Jest tests in `frontend/src/__tests__/`.

## 8. Plan Status — Both Plans 100% Checked

### `docs/compose/plans/2026-08-09-e-registry-mail-workflow-automation.md` — 24/24 checkboxes `[x]`, 0 unchecked
Completed tasks (Task 1–5, S1–S4):
1. WorkflowService created (`apps/workflows/services/workflow_service.py`) + `seed_workflows` management command + service tests.
2. `WorkflowInstanceViewSet` got `start`/`advance` actions.
3. Registry `MemoApprovalViewSet`/`MemoCirculationViewSet` added + routes `memo-approvals`/`memo-circulations` + admin + full-flow API test (create→submit→approve→circulate→acknowledge→archive).
4. Mail workflow movement viewsets (incoming-movements, outgoing-movements, school-hq-movements, correspondence-movements) + routes + admin + tests.
5. Full verification: `python manage.py test apps.workflows apps.registry apps.mail_workflow` expected ALL PASS; `makemigrations --check` clean; `seed_workflows` expected 7 created/0 updated first run.

### `docs/compose/plans/2026-08-01-enterprise-file-movement-complete.md` — 43/43 checkboxes `[x]`, 0 unchecked
Verified features (from plan "Features Verified" table):
- Scalability (pagination, caching, query opt), keyword-based auto department routing, configurable deadlines (`WorkflowConfig`), Elasticsearch w/ DB fallback (`search_service.py`), mobile offline queue/sync (`OfflineQueue` + `offline_sync_service.py`), file templates (`template_service.py`), AI content classification (`classification_service.py`), immutable audit (`AuditLog` + `audit_service.py`), multi-channel notifications, role-based access, 11-step incoming/7-step outgoing workflow, import/export (doc, docx, xls, xlsx, pdf, jpeg, png, csv, txt), file dashboard, bulk operations, workflow visualization, 60+ tests claimed by plan.
- Discrepancy: plan lists tests under `backend/apps/files/tests/test_*.py` but actual files live at app root (`tests_classification_service.py`, `tests_file_movement_service.py`, `tests_services.py`).

## 9. Critical Paths (do-not-break surfaces)

### URL routing
- `backend/config/urls.py` — single source: `/health/`, `/api/health/`, `/wake/`, `/debug/files/` (DEBUG only), Django admin; all app routers mounted under both `api/v1/` and unversioned `api/`; SPA catch-all `re_path(r"^(?P<path>.*)$", serve_frontend)` MUST stay last. MEDIA serving only in DEBUG.
- Root project `ediv_portal/urls.py` re-exports `config.urls.urlpatterns`; `ediv_portal/settings.py` is a shim that imports `config.settings.production`.

### Auth / RBAC
- `backend/config/permissions.py` — `IsAdminOrTGOrDeptHead` (used by registry Document/Correspondence/Filing/Version viewsets and data_import_export).
- `backend/config/rbac.py` — role/module access enforcement (used in user module access).
- `backend/config/security.py` — `AuditLogger.log_action` (called by registry, data_import_export, workflows automation).
- `apps/users/models.py` — `User.Role` (21 choices incl. SYSADMIN, TG_PS, REG, REG_OFF, PRI, VP), `is_department_head`, `can_access_module()`. Role strings appear in viewset action gates (registry approve/reject, memo approve/reject).

### File movement flow (core loop)
1. Create file: `File` (files/models.py) with auto `file_number`; status DRAFT → ACTIVE; `created_offline`/offline flags for mobile.
2. Route/classify: `files/services/classification_service.py` + `workflows/automation.py` (`FileDistributor`/`DepartmentAgent`) → sets `File.assigned_department` + `FileClassification`.
3. Move: `files/services/file_movement_service.py` (`FileMovementService`) writes `FileMovement` rows (from_holder/to_holder, action, workflow_step, expected_completion, is_overdue), advances `File.current_workflow_step`, updates `current_holder`, `last_moved_at`.
4. Configure: `WorkflowConfig` step deadlines; `NotificationService` reminders; `AuditLogger` trail.
5. Dashboard/ops: `FileDashboardView`, `WorkflowMoveView`, `WorkflowAdvanceView`, `WorkflowVisualizationView`, bulk archive/escalate, `OfflineQueue` sync.

## 10. Scope Limits (not inspected)

- `mobile/` app contents; `frontend/` internals beyond page/file listing; `scripts/`, `frontend-server/`, `docker-compose.yml`, `Dockerfile` contents.
- Source of ~22 non-core apps (listed in §2) beyond INSTALLED_APPS/routing evidence; app `views.py`/`serializers.py` for those apps; `data_import_export` serializers and parser internals beyond `views.py`; `files/views.py` and `serializers.py` bodies (only urls/models/services inspected); `config/rbac.py` and `config/security.py` bodies (only usages).