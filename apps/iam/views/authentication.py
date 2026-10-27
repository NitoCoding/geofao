from django.conf import settings
from django.contrib.auth import login, logout
from django.shortcuts import render, redirect
from django_htmx.http import HttpResponseClientRedirect

from apps.iam.forms import LoginForm


def login_view(request):
    next_url = request.GET.get('next') or request.POST.get('next')

    if request.user.is_authenticated:
        redirect_to = next_url or settings.LOGIN_REDIRECT_URL
        if request.htmx:
            return HttpResponseClientRedirect(redirect_to)
        return redirect(redirect_to)

    if request.method == 'POST':
        form = LoginForm(data=request.POST, request=request)

        if form.is_valid():
            user = form.get_user()
            login(request, user)
            redirect_to = next_url or settings.LOGIN_REDIRECT_URL
            if request.htmx:
                return HttpResponseClientRedirect(redirect_to)
            return redirect(redirect_to)
    else:
        form = LoginForm()

    context = {
        'form': form,
        'next': next_url or '',
        'title': 'Masuk',
    }

    # HTMX request → partial form saja
    if request.htmx:
        return render(request, 'iam/authentication/partials/login_form.html', context)

    return render(request, 'iam/authentication/login.html', context)


def logout_view(request):
    logout(request)
    return redirect(settings.LOGOUT_REDIRECT_URL)