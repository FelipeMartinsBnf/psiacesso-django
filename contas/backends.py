# contas/backends.py

from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model

class EmailBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        UserModel = get_user_model()
        try:
            # Busca o usuário pelo e-mail, ignorando se é maiúsculo ou minúsculo
            user = UserModel.objects.get(email__iexact=username)
        except UserModel.DoesNotExist:
            return None # Se não encontrar, retorna None
        
        # Se encontrou o usuário, verifica se a senha está correta
        if user.check_password(password):
            return user # Se a senha estiver correta, retorna o objeto do usuário
        
        return None # Se a senha estiver incorreta, retorna None

    def get_user(self, user_id):
        UserModel = get_user_model()
        try:
            return UserModel.objects.get(pk=user_id)
        except UserModel.DoesNotExist:
            return None