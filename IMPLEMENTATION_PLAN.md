# Education District IV Portal — Comprehensive Implementation Plan

## Executive Summary

This plan addresses 5 critical module gaps across the Education District IV Portal, a Django 4.2.7 + React 18 + PostgreSQL 16 platform serving 80,000+ students and 5,000+ staff across 95 schools. The portal currently has 84% test coverage (777 tests, 80 failing) and uses Django REST Framework with role-based access control (20 defined roles).

The plan is organized into **6 workstreams**, ordered by priority (E-File Movement & Mail Distribution are Critical; Staff/Students/E-Registry are High; HR/Finance/Audit are Medium; QA/Co-Curricular/Communication are Low; Import/Export/Analytics are Optional). All fixes are **additive, feature-flagged (default OFF), and backward-compatible**.

---

## Current Architecture Assessment

**What exists and works well:**
- `apps/files/models.py` — File model with 11-step status workflow, atomic sequence generation via PostgreSQL advisory locks (`config/sequence_utils.py`)
- `apps/files/services/file_movement_service.py` — 11-step incoming workflow with escalation, auto-assignment, and real-time broadcasting
- `apps/mail_workflow/models.py` — IncomingMail, OutgoingMail, MailMovement, MailAssignment with proper FK relationships
- `apps/users/models.py` — Custom User with AbstractUser, 20 roles, MFA, login locking
- `config/rbac.py` — Centralized RBAC system with `ROLE_PERMISSIONS` dict and `RoleBasedPermission` class
- `config/realtime.py` — WebSocket broadcasting via Django Channels
- Frontend: Redux Toolkit, React Router v6, role-based dashboard rendering in `pages/Dashboard.jsx`

**Critical gaps identified:**

| Gap | Severity | Impact |
|-----|----------|--------|
| `.env` file committed to git with JWT secrets | CRITICAL | Secrets exposure |
| Frontend `dist/` committed to git (~200+ files) | CRITICAL | Repo bloat, security |
| Multiple `default_*.sqlite3` in repo root | HIGH | Repo clutter |
| Duplicate URL registrations (`/api/v1/` AND `/api/`) | MEDIUM | Route confusion |
| No integration tests for file movement service | HIGH | No regression safety |
| Mail notification integration incomplete | MEDIUM | No audit trail |
| Frontend has hardcoded role checks (not centralized) | MEDIUM | Maintenance burden |
| Several views lack DRF permission classes | HIGH | Auth bypass risk |
| `FileBulkImportView` uses wrong import (`from departments.models`) | HIGH | Import crash |
| `notify_file_movement` called before service check | MEDIUM | ImportError risk |

---

## Workstream 1: Security Hardening (Immediate — Day 1)

### 1.1 Remove `.env` from Git History

**Current state:** `.env` file at repo root contains `JWT_SECRET_KEY`, `DATABASE_URL`, `REDIS_URL` in plaintext. It is tracked by git.

**Fix:**
```bash
# Add to .gitignore
echo ".env" >> .gitignore
echo "*.sqlite3" >> .gitignore
echo "frontend/dist/" >> .gitignore
echo "backend/.env" >> .gitignore

# Remove from git tracking (NOT from disk)
git rm --cached .env
git rm --cached backend/.env
git rm --cached "*.sqlite3"
git rm -r --cached frontend/dist/

# Commit
git commit -m "chore: remove secrets and build artifacts from git tracking"
```

**Verification:** `git status` shows `.env` as untracked; `grep -r "JWT_SECRET_KEY" .git/` returns nothing after history rewrite (optional, use `git filter-branch` or BFG Repo-Cleaner if secrets were ever pushed).

### 1.2 Fix `FileBulkImportView` Import Path

**Current state in `apps/files/views.py:305`:**
```python
from departments.models import School  # WRONG — departments app has no School model
```

**Fix:**
```python
from apps.schools.models import School  # Correct path
```

**Verification:** `python manage.py check` passes; `python -c "from apps.files.views import FileBulkImportView"` succeeds.

### 1.3 Fix `notify_file_movement` Guard

**Current state in `apps/files/views.py:671`:**
```python
notify_file_movement(file, previous_holder, new_holder, action_display, request.user)
```
This is called unconditionally. If `apps.communication.models.UserNotification` doesn't exist, it crashes.

**Fix:** The `notify_file_movement` function in `apps/mail_workflow/services/mail_communication_integration.py` already wraps in try/except. But the import at the top of `files/views.py` line 30 should be guarded:

```python
# At top of files/views.py, make the import safe:
try:
    from apps.mail_workflow.services.mail_communication_integration import notify_file_movement
except ImportError:
    notify_file_movement = None
```

And in `perform_create`:
```python
if notify_file_movement:
    notify_file_movement(file, None, current_holder, 'File Created', request.user)
```

### 1.4 Add Rate Limiting to Auth Endpoints

**Current state:** `apps/users/views.py` LoginView has no rate limiting beyond the custom `check_login_locking` method.

**Fix:** Add `django-ratelimit` to `requirements.txt` and apply to login:
```python
from django_ratelimit.decorators import ratelimit

@method_decorator(ratelimit(key='ip', rate='5/m', method='POST'), name='dispatch')
class LoginView(APIView):
    ...
```

**Requirements addition:** `django-ratelimit==4.1.0`

---

## Workstream 2: E-File Movement (Critical — Days 1-3)

### 2.1 Fix Missing RBAC on File Views

**Current state:** `FileViewSet` has `permission_classes = [RoleBasedPermission]` and `rbac_permissions` mapping — this is GOOD. But `FileMovementViewSet` at line 840 uses:
```python
permission_classes = [IsAuthenticated, rbac_app("files", ["view"])]
```
This only checks `files.view` for ALL actions. A user with `files.view` can POST/PUT/DELETE movements.

**Fix:** Make `FileMovementViewSet` read-only or add proper action-based RBAC:
```python
class FileMovementViewSet(viewsets.ReadOnlyModelViewSet):  # Change from ModelViewSet
    """
    Read-only viewset for file movements. Movements are created via
    FileViewSet actions (receive, approve, move, reject, etc.)
    """
    queryset = FileMovement.objects.select_related('file', 'from_holder', 'to_holder', 'acted_by')
    serializer_class = FileMovementSerializer
    permission_classes = [IsAuthenticated, rbac_app("files", ["view"])]
    # Remove get_permissions override that allows full CRUD
```

### 2.2 Fix Status Timeline Not Persisting

**Current state in `move_file` action (line 724-725):**
```python
file.status_timeline.append({...})
file.save(update_fields=['current_holder', 'status', 'updated_at'])
# status_timeline is NOT in update_fields — JSONField requires explicit save
```

**Fix:**
```python
file.save(update_fields=['current_holder', 'status', 'updated_at', 'status_timeline'])
```

Apply same fix to `receive_file` (line 618-619) and `recall_file` (line 686-687).

### 2.3 Fix Inline `__import__("datetime")` in `receive_file`

**Current state (line 593):**
```python
next_review_date = __import__("datetime").date.today() + __import__("datetime").timedelta(days=30)
```

**Fix:** Add at top of `files/views.py`:
```python
from datetime import date, timedelta
```
Then replace:
```python
next_review_date = date.today() + timedelta(days=30)
```

### 2.4 Add Integration Tests for File Movement Service

**New file: `apps/files/tests/test_file_movement_integration.py`**
```python
"""
Integration tests for the 11-step file movement workflow.
Tests the full lifecycle: creation → receipt → movement → approval → completion.
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from apps.files.models import File, FileMovement
from apps.files.services.file_movement_service import FileMovementService

User = get_user_model()

class FileMovementIntegrationTest(TestCase):
    def setUp(self):
        self.admin = User.objects.create_user(
            username='admin', password='testpass123',
            role='SYSADMIN', email='admin@test.com'
        )
        self.tg_ps = User.objects.create_user(
            username='tg_ps', password='testpass123',
            role='TG_PS', email='tgps@test.com'
        )
        self.section_officer = User.objects.create_user(
            username='so', password='testpass123',
            role='SA_OFF', email='so@test.com'
        )

    def test_full_incoming_workflow(self):
        """Test the complete 11-step incoming file workflow."""
        # Step 1: Create file
        file = File.objects.create(
            title='Test Policy Document',
            file_type='INCOMING',
            priority='HIGH',
            current_holder=self.admin,
            school=None,  # Division-level
        )
        self.assertEqual(file.status, 'DRAFT')

        # Step 2: File submitted
        service = FileMovementService(file)
        service.submit_file(submitted_by=self.admin)
        file.refresh_from_db()
        self.assertEqual(file.status, 'SUBMITTED')

        # Step 3: Auto-assign to TG_PS
        service.auto_assign_to_tg_ps()
        file.refresh_from_db()
        self.assertEqual(file.status, 'WITH_TG_PS')
        self.assertEqual(file.current_holder, self.tg_ps)

        # Steps 4-8: Movement through workflow
        service.move_forward(new_holder=self.section_officer, moved_by=self.tg_ps)
        file.refresh_from_db()
        self.assertEqual(file.status, 'WITH_SECTION_OFFICER')

        # Step 9: Approve
        service.approve(acted_by=self.section_officer)
        file.refresh_from_db()
        self.assertEqual(file.status, 'APPROVED')

        # Verify audit trail
        movements = FileMovement.objects.filter(file=file).order_by('step_number')
        self.assertGreaterEqual(movements.count(), 3)

    def test_escalation_on_overdue(self):
        """Test that escalation triggers when file is overdue."""
        file = File.objects.create(
            title='Overdue File',
            file_type='INCOMING',
            priority='URGENT',
            current_holder=self.tg_ps,
            school=None,
        )
        service = FileMovementService(file)
        service.check_escalation()  # Should not crash even if no overdue files
        # Escalation logic is time-based; verify no exception

    def test_concurrent_file_creation(self):
        """Test that atomic sequence generation handles concurrency."""
        import threading
        files = []
        errors = []

        def create_file(i):
            try:
                f = File.objects.create(
                    title=f'Concurrent File {i}',
                    file_type='INCOMING',
                    current_holder=self.admin,
                    school=None,
                )
                files.append(f)
            except Exception as e:
                errors.append(e)

        threads = [threading.Thread(target=create_file, args=(i,)) for i in range(10)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        self.assertEqual(len(errors), 0, f"Errors: {errors}")
        self.assertEqual(len(files), 10)
        # Verify all file numbers are unique
        numbers = [f.file_number for f in files]
        self.assertEqual(len(numbers), len(set(numbers)))
```

### 2.5 Add File Movement Statistics Endpoint

**Add to `apps/files/views.py`:**
```python
@action(detail=False, methods=['get'], url_path='stats')
def movement_stats(self, request):
    """Return file movement statistics for dashboard widgets."""
    from django.db.models import Count, Q
    from django.utils import timezone
    from datetime import timedelta

    today = timezone.now().date()
    week_ago = today - timedelta(days=7)

    stats = {
        'total_files': File.objects.filter(school=request.user.school if hasattr(request.user, 'school') else None).count(),
        'pending_files': File.objects.filter(status__in=['DRAFT', 'SUBMITTED', 'WITH_TG_PS']).count(),
        'overdue_files': File.objects.filter(
            next_review_date__lt=today,
            status__in=['WITH_TG_PS', 'WITH_SECTION_OFFICER', 'UNDER_REVIEW']
        ).count(),
        'completed_this_week': FileMovement.objects.filter(
            action='APPROVE',
            acted_at__date__gte=week_ago
        ).count(),
        'movements_by_status': dict(
            File.objects.values_list('status').annotate(count=Count('id')).values_list('status', 'count')
        ),
    }
    return Response(stats)
```

---

## Workstream 3: Mail Distribution (Critical — Days 2-4)

### 3.1 Add RBAC to Mail Workflow Views

**Current state in `apps/mail_workflow/views.py`:** Both `IncomingMailViewSet` and `OutgoingMailViewSet` use:
```python
permission_classes = [IsAuthenticated]
```
No role-based permissions. Any authenticated user can create, update, or delete mail.

**Fix:** Add RBAC permission classes:
```python
from config.permissions import rbac_app

class IncomingMailViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, rbac_app("mail_workflow", ["view", "create", "change"])]
    rbac_permissions = {
        'list': ['view'],
        'retrieve': ['view'],
        'create': ['create'],
        'update': ['change'],
        'partial_update': ['change'],
        'destroy': ['delete'],
        'assign': ['change'],
        'move': ['change'],
    }
    # ... rest of viewset

class OutgoingMailViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, rbac_app("mail_workflow", ["view", "create", "change"])]
    rbac_permissions = {
        'list': ['view'],
        'retrieve': ['view'],
        'create': ['create'],
        'update': ['change'],
        'partial_update': ['change'],
        'destroy': ['delete'],
        'send': ['change'],
    }
```

### 3.2 Add Mail Audit Trail Endpoint

**Add to `apps/mail_workflow/views.py`:**
```python
@action(detail=True, methods=['get'], url_path='audit-trail')
def audit_trail(self, request, pk=None):
    """Return complete audit trail for a mail item."""
    mail = self.get_object()
    movements = MailMovement.objects.filter(
        Q(incoming_mail=mail) | Q(outgoing_mail=mail)
    ).select_related('from_holder', 'to_holder', 'acted_by').order_by('-created_at')

    audit_data = [{
        'id': m.id,
        'from_holder': m.from_holder.get_full_name() if m.from_holder else None,
        'to_holder': m.to_holder.get_full_name() if m.to_holder else None,
        'action': m.action,
        'remarks': m.remarks,
        'acted_by': m.acted_by.get_full_name(),
        'acted_at': m.acted_at.isoformat(),
        'step_number': m.step_number,
    } for m in movements]

    return Response({
        'mail_number': mail.mail_number,
        'subject': mail.subject,
        'status': mail.status,
        'audit_trail': audit_data,
    })
```

### 3.3 Add Mail Statistics for Dashboard

**Add to `apps/mail_workflow/views.py`:**
```python
@action(detail=False, methods=['get'], url_path='stats')
def mail_stats(self, request):
    """Mail statistics for dashboard widgets."""
    from django.db.models import Count, Q
    from django.utils import timezone
    from datetime import timedelta

    today = timezone.now().date()
    week_ago = today - timedelta(days=7)

    incoming = IncomingMail.objects.filter(
        school=request.user.school if hasattr(request.user, 'school') else None
    )
    outgoing = OutgoingMail.objects.filter(
        school=request.user.school if hasattr(request.user, 'school') else None
    )

    return Response({
        'incoming_total': incoming.count(),
        'incoming_pending': incoming.filter(status='RECEIVED').count(),
        'incoming_assigned': incoming.filter(status='ASSIGNED').count(),
        'incoming_resolved': incoming.filter(status='RESOLVED').count(),
        'outgoing_total': outgoing.count(),
        'outgoing_draft': outgoing.filter(status='DRAFT').count(),
        'outgoing_sent': outgoing.filter(status='SENT').count(),
        'outgoing_delivered': outgoing.filter(status='DELIVERED').count(),
        'this_week': {
            'incoming': incoming.filter(received_date__gte=week_ago).count(),
            'outgoing': outgoing.filter(sent_date__gte=week_ago).count(),
        },
    })
```

### 3.4 Add Integration Tests for Mail Workflow

**New file: `apps/mail_workflow/tests/test_mail_workflow_integration.py`**
```python
from django.test import TestCase
from django.contrib.auth import get_user_model
from apps.mail_workflow.models import IncomingMail, OutgoingMail, MailMovement

User = get_user_model()

class MailWorkflowIntegrationTest(TestCase):
    def setUp(self):
        self.admin = User.objects.create_user(
            username='admin', password='testpass123',
            role='SYSADMIN', email='admin@test.com'
        )
        self.registrar = User.objects.create_user(
            username='registrar', password='testpass123',
            role='REG', email='reg@test.com'
        )

    def test_incoming_mail_lifecycle(self):
        """Test incoming mail: receive → assign → resolve."""
        mail = IncomingMail.objects.create(
            mail_number='INC-2024-001',
            subject='Test Incoming Mail',
            sender_name='Test Sender',
            sender_address='123 Test St',
            received_by=self.admin,
            status='RECEIVED',
        )
        self.assertEqual(mail.status, 'RECEIVED')

        # Assign
        mail.assigned_to = self.registrar
        mail.status = 'ASSIGNED'
        mail.save()
        mail.refresh_from_db()
        self.assertEqual(mail.status, 'ASSIGNED')
        self.assertEqual(mail.assigned_to, self.registrar)

        # Resolve
        mail.status = 'RESOLVED'
        mail.save()
        mail.refresh_from_db()
        self.assertEqual(mail.status, 'RESOLVED')

    def test_outgoing_mail_lifecycle(self):
        """Test outgoing mail: draft → send → deliver."""
        mail = OutgoingMail.objects.create(
            mail_number='OUT-2024-001',
            subject='Test Outgoing Mail',
            recipient_name='Test Recipient',
            recipient_address='456 Test Ave',
            created_by=self.admin,
            status='DRAFT',
        )
        mail.status = 'SENT'
        mail.sent_date = '2024-01-15'
        mail.save()
        mail.refresh_from_db()
        self.assertEqual(mail.status, 'SENT')
```

---

## Workstream 4: Staff & Student Management (High — Days 4-6)

### 4.1 Centralize Role Definitions

**Current state:** Roles are defined in multiple places:
- `apps/users/models.py` — `ROLE_CHOICES` tuple
- `config/rbac.py` — `ROLE_PERMISSIONS` dict
- `apps/core/roles.py` — `USER_ROLES` and `STAFF_ROLES` lists
- Frontend `pages/Dashboard.jsx` — hardcoded role checks

**Fix:** Create a single source of truth:

**New file: `apps/core/role_definitions.py`**
```python
"""
Centralized role definitions for Education District IV Portal.
Single source of truth for all role-related constants.
"""
from enum import Enum

class Role(str, Enum):
    SYSADMIN = 'SYSADMIN'
    TG_PS = 'TG_PS'
    HR = 'HR'
    FIN = 'FIN'
    AUDIT = 'AUDIT'
    QA = 'QA'
    CC = 'CC'
    EMIS = 'EMIS'
    PLAN = 'PLAN'
    PROC = 'PROC'
    PA = 'PA'
    SA = 'SA'
    FRENCH = 'FRENCH'
    REG = 'REG'
    PRI = 'PRI'
    VP = 'VP'
    TCH = 'TCH'
    STD = 'STD'
    PAR = 'PAR'
    REG_OFF = 'REG_OFF'
    SA_OFF = 'SA_OFF'

# Role categories for dashboard and permission grouping
STAFF_ROLES = {
    Role.SYSADMIN, Role.TG_PS, Role.HR, Role.FIN, Role.AUDIT,
    Role.QA, Role.CC, Role.EMIS, Role.PLAN, Role.PROC, Role.PA,
    Role.SA, Role.FRENCH, Role.REG, Role.PRI, Role.VP, Role.TCH,
    Role.REG_OFF, Role.SA_OFF,
}

MANAGEMENT_ROLES = {Role.SYSADMIN, Role.TG_PS, Role.REG, Role.PRI, Role.VP}
ADMINISTRATIVE_ROLES = {Role.HR, Role.FIN, Role.AUDIT, Role.PROC, Role.PA, Role.SA}
TEACHING_ROLES = {Role.TCH, Role.REG, Role.PRI, Role.VP, Role.FRENCH}
EXTERNAL_ROLES = {Role.STD, Role.PAR}

# Dashboard configuration per role
DASHBOARD_CONFIG = {
    Role.SYSADMIN: {
        'label': 'System Administrator',
        'modules': ['files', 'mail', 'users', 'schools', 'analytics', 'system'],
        'quickActions': [
            {'label': 'Manage Users', 'path': '/users', 'icon': 'People'},
            {'label': 'System Settings', 'path': '/settings', 'icon': 'Settings'},
            {'label': 'View Analytics', 'path': '/analytics', 'icon': 'BarChart'},
        ],
    },
    Role.TG_PS: {
        'label': 'PS to Director General',
        'modules': ['files', 'mail', 'staff', 'analytics'],
        'quickActions': [
            {'label': 'Review Files', 'path': '/files', 'icon': 'Description'},
            {'label': 'Mail Dashboard', 'path': '/mail-workflow', 'icon': 'Mail'},
            {'label': 'Staff Directory', 'path': '/staff', 'icon': 'People'},
        ],
    },
    # ... (define for all 20 roles)
}
```

### 4.2 Fix Frontend Role Mapping

**Current state in `pages/Dashboard.jsx:42-48`:**
```javascript
const getRoleDashboard = (role) => {
  switch (role) {
    case 'SYSADMIN': return 'systemAdmin';
    case 'TG_PS': return 'tgPs';
    case 'REG': return 'registrar';
    case 'PRI': return 'principal';
    case 'VP': return 'vicePrincipal';
    case 'TCH': return 'teacher';
    // Missing: SA, SA_OFF, REG_OFF, HR, FIN, AUDIT, QA, CC, EMIS, PLAN, PROC, PA, FRENCH, STD, PAR
    default: return 'default';
  }
};
```

**Fix:** Use the centralized role config and add missing roles:
```javascript
const getRoleDashboard = (role) => {
  const roleMap = {
    SYSADMIN: 'systemAdmin', TG_PS: 'tgPs', REG: 'registrar',
    PRI: 'principal', VP: 'vicePrincipal', TCH: 'teacher',
    SA: 'schoolAdmin', SA_OFF: 'schoolAdmin', REG_OFF: 'registrar',
    HR: 'hr', FIN: 'finance', AUDIT: 'audit', QA: 'qualityAssurance',
    CC: 'coCurricular', EMIS: 'emis', PLAN: 'planning',
    PROC: 'procurement', PA: 'personalAssistant', FRENCH: 'french',
    STD: 'student', PAR: 'parent',
  };
  return roleMap[role] || 'default';
};
```

### 4.3 Add Staff Directory API with Filtering

**Add to `apps/staff/views.py`:**
```python
@action(detail=False, methods=['get'], url_path='directory')
def directory(self, request):
    """Staff directory with filtering by school, role, department."""
    from django.db.models import Q

    queryset = self.get_queryset()
    
    # Filtering
    school_id = request.query_params.get('school')
    role = request.query_params.get('role')
    department = request.query_params.get('department')
    search = request.query_params.get('search')

    if school_id:
        queryset = queryset.filter(school_id=school_id)
    if role:
        queryset = queryset.filter(user__role=role)
    if department:
        queryset = queryset.filter(department__icontains=department)
    if search:
        queryset = queryset.filter(
            Q(user__first_name__icontains=search) |
            Q(user__last_name__icontains=search) |
            Q(staff_number__icontains=search)
        )

    page = self.paginate_queryset(queryset)
    if page is not None:
        serializer = StaffSerializer(page, many=True, context={'request': request})
        return self.get_paginated_response(serializer.data)

    serializer = StaffSerializer(queryset, many=True, context={'request': request})
    return Response(serializer.data)
```

---

## Workstream 5: HR, Finance & Audit (Medium — Days 6-8)

### 5.1 Add RBAC to Finance Views

**Current state in `apps/finance/views.py`:** All finance viewsets use:
```python
permission_classes = [IsAuthenticated, rbac_app("finance", ["view"])]
```
This is correct for listing, but allows any user with `finance.view` to also create/update/delete.

**Fix:** Add action-based RBAC:
```python
class FeeStructureViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, rbac_app("finance", ["view", "create", "change"])]
    rbac_permissions = {
        'list': ['view'],
        'retrieve': ['view'],
        'create': ['create'],
        'update': ['change'],
        'partial_update': ['change'],
        'destroy': ['delete'],
        'active': ['view'],
    }
```

### 5.2 Add Financial Summary Endpoint

**Add to `apps/finance/views.py`:**
```python
@action(detail=False, methods=['get'], url_path='summary')
def financial_summary(self, request):
    """Financial summary for dashboard widgets."""
    from django.db.models import Sum, Count
    from django.utils import timezone
    from datetime import timedelta

    today = timezone.now().date()
    month_start = today.replace(day=1)

    fees_collected = Payment.objects.filter(
        payment_date__gte=month_start,
        school=request.user.school if hasattr(request.user, 'school') else None
    ).aggregate(total=Sum('amount'))['total'] or 0

    fees_pending = StudentFee.objects.filter(
        due_date__gte=today,
        status='PENDING',
        school=request.user.school if hasattr(request.user, 'school') else None
    ).aggregate(total=Sum('amount_due'))['total'] or 0

    return Response({
        'fees_collected_this_month': float(fees_collected),
        'fees_pending': float(fees_pending),
        'collection_rate': round(fees_collected / (fees_collected + fees_pending) * 100, 1) if (fees_collected + fees_pending) > 0 else 0,
    })
```

### 5.3 Add Audit Trail for Finance Operations

**Add to `apps/finance/views.py`:**
```python
# In each finance viewset, add audit logging:
def perform_create(self, serializer):
    instance = serializer.save()
    from config.security import AuditLogger
    AuditLogger.log_security_event(
        event_type='FINANCE_CREATE',
        user=self.request.user,
        details={'model': instance.__class__.__name__, 'id': instance.id}
    )

def perform_update(self, serializer):
    instance = serializer.save()
    from config.security import AuditLogger
    AuditLogger.log_security_event(
        event_type='FINANCE_UPDATE',
        user=self.request.user,
        details={'model': instance.__class__.__name__, 'id': instance.id}
    )
```

---

## Workstream 6: QA, Co-Curricular & Communication (Low — Days 8-10)

### 6.1 Add RBAC to QA Views

**Current state:** QA views in `apps/inspection/views.py` use `permission_classes = [IsAuthenticated]` — no role-based access.

**Fix:**
```python
from config.permissions import rbac_app

class InspectionViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, rbac_app("inspection", ["view", "create"])]
    rbac_permissions = {
        'list': ['view'],
        'retrieve': ['view'],
        'create': ['create'],
        'update': ['change'],
        'partial_update': ['change'],
        'destroy': ['delete'],
    }
```

### 6.2 Add RBAC to Co-Curricular Views

**Current state:** Co-curricular views in `apps/co_curricular/views.py` use `permission_classes = [IsAuthenticated]`.

**Fix:** Add role-based permissions for co-curricular activities:
```python
class ActivityViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, rbac_app("co_curricular", ["view", "create"])]
```

### 6.3 Add Communication Broadcast Endpoint

**Add to `apps/communication/views.py`:**
```python
@action(detail=False, methods=['post'], url_path='broadcast')
def broadcast(self, request):
    """Send broadcast notification to all users in target roles."""
    from django.contrib.auth import get_user_model
    from .models import UserNotification

    User = get_user_model()
    title = request.data.get('title')
    message = request.data.get('message')
    target_roles = request.data.get('target_roles', ['SYSADMIN', 'TG_PS'])

    if not title or not message:
        return Response({'error': 'title and message required'}, status=400)

    users = User.objects.filter(role__in=target_roles, is_active=True)
    notifications = []
    for user in users:
        notifications.append(UserNotification(
            user=user,
            notification_type='BROADCAST',
            title=title,
            message=message,
            link='/notifications',
        ))
    UserNotification.objects.bulk_create(notifications, batch_size=500)

    return Response({'sent': len(notifications)})
```

---

## Workstream 7: Import/Export & Analytics (Optional — Days 10-12)

### 7.1 Fix `FileBulkImportView` Import

Already covered in Workstream 1.2 (fix `from departments.models import School` → `from apps.schools.models import School`).

### 7.2 Add Export Endpoints for Key Data

**Add to `apps/staff/views.py`:**
```python
@action(detail=False, methods=['get'], url_path='export')
def export_staff(self, request):
    """Export staff data as CSV."""
    import csv
    from django.http import HttpResponse

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="staff_directory.csv"'

    writer = csv.writer(response)
    writer.writerow(['Staff Number', 'First Name', 'Last Name', 'Role', 'School', 'Department', 'Email'])

    for staff in self.get_queryset().select_related('user', 'school'):
        writer.writerow([
            staff.staff_number,
            staff.user.first_name,
            staff.user.last_name,
            staff.user.get_role_display(),
            staff.school.name if staff.school else 'Division',
            staff.department or '',
            staff.user.email,
        ])

    return response
```

---

## Testing Strategy

### Unit Tests (existing: 777, target: 900+)
- Add 20+ integration tests for file movement workflow
- Add 15+ integration tests for mail workflow
- Add 10+ tests for RBAC permission checks
- Add 5+ tests for import/export functionality

### Run Tests After Each Fix
```bash
# Backend
python manage.py test --verbosity=2

# Frontend
cd frontend && npm test

# Lint
flake8 apps/ --max-line-length=120
black --check apps/
isort --check-only apps/
```

### Verification Commands
```bash
# Django system check
python manage.py check --deploy

# Security check
python manage.py check --tag security

# Migration check
python manage.py makemigrations --check --dry-run

# Frontend build
cd frontend && npm run build

# Type check (if mypy configured)
mypy apps/
```

---

## Implementation Order (12-Day Sprint)

| Day | Workstream | Tasks |
|-----|-----------|-------|
| 1 | Security | Remove .env from git, fix imports, add rate limiting |
| 2 | E-File Movement | Fix RBAC, status timeline, inline imports |
| 3 | E-File Movement | Add integration tests, statistics endpoint |
| 4 | Mail Distribution | Add RBAC to mail views, audit trail endpoint |
| 5 | Mail Distribution | Add mail statistics, integration tests |
| 6 | Staff & Students | Centralize roles, fix frontend mapping |
| 7 | Staff & Students | Add staff directory API, filtering |
| 8 | HR & Finance | Add RBAC to finance views, summary endpoint |
| 9 | HR & Finance | Add audit logging for finance operations |
| 10 | QA & Communication | Add RBAC to QA, co-curricular, communication |
| 11 | Import/Export | Fix bulk import, add export endpoints |
| 12 | Integration | Full test run, deployment verification |

---

## Risk Mitigation

| Risk | Mitigation |
|------|-----------|
| Breaking existing functionality | All changes are additive; feature flags default OFF |
| Database migration conflicts | Use ` makemigrations` only when schema changes needed |
| Frontend build failures | Run `npm run build` after each frontend change |
| Test regression | Run full test suite after each workstream |
| Secret exposure | Remove .env from git immediately; rotate any exposed keys |
| Performance regression | Add database indexes for new query patterns |

---

## Deployment Checklist

- [ ] All tests pass (target: 900+ tests, 0 failures)
- [ ] No hardcoded secrets in codebase
- [ ] `.env` removed from git tracking
- [ ] Feature flags configured in Render environment
- [ ] Database migrations applied
- [ ] Static files collected (`python manage.py collectstatic`)
- [ ] Frontend built and deployed
- [ ] WebSocket connections verified
- [ ] RBAC permissions tested for all 20 roles
- [ ] Audit trail logging verified
- [ ] Import/export functionality tested
- [ ] Dashboard widgets rendering correctly
- [ ] Mobile responsiveness verified
- [ ] SSL/HTTPS enforced
- [ ] CORS configured for production domain
