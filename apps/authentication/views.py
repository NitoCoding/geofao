from django.contrib import messages

from django.shortcuts import redirect, render
from django.urls import reverse
from django.contrib.auth import login
from django_htmx.http import HttpResponseClientRedirect
from modules.authentication.forms import LoginForm
from modules.users.models import User


def login_view(request):
    # Ambil next url dari GET atau POST
    next_url = request.GET.get('next') or request.POST.get('next')

    # Jika user sudah login, langsung redirect ke next_url atau dashboard
    if request.user.is_authenticated:
        redirect_to = next_url or reverse('dashboard')
        if request.htmx:
            return HttpResponseClientRedirect(redirect_to)
        return redirect(redirect_to)

    if request.method == 'POST':
        form = LoginForm(data=request.POST)

        if form.is_valid():
            user = form.get_user()
            login(request, user)

            # Tentukan tujuan redirect
            redirect_to = next_url or reverse('dashboard')

            # Redirect yang kompatibel dengan HTMX
            if request.htmx:
                return HttpResponseClientRedirect(redirect_to)

            # Redirect biasa (full page)
            return redirect(redirect_to)

        # === FORM ERROR ===
        # Render partial form + error message (untuk HTMX)
        if request.htmx:
            return render(request, 'partials/login_form.html', {
                'form': form,
                'next': next_url,          # kirim next supaya tetap ada di form
            })

    else:
        form = LoginForm()

    # GET request → tampilkan full login page
    return render(request, 'auth/login.html', {
        'form': form,
        'next': next_url,
    })

def logout_view(request):
    from django.contrib.auth import logout
    logout(request)
    return redirect('/login/')

def register_page(request):
    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        # Check if a user with the provided username already exists
        user = User.objects.filter(username=username)
        
        if user.exists():
            # Display an information message if the username is taken
            messages.info(request, "Username already taken!")
            return redirect('/register/')
        
        # Create a new User object with the provided information
        user = User.objects.create_user(
            first_name=first_name,
            last_name=last_name,
            username=username
        )
        
        # Set the user's password and save the user object
        user.set_password(password)
        user.save()
        
        # Display an information message indicating successful account creation
        messages.info(request, "Account created Successfully!")
        return redirect('/register/')
    
    return render(request, 'register.html')