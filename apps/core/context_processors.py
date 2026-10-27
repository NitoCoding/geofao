from apps.master_data.models import DataYear


def user_context(request):
    """
    Context processor untuk active data year.
    Menambahkan data user context ke semua templates.
    """
    context = {}

    if request.user.is_authenticated:
        # Active Data Year (dari session)
        year_id = request.session.get('active_data_year_id')
        if year_id:
            try:
                context['active_data_year'] = DataYear.objects.get(id=year_id)
            except DataYear.DoesNotExist:
                context['active_data_year'] = None
        else:
            context['active_data_year'] = None
        context['available_data_years'] = DataYear.objects.filter(is_active=True).order_by('-year')

    return context
