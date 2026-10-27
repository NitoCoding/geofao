
import json
import logging
from django.shortcuts import redirect
from django.urls import reverse
from django.utils import timezone
from django.db.models import Q

from modules.users.models import UserProfile
from modules.master_data.models import DataYear

logger = logging.getLogger(__name__)
logging.disable(logging.CRITICAL)  # Aktifkan logging untuk middleware ini

class ProfileMiddleware:
    """
    Middleware untuk attach active profile ke request.
    Prioritas: Session > Latest Login History > First Available
    """
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        logger.debug("ProfileMiddleware dipanggil untuk request: %s %s", request.method, request.path)
        if request.user.is_authenticated:
            active_profile = self._get_active_profile(request)
            request.profile_active = active_profile  # Attach ke request, bukan user
            
            # Simpan ke session jika belum ada
            if active_profile and not request.session.get('active_profile_id'):
                request.session['active_profile_id'] = active_profile.id
        
        else:
            request.profile_active = None
        
        response = self.get_response(request)
        return response
    
    def _get_active_profile(self, request):
        """Get active profile dengan fallback logic"""
        now = timezone.now().date()
        user = request.user

        logger.debug(f"Mencari active profile untuk user: {user.username}")
        
        # PRIORITAS 1: Dari session
        session_profile_id = request.session.get('active_profile_id')
        logger.debug(f"Mencari active profile dari session: {session_profile_id}")
        if session_profile_id:
            try:
                profile = UserProfile.objects.select_related('role').get(
                    id=session_profile_id,
                    user=user,
                    is_active=True,
                    mulai__lte=now,
                )
                # Now check the selesai condition manually
                if profile.selesai and profile.selesai < now:
                    profile = None
                # print("Profile dari session sudah expired:", profile.id if profile else None)
                
                if profile:
                    request.session['active_profile_id'] = profile.id
                    logger.debug(f"Menemukan active profile dari session: {profile.id}")
                    return profile
            except UserProfile.DoesNotExist:
                profile = None  # Continue to fallback
        
        # # PRIORITAS 2: Dari latest LoginHistory
        # try:
        #     latest_login = LoginHistory.objects.filter(user=user).select_related('profile', 'profile__role', 'profile__department').latest('login_time')
        #     logger.debug(f"Mencari active profile dari latest login: {latest_login.profile.id if latest_login.profile else None}")

        #     if latest_login.profile and latest_login.profile.is_current:
        #         # Update session
        #         request.session['active_profile_id'] = latest_login.profile.id
        #         return latest_login.profile
        # except LoginHistory.DoesNotExist:
        #     profile = None
        
        # PRIORITAS 3: First available active profile
        profile = UserProfile.objects.filter(
            user=user,
            is_active=True,
            mulai__lte=now
        ).filter(
            Q(selesai__isnull=True) | Q(selesai__gte=now)
        ).select_related('role').first()

        logger.debug(f"Mencari active profile dari first available: {profile.id if profile else None}")
        
        if profile:
            logger.debug(f"Menemukan active profile: {profile.id}")
            request.session['active_profile_id'] = profile.id
        
        return profile

class ActiveYearMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        exempt_urls = [reverse('login'), reverse('select_year'), reverse('logout')]

        if request.user.is_authenticated and request.path not in exempt_urls:
            active_year = request.session.get('active_year')
            
            if not active_year:
                try:
                    default_year = DataYear.objects.filter(is_default=True)
                    active_year = default_year.year
                    request.session['active_year'] = active_year
                except DataYear.DoesNotExist:
                    return redirect('select_year')
                except DataYear.MultipleObjectsReturned:
                    default_year = DataYear.objects.filter(is_default=True).order_by('year').first()
                    active_year = default_year.year
                    request.session['active_year'] = active_year

            request.active_year = active_year   # attach selalu kalau user login
            
        return self.get_response(request)