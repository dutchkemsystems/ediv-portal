"""
Role-Based Access Control (RBAC) permissions for Education District IV Portal.

Enforces role-based access at the API view level.

This module now integrates with the centralized RBAC system in ``config.rbac``
while preserving backward-compatible permission classes.
"""

from rest_framework import permissions

from config.rbac import (
    GLOBAL_ROLES,
    IsOwnerOrAdmin,
    IsRoleAllowed,
    RoleBasedPermission,
    SchoolScopedPermission,
    SchoolScopedQuerysetMixin,
)

# Backward-compatible alias — RolePermissions was removed during rbac refactor
RolePermissions = RoleBasedPermission


# ── Legacy role constants (kept for backward compatibility) ──────────────
SYSADMIN = "SYSADMIN"
TG_PS = "TG_PS"
DEPARTMENT_HEADS = (
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
)
SCHOOL_MANAGEMENT = ("PRI", "VP")
SCHOOL_STAFF = ("TCH", "SA_OFF", "REG_OFF")
END_USERS = ("STD", "PAR")

ALL_ADMIN_ROLES = (SYSADMIN, TG_PS) + DEPARTMENT_HEADS
ALL_SCHOOL_ROLES = SCHOOL_MANAGEMENT + SCHOOL_STAFF


# ── Legacy permission classes (now thin wrappers around RBAC) ─────────────


class IsAdminUser(permissions.BasePermission):
    """Only SYSADMIN can access."""

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.role == SYSADMIN
        )


class IsAdminOrTG(permissions.BasePermission):
    """SYSADMIN or TG_PS can access."""

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.role in (SYSADMIN, TG_PS)
        )


class IsAdminOrTGOrDeptHead(permissions.BasePermission):
    """SYSADMIN, TG_PS, or department heads can access."""

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.role in ALL_ADMIN_ROLES
        )


class IsSchoolManagementOrAbove(permissions.BasePermission):
    """School management (PRI, VP) and above can access."""

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.role
            in (SYSADMIN, TG_PS) + DEPARTMENT_HEADS + SCHOOL_MANAGEMENT
        )


class IsStaffReadOnly(permissions.BasePermission):
    """Read-only for all authenticated, write only for admin/management."""

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return request.user and request.user.is_authenticated
        return (
            request.user
            and request.user.is_authenticated
            and request.user.role
            in (SYSADMIN, TG_PS) + DEPARTMENT_HEADS + SCHOOL_MANAGEMENT
        )


class IsFinanceOrAdmin(permissions.BasePermission):
    """Finance operations: only SYSADMIN, TG_PS, FIN, PRI."""

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.role in (SYSADMIN, TG_PS, "FIN", "PRI")
        )


class IsHROrAdmin(permissions.BasePermission):
    """HR operations: only SYSADMIN, TG_PS, HR."""

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.role in (SYSADMIN, TG_PS, "HR")
        )


class IsAcademicStaff(permissions.BasePermission):
    """Academic operations: admin, dept heads, school management, teachers."""

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return request.user and request.user.is_authenticated
        return (
            request.user
            and request.user.is_authenticated
            and request.user.role
            in (SYSADMIN, TG_PS) + DEPARTMENT_HEADS + ALL_SCHOOL_ROLES
        )


class IsSchoolStaffOrAdmin(permissions.BasePermission):
    """School-level operations: admin, school management, school staff."""

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return request.user and request.user.is_authenticated
        return (
            request.user
            and request.user.is_authenticated
            and request.user.role in (SYSADMIN, TG_PS) + ALL_SCHOOL_ROLES
        )


class IsMailStaff(permissions.BasePermission):
    """Mail operations: admin, dept heads, registry, school management."""

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return request.user and request.user.is_authenticated
        return (
            request.user
            and request.user.is_authenticated
            and request.user.role
            in (SYSADMIN, TG_PS) + DEPARTMENT_HEADS + SCHOOL_MANAGEMENT + ("REG_OFF",)
        )


class CanApproveOutgoingMail(permissions.BasePermission):
    """Only SYSADMIN, TG_PS, or REG can approve/reject outgoing mail."""

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.role in (SYSADMIN, TG_PS, "REG", "PRI")
        )
