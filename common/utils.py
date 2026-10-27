from modules.users.models import UserProfile
import logging
logger = logging.getLogger(__name__)


def get_current_profile(request):
    """Helper untuk ambil profile aktif dari request"""
    return getattr(request, 'profile_active', None)

def get_current_role(request):
    """Helper untuk ambil role aktif"""
    profile = get_current_profile(request)
    return profile.role if profile else None

def switch_profile(request, profile_id):
    """Helper untuk switch profile programmatically"""
    try:
        profile = UserProfile.objects.get(
            id=profile_id,
            user=request.user,
            is_active=True
        )
        
        if not profile.is_current:
            return False, "Profile tidak aktif (expired)"
        
        # Set session
        request.session['active_profile_id'] = profile.id
        request.session.pop('last_logged_profile_id', None)  # Force re-log
        
        return True, f"Switched to {profile.role.name}"
        
    except UserProfile.DoesNotExist:
        return False, "Profile tidak ditemukan"