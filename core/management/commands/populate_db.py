# import django
import csv

from django.contrib.auth.hashers import make_password
from django.core.management.base import BaseCommand

from cards.models import Categoria, Estado, Municipio
from cards.utils import make_vcf
from usuarios.models import Perfil, Usuario

# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'root.settings')
# django.setup()


ESTADOS = []
MUNICIPIOS = []

ARQUIVO_ESTADOS = 'estados.csv'
ARQUIVO_MUNICIPIOS = 'municipios.csv'

CATEGORIAS = [
    'Dentista',
    'Artesão',
]

SUBCATEGORIAS = [
    (1, 'Ortodontista'),
    (2, 'Livros sensoriais'),
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
        print('\nTabela Estados populada com sucesso!')

        # CATEGORIA
        for i, categoria in enumerate(CATEGORIAS):
            Categoria.objects.get_or_create(nome=categoria)
        print('\nTabela Categoria populada com sucesso!')

    # CRIA CONTEUDO
    # def _create_conteudo(self):
    #     site = 'https://siteteste.com.br'
    #     Conteudo.objects.get_or_create(
    #         defaults={
    #             'site': site,
    #         }
    #     )

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

    # CRIA CARD
    # def _create_card(self):
    #     nome_display = 'Teste'
    #     cargo = 'gerente'
    #     telefone = '16981000167'
    #     whatsapp = '16981000167'
    #     facebook = 'https://facebook.com/teste'
    #     instagram = 'https://instagram.com/teste'
    #     linkedin = 'https://linkedin.com/teste'
    #     conteudo = Conteudo.objects.first()
    #     categoria = Categoria.objects.first()
    #     subcategoria = Subcategoria.objects.first()
    #     estado = Estado.objects.first()
    #     municipio = Municipio.objects.first()
    #     empresa = Empresa.objects.first()
    #     usuario = Usuario.objects.first()

    #     #Gera vcf
    #     vcf_content = make_vcf(usuario.first_name, usuario.last_name, empresa.nome,
    #                                telefone, whatsapp, facebook, instagram, linkedin, usuario.email)
    #     vcf_name = 'card_teste.vcf'

    #     #Gera qr_code
    #     qr_code = self.gera_qrcode(card)
    #     content = '\n'.join([str(line) for line in vcf_content])
    #     vcf_file = ContentFile(content)
    #     card.vcf.save(vcf_name, vcf_file)
    #     qr_code = self.gera_qrcode(card)
    #     card.save()

    #     Card.objects.get_or_create(
    #         defaults={
    #             'tipo_cnd': tipo_cnd,
    #             'observacoes': observacoes,
    #             'status': status,
    #             'contribuinte': contribuinte,
    #             'responsavel': responsavel,
    #         }
    #     )

    def handle(self, *args, **options):
        if input('\nDo you want to populate tables? (y/n): ') == str.lower('y'):
            self._populate_basic_tables()
            # self._create_card()

            print('\npopulate db success!!')
        else:
            print('\npopulate db fail..')
