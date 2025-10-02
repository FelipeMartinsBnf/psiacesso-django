# contas/forms.py

from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Usuario # Importe seu modelo de usuário customizado

class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = Usuario
        fields = ('first_name', 'last_name', 'email', 'password', 'role')