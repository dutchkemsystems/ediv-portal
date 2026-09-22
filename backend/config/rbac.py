"""
Centralized Role-Based Access Control (RBAC) permission system for Education District IV Portal.

Provides role-to-action permission mapping and DRF permission classes that
enforce access at the API view level.
"""

from rest_framework import permissions

# ── Role permission mapping ──────────────────────────────────────────────
# Each app maps actions to the list of roles allowed to perform them.
# Actions: view, create, edit, delete, and app-specific (move, approve, process).

ROLE_PERMISSIONS = {
    "finance": {
        "view": ["SYSADMIN", "TG_PS", "FIN", "PRI"],
        "create": ["SYSADMIN", "TG_PS", "FIN"],
        "edit": ["SYSADMIN", "TG_PS", "FIN"],
        "delete": ["SYSADMIN", "TG_PS"],
    },
    "hr": {
        "view": ["SYSADMIN", "TG_PS", "HR"],
        "create": ["SYSADMIN", "TG_PS", "HR"],
        "edit": ["SYSADMIN", "TG_PS", "HR"],
        "delete": ["SYSADMIN", "TG_PS"],
    },
    "academics": {
        "view": ["SYSADMIN", "TG_PS", "PRI", "VP", "TCH"],
        "create": ["SYSADMIN", "TG_PS", "PRI", "VP", "TCH"],
        "edit": ["SYSADMIN", "TG_PS", "PRI", "VP", "TCH"],
        "delete": ["SYSADMIN", "TG_PS", "PRI"],
    },
    "attendance": {
        "view": ["SYSADMIN", "TG_PS", "PRI", "VP", "TCH"],
        "create": ["SYSADMIN", "TG_PS", "PRI", "VP", "TCH"],
        "edit": ["SYSADMIN", "TG_PS", "PRI", "VP", "TCH"],
        "delete": ["SYSADMIN", "TG_PS"],
    },
    "students": {
        "view": ["SYSADMIN", "TG_PS", "PRI", "VP", "TCH", "PAR"],
        "create": ["SYSADMIN", "TG_PS", "PRI", "VP"],
        "edit": ["SYSADMIN", "TG_PS", "PRI", "VP"],
        "delete": ["SYSADMIN", "TG_PS"],
    },
    "staff": {
        "view": ["SYSADMIN", "TG_PS", "HR", "PRI", "VP"],
        "create": ["SYSADMIN", "TG_PS", "HR"],
        "edit": ["SYSADMIN", "TG_PS", "HR"],
        "delete": ["SYSADMIN", "TG_PS"],
    },
    "files": {
        "view": [
            "SYSADMIN",
            "TG_PS",
            "REG",
            "REG_OFF",
            "PRI",
            "VP",
            "HR",
            "FIN",
            "SA",
            "SA_OFF",
        ],
        "create": ["SYSADMIN", "TG_PS", "REG", "REG_OFF", "PRI", "VP"],
        "move": [
            "SYSADMIN",
            "TG_PS",
            "REG",
            "REG_OFF",
            "PRI",
            "VP",
            "HR",
            "FIN",
            "TCH",
        ],
        "receive": [
            "SYSADMIN",
            "TG_PS",
            "REG",
            "REG_OFF",
            "PRI",
            "VP",
            "HR",
            "FIN",
            "TCH",
        ],
        "close": ["SYSADMIN", "TG_PS", "REG", "REG_OFF", "PRI", "VP", "HR", "FIN"],
        "log_status": [
            "SYSADMIN",
            "TG_PS",
            "REG",
            "REG_OFF",
            "PRI",
            "VP",
            "HR",
            "FIN",
            "TCH",
            "SA",
        ],
        "submit": ["SYSADMIN", "TG_PS", "REG", "REG_OFF", "PRI", "VP"],
        "approve": ["SYSADMIN", "TG_PS", "REG", "PRI"],
        "reject": ["SYSADMIN", "TG_PS", "REG", "PRI"],
        "escalate": ["SYSADMIN", "TG_PS", "REG", "REG_OFF", "PRI", "VP"],
        "delete": ["SYSADMIN", "TG_PS"],
    },
    "mail_workflow": {
        "view": [
            "SYSADMIN",
            "TG_PS",
            "REG",
            "REG_OFF",
            "PRI",
            "VP",
            "HR",
            "FIN",
            "SA",
            "SA_OFF",
        ],
        "create": ["SYSADMIN", "TG_PS", "REG", "REG_OFF", "PRI", "VP"],
        "edit": ["SYSADMIN", "TG_PS", "REG", "REG_OFF", "PRI", "VP"],
        "process": ["SYSADMIN", "TG_PS", "REG", "REG_OFF", "PRI", "VP"],
        "approve": ["SYSADMIN", "TG_PS", "REG", "PRI"],
        "delete": ["SYSADMIN", "TG_PS"],
    },
    "analytics": {
        "view": ["SYSADMIN", "TG_PS", "HR", "FIN", "PRI", "VP"],
        "create": ["SYSADMIN", "TG_PS", "HR", "FIN", "PRI", "VP"],
        "edit": ["SYSADMIN", "TG_PS", "HR", "FIN"],
        "delete": ["SYSADMIN", "TG_PS"],
    },
}


# ── Roles that see all data (not scoped to a school) ────────────────────
GLOBAL_ROLES = frozenset(
    [
        "SYSADMIN",
        "TG_PS",
        "HR",
        "FIN",
        "AUDIT",
        "QA",
        "CC",
        "EMIS",
        "PLAN",
        "PROC",
        "PA",
        "SA",
        "FRENCH",
        "REG",
    ]
)

# Roles scoped to a single school
SCHOOL_SCOPED_ROLES = frozenset(["PRI", "VP", "TCH", "SA_OFF", "REG_OFF"])


# ── Helper: resolve the DRF action to a permission action ───────────────
_ACTION_MAP = {
    "list": "view",
    "retrieve": "view",
    "create": "create",
    "update": "edit",
    "partial_update": "edit",
    "destroy": "delete",
}

# Custom action name -> RBAC key (DRF uses method name, RBAC uses shorter key)
_CUSTOM_ACTION_MAP = {
    # files actions
    "move_file": "move",
    "receive_file": "receive",
    "close_file": "close",
    "log_status": "log_status",
    "log_status_change": "log_status",
    "submit_file": "submit",
    "approve_file": "approve",
    "reject_file": "reject",
    "escalate_file": "escalate",
    "generate_file": "create",
    # mail_workflow actions
    "scan_mail": "create",
    "classify_mail": "edit",
    "assign_mail": "process",
    "forward_mail": "process",
    "respond_to_mail": "process",
    "dispatch_mail": "process",
    "archive_mail": "edit",
    "submit_for_approval": "create",
    "approve_mail": "approve",
    "reject_mail": "reject",
    "deliver_mail": "process",
    "submit_correspondence": "create",
    "receive_correspondence": "process",
    "respond_to_correspondence": "process",
}


def _resolve_action(view):
    """Map a DRF view action to an RBAC action key."""
    action = getattr(view, "action", None)
    if action in _ACTION_MAP:
        return _ACTION_MAP[action]
    if action in _CUSTOM_ACTION_MAP:
        return _CUSTOM_ACTION_MAP[action]
    return action


# ── Permission classes ───────────────────────────────────────────────────


class IsRoleAllowed(permissions.BasePermission):
    """
    Checks whether the requesting user's role is in the allowed list for
    a specific app + action combination.

    Usage (class-level):
        permission_classes = [IsRoleAllowed.for_action('finance', 'view')]

    Usage (dynamic per-action):
        permission_classes = [RoleBasedPermission]
    """

    def __init__(self, allowed_roles=None, app_label=None, action_key=None):
        self.allowed_roles = frozenset(allowed_roles or [])
        self.app_label = app_label
        self.action_key = action_key

    def has_permission(self, request, view):
        if not (request.user and request.user.is_authenticated):
            return False
        return request.user.role in self.allowed_roles

    @classmethod
    def for_action(cls, app_label, action_key):
        """Factory: returns a pre-configured permission instance."""
        allowed = ROLE_PERMISSIONS.get(app_label, {}).get(action_key, [])
        return cls(allowed_roles=allowed, app_label=app_label, action_key=action_key)


class RoleBasedPermission(permissions.BasePermission):
    """
    Generic DRF permission class that reads the app name from the view
    (via ``view.rbac_app``) and the resolved action, then checks the
    ROLE_PERMISSIONS mapping.

    ViewSet usage:
        class MyViewSet(viewsets.ModelViewSet):
            rbac_app = "finance"
            permission_classes = [RoleBasedPermission]
    """

    def has_permission(self, request, view):
        if not (request.user and request.user.is_authenticated):
            return False

        app_label = getattr(view, "rbac_app", None)
        if app_label is None:
            # Fallback: try to derive from the view's module path
            module = getattr(view, "__module__", "")
            for key in ROLE_PERMISSIONS:
                if key in module:
                    app_label = key
                    break

        if app_label is None:
            # No RBAC mapping — deny by default
            return False

        action_key = _resolve_action(view)
        allowed_roles = ROLE_PERMISSIONS.get(app_label, {}).get(action_key, [])
        return request.user.role in allowed_roles


class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Object-level permission: users can view/edit their own resources,
    admins (SYSADMIN, TG_PS) and department heads can view/edit all.

    The view must expose a ``owner_field`` attribute that points to the
    field on the model instance holding the user reference (default ``user``).
    """

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        user = request.user
        # Admins always pass
        if user.role in ("SYSADMIN", "TG_PS"):
            return True
        # Department heads pass on read
        if user.is_department_head and request.method in permissions.SAFE_METHODS:
            return True
        # Owner check
        owner_field = getattr(view, "owner_field", "user")
        owner = getattr(obj, owner_field, None)
        if owner is None:
            return False
        # owner can be a User instance or a FK — handle both
        if hasattr(owner, "pk"):
            return owner.pk == user.pk
        return owner == user.pk


class SchoolScopedPermission(permissions.BasePermission):
    """
    Combines role-based access with school-scoped filtering.

    For school-scoped roles (PRI, VP, TCH, SA_OFF, REG_OFF), querysets are
    filtered to only show data from their school.  Global roles see all data.

    ViewSet usage:
        class MyViewSet(viewsets.ModelViewSet):
            rbac_app = "students"
            permission_classes = [SchoolScopedPermission]

    The view should define ``school_filter_field`` (default ``school``) if the
    FK name differs.
    """

    def has_permission(self, request, view):
        if not (request.user and request.user.is_authenticated):
            return False
        app_label = getattr(view, "rbac_app", None)
        if app_label is None:
            return False
        action_key = _resolve_action(view)
        allowed_roles = ROLE_PERMISSIONS.get(app_label, {}).get(action_key, [])
        return request.user.role in allowed_roles

    def filter_queryset(self, request, queryset, view):
        """Apply school-scoped filtering to the queryset."""
        user = request.user
        if user.role in SCHOOL_SCOPED_ROLES:
            school_filter_field = getattr(view, "school_filter_field", "school")
            # Try to get the staff profile's school
            try:
                school = user.staff_profile.school
                if school:
                    return queryset.filter(**{school_filter_field: school})
            except Exception:
                pass
        return queryset


# ── Convenience: school-scoped queryset mixin ────────────────────────────


class SchoolScopedQuerysetMixin:
    """
    Mixin for ViewSets that should filter querysets based on the user's
    school assignment.  Use with ``SchoolScopedPermission`` or standalone.

    Views must define ``rbac_app`` and optionally ``school_filter_field``.
    """

    school_filter_field = "school"

    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user
        if user.role in SCHOOL_SCOPED_ROLES:
            try:
                school = user.staff_profile.school
                if school:
                    return qs.filter(**{self.school_filter_field: school})
            except Exception:
                pass
        return qs
