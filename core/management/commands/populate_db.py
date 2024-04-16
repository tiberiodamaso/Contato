# import django
import csv
from io import BytesIO

import qrcode
import qrcode.image.svg
from django.contrib.auth.hashers import make_password
from django.core.files import File
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand

from cards.models import Card, Categoria, Subcategoria, Conteudo, Estado, Municipio, TipoConteudo, CodigoPais
from cards.utils import make_vcf
from usuarios.models import Usuario

# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'root.settings')
# django.setup()


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

TIPOS_CONTEUDOS = [
    'Serviço',
    'Produto',
    'Promoção',
    'Portfólio',
    'Curso',
]


class Command(BaseCommand):
    def cria_lista_obj_estados(self):
        estados_existentes = [estado.nome for estado in Estado.objects.all()]
        print(f'\nA Tabela Estados contém {len(estados_existentes)} registros.')

        with open(ARQUIVO_ESTADOS, 'r') as arquivo_estados:
            leitor_csv = csv.DictReader(arquivo_estados, delimiter=';')
            contador_registros = 0
            for linha in leitor_csv:
                if linha['name'] not in estados_existentes:
                    contador_registros += 1
                    registro = Estado(nome=linha['name'], sigla=linha['uf_code'])
                    ESTADOS.append(registro)

        print(f'\nVão ser adicionados {contador_registros} Estados na Tabela de Estados.')
        return ESTADOS

    def cria_lista_obj_municipio(self):
        municipios_existentes = [municipio.nome for municipio in Municipio.objects.all()]
        print(f'\nA Tabela Municípios contém {len(municipios_existentes)} registros.')

        with open(ARQUIVO_MUNICIPIOS, 'r') as arquivo_municipios:
            leitor_csv = csv.DictReader(arquivo_municipios, delimiter=';')
            contador_registros = 0
            estado_linha_anterior = ''
            for linha in leitor_csv:
                estado_linha_atual = linha['uf_code']
                if estado_linha_atual != estado_linha_anterior:
                    estado_linha_anterior = estado_linha_atual
                    estado_obj = Estado.objects.get(sigla=estado_linha_atual)

                if linha['name'] not in municipios_existentes and estado_obj:
                    contador_registros += 1
                    registro = Municipio(nome=linha['name'], estado=estado_obj)
                    MUNICIPIOS.append(registro)

        print(f'\nVão ser adicionados {contador_registros} Municípios na Tabela de Municípios.')
        return MUNICIPIOS

    def cria_lista_obj_codigo_pais(self):
        codigos_existentes = [obj.codigo for obj in CodigoPais.objects.all()]
        print(f'\nA Tabela Códigos de País contém {len(codigos_existentes)} registros.')

        with open(ARQUIVO_CODIGOS_PAIS, 'r') as arquivo_codigos_pais:
            leitor_csv = csv.DictReader(arquivo_codigos_pais, delimiter=';')
            contador_registros = 0
            for linha in leitor_csv:
                if linha['codigo'] not in codigos_existentes:
                    contador_registros += 1
                    registro = CodigoPais(pais=str(linha['pais']), codigo=str(linha['codigo']))
                    CODIGO_PAIS.append(registro)

        print(f'\nVão ser adicionados {contador_registros} códigos de país na Tabela de Código País.')
        return CODIGO_PAIS

    def _create_usuarios(self, username, first_name, last_name, email):
        password = make_password('123')
        is_staff = True
        is_active = True
        is_superuser = False
        Usuario.objects.get_or_create(
            username=username,
            first_name=first_name,
            last_name=last_name,
            defaults={
                'email': email,
                'is_staff': is_staff,
                'is_active': is_active,
                'is_superuser': is_superuser,
                'password': password,
            },
        )

    def _populate_basic_tables(self):

        # USUÁRIOS PARA TESTE
        self._create_usuarios(
            username='margot',
            first_name='Margot',
            last_name='Robie',
            email='margot@email.com',
        )
        self._create_usuarios(
            username='keanu',
            first_name='Keanu',
            last_name='Reeves',
            email='keanu@email.com',
        )
        self._create_usuarios(
            username='tom',
            first_name='Tom',
            last_name='Cruise',
            email='tom@email.com',
        )
        print('Usuarios criados!')

        # ESTADOS
        Estado.objects.bulk_create(self.cria_lista_obj_estados())
        print('\nTabela Estados populada com sucesso!')

        # MUNICIPIOS
        Municipio.objects.bulk_create(self.cria_lista_obj_municipio())
        print('\nTabela Municípios populada com sucesso!')

        # CODIGO PAIS
        CodigoPais.objects.bulk_create(self.cria_lista_obj_codigo_pais())
        print('\nTabela Códigos de País populada com sucesso!')

        # CATEGORIA
        for categoria in CATEGORIAS:
            Categoria.objects.get_or_create(nome=categoria)
        print('\nTabela Categoria populada com sucesso!')

        # SUBCATEGORIA
        for subcategoria in SUBCATEGORIAS:
            id_categoria, nome = subcategoria
            categoria = Categoria.objects.get(id=id_categoria)
            Subcategoria.objects.get_or_create(categoria=categoria, nome=nome)
        print('\nTabela Subcategoria populada com sucesso!')

        # TIPO CONTEUDO
        for nome in TIPOS_CONTEUDOS:
            TipoConteudo.objects.get_or_create(nome=nome)
        print('\n Tabela Tipo Conteudo populada com sucesso!')

    # CRIA CONTEUDO
    def _create_conteudo(self):
        tipo1 = TipoConteudo.objects.first()
        tipo2 = TipoConteudo.objects.last()
        conteudo = Conteudo(
            card=Card.objects.first(),
            tipo=tipo1,
            link='https://www.google.com',
        )
        conteudo.save()
        print(f'\nCriou conteudo do tipo: {tipo1}')

        conteudo2 = Conteudo(
            card=Card.objects.first(),
            tipo=tipo2,
            link='https://www.outlook.com',
        )
        conteudo2.save()
        print(f'\nCriou conteudo do tipo: {tipo2}')

    # CRIA EMPRESA
    # def _create_empresa(self):
    #     nome = 'Empresa Teste'
    #     cnpj = '13219048000137'
    #     colaboradores = [Usuario.object.order_by('-date_joined').first()]
    #     empresa = Empresa()
    #     empresa.nome = nome
    #     empresa.cnpj = cnpj
    #     empresa.save(commit=False)
    #     empresa.colaboradores.add(colaboradores)

    # CRIA QRCODE
    def gera_qrcode(self, card):
        host = 'http://127.0.0.1'
        vcf_url = card.vcf.url
        url = f'{host}{vcf_url}'
        qr_code = qrcode.make(url, box_size=20)
        name = f'{card.slug}-qrcode.png'
        blob = BytesIO()
        qr_code.save(blob)
        card.qr_code.save(name, File(blob), save=False)
        return None

    # CRIA CARD
    def _create_card(self):
        usuario = Usuario.objects.first()
        # verifica se existe card para esse usuario
        if len(Card.objects.filter(proprietario=usuario)) > 0:
            print(f'\nO usuário {str(usuario)} já possui card. Não será criado nenhum card.')
            return None

        print('\nInicia criação de um card')

        # gera um card vazio
        card = Card()

        # Campos Básicos
        # vcf - abaixo
        # qr_code - abaixo
        card.nome_display = 'Nome Display Populate'
        card.img_perfil = File('models.jpg') if File('models.jpg') else None
        card.categoria = Categoria.objects.first()
        card.subcategoria = Subcategoria.objects.first()

        card.proprietario = Usuario.objects.first()
        card.cargo = 'gerente'
        card.telefone = '16981000167'
        card.whatsapp = '16981000167'
        card.estado = Estado.objects.first()
        card.municipio = Municipio.objects.first()
        card.empresa = 'Nome Empresa Populate'
        card.logotipo = File('models.jpg') if File('models.jpg') else None
        card.site = 'https://www.google.com'

        card.facebook = 'https://facebook.com/teste'
        card.instagram = 'https://instagram.com/teste'
        card.linkedin = 'https://linkedin.com/teste'
        card.youtube = 'https://youtube.com/teste'
        card.tik_tok = 'https://tiktok.com/teste'

        # salva card parcial
        card.save()
        print('\nSalva card parcial')

        # Gera vcf
        print('\nVai criar vcf')
        vcf_content = make_vcf(
            usuario.first_name,
            usuario.last_name,
            card.empresa,
            card.telefone,
            card.whatsapp,
            card.facebook,
            card.instagram,
            card.linkedin,
            usuario.email,
            card.youtube,
            card.tik_tok,
        )
        vcf_name = 'card_teste.vcf'
        content = '\n'.join([str(line) for line in vcf_content])
        vcf_file = ContentFile(content)
        card.vcf.save(vcf_name, vcf_file)
        print('\nVcf criado com sucesso')

        # Gera qr_code
        print('\nVai criar qr_code')
        self.gera_qrcode(card)
        print('\nQr_code criado com sucesso')
        card.save()
        print('\nCard salvo com sucesso')

    def handle(self, *args, **options):
        if input('\nDo you want to populate tables? (y/n): ') == str.lower('y'):
            self._populate_basic_tables()
            # self._create_card()
            # self._create_conteudo()

            print('\npopulate db success!!')
        else:
            print('\npopulate db fail..')
