import os, uuid
from pathlib import Path
from django.db import models
from django.core.validators import URLValidator, FileExtensionValidator
from django.template.defaultfilters import slugify
from usuarios.models import Usuario
from django.conf import settings
from .utils import validate_file_extension, make_vcf, valida_cnpj
from django.core.files.base import ContentFile, File
from django.utils.crypto import get_random_string


def get_path(instance, filename):
  instance = instance.user.id.hex
  arquivo = slugify(os.path.splitext(filename)[0])
  extensao = os.path.splitext(filename)[1]
  filename = f'{arquivo}{extensao}'
  return os.path.join(instance, filename)


class Conteudo(models.Model):
  site = models.URLField(verbose_name='Site', blank=True, null=True, validators=[URLValidator(schemes=['http', 'https'])])
  promo1 = models.ImageField(verbose_name='Promo1', upload_to=get_path, blank=True, null=True,
                              validators=[FileExtensionValidator(allowed_extensions=['jpg', 'png', 'jpeg', 'svg'])])
  promo1_link = models.URLField(verbose_name='Promo1 link', max_length=1000, blank=True, null=True, validators=[
                              URLValidator(schemes=['http', 'https'])])
  promo2 = models.ImageField(verbose_name='Promo2', upload_to=get_path, blank=True, null=True,
                              validators=[FileExtensionValidator(allowed_extensions=['jpg', 'png', 'jpeg', 'svg'])])
  promo2_link = models.URLField(verbose_name='Promo2 link', max_length=1000, blank=True, null=True, validators=[
                              URLValidator(schemes=['http', 'https'])])
  promo3 = models.ImageField(verbose_name='Promo3', upload_to=get_path, blank=True, null=True,
                              validators=[FileExtensionValidator(allowed_extensions=['jpg', 'png', 'jpeg', 'svg'])])
  promo3_link = models.URLField(verbose_name='Promo3 link', max_length=1000, blank=True, null=True, validators=[
                              URLValidator(schemes=['http', 'https'])])
  servico1 = models.ImageField(verbose_name='servico1', upload_to=get_path, blank=True, null=True,
                              validators=[FileExtensionValidator(allowed_extensions=['jpg', 'png', 'jpeg', 'svg'])])
  servico1_link = models.URLField(verbose_name='servico1 link', max_length=1000, blank=True, null=True, validators=[
                              URLValidator(schemes=['http', 'https'])])
  servico2 = models.ImageField(verbose_name='servico2', upload_to=get_path, blank=True, null=True,
                              validators=[FileExtensionValidator(allowed_extensions=['jpg', 'png', 'jpeg', 'svg'])])
  servico2_link = models.URLField(verbose_name='servico2 link', max_length=1000, blank=True, null=True, validators=[
                              URLValidator(schemes=['http', 'https'])])
  servico3 = models.ImageField(verbose_name='servico3', upload_to=get_path, blank=True, null=True,
                              validators=[FileExtensionValidator(allowed_extensions=['jpg', 'png', 'jpeg', 'svg'])])
  servico3_link = models.URLField(verbose_name='servico3 link', max_length=1000, blank=True, null=True, validators=[
                              URLValidator(schemes=['http', 'https'])])
  produto1 = models.ImageField(verbose_name='produto1', upload_to=get_path, blank=True, null=True,
                              validators=[FileExtensionValidator(allowed_extensions=['jpg', 'png', 'jpeg', 'svg'])])
  produto1_link = models.URLField(verbose_name='produto1 link', max_length=1000, blank=True, null=True, validators=[
                              URLValidator(schemes=['http', 'https'])])
  produto2 = models.ImageField(verbose_name='produto2', upload_to=get_path, blank=True, null=True,
                              validators=[FileExtensionValidator(allowed_extensions=['jpg', 'png', 'jpeg', 'svg'])])
  produto2_link = models.URLField(verbose_name='produto2 link', max_length=1000, blank=True, null=True, validators=[
                              URLValidator(schemes=['http', 'https'])])
  produto3 = models.ImageField(verbose_name='produto3', upload_to=get_path, blank=True, null=True,
                              validators=[FileExtensionValidator(allowed_extensions=['jpg', 'png', 'jpeg', 'svg'])])
  produto3_link = models.URLField(verbose_name='produto3 link', max_length=1000, blank=True, null=True, validators=[
                              URLValidator(schemes=['http', 'https'])])
  portifolio1 = models.ImageField(verbose_name='portifolio1', upload_to=get_path, blank=True, null=True,
                              validators=[FileExtensionValidator(allowed_extensions=['jpg', 'png', 'jpeg', 'svg'])])
  portifolio1_link = models.URLField(verbose_name='portifolio1 link', max_length=1000, blank=True, null=True, validators=[
                              URLValidator(schemes=['http', 'https'])])
  portifolio2 = models.ImageField(verbose_name='portifolio2', upload_to=get_path, blank=True, null=True,
                              validators=[FileExtensionValidator(allowed_extensions=['jpg', 'png', 'jpeg', 'svg'])])
  portifolio2_link = models.URLField(verbose_name='portifolio2 link', max_length=1000, blank=True, null=True, validators=[
                              URLValidator(schemes=['http', 'https'])])
  portifolio3 = models.ImageField(verbose_name='portifolio3', upload_to=get_path, blank=True, null=True,
                              validators=[FileExtensionValidator(allowed_extensions=['jpg', 'png', 'jpeg', 'svg'])])
  portifolio3_link = models.URLField(verbose_name='portifolio3 link', max_length=1000, blank=True, null=True, validators=[
                              URLValidator(schemes=['http', 'https'])])
  
  class Meta:
        verbose_name = 'Conteúdo'
        verbose_name_plural = 'Conteúdos'

  def __str__(self):
      return str(int(self.id))


class Categoria(models.Model):
  nome = models.CharField(verbose_name='Categoria', max_length=100)

  class Meta:
    verbose_name = 'Categoria'
    verbose_name_plural = 'Categorias'

  def __str__(self):
    return self.nome


class Estado(models.Model):
  nome = models.CharField(verbose_name='Estado', max_length=100)
  sigla = models.CharField(verbose_name='Sigla', max_length=2)

  class Meta:
    verbose_name = 'Estado'
    verbose_name_plural = 'Estados'

  def __str__(self):
    return self.nome


class Municipio(models.Model):
  nome = models.CharField(verbose_name='Município', max_length=100)
  estado = models.ForeignKey(Estado, verbose_name='Estado', on_delete=models.CASCADE)

  class Meta:
    verbose_name = 'Município'
    verbose_name_plural = 'Municípios'

  def __str__(self):
    return self.nome


class Empresa(models.Model):
  nome = models.CharField(verbose_name='Nome', max_length=200)
  cnpj = models.CharField(verbose_name='CNPJ', max_length=14, unique=True, validators=[valida_cnpj], blank=True )
  logotipo = models.FileField(verbose_name='Logotipo', upload_to=get_path, blank=True, null=True, validators=[
                              FileExtensionValidator(allowed_extensions=['jpg', 'png', 'jpeg', 'svg'])])
  proprietario = models.ForeignKey(Usuario, verbose_name='Proprietário', on_delete=models.PROTECT, related_name='empresas')
  slug = models.SlugField(verbose_name='Slug', unique=True, editable=False)
  criada = models.DateField(verbose_name='Criada', auto_now_add=True)
  atualizada = models.DateField(verbose_name='Atualizada', auto_now=True)

  class Meta:
    verbose_name = 'Empresa'
    verbose_name_plural = 'Empresas'

  def __str__(self):
    return self.nome

  def save(self, *args, **kwargs):
    self.slug = slugify(f'{self.cnpj}-{self.nome}')
    super().save(*args, **kwargs)


class Card(models.Model):
  vcf = models.FileField(verbose_name='VCF', upload_to=get_path, blank=True, null=True, validators=[
                            FileExtensionValidator(allowed_extensions=['vcf'])])
  qr_code = models.ImageField(verbose_name='QR Code', upload_to=get_path, blank=True, null=True,
                              validators=[FileExtensionValidator(allowed_extensions=['jpg', 'png', 'jpeg', 'svg'])])
  facebook = models.URLField(verbose_name='Facebook', max_length=200, blank=True, validators=[
                              URLValidator(schemes=['http', 'https'])])
  instagram = models.URLField(verbose_name='Instagram', max_length=200, blank=True, validators=[
                              URLValidator(schemes=['http', 'https'])])
  linkedin = models.URLField(verbose_name='Linkedin', max_length=200, blank=True, validators=[
                              URLValidator(schemes=['http', 'https'])])
  youtube = models.URLField(verbose_name='Youtube', max_length=200, blank=True, validators=[
                              URLValidator(schemes=['http', 'https'])])
  tik_tok = models.URLField(verbose_name='Tik_tok', max_length=200, blank=True, validators=[
                              URLValidator(schemes=['http', 'https'])])
  nome_display = models.CharField(verbose_name='Nome display', max_length=50)
  slug = models.SlugField(verbose_name='Slug', max_length=200, editable=False, unique=True)
  cargo = models.CharField(verbose_name='Cargo', max_length=50, blank=True, null=True)
  telefone = models.CharField(verbose_name='Telefone', max_length=11, unique=True)
  whatsapp = models.CharField(verbose_name='Whatsapp', max_length=11)
  conteudo = models.ForeignKey(Conteudo, verbose_name='Conteúdo', on_delete=models.CASCADE, related_name='cards', blank=True, null=True)
  categoria = models.ForeignKey(Categoria, verbose_name='Categoria', on_delete=models.CASCADE, related_name='cards')
  estado = models.ForeignKey(Estado, verbose_name='Estado', on_delete=models.CASCADE, related_name='cards')
  municipio = models.ForeignKey(Municipio, verbose_name='Município', on_delete=models.CASCADE, related_name='cards')
  empresa = models.ForeignKey(Empresa, verbose_name='Empresa', on_delete=models.CASCADE, related_name='cards')
  usuario = models.ForeignKey(Usuario, verbose_name='Usuário', on_delete=models.CASCADE, related_name='cards')
  criado = models.DateField(verbose_name='Criado', auto_now_add=True)
  atualizado = models.DateField(verbose_name='Atualizado', auto_now=True)

  class Meta:
    verbose_name = 'Card'
    verbose_name_plural = 'Cards'

  def __str__(self):
    return str(self.usuario)

  def save(self, *args, **kwargs):
    if not self.slug:
      self.slug = slugify(self.usuario)
      if Card.objects.filter(slug=self.slug):
        # Se existir, gera um novo slug adicionando um sufixo aleatório
        self.slug = f"{get_random_string(length=4)}-{self.slug}"

    if not self.empresa:
      self.empresa = Empresa.objects.create(
        nome = slugify(self.usuario)
      )
    super().save(*args, **kwargs)

