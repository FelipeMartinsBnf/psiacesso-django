# perfis/forms.py
from psiacesso_main.models import Consulta
from django import forms

# ...

class ConsultaForm(forms.ModelForm):
    class Meta:
        model = Consulta
        fields = ['modalidade'] # O paciente só escolhe a modalidade
        labels = {
            'modalidade': 'Modalidade da Consulta'
        }