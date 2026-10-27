"""
Role-Based Authorization System

Fokus pada pengecekan role untuk mengontrol akses ke views.
Tidak menggunakan Django's permission system, hanya role-based.
"""

from django.core.exceptions import PermissionDenied
from django.http import HttpResponseForbidden
from functools import wraps

from apps.iam.models.role import UserRole


# =============================================================================
# ROLE CONSTANTS - Definisi role yang tersedia di sistem
# =============================================================================

class Role:
    """Constants untuk role codes"""
    ADMIN = 'admin'
    SUPERUSER = 'superuser'
    OPERATOR = 'operator'
    ASESOR = 'asesor'

    CAN_MANAGE_PROGRAM = [ADMIN, SUPERUSER, OPERATOR]
    CAN_MANAGE_USER = [ADMIN, SUPERUSER]
    CAN_ASSESSMENT = [ADMIN, SUPERUSER, OPERATOR, ASESOR]
    CAN_MANAGE_MASTER_DATA = [ADMIN, SUPERUSER, OPERATOR]


# =============================================================================
# CORE ROLE CHECKING FUNCTIONS
# =============================================================================

def get_user_roles(user):
    if not user or not user.is_authenticated:
        return set()

    from apps.iam.apps import IamConfig
    if IamConfig.rbac_enable_multi_role:
        # Multi-role path: query ManyToMany seperti saat ini
        return set(user.roles.filter(is_active=True).values_list('code', flat=True))
    else:
        # Single-role path: query 1-to-1, lebih efisien
        user_role = UserRole.objects.filter(user=user).select_related('role').first()
        if user_role and user_role.role.is_active:
            return {user_role.role.code}
        return set()



def has_role(user, allowed_roles):
    """
    Cek apakah user memiliki salah satu role yang diizinkan.

    Args:
        user: User instance
        allowed_roles: string atau list/tuple of role codes

    Returns:
        bool: True jika user punya salah satu role

    Examples:
        has_role(request.user, 'admin')
        has_role(request.user, ['admin', 'operator'])
    """
    if not user or not user.is_authenticated:
        return False

    # Superuser selalu punya akses
    if user.is_superuser:
        return True

    # Normalisasi allowed_roles ke list
    if isinstance(allowed_roles, str):
        allowed_roles = [allowed_roles]

    user_roles = get_user_roles(user)
    return bool(user_roles & set(allowed_roles))


def require_role(user, allowed_roles, raise_exception=True):
    """
    Cek role dan raise exception jika tidak memenuhi.

    Args:
        user: User instance
        allowed_roles: string atau list of role codes
        raise_exception: jika True, raise PermissionDenied

    Returns:
        bool: True jika punya role

    Raises:
        PermissionDenied: jika tidak punya role dan raise_exception=True
    """
    if has_role(user, allowed_roles):
        return True

    if raise_exception:
        raise PermissionDenied("Anda tidak memiliki akses ke halaman ini")
    return False


# =============================================================================
# DECORATORS - Untuk views
# =============================================================================

def role_required(allowed_roles, allow_superuser=True):
    """
    Decorator untuk membatasi akses view berdasarkan role.

    Args:
        allowed_roles: string atau list/tuple of role codes
        allow_superuser: jika True, superuser bypass pengecekan

    Usage:
        @login_required
        @role_required('admin')
        def my_view(request):
            ...

        @login_required
        @role_required(['admin', 'operator'])
        def my_view(request):
            ...

    Note: Selalu gunakan @login_required SEBELUM @role_required
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            # Cek superuser bypass
            print(request.user.is_superuser)
            if allow_superuser and request.user.is_superuser:
                return view_func(request, *args, **kwargs)

            # Normalisasi ke list
            roles = [allowed_roles] if isinstance(allowed_roles, str) else allowed_roles

            # Cek role
            if not has_role(request.user, roles):
                print("check")
                raise PermissionDenied(
                    f"Anda memerlukan salah satu role berikut: {', '.join(roles)}"
                )

            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator


def admin_required(view_func):
    """
    Shortcut decorator untuk admin only.

    Usage:
        @login_required
        @admin_required
        def my_view(request):
            ...
    """
    return role_required(Role.ADMIN)(view_func)


def management_required(view_func):
    """
    Shortcut decorator untuk management (admin, operator).

    Usage:
        @login_required
        @management_required
        def my_view(request):
            ...
    """
    return role_required(Role.MANAGEMENT)(view_func)


def staff_required(view_func):
    """
    Shortcut decorator untuk semua staff (admin, operator, asesor, dosen).

    Usage:
        @login_required
        @staff_required
        def my_view(request):
            ...
    """
    return role_required(Role.ALL_STAFF)(view_func)



# =============================================================================
# TEMPLATE TAGS HELPERS - Untuk templates
# =============================================================================

def get_template_context(request):
    from apps.accounts.apps import AccountsConfig

    if not request.user.is_authenticated:
        return {
            'user_roles': [],
            'user_is_superuser': False,
            'user_is_admin': False,
            'user_is_operator': False,
            'user_is_asesor': False,
            'user_is_dosen': False,
            'user_is_management': False,
            'user_is_staff': False,
            'active_role': None,
            'has_multiple_roles': False,
            'available_roles': [],
        }

    roles = get_user_roles(request.user)

    # Get active role dari session
    active_role = get_active_role(request)

    return {
        'user_roles': list(roles),
        'user_is_superuser': Role.SUPERUSER in roles or request.user.is_superuser,
        'user_is_admin': Role.ADMIN in roles,
        'user_is_operator': Role.OPERATOR in roles,
        'user_is_asesor': Role.ASESOR in roles,
        'active_role': active_role,
        'has_multiple_roles': len(roles) > 1,
        'available_roles': list(roles),
        'rbac_enable_multi_role': AccountsConfig.rbac_enable_multi_role,
    }

SESSION_ACTIVE_ROLE_KEY = '_active_role_code'


def set_active_role(request, role_code):
    """
    Set role aktif untuk session ini.
    Returns True jika berhasil, False jika role tidak valid.
    """
    user_roles = get_user_roles(request.user)

    if role_code not in user_roles:
        return False

    request.session[SESSION_ACTIVE_ROLE_KEY] = role_code
    return True


def get_active_role(request):
    """
    Get role aktif untuk session ini.
    Returns role code atau None.
    """
    if not request.user.is_authenticated:
        return None

    active_role = request.session.get(SESSION_ACTIVE_ROLE_KEY)

    # Validasi: pastikan user masih punya role ini
    if active_role and active_role in get_user_roles(request.user):
        return active_role

    # Auto-set jika user hanya punya 1 role
    user_roles = get_user_roles(request.user)
    if len(user_roles) == 1:
        single_role = list(user_roles)[0]
        set_active_role(request, single_role)
        return single_role

    return None


def clear_active_role(request):
    """Clear role aktif dari session"""
    if SESSION_ACTIVE_ROLE_KEY in request.session:
        del request.session[SESSION_ACTIVE_ROLE_KEY]


def get_available_roles_detail(request):
    """
    Get semua role detail yang tersedia untuk user (untuk switcher UI).
    Returns list of dict: [{'code': 'admin', 'name': 'Administrator'}, ...]
    """
    if not request.user.is_authenticated:
        return []

    from apps.accounts.models import Role

    user_role_codes = get_user_roles(request.user)
    roles = Role.objects.filter(
        code__in=user_role_codes,
        is_active=True
    ).values('code', 'name').order_by('name')

    return list(roles)


def has_multiple_roles(request):
    """Cek apakah user punya lebih dari 1 role"""
    if not request.user.is_authenticated:
        return False
    return len(get_user_roles(request.user)) > 1


# apps/core/decorators.py - secure_action implementation
import logging
from functools import wraps
from typing import Optional, Union, List, Callable

from django.core.exceptions import PermissionDenied
from django.db.models import Model
from django.http import HttpRequest
from django.shortcuts import get_object_or_404
# from icecream import ic
logger = logging.getLogger(__name__)


def secure_action(
    # Role checks
    role: Optional[Union[str, List[str]]] = None,
    # Django permission checks
    perm: Optional[Union[str, List[str]]] = None,
    # Object-level checks
    model_class: Optional[type[Model]] = None,
    pk_param: str = 'pk',  # Konfigurabel: 'pk', 'slug', 'uuid', dll
    ownership_check: Optional[Callable] = None,
    # Options
    allow_superuser: bool = True,
    audit_log: bool = True,
    # Custom error messages
    role_message: Optional[str] = None,
    perm_message: Optional[str] = None,
    ownership_message: Optional[str] = None,
):
    """
    Decorator terpusat untuk authorization dengan RBAC sistem yang ada.

    Usage:
        # Role only
        @secure_action(role='asesor')

        # Multiple roles (OR logic)
        @secure_action(role=['admin', 'operator'])

        # Permission only
        @secure_action(perm='program.change_program')

        # Role + Permission
        @secure_action(role='asesor', perm='program.add_judgement')

        # With object-level ownership
        @secure_action(
            role='asesor',
            model_class=ProgramJudgement,
            ownership_check=lambda user, obj: obj.asesor == user
        )

        # Custom PK parameter
        @secure_action(
            role='asesor',
            model_class=Program,
            pk_param='program_id'  # Untuk URL /program/<program_id>/action/
        )
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request: HttpRequest, *args, **kwargs):
            user = request.user

            # 1. Superuser bypass (jika diizinkan)
            if allow_superuser and user.is_superuser:
                return view_func(request, *args, **kwargs)

            # 2. Role Check (menggunakan sistem Role yang sudah ada)
            if role:
                _check_role(user, role, role_message)

            # 3. Permission Check (Django permissions)
            if perm:
                _check_permission(user, perm, perm_message)

            # 4. Object-Level Check
            obj = None
            if model_class:
                obj = _get_and_check_object(
                    request, user, model_class, pk_param, kwargs,
                    ownership_check, ownership_message
                )
                # Attach ke request untuk reuse di view
                request.resource_obj = obj

            # 5. Audit Log
            if audit_log:
                _log_access(request, view_func.__name__, obj)

            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator


def _check_role(user, allowed_roles: Union[str, List[str]], custom_message: Optional[str]):
    """Cek role menggunakan sistem Role yang sudah ada."""
    # Gunakan has_role yang sudah didefinisikan di atas
    if isinstance(allowed_roles, str):
        allowed_roles = [allowed_roles]

    if not has_role(user, allowed_roles):
        message = custom_message or (
            f"Anda memerlukan salah satu role: {', '.join(allowed_roles)}"
        )
        logger.warning(f"Role check failed for user {user}: needs {allowed_roles}")
        raise PermissionDenied(message)


def _check_permission(user, required_perms: Union[str, List[str]], custom_message: Optional[str]):
    """Cek Django permissions."""
    if isinstance(required_perms, str):
        required_perms = [required_perms]

    missing_perms = [p for p in required_perms if not user.has_perm(p)]

    if missing_perms:
        message = custom_message or (
            f"Izin tidak mencukupi. Dibutuhkan: {', '.join(missing_perms)}"
        )
        logger.warning(f"Permission check failed for user {user}: needs {missing_perms}")
        raise PermissionDenied(message)


def _get_and_check_object(
    request, user, model_class, pk_param, kwargs,
    ownership_check, custom_message
):
    """Ambil objek dan cek ownership jika diperlukan."""
    pk = kwargs.get(pk_param)

    if not pk:
        raise PermissionDenied(f"Parameter '{pk_param}' tidak ditemukan di URL")

    # Gunakan select_related untuk optimasi jika model punya FK ke User
    queryset = model_class.objects.all()
    if hasattr(model_class, 'created_by'):
        queryset = queryset.select_related('created_by')

    obj = get_object_or_404(queryset, pk=pk)

    # Ownership check
    if ownership_check and not ownership_check(user, obj):
        message = custom_message or "Anda tidak memiliki akses ke objek ini"
        logger.warning(
            f"Ownership check failed for user {user} on {model_class.__name__}({pk})"
        )
        raise PermissionDenied(message)

    return obj


def _log_access(request, view_name, obj):
    """Audit logging untuk tracking akses."""
    obj_info = f" on {obj.__class__.__name__}({obj.pk})" if obj else ""
    logger.info(f"User {request.user} accessed {view_name}{obj_info}")
