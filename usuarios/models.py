from django.db import models
from django.contrib.auth.models import AbstractUser
# from cards.models import Empresa

class Usuario(AbstractUser):

    username = models.CharField(max_length=20, unique=True, verbose_name='Username')
    first_name = models.CharField(max_length=20, verbose_name='Primeiro nome')
    last_name = models.CharField(max_length=20, verbose_name='Último nome')
    email = models.EmailField(verbose_name='E-mail', unique=True)

    REQUIRED_FIELDS = ['first_name', 'last_name', 'email']

    class Meta:
        verbose_name = 'Usuário'
        verbose_name_plural = 'Usuários'

    def __str__(self):
        return self.get_full_name()

