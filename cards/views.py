import re
import os
import qrcode
import shutil
import io
import uuid
import tempfile
import qrcode.image.svg
from io import BytesIO
from pathlib import Path
from django.conf import settings
from django.core.files import File
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.core.files.base import ContentFile
from django.conf import settings
from django.contrib import messages
from django.shortcuts import render
from django.urls import reverse, reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.views.generic import ListView, TemplateView, UpdateView, DetailView, CreateView, DeleteView
from core import analytics_data_api
from .models import Card, Conteudo, Estado, Municipio, Categoria, Subcategoria
from usuarios.models import Usuario
from .forms import CardEditForm, ConteudoEditForm
from .utils import make_vcf, cleaner, resize_image
from django.template.defaultfilters import slugify
from usuarios.tokens import account_activation_token
from django.core.mail import EmailMessage
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template.loader import render_to_string
from django.db.models import Count
from django.http import HttpResponseRedirect, HttpResponse


reg_b = re.compile(r"(android|bb\\d+|meego).+mobile|avantgo|bada\\/|blackberry|blazer|compal|elaine|fennec|hiptop|iemobile|ip(hone|od)|iris|kindle|lge |maemo|midp|mmp|mobile.+firefox|netfront|opera m(ob|in)i|palm( os)?|phone|p(ixi|re)\\/|plucker|pocket|psp|series(4|6)0|symbian|treo|up\\.(browser|link)|vodafone|wap|windows ce|xda|xiino", re.I | re.M)


reg_v = re.compile(r"1207|6310|6590|3gso|4thp|50[1-6]i|770s|802s|a wa|abac|ac(er|oo|s\\-)|ai(ko|rn)|al(av|ca|co)|amoi|an(ex|ny|yw)|aptu|ar(ch|go)|as(te|us)|attw|au(di|\\-m|r |s )|avan|be(ck|ll|nq)|bi(lb|rd)|bl(ac|az)|br(e|v)w|bumb|bw\\-(n|u)|c55\\/|capi|ccwa|cdm\\-|cell|chtm|cldc|cmd\\-|co(mp|nd)|craw|da(it|ll|ng)|dbte|dc\\-s|devi|dica|dmob|do(c|p)o|ds(12|\\-d)|el(49|ai)|em(l2|ul)|er(ic|k0)|esl8|ez([4-7]0|os|wa|ze)|fetc|fly(\\-|_)|g1 u|g560|gene|gf\\-5|g\\-mo|go(\\.w|od)|gr(ad|un)|haie|hcit|hd\\-(m|p|t)|hei\\-|hi(pt|ta)|hp( i|ip)|hs\\-c|ht(c(\\-| |_|a|g|p|s|t)|tp)|hu(aw|tc)|i\\-(20|go|ma)|i230|iac( |\\-|\\/)|ibro|idea|ig01|ikom|im1k|inno|ipaq|iris|ja(t|v)a|jbro|jemu|jigs|kddi|keji|kgt( |\\/)|klon|kpt |kwc\\-|kyo(c|k)|le(no|xi)|lg( g|\\/(k|l|u)|50|54|\\-[a-w])|libw|lynx|m1\\-w|m3ga|m50\\/|ma(te|ui|xo)|mc(01|21|ca)|m\\-cr|me(rc|ri)|mi(o8|oa|ts)|mmef|mo(01|02|bi|de|do|t(\\-| |o|v)|zz)|mt(50|p1|v )|mwbp|mywa|n10[0-2]|n20[2-3]|n30(0|2)|n50(0|2|5)|n7(0(0|1)|10)|ne((c|m)\\-|on|tf|wf|wg|wt)|nok(6|i)|nzph|o2im|op(ti|wv)|oran|owg1|p800|pan(a|d|t)|pdxg|pg(13|\\-([1-8]|c))|phil|pire|pl(ay|uc)|pn\\-2|po(ck|rt|se)|prox|psio|pt\\-g|qa\\-a|qc(07|12|21|32|60|\\-[2-7]|i\\-)|qtek|r380|r600|raks|rim9|ro(ve|zo)|s55\\/|sa(ge|ma|mm|ms|ny|va)|sc(01|h\\-|oo|p\\-)|sdk\\/|se(c(\\-|0|1)|47|mc|nd|ri)|sgh\\-|shar|sie(\\-|m)|sk\\-0|sl(45|id)|sm(al|ar|b3|it|t5)|so(ft|ny)|sp(01|h\\-|v\\-|v )|sy(01|mb)|t2(18|50)|t6(00|10|18)|ta(gt|lk)|tcl\\-|tdg\\-|tel(i|m)|tim\\-|t\\-mo|to(pl|sh)|ts(70|m\\-|m3|m5)|tx\\-9|up(\\.b|g1|si)|utst|v400|v750|veri|vi(rg|te)|vk(40|5[0-3]|\\-v)|vm40|voda|vulc|vx(52|53|60|61|70|80|81|83|85|98)|w3c(\\-| )|webc|whit|wi(g |nc|nw)|wmlb|wonu|x700|yas\\-|your|zeto|zte\\-", re.I | re.M)


class Listar(LoginRequiredMixin, ListView):
    model = Card
    template_name = 'cards/card-lista.html'
    context_object_name = 'cards'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        empresa = Empresa.objects.get(slug=self.kwargs['empresa'])
        ua = self.request.META['HTTP_USER_AGENT']
        queryset = Card.objects.filter(empresa__slug=empresa.slug)
        context['cards'] = queryset
        context['empresa'] = empresa
        return context


class Dashboard(LoginRequiredMixin, TemplateView):
    template_name = 'cards/dashboard-card.html'

    def process_request(self):
        self.request.mobile = False
        if self.request.META['HTTP_USER_AGENT']:
            user_agent = self.request.META['HTTP_USER_AGENT']
            b = reg_b.search(user_agent)
            v = reg_v.search(user_agent[0:4])
            if b or v:
                return True

    def get_data():
        url = ''
        response = request.get(url)
        data = response.json()['data']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.process_request():
            context['mobile'] = True
        card = self.request.user.cards.first()
        pagina = f'/{card.slug_empresa}/card/{card.slug}/'
        data_city = analytics_data_api.run_report_city(
            property_id=None, pagina=pagina)
        data_session_origin = analytics_data_api.run_report_session_origin(
            property_id=None, pagina=pagina)

        resultados = {}
        origens = []
        usuarios_por_origem = []
        if not data_session_origin.rows or not data_city.rows:
            context['resultados'] = None
            return context

        for row in data_session_origin.rows[0].dimension_values:
            origens.append(row.value)
            resultados['origens'] = origens
        for row in data_session_origin.rows[0].metric_values:
            usuarios_por_origem = [row.value]
            resultados['usuarios_por_origem'] = usuarios_por_origem

        context['card'] = card
        context['empresa'] = card.empresa

        # AQUISIÇÃO DE USUÁRIOS
        context['total_de_usuarios'] = data_city.totals[0].metric_values[0].value
        context['usuarios_ativos'] = data_city.totals[0].metric_values[1].value
        context['novos_usuarios'] = data_city.totals[0].metric_values[2].value
        context['tempo_de_interacao'] = data_city.totals[0].metric_values[3].value

        # AQUISIÇÃO DE TRÁFEGO
        context['sessoes'] = data_city.totals[0].metric_values[4].value
        context['duracao_media_sessao'] = data_city.totals[0].metric_values[5].value
        # context['sessoes_engajadas'] = data.totals[0].metric_values[6].value
        context['visualizacoes'] = data_city.totals[0].metric_values[6].value
        # context['visualizacoes_por_sessao'] = data.totals[0].metric_values[8].value
        context['rejeicao'] = data_city.totals[0].metric_values[7].value
        context['data'] = data_city

        # ORIGEM DE TRÁFEGO
        context['resultados'] = resultados
        return context


class Criar(LoginRequiredMixin, UserPassesTestMixin, SuccessMessageMixin, CreateView):
    model = Card
    form_class = CardEditForm
    template_name = 'cards/card-criar.html'
    success_message = 'Card criado com sucesso.'

    def test_func(self):
        assinaturas = self.request.user.assinaturas.all()
        for assinatura in assinaturas:
            if assinatura.status == 'authorized':
                return True

    def handle_no_permission(self):
        return render(self.request, 'cards/permissao-negada.html', status=403)

    def get_success_url(self, card):
        return reverse('core:detalhe', kwargs={'empresa': card.slug_empresa, 'slug': card.slug})

    def get_context_data(self, form=None):
        context = super().get_context_data()
        estados = Estado.objects.all()
        municipios = Municipio.objects.all()
        categorias = Categoria.objects.all()
        subcategorias = Subcategoria.objects.all()
        user = self.request.user
        try:
            card = Card.objects.get(proprietario=user)
            context['card'] = card
        except ObjectDoesNotExist as err:
            print(err)
            card = None
        context['categorias'] = categorias
        context['subcategorias'] = subcategorias
        context['estados'] = estados
        context['municipios'] = municipios
        return context

    def gera_qrcode(self, card, **kwargs):
        host = self.request.get_host()
        vcf_url = card.vcf.url
        url = f'{host}{vcf_url}'
        qr_code = qrcode.make(url, box_size=20)
        name = f'{uuid.uuid4().hex}.png'
        blob = BytesIO()
        qr_code.save(blob)
        card.qr_code.save(name, File(blob))

    def form_valid(self, form):
        card = form.save(commit=False)
        proprietario = self.request.user
        card.proprietario = proprietario
        pasta_usuario = card.proprietario.id.hex
        empresa = form.cleaned_data['empresa']
        telefone= form.cleaned_data['telefone']
        whatsapp = form.cleaned_data['whatsapp']
        facebook = form.cleaned_data['facebook']
        instagram = form.cleaned_data['instagram']
        linkedin = form.cleaned_data['linkedin']
        youtube = form.cleaned_data['youtube']
        tik_tok = form.cleaned_data['tik_tok']
        categoria = form.cleaned_data['categoria']
        subcategoria = form.cleaned_data['subcategoria']
        estado = form.cleaned_data['estado']
        municipio = form.cleaned_data['municipio']
        img_perfil = form.cleaned_data.get('img_perfil')
        logotipo = form.cleaned_data.get('logotipo')
        tamanho_maximo = 1 * 1024 * 1024  # 1 MB em bytes

        # VALIDA TAMANHO DE ARQUIVOS
        if img_perfil:
            if img_perfil.size > tamanho_maximo:
                messages.error(
                    self.request, 'O arquivo de foto excede o tamanho máximo permitido 1 MB.')
                return self.form_invalid(form)


        if logotipo:
            tamanho_maximo = 1 * 1024 * 1024  # 1 MB em bytes
            if logotipo.size > tamanho_maximo:
                messages.error(
                    self.request, 'O arquivo de logotipo excede o tamanho máximo permitido 1 MB.')
                return self.form_invalid(form)

            # Redimensiona logotipo se existe
            largura_desejada = 300
            altura_desejada = 300
            _, extensao = os.path.splitext(logotipo.name)
            extensao = extensao.lstrip('.').upper()
            logotipo_redimensionado = resize_image(logotipo, largura_desejada, altura_desejada)

            # Crie um arquivo temporário para a imagem redimensionada
            temp_file = tempfile.NamedTemporaryFile(delete=False)
            logotipo_redimensionado.save(temp_file, format=extensao) 
            card.logotipo.save(name=logotipo.name, content=temp_file, save=True)
            temp_file.close()
            os.remove(temp_file.name)

        #CRIA VCF
        vcf_content = make_vcf(proprietario.first_name, proprietario.last_name, empresa,
                               telefone, whatsapp, facebook, instagram, linkedin, proprietario.email, youtube, tik_tok)

        vcf_name = f'{uuid.uuid4().hex}.vcf'
        content = '\n'.join([str(line) for line in vcf_content])
        vcf_file = ContentFile(content)
        card.vcf.save(vcf_name, vcf_file)

        # CRIA QRCODE
        self.gera_qrcode(card)

        return HttpResponseRedirect(self.get_success_url(card))


class Editar(LoginRequiredMixin, UserPassesTestMixin, SuccessMessageMixin, UpdateView):
    model = Card
    form_class = CardEditForm
    template_name = 'cards/card-editar.html'
    success_message = 'Card atualizado com sucesso!'

    def test_func(self):
        assinaturas = self.request.user.assinaturas.all()
        for assinatura in assinaturas:
            if assinatura.status == 'authorized':
                return True

    def handle_no_permission(self):
        return render(self.request, 'cards/permissao-negada.html', status=403)

    def get_success_url(self, card):
        user = self.request.user
        card = Card.objects.get(proprietario=user)
        return reverse('core:detalhe', kwargs={'empresa': card.slug_empresa, 'slug': card.slug})

    def get_context_data(self, form=None):
       context = super().get_context_data()
       estados = Estado.objects.all()
       categorias = Categoria.objects.all()
       subcategorias = Subcategoria.objects.all()
       categoria_atual = self.object.categoria
       subcategoria_atual = self.object.subcategoria
       estado_atual = self.object.estado
       municipio_atual = self.object.municipio
       context['categorias'] = categorias
       context['subcategorias'] = subcategorias
       context['estados'] = estados
       context['municipios'] = Municipio.objects.all()
       context['categoria_atual'] = categoria_atual
       context['subcategoria_atual'] = subcategoria_atual
       context['estado_atual'] = estado_atual
       context['municipio_atual'] = municipio_atual
       return context

    def gera_qrcode(self, card, **kwargs):
        host = self.request.get_host()
        vcf_url = card.vcf.url
        url = f'{host}{vcf_url}'
        qr_code = qrcode.make(url, box_size=20)
        name = f'{uuid.uuid4().hex}.png'
        blob = BytesIO()
        qr_code.save(blob)
        card.qr_code.save(name, File(blob), save=False)
        return card.qr_code

    def form_valid(self, form):
        card = self.get_object()
        proprietario = self.request.user
        card.proprietario = proprietario
        empresa = form.cleaned_data['empresa']
        nome_display = form.cleaned_data['nome_display']
        site = form.cleaned_data['site']
        cargo = form.cleaned_data['cargo']
        categoria = form.cleaned_data['categoria']
        subcategoria = form.cleaned_data['subcategoria']
        estado = form.cleaned_data['estado']
        municipio = form.cleaned_data['municipio']
        telefone = form.cleaned_data['telefone']
        whatsapp = form.cleaned_data['whatsapp']
        facebook = form.cleaned_data['facebook']
        instagram = form.cleaned_data['instagram']
        linkedin = form.cleaned_data['linkedin']
        youtube = form.cleaned_data['youtube']
        tik_tok = form.cleaned_data['tik_tok']
        img_perfil = self.request.FILES['img_perfil'] if 'img_perfil' in self.request.FILES else ''
        logotipo = self.request.FILES['logotipo'] if 'logotipo' in self.request.FILES else ''
        tamanho_maximo = 1 * 1024 * 1024

        # VALIDA TAMANHO DE ARQUIVOS
        if img_perfil and img_perfil.size > tamanho_maximo:
            messages.error(
                self.request, 'O arquivo de foto excede o tamanho máximo permitido 1 MB.')
            return self.form_invalid(form)

        if logotipo and logotipo.size > tamanho_maximo:
            messages.error(
                self.request, 'O arquivo de logotipo excede o tamanho máximo permitido 1 MB.')
            return self.form_invalid(form)

        # APAGA IMGAGEM PERFIL ANTIGA
        if img_perfil:
            if card.img_perfil:
                try:
                    os.remove(card.img_perfil.path)
                    card.img_perfil.delete()
                except FileNotFoundError as err:
                    print(err)
            card.img_perfil = img_perfil
            card.img_perfil.save(name=img_perfil.name, content=img_perfil.file)

        # APAGA LOGOTIPO ANTIGO E SALVA NOVO
        if logotipo:
            if card.logotipo:
                try:
                    os.remove(card.logotipo.path)
                    card.logotipo.delete()
                except FileNotFoundError as err:
                    print(err)

            # Redimensiona logotipo se existe
            largura_desejada = 300
            altura_desejada = 300
            _, extensao = os.path.splitext(logotipo.name)
            extensao = extensao.lstrip('.').upper()
            logotipo_redimensionado = resize_image(logotipo, largura_desejada, altura_desejada)

            # Crie um arquivo temporário para a imagem redimensionada
            temp_file = tempfile.NamedTemporaryFile(delete=False)
            logotipo_redimensionado.save(temp_file, format=extensao) 
            card.logotipo.save(name=logotipo.name, content=temp_file, save=True)
            temp_file.close()
            os.remove(temp_file.name)

        # APAGA VCF ANTIGO SALVA NOVO
        if card.vcf:
            try:
                os.remove(card.vcf.path)
                card.vcf.delete()
                vcf_content = make_vcf(proprietario.first_name, proprietario.last_name, empresa,
                                    telefone, whatsapp, facebook, instagram, linkedin, proprietario.email, youtube, tik_tok)

                vcf_name = f'{uuid.uuid4().hex}.vcf'
                content = '\n'.join([str(line) for line in vcf_content])
                vcf_file = ContentFile(content)
                card.vcf.save(vcf_name, vcf_file)
            except FileNotFoundError as err:
                print(err)

        # APAGA QRCODE ANTIGO E SALVA NOVO
        if card.qr_code:
            try:
                os.remove(card.qr_code.path)
                card.qr_code.delete()
                qr_code = self.gera_qrcode(card)
            except FileNotFoundError as err:
                print(err)

        card.nome_display = nome_display
        card.empresa = empresa
        card.site = site
        card.cargo = cargo
        card.categoria = categoria
        card.subcategoria = subcategoria
        card.estado = estado
        card.municipio = municipio
        card.telefone = telefone
        card.whatsapp = whatsapp
        card.facebook = facebook
        card.instagram = instagram
        card.linkedin = linkedin
        card.youtube = youtube
        card.tik_tok = tik_tok
        card.save()

        return HttpResponseRedirect(self.get_success_url(card))


class Detalhar(DetailView):
    model = Card
    template_name = 'cards/meu-card.html'

    # def test_func(self):
    #     assinaturas = self.request.user.assinaturas.all()
    #     for assinatura in assinaturas:
    #         if assinatura.status == 'authorized':
    #             return True

    # def handle_no_permission(self):
    #     return render(self.request, 'cards/permissao-negada.html', status=403)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        card = self.get_object()
        conteudos = card.conteudos.all()
        produtos = []
        servicos = []
        portfolios = []
        promocoes = []
        cursos = []
        for conteudo in conteudos:
            if conteudo.tipo.nome == 'Produto':
                produtos.append(conteudo)
            if conteudo.tipo.nome == 'Serviço':
                servicos.append(conteudo)
            if conteudo.tipo.nome == 'Promoção':
                promocoes.append(conteudo)
            if conteudo.tipo.nome == 'Portfólio':
                portfolios.append(conteudo)
            if conteudo.tipo.nome == 'Curso':
                cursos.append(conteudo)

        context['produtos'] = produtos
        context['servicos'] = servicos
        context['portfolios'] = portfolios
        context['promocoes'] = promocoes
        context['cursos'] = cursos
        return context


class Deletar(LoginRequiredMixin, SuccessMessageMixin, DeleteView):

    model = Card
    success_message = 'Card apagado com sucesso!'
    template_name = 'cards/card-criar.html'

    def get_success_url(self):
        return reverse('core:criar')

    def post(self, request, *args, **kwargs):
        card = self.get_object()
        conteudos = Conteudo.objects.filter(card=card)
        for conteudo in conteudos:
            conteudo.delete()

        # Apagar arquivos associados ao conteúdo
        path = os.path.join(settings.MEDIA_ROOT, self.request.user.id.hex)
        try:
            shutil.rmtree(path)
        except FileNotFoundError as err:
            print(err)

        return super().post(request, *args, **kwargs)


class Todos(LoginRequiredMixin, ListView):

    model = Card
    template_name = 'cards/todos-cards.html'
    context_object_name = 'cards'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        ua = self.request.META['HTTP_USER_AGENT']
        cards = Card.objects.all()
        cards_por_empresa = Empresa.objects.values(
            'nome').annotate(num_cards=Count('cards'))
        context['cards'] = cards
        context['cards_por_empresa'] = cards_por_empresa
        return context


class DashboardEmpresa(TemplateView):
    template_name = 'cards/dashboard-empresa.html'

    def process_request(self):
        self.request.mobile = False
        if self.request.META['HTTP_USER_AGENT']:
            user_agent = self.request.META['HTTP_USER_AGENT']
            b = reg_b.search(user_agent)
            v = reg_v.search(user_agent[0:4])
            if b or v:
                return True

    # def get_data():
    #     url = ''
    #     response = request.get(url)
    #     data = response.json()['data']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.process_request():
            context['mobile'] = True
        empresa = Empresa.objects.get(slug=self.kwargs['empresa'])
        cards = Card.objects.filter(empresa=empresa)
        paginas = [f'/{empresa.slug}/card/{card.slug}/' for card in cards]
        # data_city = analytics_data_api.run_report_city(property_id=None, pagina=paginas)
        # data_session_origin = analytics_data_api.run_report_session_origin(property_id=None, pagina=pagina)
        data_page_path = analytics_data_api.run_report_page_path(
            property_id=None, pagina=paginas)
        data_source_traffic = analytics_data_api.run_report_source_traffic(
            property_id=None, pagina=paginas)

        resultados = {}
        # origens = []
        visualizacoes = []
        origens = []
        origens_visualizacoes = []
        cards_slugs = [card.slug for card in cards]
        resultados['cards'] = cards_slugs
        for i, row in enumerate(data_page_path.rows):
            visualizacoes.append(data_page_path.rows[i].metric_values[0].value)
        resultados['visualizacoes'] = visualizacoes
        for i, row in enumerate(data_source_traffic.rows):
            origens.append(
                data_source_traffic.rows[i].dimension_values[1].value)
            origens_visualizacoes.append(
                data_source_traffic.rows[i].metric_values[0].value)
        resultados['origens'] = origens
        resultados['origens_visualizacoes'] = origens_visualizacoes
        # for row in data_session_origin.rows[0].dimension_values:
        #     origens.append(row.value)
        #     resultados['origens'] = origens
        # for row in data_session_origin.rows[0].metric_values:
        #     usuarios_por_origem = [row.value]
        #     resultados['usuarios_por_origem'] = usuarios_por_origem
        # for row in data_page_path.rows:
        #     pages.append(row.dimension_values)
        #     visualizacoes.append(row.metric_values)
        #     resultados['pages'] = pages

        # EMPRESA
        context['empresa'] = empresa

        # AQUISIÇÃO DE USUÁRIOS
        # context['total_de_usuarios'] = data_city.totals[0].metric_values[0].value
        # context['usuarios_ativos'] = data_city.totals[0].metric_values[1].value
        # context['novos_usuarios'] = data_city.totals[0].metric_values[2].value
        # context['tempo_de_interacao'] = data_city.totals[0].metric_values[3].value

        # AQUISIÇÃO DE TRÁFEGO
        # context['sessoes'] = data_city.totals[0].metric_values[4].value
        # context['duracao_media_sessao'] = data_city.totals[0].metric_values[5].value
        # context['sessoes_engajadas'] = data.totals[0].metric_values[6].value
        # context['visualizacoes'] = data_city.totals[0].metric_values[6].value
        # context['visualizacoes_por_sessao'] = data.totals[0].metric_values[8].value
        # context['rejeicao'] = data_city.totals[0].metric_values[7].value
        # context['data'] = data_city

        # ORIGEM DE TRÁFEGO
        context['resultados'] = resultados

        # VISUALIZAÇÕES
        # context['pages'] = pages

        return context


class ConteudoCriar(LoginRequiredMixin, UserPassesTestMixin, SuccessMessageMixin, CreateView):
    model = Conteudo
    form_class = ConteudoEditForm
    success_url = '.'
    template_name = 'cards/conteudo-criar.html'
    success_message = 'Conteúdo criado com sucesso!'

    def test_func(self):
        assinaturas = self.request.user.assinaturas.all()
        for assinatura in assinaturas:
            if assinatura.status == 'authorized':
                return True

    def handle_no_permission(self):
        return render(self.request, 'cards/permissao-negada.html', status=403)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        usuario = self.request.user
        card = usuario.cards.first()
        conteudos = Conteudo.objects.filter(card__proprietario=usuario)
        quantidade_conteudo = len(conteudos)
        context['card'] = card
        context['conteudos'] = conteudos
        context['quantidade_conteudo'] = quantidade_conteudo
        return context

    def form_valid(self, form):
        conteudo = form.save(commit=False)
        usuario = self.request.user
        # validação da quantidade de conteúdos criados
        conteudos = Conteudo.objects.filter(card__proprietario=usuario)
        if len(conteudos) > 10:
            messages.error(
                    self.request, 'Quantidade máxima de conteúdos atingidos - 10 conteúdos.')
            return self.form_invalid(form)
        card = usuario.cards.first()
        conteudo.card = card
        img = form.cleaned_data['img']
        largura_desejada = 300
        altura_desejada = 300
        tamanho_maximo = 1 * 1024 * 1024

        # Valida tamanho da imagem
        if img:
            if img.size > tamanho_maximo:
                messages.error(
                    self.request, 'O arquivo excede o tamanho máximo permitido 1 MB.')
                return self.form_invalid(form)
            
            extensao = slugify(os.path.splitext(img.name)[1])
            if extensao == 'jpg':
                extensao = 'jpeg'

            # Redimensiona imagem se existe
            img_redimensionada = resize_image(img, largura_desejada, altura_desejada)

            # Crie um arquivo temporário para a imagem redimensionada
            temp_file = tempfile.NamedTemporaryFile(delete=False)
            img_redimensionada.save(temp_file, format=extensao) 
            conteudo.img.save(name=img.name, content=temp_file, save=True)
            temp_file.close()
            os.remove(temp_file.name)

        conteudo.save()

        return super().form_valid(form)


class ConteudoExcluir(LoginRequiredMixin, SuccessMessageMixin, DeleteView):
    model = Conteudo
    template_name = 'cards/conteudo-criar.html'
    success_message = 'Conteúdo atualizado com sucesso!'
    success_url = '.'

    def get_success_url(self, card):
        return reverse('core:conteudo-criar', kwargs={'empresa': card.slug_empresa, 'slug': card.slug})

    def post(self, request, *args, **kwargs):
        conteudo = Conteudo.objects.filter(id=self.kwargs['pk']).first()
        card = conteudo.card
        path = conteudo.img.path

        # APAGA ARQUIVOS ANTIGOS E EXCLUI REGISTRO DO BANCO
        try:
            conteudo.delete()
            os.remove(path)
        except FileNotFoundError as err:
            print(err)

        return HttpResponseRedirect(self.get_success_url(card))


class ConteudoEditarNome(LoginRequiredMixin, UpdateView):
    model = Conteudo
    fields = ['nome']
    template_name = 'cards/conteudo-editar-nome.html'
    success_url = '.'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        usuario = self.request.user
        conteudo = self.get_object()
        context['usuario'] = usuario
        context['conteudo'] = conteudo
        return context

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        botao = self.kwargs['botao']
        if botao == 'cancelar':
            return HttpResponse(self.object.nome)
        return super().get(request, *args, **kwargs)

    def get_form(self, form_class=None):
        # Inicializa o formulário com a classe Bootstrap desejada
        form = super().get_form(form_class)
        form.fields['nome'].widget.attrs.update({'class': 'form-control'})
        return form

    def form_valid(self, form):
        conteudo = form.save()
        return HttpResponse(conteudo.nome)


class ConteudoEditarDescricao(LoginRequiredMixin, UpdateView):
    model = Conteudo
    fields = ['descricao']
    template_name = 'cards/conteudo-editar-descricao.html'
    success_url = '.'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        usuario = self.request.user
        conteudo = self.get_object
        context['usuario'] = usuario
        context['conteudo'] = conteudo
        return context

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        botao = self.kwargs['botao']
        if botao == 'cancelar':
            return HttpResponse(self.object.descricao)
        return super().get(request, *args, **kwargs)

    def get_form(self, form_class=None):
        # Inicializa o formulário com a classe Bootstrap desejada
        form = super().get_form(form_class)
        form.fields['descricao'].widget.attrs.update({'class': 'form-control', 'rows':'3'})
        return form

    def form_valid(self, form):
        conteudo = form.save()
        return HttpResponse(conteudo.descricao)


class ConteudoEditarLink(LoginRequiredMixin, UpdateView):
    model = Conteudo
    fields = ['link']
    template_name = 'cards/conteudo-editar-link.html'
    success_url = '.'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        usuario = self.request.user
        conteudo = self.get_object
        context['usuario'] = usuario
        context['conteudo'] = conteudo
        return context

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        botao = self.kwargs['botao']
        if botao == 'cancelar':
            return HttpResponse(self.object.link)
        return super().get(request, *args, **kwargs)

    def get_form(self, form_class=None):
        # Inicializa o formulário com a classe Bootstrap desejada
        form = super().get_form(form_class)
        form.fields['link'].widget.attrs.update({'class': 'form-control'})
        return form

    def form_valid(self, form):
        conteudo = form.save()
        return HttpResponse(conteudo.link)


class CriarEmpresa(LoginRequiredMixin, SuccessMessageMixin, CreateView):

    model = Card
    form_class = CardEditForm
    template_name = 'cards/card-criar.html'
    success_url = '.'
    success_message = 'Card criado com sucesso. Solicite ao dono do card que ative-o clicando no link que ele recebeu por email'

    # def get_context_data(self, **kwargs):
    #     context = super().get_context_data(**kwargs)
    #     usuario = self.request.user
    #     empresa = Empresa.objects.get(slug=self.kwargs['empresa'])
    #     context['empresa'] = empresa
    #     return context

    def gera_qrcode(self, card, **kwargs):
        host = self.request.get_host()
        vcf_url = card.vcf.url
        url = f'{host}{vcf_url}'
        qr_code = qrcode.make(url, box_size=20)
        name = f'{card.slug}-qrcode.png'
        blob = BytesIO()
        if card.qr_code:
            try:
                os.remove(card.qr_code.path)
                card.qr_code.delete()
                card.save()
            except FileNotFoundError as err:
                print(err)
        qr_code.save(blob)
        card.qr_code.save(name, File(blob), save=False)
        return card.qr_code

    def form_valid(self, form):

        # CRIA NOVO USUÁRIO
        usuario = self.request.user
        email = form.data['email']
        # if email in [usuario.email for usuario in Usuario.objects.all()] or not email:
        #     # TODO Consertar essa mensagem. Está adicionando o erro ao campo de telefone porque o modelform não tem o campo email
        #     form.add_error(
        #         'telefone', 'Card com esse email já existe ou email inválido')
        #     return super().form_invalid(form)
        first_name = form.data['primeiro_nome']
        last_name = form.data['ultimo_nome']
        username = f'{first_name.lower()}.{last_name.lower()}'
        password = Usuario.objects.make_random_password()
        novo_usuario = Usuario.objects.create(email=email, first_name=first_name, last_name=last_name, username=username,
                                              is_active=False)
        novo_usuario.set_password(password)
        novo_usuario.save()

        # CRIA EMPRESA
        if form.data['empresa']:
          nome = form.data['empresa']
          # cnpj = form.data['cnpj']
          nova_empresa = Empresa.objects.create(nome=nome)
        else:
          nova_empresa = Empresa.objects.create(
              nome=slugify(f'{first_name}-{last-name}'))

        # CRIA NOVO CARD
        card = form.save(commit=False)
        card.usuario = novo_usuario
        card.empresa = nova_empresa
        telefone = form.cleaned_data['telefone']
        whatsapp = form.cleaned_data['whatsapp']
        facebook = form.cleaned_data['facebook']
        instagram = form.cleaned_data['instagram']
        linkedin = form.cleaned_data['linkedin']
        youtube = form.cleaned_data['youtube']
        tik_tok = form.cleaned_data['tik_tok']
        cargo = form.cleaned_data['cargo']
        vcf_content = make_vcf(novo_usuario.first_name, novo_usuario.last_name, nova_empresa.nome,
                               telefone, whatsapp, facebook, instagram, linkedin, novo_usuario.email, youtube, tik_tok)

        vcf_name = f'{slugify(novo_usuario.get_full_name())}.vcf'
        content = '\n'.join([str(line) for line in vcf_content])
        vcf_file = ContentFile(content)
        card.vcf.save(vcf_name, vcf_file)
        qr_code = self.gera_qrcode(card)
        card.save()

        # ENVIA EMAIL PARA ATIVAÇÃO DA CONTA
        current_site = get_current_site(self.request)
        subject = 'Ative a sua conta'
        to = novo_usuario.email
        context = {'usuario': novo_usuario, 'dominio': current_site.domain, 'uid': urlsafe_base64_encode(force_bytes(novo_usuario.pk)),
                   'token': account_activation_token.make_token(novo_usuario)}
        body = render_to_string(
            'usuarios/email-ativacao.html', context=context)
        msg = EmailMessage(subject, body, to=[to])
        msg.content_subtype = "html"  # Main content is now text/html
        msg.send()

        return super().form_valid(form)


class Pesquisar(ListView):
    model = Card
    template_name = 'cards/pesquisar.html'
    context_object_name = 'cards'

    def process_request(self):
        self.request.mobile = False
        if self.request.META['HTTP_USER_AGENT']:
            user_agent = self.request.META['HTTP_USER_AGENT']
            b = reg_b.search(user_agent)
            v = reg_v.search(user_agent[0:4])
            if b or v:
                return True

    def get_context_data(self):
        context = super().get_context_data()
        if self.process_request():
            context['mobile'] = True
        estados = Estado.objects.all()
        categorias = Categoria.objects.all()
        context['categorias'] = categorias
        context['subcategorias'] = Subcategoria.objects.filter(
            categoria=categorias.first())
        context['estados'] = estados
        context['municipios'] = Municipio.objects.filter(
            estado=estados.first())
        return context

    def get_queryset(self):
        conteudo_pesquisado = self.request.GET.get("pesquisar")
        categoria = self.request.GET.get(
            "categoria") if self.request.GET.get("categoria") != '0' else None
        subcategoria = self.request.GET.get(
            "subcategoria") if self.request.GET.get("subcategoria") != '0' else None
        queryset = Card.objects.all()
        if conteudo_pesquisado and conteudo_pesquisado != 'None':
            conteudo_pesquisado_limpo = cleaner(conteudo_pesquisado)
            queryset = queryset.filter(
                conteudo_pesquisavel__contains=conteudo_pesquisado_limpo)
        if categoria and categoria != 'None':
            queryset = queryset.filter(categoria=categoria)
        if subcategoria and subcategoria != 'None':
            queryset = queryset.filter(subcategoria=subcategoria)

        return queryset
