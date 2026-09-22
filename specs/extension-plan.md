# Extension Plan — E-Registry Phase 2 (Full File Import, Auto-Assignment, Complete Registry Digitalization)

Design-only document. No code changes made. Additive constraints only: no renames, no endpoint removals, no
`config/urls.py` catch-all reordering, no `User.Role`/RBAC semantic changes. Every migration is reversible.
New dependency policy: none required — all gaps are covered by existing libs (python-docx, openpyxl, xlrd,
PyPDF2, Pillow) + existing Celery infra.

---

## 1. Gap Analysis Per Feature

### Feature A — FULL FILE IMPORT (doc, docx, xls, xlsx, mdb/accdb, jpeg, pdf, mp3, mp4)

| # | Gap | Evidence | Impact |
|---|-----|----------|--------|
| A1 | `mdb/accdb` missing from file import formats | `backend/apps/files/services/import_export_service.py:20` → `SUPPORTED_IMPORT_FORMATS = [doc, docx, xls, xlsx, pdf, jpeg, jpg, png, csv, txt]` | Access import exists only in `data_import_export` (mdbtools via `subprocess`, `ImportJob` PENDING/PROCESSING/COMPLETED/FAILED state machine). Files app cannot ingest `.mdb`/`.accdb` as file attachments. |
| A2 | `mp3` / `mp4` unsupported everywhere | `MIME_FORMAT_MAP` / `EXT_FORMAT_MAP` in `import_export_service.py` have no `audio/mpeg` or `video/mp4` entries | Media files rejected at `detect_format()` and `FileImportView` (`files/views.py:897` `ext_map.get(ext, "txt")` silently mislabels mp3/mp4 as txt). |
| A3 | File import is synchronous only | `files/views.py` `FileImportView` runs `ImportExportService.import_file()` inline (no job record) | Large mp4 / big PDFs block request thread. Celery is already configured (`config/settings/base.py:252-267`, `files/tasks.py` has 4 tasks, `CELERY_TASK_ALWAYS_EAGER=True` when no broker → test-safe). Reuse `data_import_export.ImportJob`-style state machine without new dependency. |
| A4 | Upload size limit not centralized | No shared `MAX_UPLOAD_SIZE_MB` constant found; `files/views.py` relies on framework default | mp4 will hit default 2.5 MB DRF limit. Need explicit, documented cap per format family. |
| A5 | `FileAttachment.file_format` choices may not include media | Defined in `backend/apps/files/migrations/0005_...` (`models.py:203`) | Choices-only migration required if `mp3`/`mp4` absent (verify against current choices before planning DB task). |

### Feature B — AUTO-ASSIGNMENT ENGINE EXTENSION

| # | Gap | Evidence | Impact |
|---|-----|----------|--------|
| B1 | Automation logic exists but is not exposed via API | `backend/apps/workflows/automation.py` has `DEPARTMENT_KEYWORDS`, `get_department_head` (role fallback map TG_PS/HR/FIN/AUDIT/QA/CC/FRENCH/EMIS/PLAN/PROC/PA/SA/REG), `get_department_staff`, `auto_assign_task`, `distribute`, `determine_next_holder`, `bulk_distribute`; `workflows/urls.py:6-10` registers only workflows/steps/instances/tasks | No endpoint to trigger or preview assignment; frontend `Workflows.jsx` and `MailWorkflow.jsx` cannot call it. |
| B2 | No rule override / config model | `automation.py` keyword matching + sequential staff rotation is hardcoded | Auto-assignment is synchronous-only with no per-department weight or manual override persisted. |
| B3 | Assignment target resolution is team-only | `get_department_head`, `get_department_staff` resolve Department → Staff; Staff has `role` (RBAC) | Registry `Correspondence.requires_response` (registry/models.py:80) never flows into assignment → feature C tie-in. |
| B4 | No workload balancing input | `bulk_distribute` rotation ignores open-task counts | Nice-to-have: score by open task count — defer (YAGNI unless ops asks). |

### Feature C — COMPLETE E-REGISTRY DIGITALIZATION

| # | Gap | Evidence | Impact |
|---|-----|----------|--------|
| C1 | No registry audit trail | `Document` has only `created_at/updated_at` (registry/models.py:51-52) | No who-changed-what history for restricted documents; compliance gap. |
| C2 | Correspondence follow-up not tracked | `Correspondence.requires_response` + `response_deadline` exist but no follow-up/reminder model | "Complete digitalization" stalls at registration; no escalations or overdue flags. |
| C3 | Memo approval order is flat `IntegerField` | `MemoApproval.approval_order` (registry/models.py:161), no workflow-sequence config | No branching/parallel approval; approval chain is manual. |
| C4 | No registry record export/print index | `registry/urls.py` routers only; no export endpoint | Archive/legal need export of the registry index (mirror `data_import_export` export pattern or add `DocumentViewSet` serializer-level export). |
| C5 | Docs uploaded as flat `FileField` | `Document.attachment` (registry/models.py:30-32) — single attachment | Multiple annexes (minutes, photos) need child `DocumentAttachment` model OR reuse files app. Reuse is cheaper. |
| C6 | Registry ↔ automation disconnection | `registry` has no import of `workflows/automation` | `Correspondence.requires_response` should auto-create a `Task` (ties to B). |
| C7 | Migration numbering trap | `registry/migrations/` contains duplicate `0002_initial` + `0002_document_attachment`, latest `0004_merge_20260921_1122` | New registry migration MUST be `0005_...` and depend on `0004_merge_20260921_1122`. |

---

## 2. Design

### Feature A — Full File Import

- **Files**: extend `backend/apps/files/services/import_export_service.py` + `backend/apps/files/views.py` (+ optional `backend/apps/files/tasks.py`).
- **API surface** (additive, no renames):
  - `POST /api/v1/files/import/` gains `format=access|mp3|mp4` handling (existing endpoint shape kept).
  - `POST /api/v1/data-import-export/import/` already handles `.accdb/.mdb` (frontend `DataImportExport.jsx:290` sends them today) — keep, do NOT duplicate; unify format tables instead.
  - New lookup endpoint `GET /api/v1/files/import/formats/` returns supported formats + per-format `max_size_mb` for frontend `accept` + client-side validation.
- **Data model**: `FileAttachment.file_format` choices extended with `access`, `mp3`, `mp4` (choices-only migration, reversible).
- **Size policy**: `MAX_UPLOAD_SIZE_MB` per family in `import_export_service.py` — `doc/pdf: 25`, `xls/xlsx/access: 50`, `jpeg: 10`, `mp3: 50`, `mp4: 200`; reject at `FileImportView` with 413-class DRF error.
- **Async decision**: keep synchronous default (flag `FILES_ASYNC_IMPORT` default `off`); when on, wrap import in a Celery task reusing `ImportJob`-style states. Default-off = zero behavior change, reversible.
- **New deps**: none. (mp3/mp4 are stored as attachments, not parsed — no codec lib. `.doc`/`.xls` already parse via existing `_import_document`/`_import_spreadsheet` paths.)

### Feature B — Auto-Assignment Engine

- **Files**: `backend/apps/workflows/automation.py` (extend) + new `backend/apps/workflows/views_automation.py` (read-only exposure) + `backend/apps/workflows/urls.py` (add router).
- **API surface** (additive):
  - `GET /api/v1/workflows/automation/config/` — dept → roles/keywords mapping (read-only, from existing constants).
  - `POST /api/v1/workflows/automation/preview/` — dry-run: returns proposed assignment without persisting.
  - `POST /api/v1/workflows/automation/assign/` — executes `auto_assign_task`/`bulk_distribute` for a given file/correspondence.
- **Data model**: optional `AssignmentRule` model (dept, keyword overrides, round-robin weight) behind flag `AUTO_ASSIGN_RULES` default `off` → migration `workflows/0002_assignmentrule` reversible. If flag stays off, no table created (design keeps both paths).
- **No new deps.**

### Feature C — Complete E-Registry Digitalization

- **Files**: `backend/apps/registry/models.py`, `views.py`, `serializers.py`, `urls.py`, new `backend/apps/registry/services/registry_service.py`.
- **API surface** (additive):
  - `GET /api/v1/registry/documents/{id}/history/` — audit entries (read-only).
  - `POST /api/v1/registry/documents/{id}/follow-ups/` — create follow-up on `requires_response` correspondence.
  - `POST /api/v1/registry/documents/{id}/assign/` — hand off to workflows automation (feature B endpoint).
  - Export: extend existing `DocumentViewSet` with `?format=csv|xlsx` query param (reuse `data_import_export` export utilities) — still additive, no new route.
- **Data model** (new migrations, all reversible):
  - `registry/0005_documentauditentry_followup`: `DocumentAuditEntry` (document FK, action, user, timestamp) + optional `FollowUp` (document, assignee, due_date, status) — C1/C2.
  - Registry multi-attachment reuses `files.FileAttachment` linked via `File` instead of a new model (C5).
  - Memo approvals (C3) use existing `MemoApproval.approval_order` — add `parallel` boolean only if ops requires; deferred.
- **No new deps.**

---

## 3. Task Breakdown

ID convention: `DB-` schema, `BE-` Django/DRF, `FE-` React. Each task lists acceptance criteria + dependencies.

### Phase 1 — Data/Schema (DB)

| ID | Task | Acceptance criteria | Depends on |
|----|------|--------------------|-----------|
| DB-001 | Extend `FileAttachment.file_format` choices with `access`, `mp3`, `mp4`; files `0007_...` migration | `python manage.py migrate` clean; reversal `migrate files 0006` clean; `test_file_format_choices` updated passes | — |
| DB-002 | `workflows/0002_assignmentrule` (only when flag on) | Reversible; `makemigrations --check` clean | — |
| DB-003 | `registry/0005_documentauditentry_followup` depending on `0004_merge_20260921_1122` | Reverse clean; model tests pass | — |

### Phase 2 — Backend (BE)

| ID | Task | Acceptance criteria | Depends on |
|----|------|--------------------|-----------|
| BE-001 | Add `access`, `mp3`, `mp4` to `SUPPORTED_IMPORT_FORMATS` + `MIME_FORMAT_MAP`/`EXT_FORMAT_MAP`; add `MAX_UPLOAD_SIZE_MB` table + format family validation in `import_export_service.py` | `detect_format` returns `access/mp3/mp4` for correct MIME; size rejection returns 413-format error; existing import tests still pass | DB-001 |
| BE-002 | `GET /api/v1/files/import/formats/` lookup endpoint | Returns format list + `max_size_mb`; authenticated; unit test | BE-001 |
| BE-003 | Optional async import path behind `FILES_ASYNC_IMPORT` flag (Celery task, ImportJob-style state, default `off`) | Flag off: sync path byte-identical behavior; flag on: `CELERY_TASK_ALWAYS_EAGER` test passes | BE-001 |
| BE-004 | `automation_views`: `config/`, `preview/`, `assign/` endpoints + router in `workflows/urls.py` | `preview` persists nothing (assert row count unchanged); `assign` creates Task; RBAC enforced | DB-002 |
| BE-005 | Registry audit + follow-ups + assign: model wiring in `registry_service.py`, `history/` & `follow-ups/` endpoints, `?format=` export | Audit entry written on Document update; follow-up created on requires_response; export CSV valid | DB-003 |
| BE-006 | `Correspondence.requires_response` → auto Task creation via automation (default off flag `REGISTRY_AUTO_TASK`) | When on, saving correspondence creates PENDING Task; when off, no side effect | BE-004, BE-005 |

### Phase 3 — Frontend (FE)

| ID | Task | Acceptance criteria | Depends on |
|----|------|--------------------|-----------|
| FE-001 | `Files.jsx` import dialog: accept=`add .mdb,.accdb,.mp3,.mp4`, client-side size check from `/import/formats/` | FilePicker restricts new formats; oversized file blocked before upload | BE-002 |
| FE-002 | `Workflows.jsx` → add auto-assign preview panel (config + dry-run + confirm) | Preview table renders proposed assignee; confirm triggers assign endpoint | BE-004 |
| FE-003 | `Registry.jsx` → history drawer, follow-up button on requires_response, export button | History rows render; follow-up POST succeeds; export downloads blob | BE-005 |
| FE-004 | `MailWorkflow.jsx`/`MemoWorkflow.jsx` → optional assignment hint banner (flag-gated) | Banner hidden when `REGISTRY_AUTO_TASK` off | BE-006 |

---

## 4. Ordered Implementation Sequence

1. DB-001 → DB-002 → DB-003 (schema first, all reversible; verify `migrate` + `migrate <app> <prev>` on each).
2. BE-001 → BE-002/003 (file import, backend first).
3. BE-004 (automation endpoints) → BE-005/006 (registry wiring).
4. FE-001 → FE-002 → FE-003 → FE-004 (after each BE endpoint is green in DRF browsable API).
5. Verification sweep: full `manage.py test`, `npm run build`, manual smoke of import → assign → registry history.

Gate per phase: no next phase until `manage.py test` passes for changed apps.

---

## 5. Test Plan (per task, `manage.py test`, in-memory SQLite)

- **DB-001/002/003**: migration test (apply + reverse + re-apply); model field/choice assertions in `files/tests/test_models.py` (`FileAttachmentFieldsTest.test_file_format_choices`), new `workflows/tests/test_assignment_rule.py`, `registry/tests.py` additions.
- **BE-001**: extend `files/tests/test_import_export_service.py` — add `access/mp3/mp4` to format support test (-already asserts members- update), size-limit rejection test, MIME mapping test.
- **BE-002**: DRF APIClient test — formats endpoint returns schema, 401 unauthenticated.
- **BE-003**: async flag on/off behavior tests (eager mode), ImportJob state transitions.
- **BE-004**: unit — `preview` no row writes; `assign` creates `Task` with correct assignee from DEPARTMENT_KEYWORDS; RBAC 403 for non-staff. Integration — assign via DRF client.
- **BE-005**: registry service unit tests (audit write on update, follow-up creation, CSV export of index).
- **BE-006**: toggle test — flag off no Task, flag on Task created; correspondence fixture.
- **FE-001..004**: run `npm run build` + `npx tsc --noEmit`; manual smoke (import new formats, auto-assign preview, registry history/follow-up/export). No Playwright suite exists — add only if regression observed.

## 6. Risks + Rollback

| Risk | Mitigation | Rollback |
|------|-----------|----------|
| mp3/mp4 size blowout | `MAX_UPLOAD_SIZE_MB` per family enforced server-side; `accept=` + pre-check client-side | Flag/constant change only; no migration impact |
| Celery async changes behavior | Default `off`; eager mode in tests | Flip flag back off |
| Registry migration numbering (duplicate 0002 exists) | New migration is `0005_...` explicitly depending on `0004_merge_20260921_1122`; validate `migrate --plan` first | `migrate registry 0004` reverses all additions |
| Auto-task side effects on correspondence | `REGISTRY_AUTO_TASK` default off | Flag off; delete tasks created while on |
| Choice extension breaks serializers | Additive choices only; serializer field untouched | Reverse choices migration (choices are not DB-constraining in Postgres) |
| Legacy `.doc`/`.xls` parse instability | Existing line-based parsers unchanged; failure captured per-file into errors list (service already returns `errors`) | No schema change; file stored regardless of parse success |

**Deferred (explicit non-goals, revisit only if ops asks)**: workload-balancing scores (B4), parallel memo approvals (C3), multi-attachment registry model (C5 — reuse files app instead), Playwright E2E suite.