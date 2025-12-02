# models.py (em contas ou na sua app de usuário)

from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.utils.translation import gettext_lazy as _

# ========================================
# Usuário customizado
# ========================================

class CustomUserManager(BaseUserManager):
    """
    Manager customizado para o modelo de usuário onde o e-mail é o identificador
    único para autenticação em vez de usernames.
    """
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError(_('O E-mail deve ser fornecido'))
        email = self.normalize_email(email)
        extra_fields.setdefault('username', email)  # garante compatibilidade
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password, **extra_fields):
        """
        Cria e salva um superusuário com o e-mail e a senha fornecidos.
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser must have is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser must have is_superuser=True.'))
        
        return self.create_user(email, password, **extra_fields)

class Usuario(AbstractUser):
    class Role(models.TextChoices):
        PSICOLOGO = 'PSICOLOGO', 'Psicólogo'
        USUARIO = 'USUARIO', 'Usuário'
    
    class Gender(models.TextChoices):
        MASCULINO = 'MASCULINO', 'Masculino'
        FEMININO = 'FEMININO', 'Feminino'  # remova a vírgula
        NAO_INFORMAR = 'NAO_INFORMAR', 'Não informar'  # remova a vírgula
        OUTRO = 'OUTRO', 'Outro'
        
    #Username, sem uso - somente para o superuser
    username = models.CharField(max_length=150, unique=True, blank=True)
    role = models.CharField(max_length=50, choices=Role.choices, default=Role.USUARIO)
    email = models.EmailField(unique=True)
    cpf = models.CharField(max_length=50, unique=True)
    gender = models.CharField(max_length=50, choices=Gender.choices)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    ### CORREÇÃO 2: Conectando o manager ao modelo ###
    objects = CustomUserManager()

    def __str__(self):
        return self.email


# ========================================
# Perfis
# ========================================
# Supondo que estes modelos estão no mesmo arquivo, senão ajuste os imports
class Paciente(models.Model):
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE)
    data_nascimento = models.DateField()
    ativo = models.BooleanField(default=True)

    def __str__(self):
        ### CORREÇÃO 3: Usando get_full_name() ou email ###
        return self.usuario.get_full_name() or self.usuario.email


# ========================================
# Especialidades
# ========================================
class Especialidade(models.Model):
    nome = models.CharField(max_length=100, unique=True)
    descricao = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.nome


class Psicologo(models.Model):
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE)
    crp = models.CharField(max_length=50, unique=True)
    preco_consulta = models.DecimalField(max_digits=8, decimal_places=2)
    duracao_minutos = models.PositiveIntegerField(default=50)
    especialidade = models.ForeignKey(Especialidade, on_delete=models.SET_NULL, null=True, blank=True)
    atendimento_online = models.BooleanField(default=False) 
    atendimento_presencial = models.BooleanField(default=False)
    
    biografia = models.TextField(blank=True, null=True)
    telefone = models.CharField(max_length=20, blank=True, null=True)
    foto = models.ImageField(upload_to='psicologos_fotos/', blank=True, null=True)

    ativo = models.BooleanField(default=True)
    aprovado = models.BooleanField(default=False)

    def __str__(self):
        nome = self.usuario.get_full_name() or self.usuario.email
        return f"{nome} - CRP {self.crp}"
    
class Endereco(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name="enderecos")
    cidade = models.CharField(max_length=100) 
    rua = models.CharField(max_length=100)      
    estado = models.CharField(max_length=100)
    bairro = models.CharField(max_length=100, blank=True, null=True)
    cep = models.CharField(max_length=50, blank=True, null=True)     
    numero = models.CharField(max_length=20,  blank=True, null=True)
    complemento = models.CharField(max_length=100, blank=True, null=True)
    
