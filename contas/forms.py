# contas/forms.py

from multiprocessing import AuthenticationError
from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import Paciente, Psicologo, Usuario # Importe seu modelo de usuário customizado

class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = Usuario
        fields = ('first_name', 'last_name', 'email', 'role')
        
    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = self.cleaned_data['email']
        if commit:
            user.save()
        return user
        
class EmailLoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # 2. Agora, modifica os campos que foram criados pela classe pai
        self.fields['username'].label = 'E-mail'
        self.fields['username'].widget = forms.EmailInput(attrs={
            'autofocus': True,
            'class': 'form-control', # Adicionei uma classe CSS como exemplo
            'placeholder': 'seuemail@exemplo.com'
        })
        
class PsicologoProfileForm(forms.ModelForm):
    class Meta:
        model = Psicologo
        # Liste os campos do modelo Psicologo que devem aparecer no formulário
        fields = ['crp', 'preco_consulta', 'duracao_minutos']
        
        # rótulos (labels) dos campos
        labels = {
            'crp': 'Número do CRP',
            'preco_consulta': 'Preço da Consulta (R$)',
            'duracao_minutos': 'Duração da Sessão (em minutos)',
        }

class PacienteProfileForm(forms.ModelForm):
    class Meta:
        model = Paciente
        
        fields = ['data_nascimento']
        labels = {
            'data_nascimento': 'Data de Nascimento',
        }
        # Adiciona um widget para facilitar a seleção da data
        widgets = {
            'data_nascimento': forms.DateInput(attrs={'type': 'date'}),
        }