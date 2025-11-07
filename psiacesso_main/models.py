from django.db import models
from contas.models import Paciente, Psicologo

# ========================================
# Formação psicologo
# ========================================
class Formacao(models.Model):
    TipoFormacao = (
        (0, 'ACADEMICA'),
        (1, 'CURSO'),
    )
    psicologo = models.ForeignKey(Psicologo, on_delete=models.CASCADE)
    nome = models.CharField(max_length=100)
    descricao = models.CharField(max_length=100, blank=True, null=True)
    tipo = models.IntegerField(choices=TipoFormacao)
    

# ========================================
# Agenda e Disponibilidade
# ========================================
class DisponibilidadePsicologo(models.Model):
    DIAS_CHOICES = (
        (0, 'Domingo'),
        (1, 'Segunda'),
        (2, 'Terça'),
        (3, 'Quarta'),
        (4, 'Quinta'),
        (5, 'Sexta'),
        (6, 'Sábado'),
    )
    psicologo = models.ForeignKey(Psicologo, on_delete=models.CASCADE)
    dia_semana = models.IntegerField(choices=DIAS_CHOICES)
    hora_inicio = models.TimeField()

    def __str__(self):
        return f"{self.psicologo} - {self.get_dia_semana_display()} {self.hora_inicio}-{self.hora_fim}"


class AgendaPsicologo(models.Model):
    STATUS_CHOICES = (
        ('livre', 'Livre'),
        ('reservado', 'Reservado'),
        ('concluido', 'Concluído'),
        ('cancelado', 'Cancelado'),
        ('bloqueado', 'Bloqueado'),
    )
    psicologo = models.ForeignKey(Psicologo, on_delete=models.CASCADE)
    data_horario = models.DateTimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='livre')

    def __str__(self):
        return f"{self.psicologo} - {self.data_horario} ({self.status})"


# ========================================
# Consultas
# ========================================
class Consulta(models.Model):
    STATUS_CHOICES = (
        ('confirmado', 'Confirmado'),
        ('cancelado', 'Cancelado'),
        ('concluido', 'Concluído'),
    )
    MODALIDADE_CHOICES = (
        ('online', 'Online'),
        ('presencial', 'Presencial'),
    )

    paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE)
    psicologo = models.ForeignKey(Psicologo, on_delete=models.CASCADE)
    modalidade = models.CharField(max_length=20, choices=MODALIDADE_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='confirmado')
    data_criacao = models.DateTimeField(auto_now_add=True)
    data_horario = models.DateTimeField()

    def __str__(self):
        return f"Consulta {self.id} - {self.paciente} com {self.psicologo}"


# ========================================
# Anotações privadas
# ========================================
class AnotacaoPsicologo(models.Model):
    psicologo = models.ForeignKey(Psicologo, on_delete=models.CASCADE)
    consulta = models.ForeignKey(Consulta, on_delete=models.CASCADE)
    texto = models.TextField()
    data_criacao = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Anotação {self.id} - {self.psicologo}"


# ========================================
# Avaliações
# ========================================
class Avaliacao(models.Model):
    paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE)
    psicologo = models.ForeignKey(Psicologo, on_delete=models.CASCADE)
    nota = models.PositiveIntegerField()
    comentario = models.TextField(blank=True, null=True)
    data = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('paciente', 'psicologo')  # cada paciente avalia uma vez

    def __str__(self):
        return f"Avaliação {self.nota} de {self.paciente} para {self.psicologo}"
