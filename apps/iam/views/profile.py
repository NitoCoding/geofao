from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages

from apps.iam.forms import ProfileForm
from apps.iam.models import Profile


@login_required
def profile_view(request):
    """Halaman profil user — lihat & edit data diri."""
    user = request.user
    profile, _ = Profile.objects.get_or_create(user=user)

    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=profile, user=user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profil berhasil diperbarui.')
            return redirect('iam:profile')
    else:
        form = ProfileForm(instance=profile, user=user)

    return render(request, 'iam/profile/detail.html', {
        'form': form,
        'profile': profile,
        'title': 'Profil Saya',
    })