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

    # Ambil role aktif user
    user_role = user.roles.filter(is_active=True).first()

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
        'user_role': user_role,
        'title': 'Profil Saya',
    })