from django.db import models
from django.contrib.auth.models import AbstractUser

# ========================================
# Usuário customizado
# ========================================
class Usuario(AbstractUser):
    class Role(models.TextChoices):
        PSICOLOGO = 'PSICOLOGO', 'Psicólogo'
        USUARIO = 'USUARIO', 'Usuário'
    
    #Campo base_role para definir a role Padrão
    base_role = Role.USUARIO
    
    role = models.CharField(max_length=50, choices=Role.choices, default=base_role)
    
    def save(self, *args, **kwargs):
        # Se o usuário está sendo criado e não tem uma role definida,
        # usamos a base_role. Útil para o createsuperuser.
        if not self.pk:
            self.role = self.base_role
        return super().save(*args, **kwargs)


# ========================================
# Perfis
# ========================================
class Cliente(models.Model):
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE)
    

    def __str__(self):
        return self.usuario.nome


class Psicologo(models.Model):
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE)
    crp = models.CharField(max_length=50, unique=True)  # Registro profissional
    preco_consulta = models.DecimalField(max_digits=8, decimal_places=2)
    duracao_minutos = models.PositiveIntegerField(default=50)

    def __str__(self):
        return f"{self.usuario.nome} - CRP {self.crp}"
