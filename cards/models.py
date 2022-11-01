import os
from pathlib import Path
from django.db import models
from django.core.validators import URLValidator, FileExtensionValidator
from django.template.defaultfilters import slugify
from usuarios.models import Usuario
from django.conf import settings
from .utils import validate_file_extension, make_vcard
from django.core.files.base import ContentFile, File


def get_path(instance, filename):
    if 'Empresa' in instance.__doc__:
        instance = instance.slug
    else:
        instance = instance.empresa.slug
    return os.path.join(instance, filename)


class Empresa(models.Model):
    nome = models.CharField(verbose_name='Nome', max_length=200)
    logotipo = models.FileField(verbose_name='Logotipo', upload_to=get_path, blank=True, validators=[
                                FileExtensionValidator(allowed_extensions=['jpg', 'png', 'jpeg', 'svg'])])
    slug = models.SlugField(verbose_name='Slug', unique=True, editable=False)
    gerentes = models.ManyToManyField(
        Usuario, verbose_name='Gerentes', related_name='empresa_gerentes')
    vendedores = models.ManyToManyField(
        Usuario, verbose_name='Vendedores', related_name='empresa_vendedores', blank=True)
    site = models.URLField(verbose_name='Site', validators=[
                           URLValidator(schemes=['http', 'https'])])
    slide1 = models.ImageField(verbose_name='Slide 1', upload_to=get_path, blank=True,
                                validators=[FileExtensionValidator(allowed_extensions=['jpg', 'png', 'jpeg', 'svg'])])
    slide1_link = models.URLField(verbose_name='Slide 1 link', max_length=1000, blank=True, validators=[
                               URLValidator(schemes=['http', 'https'])])
    slide2 = models.ImageField(verbose_name='Slide 2', upload_to=get_path, blank=True,
                                validators=[FileExtensionValidator(allowed_extensions=['jpg', 'png', 'jpeg', 'svg'])])
    slide2_link = models.URLField(verbose_name='Slide 2 link', max_length=1000, blank=True, validators=[
                               URLValidator(schemes=['http', 'https'])])
    slide3 = models.ImageField(verbose_name='Slide 3', upload_to=get_path, blank=True,
                                validators=[FileExtensionValidator(allowed_extensions=['jpg', 'png', 'jpeg', 'svg'])])
    slide3_link = models.URLField(verbose_name='Slide 3 link', max_length=1000, blank=True, validators=[
                               URLValidator(schemes=['http', 'https'])])
    produtos = models.ImageField(verbose_name='Produtos', upload_to=get_path, blank=True,
                                validators=[FileExtensionValidator(allowed_extensions=['jpg', 'png', 'jpeg', 'svg'])])
    produtos_link = models.URLField(verbose_name='Produtos link', max_length=1000, blank=True, validators=[
                               URLValidator(schemes=['http', 'https'])])
    servicos = models.ImageField(verbose_name='Serviços', upload_to=get_path, blank=True,
                                validators=[FileExtensionValidator(allowed_extensions=['jpg', 'png', 'jpeg', 'svg'])])
    servicos_link = models.URLField(verbose_name='Serviços link', max_length=1000, blank=True, validators=[
                               URLValidator(schemes=['http', 'https'])])
    promocoes = models.ImageField(verbose_name='Promoção', upload_to=get_path, blank=True,
                                validators=[FileExtensionValidator(allowed_extensions=['jpg', 'png', 'jpeg', 'svg'])])
    promocoes_link = models.URLField(verbose_name='Promoção link', max_length=1000, blank=True, validators=[
                               URLValidator(schemes=['http', 'https'])])
    criada = models.DateField(verbose_name='Criada', auto_now_add=True)
    atualizada = models.DateField(verbose_name='Atualizada', auto_now=True)

    class Meta:
        verbose_name = 'Empresa'
        verbose_name_plural = 'Empresas'

    def __str__(self):
        return self.nome

    def save(self, *args, **kwargs):
        self.slug = slugify(self.nome)
        super().save(*args, **kwargs)


class Card(models.Model):
    empresa = models.ForeignKey(
        Empresa, verbose_name='Empresa', on_delete=models.CASCADE, related_name='cards')
    cargo = models.CharField(verbose_name='Cargo', max_length=30, blank=True)
    img_perfil = models.FileField(verbose_name='Foto perfil', upload_to=get_path, blank=True, validators=[
                                  FileExtensionValidator(allowed_extensions=['jpg', 'png', 'jpeg', 'svg'])])
    vcard = models.FileField(verbose_name='Vcard', upload_to=get_path, blank=True, validators=[
                             FileExtensionValidator(allowed_extensions=['vcf'])])
    whatsapp = models.CharField(verbose_name='Whatsapp', max_length=30)
    facebook = models.URLField(verbose_name='Facebook', max_length=200, blank=True, validators=[
                               URLValidator(schemes=['http', 'https'])])
    instagram = models.URLField(verbose_name='Instagram', max_length=200, blank=True, validators=[
                                URLValidator(schemes=['http', 'https'])])
    linkedin = models.URLField(verbose_name='Linkedin', max_length=200, blank=True, validators=[
                               URLValidator(schemes=['http', 'https'])])
    youtube = models.TextField(verbose_name='Youtube', max_length=1000, blank=True)
    telefone = models.CharField(
        verbose_name='Telefone', max_length=30, unique=True)
    qr_code = models.ImageField(verbose_name='QR Code', upload_to=get_path, blank=True,
                                validators=[FileExtensionValidator(allowed_extensions=['jpg', 'png', 'jpeg', 'svg'])])
    criado = models.DateField(verbose_name='Criado', auto_now_add=True)
    atualizado = models.DateField(verbose_name='Atualizado', auto_now=True)
    slug = models.SlugField(verbose_name='Slug',
                            max_length=200, editable=False)
    usuario = models.ForeignKey(
        Usuario, verbose_name='Usuário', on_delete=models.CASCADE, related_name='cards')

    class Meta:
        verbose_name = 'Card'
        verbose_name_plural = 'Cards'

    def __str__(self):
        return str(self.usuario)

    def save(self, *args, **kwargs):
        usuario = self.usuario.get_full_name()
        first_name = self.usuario.first_name
        last_name = self.usuario.last_name
        self.slug = slugify(usuario)
        super().save(*args, **kwargs)

