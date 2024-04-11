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

ARQUIVO_ESTADOS = 'estados.csv'
ARQUIVO_MUNICIPIOS = 'municipios.csv'

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

CODIGO_PAIS = [
    ('+93', 'Afeganistão'),
    ('+27', 'África do Sul'),
    ('+355', 'Albânia'),
    ('+49', 'Alemanha'),
    ('+376', 'Andorra'),
    ('+244', 'Angola'),
    ('+1-268', 'Antígua e Barbuda'),
    ('+966', 'Arábia Saudita'),
    ('+213', 'Argélia'),
    ('+54', 'Argentina'),
    ('+374', 'Armênia'),
    ('+61', 'Austrália'),
    ('+43', 'Áustria'),
    ('+994', 'Azerbaijão'),
    ('+1-242', 'Bahamas'),
    ('+973', 'Bahrein'),
    ('+880', 'Bangladesh'),
    ('+1-246', 'Barbados'),
    ('+32', 'Bélgica'),
    ('+501', 'Belize'),
    ('+229', 'Benin'),
    ('+375', 'Bielorrússia'),
    ('+591', 'Bolívia'),
    ('+387', 'Bósnia e Herzegovina'),
    ('+267', 'Botsuana'),
    ('+55', 'Brasil'),
    ('+673', 'Brunei'),
    ('+359', 'Bulgária'),
    ('+226', 'Burquina Faso'),
    ('+257', 'Burundi'),
    ('+975', 'Butão'),
    ('+238', 'Cabo Verde'),
    ('+855', 'Camboja'),
    ('+237', 'Camarões'),
    ('+1', 'Canadá'),
    ('+974', 'Catar'),
    ('+7', 'Cazaquistão'),
    ('+235', 'Chade'),
    ('+56', 'Chile'),
    ('+86', 'China'),
    ('+357', 'Chipre'),
    ('+57', 'Colômbia'),
    ('+269', 'Comores'),
    ('+242', 'Congo'),
    ('+850', 'Coreia do Norte'),
    ('+82', 'Coreia do Sul'),
    ('+225', 'Costa do Marfim'),
    ('+506', 'Costa Rica'),
    ('+385', 'Croácia'),
    ('+53', 'Cuba'),
    ('+45', 'Dinamarca'),
    ('+253', 'Djibuti'),
    ('+1-767', 'Dominica'),
    ('+20', 'Egito'),
    ('+503', 'El Salvador'),
    ('+971', 'Emirados Árabes Unidos'),
    ('+593', 'Equador'),
    ('+291', 'Eritreia'),
    ('+421', 'Eslováquia'),
    ('+386', 'Eslovênia'),
    ('+34', 'Espanha'),
    ('+1', 'Estados Unidos'),
    ('+372', 'Estônia'),
    ('+251', 'Etiópia'),
    ('+679', 'Fiji'),
    ('+63', 'Filipinas'),
    ('+358', 'Finlândia'),
    ('+33', 'França'),
    ('+241', 'Gabão'),
    ('+220', 'Gâmbia'),
    ('+233', 'Gana'),
    ('+995', 'Geórgia'),
    ('+1-473', 'Granada'),
    ('+30', 'Grécia'),
    ('+502', 'Guatemala'),
    ('+592', 'Guiana'),
    ('+224', 'Guiné'),
    ('+240', 'Guiné Equatorial'),
    ('+245', 'Guiné-Bissau'),
    ('+509', 'Haiti'),
    ('+31', 'Holanda'),
    ('+504', 'Honduras'),
    ('+36', 'Hungria'),
    ('+967', 'Iêmen'),
    ('+692', 'Ilhas Marshall'),
    ('+677', 'Ilhas Salomão'),
    ('+91', 'Índia'),
    ('+62', 'Indonésia'),
    ('+98', 'Irã'),
    ('+964', 'Iraque'),
    ('+353', 'Irlanda'),
    ('+354', 'Islândia'),
    ('+972', 'Israel'),
    ('+39', 'Itália'),
    ('+1-876', 'Jamaica'),
    ('+81', 'Japão'),
    ('+962', 'Jordânia'),
    ('+686', 'Kiribati'),
    ('+383', 'Kosovo'),
    ('+965', 'Kuwait'),
    ('+856', 'Laos'),
    ('+266', 'Lesoto'),
    ('+371', 'Letônia'),
    ('+961', 'Líbano'),
    ('+231', 'Libéria'),
    ('+218', 'Líbia'),
    ('+423', 'Liechtenstein'),
    ('+370', 'Lituânia'),
    ('+352', 'Luxemburgo'),
    ('+389', 'Macedônia do Norte'),
    ('+261', 'Madagáscar'),
    ('+60', 'Malásia'),
    ('+265', 'Malaui'),
    ('+960', 'Maldivas'),
    ('+223', 'Mali'),
    ('+356', 'Malta'),
    ('+212', 'Marrocos'),
    ('+230', 'Maurício'),
    ('+222', 'Mauritânia'),
    ('+52', 'México'),
    ('+691', 'Micronésia'),
    ('+258', 'Moçambique'),
    ('+373', 'Moldávia'),
    ('+377', 'Mônaco'),
    ('+976', 'Mongólia'),
    ('+382', 'Montenegro'),
    ('+95', 'Myanmar'),
    ('+264', 'Namíbia'),
    ('+674', 'Nauru'),
    ('+977', 'Nepal'),
    ('+505', 'Nicarágua'),
    ('+227', 'Níger'),
    ('+234', 'Nigéria'),
    ('+683', 'Niue'),
    ('+47', 'Noruega'),
    ('+64', 'Nova Zelândia'),
    ('+968', 'Omã'),
    ('+680', 'Palau'),
    ('+507', 'Panamá'),
    ('+675', 'Papua-Nova Guiné'),
    ('+92', 'Paquistão'),
    ('+595', 'Paraguai'),
    ('+51', 'Peru'),
    ('+48', 'Polônia'),
    ('+351', 'Portugal'),
    ('+254', 'Quênia'),
    ('+996', 'Quirguistão'),
    ('+686', 'Quiribati'),
    ('+44', 'Reino Unido'),
    ('+236', 'República Centro-Africana'),
    ('+243', 'República Democrática do Congo'),
    ('+1-809', 'República Dominicana'),
    ('+40', 'Romênia'),
    ('+250', 'Ruanda'),
    ('+7', 'Rússia'),
    ('+212', 'Saara Ocidental'),
    ('+685', 'Samoa'),
    ('+1-758', 'Santa Lúcia'),
    ('+1-869', 'São Cristóvão e Neves'),
    ('+378', 'São Marinho'),
    ('+239', 'São Tomé e Príncipe'),
    ('+1-784', 'São Vicente e Granadinas'),
    ('+221', 'Senegal'),
    ('+232', 'Serra Leoa'),
    ('+381', 'Sérvia'),
    ('+963', 'Síria'),
    ('+252', 'Somália'),
    ('+94', 'Sri Lanka'),
    ('+268', 'Suazilândia'),
    ('+249', 'Sudão'),
    ('+211', 'Sudão do Sul'),
    ('+46', 'Suécia'),
    ('+41', 'Suíça'),
    ('+597', 'Suriname'),
    ('+992', 'Tadjiquistão'),
    ('+66', 'Tailândia'),
    ('+886', 'Taiwan'),
    ('+255', 'Tanzânia'),
    ('+420', 'Tchéquia'),
    ('+670', 'Timor-Leste'),
    ('+228', 'Togo'),
    ('+676', 'Tonga'),
    ('+1-868', 'Trindade e Tobago'),
    ('+216', 'Tunísia'),
    ('+993', 'Turcomenistão'),
    ('+90', 'Turquia'),
    ('+688', 'Tuvalu'),
    ('+380', 'Ucrânia'),
    ('+256', 'Uganda'),
    ('+598', 'Uruguai'),
    ('+998', 'Uzbequistão'),
    ('+678', 'Vanuatu'),
    ('+379', 'Vaticano'),
    ('+58', 'Venezuela'),
    ('+84', 'Vietnã'),
    ('+260', 'Zâmbia'),
    ('+263', 'Zimbábue')
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

        # CODIGO PAIS
        for tupla in CODIGO_PAIS:
            codigo, pais = tupla
            CodigoPais.objects.get_or_create(codigo=codigo, pais=pais)
        print('\nTabela CodigoPais populada com sucesso!')

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
