# contas/forms.py

from multiprocessing import AuthenticationError
from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm

from psiacesso_main.models import Formacao
from .models import Paciente, Psicologo, Usuario, Endereco 
from django.forms import inlineformset_factory

class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = Usuario
        fields = ('first_name', 'last_name', 'email', 'cpf', 'gender')
        labels = {
                'first_name': 'Seu Nome',
                'last_name': 'Sobrenome',
                'email': 'E-mail',
                'CPF': 'CPF',
                'gender': 'Gênero'
            }
        
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
            'rua': 'Rua',
            'estado': 'Estado',
            'bairro': 'Bairro',
            'cep': 'CEP',
            'numero': 'Numero',
            'complemento': 'Complemento'
        }
        
        estado = forms.ChoiceField(
             widget=forms.Select(choices=[('MG', 'MG'), ('SP', 'SP')])
        )
        
        
        
    