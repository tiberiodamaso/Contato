import os
from django.db import models
from django.template.defaultfilters import slugify
from usuarios.models import Usuario

def get_image_path(instance, filename):
    empresa = instance.empresa.slug
    return os.path.join(empresa, filename)

class Empresa(models.Model):
    nome = models.CharField(verbose_name='Nome', max_length=200)
    logo = models.ImageField(verbose_name='Logotipo', upload_to='logos/', blank=True)
    criada = models.DateField(verbose_name='Criada', auto_now_add=True)
    atualizada = models.DateField(verbose_name='Atualizada', auto_now=True)
    slug = models.SlugField(verbose_name='Slug', unique=True, editable=False)
    gerentes = models.ManyToManyField(Usuario, verbose_name='Gerentes', related_name='empresa_gerentes')
    vendedores = models.ManyToManyField(Usuario, verbose_name='Vendedores', related_name='empresa_vendedores')

    class Meta:
        verbose_name = 'Empresa'
        verbose_name_plural = 'Empresas'

    def __str__(self):
        return self.nome

    def save(self, *args, **kwargs):
        self.slug = slugify(self.nome)
        super().save(*args, **kwargs)


class Card(models.Model):
    empresa = models.ForeignKey(Empresa, verbose_name='Empresa', on_delete=models.CASCADE, related_name='cards')
    img_perfil = models.ImageField(verbose_name='Foto perfil', default='', upload_to=get_image_path, null=True, blank=True)
    whatsapp = models.CharField(verbose_name='Whatsapp', max_length=30)
    facebook = models.URLField(verbose_name='Facebook', max_length=200)
    instagram = models.URLField(verbose_name='Instagram', max_length=200)
    telefone = models.CharField(verbose_name='Telefone', max_length=30, unique=True)
    criado = models.DateField(verbose_name='Criado', auto_now_add=True)
    atualizado = models.DateField(verbose_name='Atualizado', auto_now=True)
    slug = models.SlugField(verbose_name='Slug', max_length=200, editable=False)
    usuario = models.ForeignKey(Usuario, verbose_name='Usuário', on_delete=models.CASCADE, related_name='cards')

    class Meta:
        verbose_name = 'Card'
        verbose_name_plural = 'Cards'

    def __str__(self):
        return str(self.usuario)

    def save(self, *args, **kwargs):
        usuario = self.usuario.get_full_name()
        self.slug = slugify(usuario)
        super().save(*args, **kwargs)
