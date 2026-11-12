"""
Admin Views

Handles admin/settings related views:
- Active data year selection
"""
import logging

from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages

logger = logging.getLogger(__name__)


# ========== ACTIVE DATA YEAR ==========

@login_required
def set_active_data_year(request, year_id):
    """Set active data year di session."""
    from django.urls import reverse

    request.session['active_data_year_id'] = year_id

    messages.success(request, 'Tahun data aktif berhasil diperbarui.')

    return redirect(request.META.get('HTTP_REFERER', reverse('spatial:layer_management')))
