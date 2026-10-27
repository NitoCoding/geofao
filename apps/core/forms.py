# iam/forms.py
from django import forms
from django.contrib.auth import get_user_model

class UserRoleForm(forms.ModelForm):
    class Meta:
        model = get_user_model()
        fields = ["is_active", "is_superuser"]
        labels = {"is_active": "Aktif", "is_superuser": "Superuser"}