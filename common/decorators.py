from django.shortcuts import redirect
from django.contrib import messages
from functools import wraps
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied


def role_required(*roles, login_url='/auth/login/', raise_exception=False):
    if isinstance(roles, str):
        roles = [roles]
    
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            # ✅ AMBIL DARI REQUEST (dari ProfileMiddleware)
            profile = getattr(request, 'profile_active', None)
            
            if not profile:
                if raise_exception:
                    raise PermissionDenied("Anda tidak memiliki profile aktif.")
                return redirect(login_url or '/profile/activate/')
            
            # ✅ Check role dari profile
            user_role = profile.role
            if not user_role:
                if raise_exception:
                    raise PermissionDenied("Profile tidak memiliki role.")
                return redirect(login_url or '/login/')
            
            # Check apakah role diizinkan
            role_match = user_role.name in roles
            
            if not role_match:
                if raise_exception:
                    raise PermissionDenied(f"Role '{user_role.name}' tidak diizinkan.")
                return redirect(login_url or '/login/')
            
            # Lanjutkan ke view
            return view_func(request, *args, **kwargs)
        
        return wrapper
    return decorator


def unauthorized(redirect_url='dashboard'):
    """Redirect authenticated user away from view (untuk login page, dll)"""
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if request.user.is_authenticated:
                return redirect(redirect_url)
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator
