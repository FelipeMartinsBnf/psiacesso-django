from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.


# ========================================
# Usuário customizado
# ========================================
class Usuario(AbstractUser):
    ROLE_CHOICES = (
        ('cliente', 'Cliente'),
        ('psicologo', 'Psicólogo'),
        ('admin', 'Administrador'),
    )
    nome = models.CharField(max_length=255)
    telefone = models.CharField(max_length=20, blank=True, null=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)

    def __str__(self):
        return f"{self.nome} ({self.role})"


# ========================================
# Perfis
# ========================================
class Endereco(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name="enderecos")
    cidade = models.CharField(max_lenght=100)
    rua = models.CharField(max_lenght=100)
    estado = numero = models.CharField(max_lenght=100)
    cep = models.CharField(max_lenght=100, blank=True, null=True)
    bairro = models.CharField(max_lenght=100, blank=True, null=True)
    numero = models.CharField(max_lenght=20,  blank=True, null=True)
    
class Cliente(models.Model):
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE)
    

    def __str__(self):
        return self.usuario.nome


class Psicologo(models.Model):
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE)
    crp = models.CharField(max_length=50, unique=True)  # Registro profissional
    formacao = models.TextField()
    preco_consulta = models.DecimalField(max_digits=8, decimal_places=2)
    duracao_minutos = models.PositiveIntegerField(default=50)

    def __str__(self):
        return f"{self.usuario.nome} - CRP {self.crp}"


# ========================================
# Especialidades
# ========================================
class Especialidade(models.Model):
    nome = models.CharField(max_length=100, unique=True)
    descricao = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.nome


class PsicologoEspecialidade(models.Model):
    psicologo = models.ForeignKey(Psicologo, on_delete=models.CASCADE)
    especialidade = models.ForeignKey(Especialidade, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('psicologo', 'especialidade')

    def __str__(self):
        return f"{self.psicologo} - {self.especialidade}"

# ========================================
# Formação psicologo
# ========================================
class Formacao(models.Model):
    TipoFormacao = (
        (0, 'ACADEMICA'),
        (1, 'CURSO'),
    )
    psicologo = models.ForeignKey(Psicologo, on_delete=models.CASCADE)
    nome = models.CharField(max_lenght=100)
    descricao = models.CharField(max_lenght=100, blank=True, null=True)
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
    hora_fim = models.TimeField()
    intervalo_minutos = models.PositiveIntegerField(default=50)

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

    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    psicologo = models.ForeignKey(Psicologo, on_delete=models.CASCADE)
    agenda = models.OneToOneField(AgendaPsicologo, on_delete=models.CASCADE)
    modalidade = models.CharField(max_length=20, choices=MODALIDADE_CHOICES)
    especialidade = models.ForeignKey(Especialidade, on_delete=models.SET_NULL, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='confirmado')
    data_criacao = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Consulta {self.id} - {self.cliente} com {self.psicologo}"


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
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    psicologo = models.ForeignKey(Psicologo, on_delete=models.CASCADE)
    nota = models.PositiveIntegerField()
    comentario = models.TextField(blank=True, null=True)
    data = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('cliente', 'psicologo')  # cada cliente avalia uma vez

    def __str__(self):
        return f"Avaliação {self.nota} de {self.cliente} para {self.psicologo}"
