# forms.py
from django import forms

class LoginForm(forms.Form):
    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'input input-bordered join-item w-full',
            'placeholder': 'Masukkan username'
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'input input-bordered join-item w-full',
            'placeholder': 'Masukkan password'
        })
    )
    remember_me = forms.BooleanField(
        required=False,
        label="Ingat saya",
        widget=forms.CheckboxInput(attrs={'class': 'checkbox'})
    )