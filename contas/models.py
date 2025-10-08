from django.db import models
from django.contrib.auth.models import AbstractUser

# ========================================
# Usuário customizado
# ========================================
class Usuario(AbstractUser):
    class Role(models.TextChoices):
        PSICOLOGO = 'PSICOLOGO', 'Psicólogo'
        USUARIO = 'USUARIO', 'Usuário'
    
    class Gender(models.TextChoices):
        MASCULINO = 'MASCULINO', 'Masculino'
        FEMININO = 'FEMININO', 'Feminino',
        NAO_INFORMAR = 'NAO_INFORMAR', 'Não informar',
        OUTRO = 'OUTRO', 'Outro'
        
    
    #Campo base_role para definir a role Padrão
    role = models.CharField(max_length=50, choices=Role.choices, default=Role.USUARIO)
    email = models.EmailField(unique=True)
    cpf = models.CharField(max_length=50)
    gender = models.CharField(max_length=50, choices=Gender.choices)
    
    # Removendo o 'email' dos campos obrigatórios, pois ele já é o USERNAME_FIELD
    # O username ainda é necessário para o Django, mas não será pedido ao criar um superuser
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []


# ========================================
# Perfis
# ========================================
class Paciente(models.Model):
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE)
    data_nascimento = models.DateField()

    def __str__(self):
        return self.usuario.nome


class Psicologo(models.Model):
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE)
    crp = models.CharField(max_length=50, unique=True)  # Registro profissional
    preco_consulta = models.DecimalField(max_digits=8, decimal_places=2)
    duracao_minutos = models.PositiveIntegerField(default=50)

    def __str__(self):
        return f"{self.usuario.nome} - CRP {self.crp}"

class Endereco(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name="enderecos")
    cidade = models.CharField(max_length=100) 
    rua = models.CharField(max_length=100)     
    estado = models.CharField(max_length=100)
    bairro = models.CharField(max_length=100, blank=True, null=True)
    cep = models.CharField(max_length=50, blank=True, null=True)    
    numero = models.CharField(max_length=20,  blank=True, null=True)
    complemento = models.CharField(max_length=100)

