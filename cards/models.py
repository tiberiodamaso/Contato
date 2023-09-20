import os, re
from django.core.validators import FileExtensionValidator, URLValidator
from django.db import models
from django.template.defaultfilters import slugify
from django.utils.crypto import get_random_string
from usuarios.models import Usuario
from .utils import make_vcf, valida_cnpj, validate_file_extension
from PIL import Image


def get_path(instance, filename):
    if isinstance(instance, Card):
        instance = instance.proprietario.id.hex
    else:
        instance = instance.card.proprietario.id.hex
    arquivo = slugify(os.path.splitext(filename)[0])
    extensao = os.path.splitext(filename)[1]
    filename = f'{arquivo}{extensao}'
    return os.path.join(instance, filename)


class Categoria(models.Model):
    nome = models.CharField(verbose_name='Categoria', max_length=100)

    class Meta:
        verbose_name = 'Categoria'
        verbose_name_plural = 'Categorias'

    def __str__(self):
        return self.nome


class Subcategoria(models.Model):
    categoria = models.ForeignKey(Categoria, verbose_name='Categoria', on_delete=models.CASCADE, related_name='subcategorias')
    nome = models.CharField(verbose_name='Subcategoria', max_length=100)

    class Meta:
        verbose_name = 'Subcategoria'
        verbose_name_plural = 'Subcategorias'

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


class Card(models.Model):
    # info do card
    vcf = models.FileField(
        verbose_name='VCF',
        upload_to=get_path,
        blank=True,
        null=True,
        validators=[FileExtensionValidator(allowed_extensions=['vcf'])],
    )
    qr_code = models.ImageField(
        verbose_name='QR Code',
        upload_to=get_path,
        blank=True,
        null=True,
        validators=[FileExtensionValidator(
            allowed_extensions=['jpg', 'png', 'jpeg', 'svg'])],
    )
    nome_display = models.CharField(verbose_name='Nome display', max_length=50)
    slug = models.SlugField(verbose_name='Slug', max_length=200, editable=False, unique=True)
    img_perfil = models.FileField(
        verbose_name='Foto perfil',
        upload_to=get_path,
        blank=True,
        null=True,
        validators=[FileExtensionValidator(
            allowed_extensions=['jpg', 'png', 'jpeg', 'svg'])],
    )
    categoria = models.ForeignKey(Categoria, verbose_name='Categoria', on_delete=models.CASCADE, related_name='cards')
    subcategoria = models.ForeignKey(Subcategoria, verbose_name='Subcategoria', on_delete=models.CASCADE, related_name='cards')

    # dados de perfil do usuario proprietario do card
    proprietario = models.ForeignKey(Usuario, verbose_name='Proprietário', on_delete=models.CASCADE, related_name='cards')
    cargo = models.CharField(verbose_name='Cargo', max_length=50, blank=True)
    telefone = models.CharField(verbose_name='Telefone', max_length=11, unique=True)
    whatsapp = models.CharField(verbose_name='Whatsapp', max_length=11)
    estado = models.ForeignKey(Estado, verbose_name='Estado', on_delete=models.CASCADE, related_name='cards')
    municipio = models.ForeignKey(Municipio, verbose_name='Município', on_delete=models.CASCADE, related_name='cards')
    empresa = models.CharField(verbose_name='Empresa', max_length=200, blank=True)
    conteudo_pesquisavel = models.TextField(verbose_name='Conteúdo pesquisável', default='', editable=False)
    logotipo = models.FileField(
        verbose_name='Logotipo',
        upload_to=get_path,
        blank=True,
        null=True,
        validators=[FileExtensionValidator(
            allowed_extensions=['jpg', 'png', 'jpeg', 'svg'])],
    )
    slug_empresa = models.SlugField(verbose_name='Slug da Empresa', max_length=200, editable=False, unique=True)
    site = models.URLField(verbose_name='Site', blank=True, validators=[URLValidator(schemes=['http', 'https'])])

    # redes sociais do usuario proprietário do card
    facebook = models.URLField(
        verbose_name='Facebook',
        max_length=200,
        blank=True,
        validators=[URLValidator(schemes=['http', 'https'])],
    )
    instagram = models.URLField(
        verbose_name='Instagram',
        max_length=200,
        blank=True,
        validators=[URLValidator(schemes=['http', 'https'])],
    )
    linkedin = models.URLField(
        verbose_name='Linkedin',
        max_length=200,
        blank=True,
        validators=[URLValidator(schemes=['http', 'https'])],
    )
    youtube = models.URLField(
        verbose_name='Youtube',
        max_length=200,
        blank=True,
        validators=[URLValidator(schemes=['http', 'https'])],
    )
    tik_tok = models.URLField(
        verbose_name='Tik_tok',
        max_length=200,
        blank=True,
        validators=[URLValidator(schemes=['http', 'https'])],
    )

    # histórico
    criado = models.DateField(verbose_name='Criado', auto_now_add=True)
    atualizado = models.DateField(verbose_name='Atualizado', auto_now=True)

    class Meta:
        verbose_name = 'Card'
        verbose_name_plural = 'Cards'

    def __str__(self):
        return str(self.proprietario)

    def prepara_conteudo_pesquisavel(self):
        conteudo = self.proprietario.get_full_name().lower() + self.estado.nome.lower() + \
            self.municipio.nome.lower() + self.categoria.nome.lower() + self.subcategoria.nome.lower()

        # substituir caracteres acentuados por não acentuados
        conteudo = re.sub(r'[áàâãä]', 'a', conteudo)
        conteudo = re.sub(r'[éèêë]', 'e', conteudo)
        conteudo = re.sub(r'[íìîï]', 'i', conteudo)
        conteudo = re.sub(r'[óòôõö]', 'o', conteudo)
        conteudo = re.sub(r'[úùûü]', 'u', conteudo)
        conteudo = re.sub('ç', 'c', conteudo)

        # remover todos os caracteres que não são números e não são letras (caracter de linha, de parágrafo etc)
        conteudo = re.sub(r'[^a-z0-9]', '', conteudo)

        return conteudo

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.nome_display)
            if Card.objects.filter(slug=self.slug):
                # Se existir, gera um novo slug adicionando um sufixo aleatório
                self.slug = f'{get_random_string(length=4)}-{self.slug}'

        if not self.empresa:
            self.slug_empresa = slugify(self.nome_display)
            if Card.objects.filter(slug_empresa=self.slug_empresa):
                # Se existir, gera um novo slug adicionando um sufixo aleatório
                self.slug_empresa = f'{get_random_string(length=4)}-{self.slug_empresa}'
        else:
            self.slug_empresa = slugify(self.empresa)
        
        self.conteudo_pesquisavel = self.prepara_conteudo_pesquisavel()

        super().save(*args, **kwargs)


class TipoConteudo(models.Model):
    nome = models.CharField(
        verbose_name='Nome', max_length=100, blank=True)

    class Meta:
        verbose_name = 'Tipo de conteúdo'
        verbose_name_plural = 'Tipos de conteúdo'

    def __str__(self):
        return self.nome


class Conteudo(models.Model):
    card = models.ForeignKey(Card, verbose_name='card', on_delete=models.CASCADE, related_name='conteudos')
    tipo = models.ForeignKey(
        TipoConteudo,
        verbose_name='Tipo',
        on_delete=models.CASCADE,
        related_name='conteudos',
    )
    img = models.ImageField(
        verbose_name='Imagem',
        upload_to=get_path,
        blank=True,
        null=True,
        validators=[FileExtensionValidator(
            allowed_extensions=['jpg', 'png', 'jpeg', 'svg'])],
    )
    link = models.URLField(
        verbose_name='Link',
        max_length=1000,
        blank=True,
        null=True,
        validators=[URLValidator(schemes=['http', 'https'])],
    )


# class Empresa(models.Model):
#   nome = models.CharField(verbose_name='Nome', max_length=200)
#   cnpj = models.CharField(verbose_name='CNPJ', max_length=14, unique=True, validators=[valida_cnpj], blank=True, null=True)
#   cnae = models.CharField(verbose_name='CNAE', max_length=7)
#   logotipo = models.FileField(verbose_name='Logotipo', upload_to=get_path, blank=True, null=True, validators=[
#                               FileExtensionValidator(allowed_extensions=['jpg', 'png', 'jpeg', 'svg'])])
#   # proprietario = models.ForeignKey(Usuario, verbose_name='Proprietário', on_delete=models.PROTECT, related_name='empresas')
#   slug = models.SlugField(verbose_name='Slug', unique=True, editable=False)
#   # site = models.URLField(verbose_name='Site', blank=True, validators=[URLValidator(schemes=['http', 'https'])])
#   criada = models.DateField(verbose_name='Criada', auto_now_add=True)
#   atualizada = models.DateField(verbose_name='Atualizada', auto_now=True)

#   class Meta:
#     verbose_name = 'Empresa'
#     verbose_name_plural = 'Empresas'

#   def __str__(self):
#     return self.nome

#   def save(self, *args, **kwargs):
#     self.slug = slugify(f'{self.nome}')
#     super().save(*args, **kwargs)