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
  cnpj_cpf = models.CharField(verbose_name='CNPJ', max_length=18, unique=True, validators=[valida_cnpj], blank=True, null=True)
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
    whatsapp = models.CharField(verbose_name='Whatsapp', max_length=15, unique=True)
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
    ativo = models.BooleanField(verbose_name='Ativo', default=True)

    class Meta:
        verbose_name = 'Card'
        verbose_name_plural = 'Cards'

    def __str__(self):
        return str(self.usuario_do_card)

    def prepara_conteudo_pesquisavel(self):
        conteudo = self.usuario_do_card.get_full_name().lower() + self.estado.nome.lower() + \
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
    criado = models.DateField(verbose_name='Criado', auto_now_add=True)
    atualizado = models.DateField(verbose_name='Atualizado', auto_now=True)
    ativo = models.BooleanField(verbose_name='Ativo', default=True)

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
    'Assistência Técnica',
    'Automóveis',

]

SUBCATEGORIAS = [
    (1, 'Cabeleleiro'),
    (1, 'Manicure'),
    (1, 'Pedicure'),
    (1, 'Esteticista'),
    (1, 'Depilação'),
    (1, 'Design de sobrancelhas'),
    (1, 'Design de cílios'),
    (2, 'Massagista'),
    (2, 'Terapeuta'),
    (2, 'Nutricionista'),
    (2, 'Remoção de tatuagem'),
    (2, 'Cozinheira'),
    (2, 'Dentista'),
    (2, 'Fisioterapeuta'),
    (2, 'Fonoaudiólogo'),
    (2, 'Quiroprata'),
    (2, 'Doula'),
    (2, 'Enfermeira'),
    (3, 'Encanador'),
    (3, 'Eletricista'),
    (3, 'Marceneiro'),
    (3, 'Serralheiro'),
    (3, 'Chaveiro'),
    (3, 'Arquiteto'),
    (3, 'Automação residencial'),
    (3, 'Design de interiores'),
    (3, 'Empreiteiro'),
    (3, 'Engenheiro'),
    (3, 'Limpeza pós obra'),
    (3, 'Marmoraria e Granitos'),
    (3, 'Pedreiro'),
    (3, 'Poço artesiano'),
    (3, 'Remoção de entulho'),
    (3, 'Instalador de gás'),
    (3, 'Gesso e Drywall'),
    (3, 'Pintor'),
    (3, 'Serralheria e solda'),
    (3, 'Vidraceiro'),
    (3, 'Dedetizador'),
    (3, 'Desentupidor'),
    (3, 'Desinfecção'),
    (3, 'Impermeabilizador'),
    (3, 'Marido de aluguel'),
    (3, 'Mudanças e carretos'),
    (3, 'Tapeceiro'),
    (3, 'Banheira'),
    (3, 'Coifas e exaustores'),
    (3, 'Decorador'),
    (3, 'Instalador de papel de parede'),
    (3, 'Jardinagem e paisagismo'),
    (3, 'Piscineiro'),
    (3, 'Redes de proteção'),
    (4, 'Diarista'),
    (4, 'Faxineira'),
    (4, 'Personal organizer'),
    (5, 'Cuidadores de idosos'),
    (5, 'Babá'),
    (5, 'Pet sitter'),
    (6, 'Consultores de negócios'),
    (6, 'Coach'),
    (6, 'Assessoria de imprensa'),
    (6, 'Administração de imóveis'),
    (6, 'Assessor de investimentos'),
    (6, 'Contador'),
    (6, 'Corretor'),
    (6, 'Despachante'),
    (6, 'Recrutamento e seleção'),
    (6, 'Segurança do trabalho'),
    (6, 'Advogado'),
    (6, 'Detetive particular'),
    (6, 'Guia de turismo'),
    (7, 'Fotógrafo'),
    (7, 'Videomaker'),
    (8, 'Designer gráfico'),
    (8, 'Web designer'),
    (9, 'Professor particular'),
    (9, 'Instrutor de música'),
    (9, 'Artes'),
    (9, 'Artesanato'),
    (9, 'Circo'),
    (9, 'Fotografia'),
    (9, 'Moda'),
    (9, 'Dança'),
    (9, 'Esportes'),
    (9, 'Luta'),
    (9, 'Desenvolvimento web'),
    (9, 'Marketing digital'),
    (10, 'Tradutor'),
    (10, 'Intérprete'),
    (11, 'Organizador de festa'),
    (11, 'Cerimonialista'),
    (11, 'Assessor de eventos'),
    (11, 'Carros de casamento'),
    (11, 'Equipamento para festas'),
    (11, 'Garçons e copeiras'),
    (11, 'Manobrista'),
    (11, 'Recepcionista'),
    (11, 'Segurança'),
    (11, 'Bartender'),
    (11, 'Buffet'),
    (11, 'Churrasqueiro'),
    (11, 'Confeiteira'),
    (11, 'Animador de festa'),
    (11, 'Bandas e cantores'),
    (11, 'DJ'),
    (11, 'Brindes e lembranças'),
    (11, 'Convites'),
    (11, 'Decoração'),
    (11, 'Edição de vídeo'),
    (11, 'Fotografia'),
    (11, 'Florista'),
    (12, 'Mecânico'),
    (12, 'Funileiro'),
    (12, 'Pintura'),
    (13, 'Jardineiro'),
    (13, 'Paisagista'),
    (14, 'Especialista em mídias sociais'),
    (14, 'Gestor de campanha online'),
    (15, 'Motoboy'),
    (15, 'Motorista de aplicativo'),
    (16, 'Livros sensoriais'),
    (16, 'Bijouterias'),
    (16, 'Artigos decorativos'),
    (17, 'Aparelho de som'),
    (17, 'Aquecedor a gás'),
    (17, 'Ar condicionado'),
    (17, 'Câmera'),
    (17, 'Televisão'),
    (17, 'Video Game'),
    (17, 'Adegas'),
    (17, 'Fogão e cooktop'),
    (17, 'Geladeira e freezer'),
    (17, 'Lava louças'),
    (17, 'Máquina de costura'),
    (17, 'Lava roupas'),
    (17, 'Microondas'),
    (17, 'Secadora de roupas'),
    (17, 'Celular'),
    (17, 'Impressora'),
    (17, 'Computador desktop'),
    (17, 'Computador notebook'),
    (17, 'Tablet'),
    (17, 'Smartwatch'),
    (18, 'Alarme'),
    (18, 'Ar condicionado'),
    (18, 'Som'),
    (18, 'Funilaria'),
    (18, 'Higienização e polimento'),
    (18, 'Martelinho de ouro'),
    (18, 'Pintura'),
    (18, 'Insulfim'),
    (18, 'Borracharia'),
    (18, 'Guincho'),
    (18, 'Mecânia em geral'),
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