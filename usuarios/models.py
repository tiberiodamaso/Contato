import uuid, os
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import FileExtensionValidator
from django.template.defaultfilters import slugify


def get_path(instance, filename):
  instance = instance.usuario.id.hex
  arquivo = slugify(os.path.splitext(filename)[0])
  extensao = os.path.splitext(filename)[1]
  filename = f'{arquivo}{extensao}'
  return os.path.join(instance, filename)


class Usuario(AbstractUser):

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    username = models.CharField(verbose_name='Username', max_length=20, unique=True)
    first_name = models.CharField(verbose_name='Primeiro nome', max_length=20)
    last_name = models.CharField(verbose_name='Último nome', max_length=20)
    email = models.EmailField(verbose_name='E-mail', unique=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'username']

    class Meta:
        verbose_name = 'Usuário'
        verbose_name_plural = 'Usuários'

    def __str__(self):
        return self.get_full_name()


class Perfil(models.Model):
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE, verbose_name='Usuário')
    descricao = models.TextField(verbose_name='Descrição', blank=True, null=True)
    img_perfil = models.FileField(verbose_name='Foto perfil', upload_to=get_path, blank=True, null=True, validators=[
                                  FileExtensionValidator(allowed_extensions=['jpg', 'png', 'jpeg', 'svg'])])

    class Meta:
        verbose_name = 'Perfil'
        verbose_name_plural = 'Perfis'

    def __str__(self):
        return self.usuario.get_full_name()