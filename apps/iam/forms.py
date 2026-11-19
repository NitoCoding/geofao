from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate

from django.contrib.auth.models import Permission

from apps.iam.models import User, Profile, Role, UserRole, Menu, MenuRole


class LoginForm(AuthenticationForm):
    username = forms.CharField(
        label="Username / Email",
        widget=forms.TextInput(attrs={
            'class': 'input input-bordered w-full',
            'placeholder': 'Masukkan username atau email',
            'autofocus': True,
        })
    )
    password = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(attrs={
            'class': 'input input-bordered w-full',
            'placeholder': 'Masukkan password',
        })
    )

    def clean(self):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')

        if username and password:
            # Coba authenticate dengan username dulu, lalu email
            self.user_cache = authenticate(
                self.request,
                username=username,
                password=password,
            )
            if self.user_cache is None:
                # Coba cari by email
                from django.contrib.auth import get_user_model
                User = get_user_model()
                try:
                    user_obj = User.objects.get(email=username)
                    self.user_cache = authenticate(
                        self.request,
                        username=user_obj.username,
                        password=password,
                    )
                except User.DoesNotExist:
                    pass

            if self.user_cache is None:
                raise forms.ValidationError(
                    "Username/email atau password salah.",
                    code='invalid_login',
                )
            else:
                self.confirm_login_allowed(self.user_cache)

        return self.cleaned_data


class UserForm(forms.ModelForm):
    password = forms.CharField(
        label="Password",
        required=False,
        widget=forms.PasswordInput(attrs={
            'class': 'input input-bordered w-full',
            'placeholder': 'Kosongkan jika tidak ingin mengubah',
        })
    )
    role = forms.ModelChoiceField(
        label="Role IAM",
        queryset=Role.objects.filter(is_active=True),
        required=False,
        widget=forms.Select(attrs={
            'class': 'select select-bordered w-full',
        }),
        help_text="Pilih satu role untuk user ini."
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'is_active', 'role']
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'input input-bordered w-full',
                'placeholder': 'Masukkan username',
            }),
            'email': forms.EmailInput(attrs={
                'class': 'input input-bordered w-full',
                'placeholder': 'Masukkan email',
            }),
            'first_name': forms.TextInput(attrs={
                'class': 'input input-bordered w-full',
                'placeholder': 'Masukkan nama depan',
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'input input-bordered w-full',
                'placeholder': 'Masukkan nama belakang',
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'checkbox checkbox-primary',
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            first_role = self.instance.roles.filter(is_active=True).first()
            if first_role:
                self.fields['role'].initial = first_role

    def save(self, commit=True):
        user = super().save(commit=False)
        password = self.cleaned_data.get('password')
        if password:
            user.set_password(password)
        if commit:
            user.save()
            # Simpan role assignments
            self._save_roles(user)
        return user

    def _save_roles(self, user):
        """Simpan role assignment via UserRole (single role)."""
        selected_role = self.cleaned_data.get('role')
        # Hapus semua existing UserRole
        UserRole.objects.filter(user=user).delete()
        # Tambahkan UserRole baru jika role dipilih
        if selected_role:
            UserRole.objects.get_or_create(
                user=user,
                role=selected_role,
                defaults={'is_active': True}
            )


class ProfileForm(forms.ModelForm):
    """Form untuk edit profil user sendiri (User + Profile)."""
    first_name = forms.CharField(
        label="Nama Depan",
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'input input-bordered w-full',
            'placeholder': 'Nama depan',
        })
    )
    last_name = forms.CharField(
        label="Nama Belakang",
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'input input-bordered w-full',
            'placeholder': 'Nama belakang',
        })
    )
    email = forms.EmailField(
        label="Email",
        widget=forms.EmailInput(attrs={
            'class': 'input input-bordered w-full',
            'placeholder': 'Masukkan email',
        })
    )
    password = forms.CharField(
        label="Password Baru",
        required=False,
        widget=forms.PasswordInput(attrs={
            'class': 'input input-bordered w-full',
            'placeholder': 'Kosongkan jika tidak ingin mengubah',
        })
    )
    password_confirm = forms.CharField(
        label="Konfirmasi Password",
        required=False,
        widget=forms.PasswordInput(attrs={
            'class': 'input input-bordered w-full',
            'placeholder': 'Ulangi password baru',
        })
    )

    class Meta:
        model = Profile
        fields = []

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if self.user:
            self.fields['first_name'].initial = self.user.first_name
            self.fields['last_name'].initial = self.user.last_name
            self.fields['email'].initial = self.user.email

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.exclude(pk=self.user.pk).filter(email=email).exists():
            raise forms.ValidationError("Email sudah digunakan oleh user lain.")
        return email

    def clean(self):
        cleaned = super().clean()
        password = cleaned.get('password')
        password_confirm = cleaned.get('password_confirm')

        if password and password != password_confirm:
            self.add_error('password_confirm', 'Password tidak cocok.')
        return cleaned

    def save(self, commit=True):
        profile = super().save(commit=False)

        # Update User fields
        if self.user:
            self.user.first_name = self.cleaned_data.get('first_name', '')
            self.user.last_name = self.cleaned_data.get('last_name', '')
            self.user.email = self.cleaned_data.get('email', '')
            password = self.cleaned_data.get('password')
            if password:
                self.user.set_password(password)
            self.user.save()

        if commit:
            profile.save()
        return profile


INPUT_CLASS = 'input input-bordered w-full'
SELECT_CLASS = 'select select-bordered w-full'


class MenuForm(forms.ModelForm):
    class Meta:
        model = Menu
        fields = ['name', 'code', 'icon', 'path', 'parent', 'menu_type', 'order', 'required_permissions', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': INPUT_CLASS, 'placeholder': 'Misal: Master Data'}),
            'code': forms.TextInput(attrs={'class': INPUT_CLASS, 'placeholder': 'Misal: master_data'}),
            'icon': forms.TextInput(attrs={'class': INPUT_CLASS, 'placeholder': 'Misal: bi-database'}),
            'path': forms.TextInput(attrs={'class': INPUT_CLASS, 'placeholder': 'Misal: /master-data/'}),
            'parent': forms.Select(attrs={'class': SELECT_CLASS}),
            'menu_type': forms.Select(attrs={'class': SELECT_CLASS}),
            'order': forms.NumberInput(attrs={'class': INPUT_CLASS}),
            'required_permissions': forms.SelectMultiple(attrs={'class': 'select select-bordered w-full h-32 text-xs'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'checkbox checkbox-primary'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['code'].required = True
        self.fields['parent'].required = False
        self.fields['parent'].empty_label = '— Tanpa induk —'
        self.fields['parent'].queryset = Menu.objects.exclude(pk=self.instance.pk).order_by('name')
        self.fields['required_permissions'].queryset = (
            Permission.objects.select_related('content_type').order_by('content_type__app_label', 'codename')
        )
        self.fields['required_permissions'].label_from_instance = (
            lambda p: f"{p.content_type.app_label}.{p.codename}"
        )


class MenuRoleForm(forms.ModelForm):
    class Meta:
        model = MenuRole
        fields = ['menu', 'role']
        widgets = {
            'menu': forms.Select(attrs={'class': SELECT_CLASS}),
            'role': forms.Select(attrs={'class': SELECT_CLASS}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['menu'].queryset = Menu.objects.order_by('name')
        self.fields['role'].queryset = Role.objects.filter(is_active=True).order_by('name')


class RolePermissionForm(forms.ModelForm):
    """Form untuk pasangan Role-Permission (tabel through dari Role.permissions)."""

    class Meta:
        model = Role.permissions.through
        fields = ['role', 'permission']
        widgets = {
            'role': forms.Select(attrs={'class': SELECT_CLASS}),
            'permission': forms.Select(attrs={'class': SELECT_CLASS}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['role'].queryset = Role.objects.filter(is_active=True).order_by('name')
        self.fields['permission'].queryset = (
            Permission.objects.select_related('content_type').order_by('content_type__app_label', 'codename')
        )
        self.fields['permission'].label_from_instance = (
            lambda p: f"{p.content_type.app_label}.{p.codename} — {p.name}"
        )