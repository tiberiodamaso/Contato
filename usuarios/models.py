import uuid, os
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import FileExtensionValidator
from django.template.defaultfilters import slugify
from django.contrib.auth.hashers import make_password
from django.db.models.signals import post_migrate
from django.dispatch import receiver


def get_path(instance, filename):
  instance = instance.usuario.id.hex
  arquivo = slugify(os.path.splitext(filename)[0])
  extensao = os.path.splitext(filename)[1]
  filename = f'{arquivo}{extensao}'
  return os.path.join(instance, filename)


class Usuario(AbstractUser):

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    username = models.CharField(verbose_name='Username', max_length=50)
    first_name = models.CharField(verbose_name='Primeiro nome', max_length=20)
    last_name = models.CharField(verbose_name='Último nome', max_length=20)
    email = models.EmailField(verbose_name='E-mail', unique=True)

    USERNAME_FIELD = 'email'
    EMAIL_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'username']

    class Meta:
        verbose_name = 'Usuário'
        verbose_name_plural = 'Usuários'

    def __str__(self):
        return self.get_full_name()
    
    def save(self, *args, **kwargs):
        # Verificar se o username já existe
        if not self.username:
            base_username = slugify(f'{self.first_name}-{self.last_name}')
            username = base_username
            count = 1

            # Certificar-se de que o username é único
            while Usuario.objects.filter(username=username).exists():
                username = f'{base_username}-{count}'
                count += 1

            self.username = username

        super().save(*args, **kwargs)



class Perfil(models.Model):
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE, verbose_name='Usuário')
    descricao = models.TextField(verbose_name='Descrição', blank=True, null=True)
    img_perfil = models.FileField(verbose_name='Foto perfil', upload_to=get_path, blank=True, null=True, validators=[
                                  FileExtensionValidator(allowed_extensions=['jpg', 'png', 'jpeg'])])
    cnpj_cpf = models.CharField(verbose_name='CPF/CNPJ', max_length=14)
    nome_fantasia = models.CharField(verbose_name='Nome Fantasia', max_length=100)

    class Meta:
        verbose_name = 'Perfil'
        verbose_name_plural = 'Perfis'

    def __str__(self):
        return self.usuario.get_full_name()


##### POPULA TABELA DE USUÁRIOS #####

def popular_usuarios():
    if not Usuario.objects.exists():
        users_data = [
            {'username': 'margot', 'email': 'margot@email.com', 'first_name': 'Margot', 'last_name': 'Robie', 
            'is_staff': True, 'is_active': True, 'is_superuser': False, 'password': make_password('123')},
            {'username': 'keanu', 'email': 'keanu@email.com', 'first_name': 'Keanu', 'last_name': 'Reeves',
             'is_staff': True, 'is_active': True, 'is_superuser': False, 'password': make_password('123')},
            {'username': 'tom', 'email': 'tom@email.com', 'first_name': 'Tom', 'last_name': 'Cruise', 
            'is_staff': True, 'is_active': True, 'is_superuser': False, 'password': make_password('123')},
        ]

        usuarios = [Usuario(
            username=data['username'], 
            email=data['email'], 
            first_name=data['first_name'], 
            last_name=data['last_name'],
            password=data['password'],
            is_staff=data['is_staff'],
            is_active=data['is_active'],
            is_superuser=data['is_superuser']) for data in users_data]

        Usuario.objects.bulk_create(usuarios)


@receiver(post_migrate)
def popular_tabelas_necessarias(sender, **kwargs):
    popular_usuarios()