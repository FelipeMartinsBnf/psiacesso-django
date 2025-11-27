from django import forms
import json
from psiacesso_main.models import AnotacaoPsicologo
from contas.models import Psicologo

class AgendaGridForm(forms.Form):
    # Um campo de texto oculto que receberá o JSON do JavaScript
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
        
class AnotacaoForm(forms.ModelForm):
    class Meta:
        model = AnotacaoPsicologo
        fields = ['texto']

class AgendaGridForm(forms.Form):
    horarios_selecionados = forms.CharField(
        widget=forms.HiddenInput(),
        required=False 
    )

    def clean_horarios_selecionados(self):
        data = self.cleaned_data['horarios_selecionados']
        if not data:
            return []
        try:
            return json.loads(data)
        except json.JSONDecodeError:
            raise forms.ValidationError("Formato de dados inválido.")
        
class AnotacaoForm(forms.ModelForm):
    class Meta:
        model = AnotacaoPsicologo
        fields = ['texto']

# --- ADICIONE ISSO AQUI EMBAIXO ---
class PsicologoProfileForm(forms.ModelForm):
    class Meta:
        model = Psicologo
        # Aqui definimos quais campos o psicólogo pode editar
        fields = ['crp', 'telefone', 'cpf', 'endereco', 'preco_consulta', 'biografia', 'foto', 'atendimento_online', 'atendimento_presencial']
        
        widgets = {
            'endereco': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Ex: Rua das Flores, 123'}),
            'telefone': forms.TextInput(attrs={'class': 'form-input', 'placeholder': '(00) 00000-0000'}),
            'preco_consulta': forms.NumberInput(attrs={'class': 'form-input', 'step': '0.01'}),
            'biografia': forms.Textarea(attrs={'class': 'form-input', 'rows': 3}),
        }