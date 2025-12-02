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
class PsicologoProfileForm(forms.ModelForm):
    
    class Meta:
        model = Psicologo

        fields = [
            'biografia', 
            'foto', 
            'telefone', 
            'preco_consulta', 
            'duracao_minutos', 
            'atendimento_online', 
            'atendimento_presencial'
        ]