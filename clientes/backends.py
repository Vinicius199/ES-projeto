from django.contrib.auth.backends import ModelBackend
from .models import Cliente 

class ClienteBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            # Tenta buscar o usuário pelo email
            user = Cliente.objects.get(email=username) 
        except Cliente.DoesNotExist:
            return None
        
        # Verifica a senha
        if user.check_password(password) and self.user_can_authenticate(user):
            return user
        return None
    
    def get_user(self, user_id):
        try:
            return Cliente.objects.get(pk=user_id)
        except Cliente.DoesNotExist:
            return None