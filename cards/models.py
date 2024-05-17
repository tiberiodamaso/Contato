import os, re, uuid, csv
from io import BytesIO
from django.core.validators import FileExtensionValidator, URLValidator
from django.db import models
from django.db.models.signals import post_migrate
from django.dispatch import receiver
from django.template.defaultfilters import slugify
from django.utils.crypto import get_random_string
from usuarios.models import Usuario
from .utils import make_vcf, valida_cnpj, validate_file_extension
from PIL import Image


def get_path(instance, filename):
    if isinstance(instance, Card):
        instance = instance.usuario_do_card.id.hex
    else:
        instance = instance.empresa.proprietario.id.hex
    arquivo = uuid.uuid4().hex
    extensao = slugify(os.path.splitext(filename)[1])
    filename = f'{arquivo}.{extensao}'
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


class CodigoPais(models.Model):
    codigo = models.CharField(verbose_name='Código', max_length=10)
    pais = models.CharField(verbose_name='País', max_length=50)

    class Meta:
        verbose_name = 'Código de país'
        verbose_name_plural = 'Códigos de países'

    def __str__(self):
        return f'({self.codigo}) {self.pais}'


class Empresa(models.Model):
  nome_fantasia = models.CharField(verbose_name='Nome Fantasia', max_length=200)
  cnpj_cpf = models.CharField(verbose_name='CNPJ', max_length=14, unique=True, validators=[valida_cnpj], blank=True, null=True)
  proprietario = models.ForeignKey(Usuario, verbose_name='Proprietário', on_delete=models.PROTECT, related_name='empresas')
  slug = models.SlugField(verbose_name='Slug', editable=False)
  criada = models.DateField(verbose_name='Criada', auto_now_add=True)
  atualizada = models.DateField(verbose_name='Atualizada', auto_now=True)

  class Meta:
    verbose_name = 'Empresa'
    verbose_name_plural = 'Empresas'

  def __str__(self):
    return self.nome_fantasia


class Card(models.Model):
    vcf = models.FileField(
        verbose_name='VCF',
        upload_to=get_path,
        blank=True,
        null=True,
        validators=[FileExtensionValidator(allowed_extensions=['vcf'])],
    )
    endereco = models.CharField(verbose_name='Endereço', max_length=500, blank=True)
    site = models.URLField(verbose_name='Site', blank=True, validators=[URLValidator(schemes=['http', 'https'])])
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
        validators=[FileExtensionValidator(
            allowed_extensions=['jpg', 'png', 'jpeg', 'svg'])],
    )
    categoria = models.ForeignKey(Categoria, verbose_name='Categoria', on_delete=models.CASCADE, related_name='cards')
    subcategoria = models.ForeignKey(Subcategoria, verbose_name='Subcategoria', on_delete=models.CASCADE, related_name='cards')

    # dados de perfil do usuario proprietario do card
    proprietario = models.ForeignKey(Usuario, verbose_name='Proprietário', on_delete=models.CASCADE, related_name='cards')
    usuario_do_card = models.ForeignKey(Usuario, verbose_name='Usuário do card', on_delete=models.CASCADE, related_name='card_do_usuario')
    cargo = models.CharField(verbose_name='Cargo', max_length=50, blank=True)
    modelo = models.CharField(verbose_name='Modelo', max_length=1)
    cor = models.CharField(verbose_name='Cor de fundo', max_length=7, default='#212529')

    # redes sociais do usuario proprietário do card
    instagram = models.URLField(
        verbose_name='Instagram',
        max_length=200,
        blank=True,
        validators=[URLValidator(schemes=['http', 'https'])],
    )
    cod_pais = models.ForeignKey(CodigoPais, verbose_name='Código do país', on_delete=models.CASCADE, related_name='cards')
    whatsapp = models.CharField(verbose_name='Whatsapp', max_length=20, unique=True)
    tik_tok = models.URLField(
        verbose_name='Tik_tok',
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
    facebook = models.URLField(
        verbose_name='Facebook',
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
    estado = models.ForeignKey(Estado, verbose_name='Estado', on_delete=models.CASCADE, related_name='cards')
    municipio = models.ForeignKey(Municipio, verbose_name='Município', on_delete=models.CASCADE, related_name='cards')
    empresa = models.ForeignKey(Empresa, verbose_name='Empresa', max_length=200, on_delete=models.CASCADE, related_name='cards')
    conteudo_pesquisavel = models.TextField(verbose_name='Conteúdo pesquisável', default='', editable=False)
    logotipo = models.FileField(
        verbose_name='Logotipo',
        upload_to=get_path,
        blank=True,
        null=True,
        validators=[FileExtensionValidator(
            allowed_extensions=['jpg', 'png', 'jpeg', 'svg'])],
    )

    # histórico
    criado = models.DateField(verbose_name='Criado', auto_now_add=True)
    atualizado = models.DateField(verbose_name='Atualizado', auto_now=True)

    class Meta:
        verbose_name = 'Card'
        verbose_name_plural = 'Cards'

    def __str__(self):
        return str(self.usuario_do_card)

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

        self.conteudo_pesquisavel = self.prepara_conteudo_pesquisavel()

        super().save(*args, **kwargs)


class TipoAnuncio(models.Model):
    nome = models.CharField(verbose_name='Nome', max_length=100, blank=True)

    class Meta:
        verbose_name = 'Tipo de anúncio'
        verbose_name_plural = 'Tipos de anúncio'

    def __str__(self):
        return self.nome


class Anuncio(models.Model):
    tipo = models.ForeignKey(TipoAnuncio, verbose_name='Tipo', on_delete=models.CASCADE, related_name='anuncios')
    empresa = models.ForeignKey(Empresa, verbose_name='Empresa', max_length=200, on_delete=models.CASCADE, related_name='anuncios')
    img = models.ImageField(
        verbose_name='Imagem',
        upload_to=get_path,
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
    nome = models.CharField(verbose_name='Nome', max_length=50)
    descricao = models.TextField(verbose_name='Descrição', blank=True)

    class Meta:
        verbose_name = 'Anúncio'
        verbose_name_plural = 'Anúncios'



###### POPULA TABELAS NECESSÁRIAS APÓS MIGRATE ######

ESTADOS = []
MUNICIPIOS = []
CODIGO_PAIS = []
ARQUIVO_ESTADOS = 'estados.csv'
ARQUIVO_MUNICIPIOS = 'municipios.csv'
ARQUIVO_CODIGOS_PAIS = 'codigos_pais.csv'

CATEGORIAS = [
    'Beleza e Estética',
    'Saúde e Bem estar',
    'Reparo e Manutenção',
    'Limpeza e Organização',
    'Cuidados pessoais',
    'Consultoria e Coaching',
    'Fotografia e Vídeo',
    'Design e Criação',
    'Aulas particulares',
    'Tradução e Interpretação',
    'Eventos',
    'Manutenção de veículos',
    'Jardinagem e Paisagismo',
    'Marketing digital',
    'Delivery e Transporte',
    'Artesanato',
]

SUBCATEGORIAS = [
    (1, 'Cabeleleiro'),
    (1, 'Manicure'),
    (1, 'Esteticista'),
    (2, 'Massagista'),
    (2, 'Terapeuta'),
    (2, 'Nutricionista'),
    (3, 'Encanador'),
    (3, 'Eletricista'),
    (3, 'Marceneiro'),
    (3, 'Serralheiro'),
    (4, 'Diarista'),
    (4, 'Faxineiro'),
    (4, 'Personal organizer'),
    (5, 'Cuidadores de idosos'),
    (5, 'Babá'),
    (5, 'Pet sitter'),
    (6, 'Consultores de negócios'),
    (6, 'Coach'),
    (6, 'Pet sitter'),
    (7, 'Fotógrafo'),
    (7, 'Videomaker'),
    (8, 'Designer gráfico'),
    (8, 'Web designer'),
    (9, 'Professor particular'),
    (9, 'Instrutor de música'),
    (10, 'Tradutor'),
    (10, 'Intérprete'),
    (11, 'Organizador de festa'),
    (11, 'Cerimonialista'),
    (12, 'Mecânico'),
    (12, 'Funileiro'),
    (12, 'Pintor'),
    (13, 'Jardineiro'),
    (13, 'Paisagista'),
    (14, 'Especialista em mídias sociais'),
    (14, 'Gestor de campanha online'),
    (15, 'Motoboy'),
    (15, 'Motorista de aplicativo'),
    (16, 'Livros sensoriais'),
    (16, 'Bijouterias'),
    (16, 'Artigos decorativos'),
]

TIPOS_ANUNCIOS = [
    'Serviço',
    'Produto',
    'Promoção',
    'Portfólio',
    'Curso',
]

def popular_estados():
    with open(ARQUIVO_ESTADOS, 'r') as arquivo_estados:
        leitor_csv = csv.DictReader(arquivo_estados, delimiter=';')
        for linha in leitor_csv:
            registro = Estado(nome=linha['name'], sigla=linha['uf_code'])
            ESTADOS.append(registro)
    Estado.objects.bulk_create(ESTADOS)
    print('\nTabela Estados populada com sucesso!')


def popular_municipios():
    with open(ARQUIVO_MUNICIPIOS, 'r') as arquivo_municipios:
        leitor_csv = csv.DictReader(arquivo_municipios, delimiter=';')
        estado_linha_anterior = ''
        for linha in leitor_csv:
            estado_linha_atual = linha['uf_code']
            if estado_linha_atual != estado_linha_anterior:
                estado_linha_anterior = estado_linha_atual
                estado_obj = Estado.objects.get(sigla=estado_linha_atual)

            if estado_obj:
                registro = Municipio(nome=linha['name'], estado=estado_obj)
                MUNICIPIOS.append(registro)
    Municipio.objects.bulk_create(MUNICIPIOS)
    print('\nTabela Municípios populada com sucesso!')


def popular_codigo_pais():
    with open(ARQUIVO_CODIGOS_PAIS, 'r') as arquivo_codigos_pais:
        leitor_csv = csv.DictReader(arquivo_codigos_pais, delimiter=';')
        for linha in leitor_csv:
            registro = CodigoPais(pais=str(linha['pais']), codigo=str(linha['codigo']))
            CODIGO_PAIS.append(registro)
    CodigoPais.objects.bulk_create(CODIGO_PAIS)
    print('\nTabela Códigos de País populada com sucesso!')


def popular_categorias():
    for categoria in CATEGORIAS:
        Categoria.objects.get_or_create(nome=categoria)
    print('\nTabela Categoria populada com sucesso!')


def popular_subcategorias():
    for subcategoria in SUBCATEGORIAS:
        id_categoria, nome = subcategoria
        categoria = Categoria.objects.get(id=id_categoria)
        Subcategoria.objects.get_or_create(categoria=categoria, nome=nome)
    print('\nTabela Subcategoria populada com sucesso!')


def popular_tipos_anuncios():
    for nome in TIPOS_ANUNCIOS:
        TipoAnuncio.objects.get_or_create(nome=nome)
    print('\n Tabela Tipo Conteúdo populada com sucesso!')


@receiver(post_migrate)
def popular_tabelas_necessarias(sender, **kwargs):
    if not Estado.objects.exists():
        popular_estados()
    if not Municipio.objects.exists():
        popular_municipios()
    if not CodigoPais.objects.exists():
        popular_codigo_pais()
    if not Categoria.objects.exists():
        popular_categorias()
    if not Subcategoria.objects.exists():
        popular_subcategorias()
    if not TipoAnuncio.objects.exists():
        popular_tipos_anuncios()