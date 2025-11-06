# contas/forms.py

import json
from multiprocessing import AuthenticationError
from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from psiacesso_main.models import Formacao
from .models import Paciente, Psicologo, Usuario, Endereco 
from django.forms import inlineformset_factory

class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = Usuario
        
        # 1. ADICIONAMOS 'username' DE VOLTA
        # O UserCreationForm PRECISA disso para funcionar.
        fields = ('username', 'first_name', 'last_name', 'email', 'cpf', 'gender') 
        
        labels = {
            'first_name': 'Nome',
            'last_name': 'Sobrenome',
            'email': 'E-mail',
            'cpf': 'CPF', 
            'gender': 'Gênero'
        }
        widgets = {
            # 2. ESCONDEMOS O CAMPO 'username'
            'username': forms.HiddenInput(),
            
            'first_name': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Seu nome', 
                'required': 'required'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Seu sobrenome', 
                'required': 'required'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control', 
                'placeholder': 'seu@email.com', 
                'required': 'required'
            }),
            'cpf': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': '000.000.000-00', 
                'required': 'required'
            }),
            'gender': forms.Select(attrs={'class': 'form-select'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Agora self.fields['password'] vai existir!
        self.fields['password1'].widget = forms.PasswordInput(attrs={
            'class': 'form-control', 
            'placeholder': 'Mínimo 8 caracteres', 
            'required': 'required'
        })
        self.fields['password2'].widget = forms.PasswordInput(attrs={
            'class': 'form-control', 
            'placeholder': 'Repita a senha', 
            'required': 'required'
        })
        self.fields['password1'].label = "Senha"
        self.fields['password2'].label = "Confirmar Senha"
        
        # Dizemos ao campo username (agora oculto) para não ser obrigatório
        # já que o usuário não vai preenchê-lo.
        self.fields['username'].required = False


    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = self.cleaned_data.get('email')
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
        self.fields['password'].widget = forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Sua senha'
        })
        
class PsicologoProfileForm(forms.ModelForm):
    # O ModelChoiceField cria um <select> populado com todas as especialidades.
    # O ModelForm já faz isso automaticamente para ForeignKeys, então só precisamos adicionar ao fields.
    class Meta:
        model = Psicologo
        # 2. Adicione 'especialidade' aos fields
        fields = ['crp', 'preco_consulta', 'duracao_minutos', 'especialidade', 'atendimento_online', 'atendimento_presencial']
        labels = {
            'crp': 'Número do CRP',
            'preco_consulta': 'Preço da Consulta (R$)',
            'duracao_minutos': 'Duração da Sessão (em minutos)',
            'especialidade': 'Principal Área de Especialidade',
            'atendimento_online': 'Atendimento Online',
            'atendimento_presencial': 'Atendimento Presencial'
        }
        
        horarios_selecionados = forms.CharField(
            widget=forms.HiddenInput(),
            required=False # Mesmo que venha vazio, é válido (ele só limpou a agenda)
        )
        def clean_horarios_selecionados(self):
            # Transforma o JSON de volta em uma lista Python
            data = self.cleaned_data['horarios_selecionados']
            if not data:
                return []
            try:
                return json.loads(data)
            except json.JSONDecodeError:
                raise forms.ValidationError("Formato de dados inválido.")
        
FormacaoFormSet = inlineformset_factory(
    Psicologo,           
    Formacao,            
    fields=('nome', 'descricao', 'tipo'),
    extra=1,                
    can_delete=False      
)

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
        
class enderecoForm(forms.ModelForm):
    class Meta:
        model = Endereco
        fields = ['cidade', 'rua', 'estado', 'bairro', 'cep', 'numero', 'complemento']
        labels = {
            'cidade': 'Cidade',
            'rua': 'Rua (Logradouro)', # Ajustado
            'estado': 'Estado',
            'bairro': 'Bairro',
            'cep': 'CEP',
            'numero': 'Número', # Ajustado
            'complemento': 'Complemento'
        }
        widgets = {
            'cidade': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Cidade', 'required': 'required'}),
            'rua': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Rua, Avenida, etc.', 'required': 'required'}),
            'bairro': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nome do bairro', 'required': 'required'}),
            'cep': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '00000-000', 'required': 'required'}),
            'numero': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '123', 'required': 'required'}),
            'complemento': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Apt, Bloco, etc.'}),
        }
        
        
        
    