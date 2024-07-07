import re
import os
import qrcode
import shutil
import io
import uuid
import tempfile
import qrcode.image.svg
import math
from io import BytesIO
from pathlib import Path
from django.conf import settings
from django.core.files import File
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.core.files.base import ContentFile
from django.conf import settings
from django.contrib import messages
from django.core.serializers import serialize
from django.shortcuts import render, redirect
from django.urls import reverse, reverse_lazy
from django.contrib.auth.hashers import make_password
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.views.generic import ListView, TemplateView, UpdateView, DetailView, CreateView, DeleteView, View
from core import analytics_data_api
from .models import Card, Anuncio, Estado, Municipio, Categoria, Subcategoria, Empresa, Avaliacao
from usuarios.models import Usuario
from compras.models import Ad
from .forms import CardEditForm, AnuncioEditForm, CardEditFormPJ
from .utils import make_vcf, cleaner, resize_image, create_in_memory_file
from django.template.defaultfilters import slugify
from usuarios.tokens import account_activation_token
from django.core.mail import EmailMessage
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template.loader import render_to_string
from django.db.models import Count
from django import forms
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse, QueryDict


reg_b = re.compile(r"(android|bb\\d+|meego).+mobile|avantgo|bada\\/|blackberry|blazer|compal|elaine|fennec|hiptop|iemobile|ip(hone|od)|iris|kindle|lge |maemo|midp|mmp|mobile.+firefox|netfront|opera m(ob|in)i|palm( os)?|phone|p(ixi|re)\\/|plucker|pocket|psp|series(4|6)0|symbian|treo|up\\.(browser|link)|vodafone|wap|windows ce|xda|xiino", re.I | re.M)


reg_v = re.compile(r"1207|6310|6590|3gso|4thp|50[1-6]i|770s|802s|a wa|abac|ac(er|oo|s\\-)|ai(ko|rn)|al(av|ca|co)|amoi|an(ex|ny|yw)|aptu|ar(ch|go)|as(te|us)|attw|au(di|\\-m|r |s )|avan|be(ck|ll|nq)|bi(lb|rd)|bl(ac|az)|br(e|v)w|bumb|bw\\-(n|u)|c55\\/|capi|ccwa|cdm\\-|cell|chtm|cldc|cmd\\-|co(mp|nd)|craw|da(it|ll|ng)|dbte|dc\\-s|devi|dica|dmob|do(c|p)o|ds(12|\\-d)|el(49|ai)|em(l2|ul)|er(ic|k0)|esl8|ez([4-7]0|os|wa|ze)|fetc|fly(\\-|_)|g1 u|g560|gene|gf\\-5|g\\-mo|go(\\.w|od)|gr(ad|un)|haie|hcit|hd\\-(m|p|t)|hei\\-|hi(pt|ta)|hp( i|ip)|hs\\-c|ht(c(\\-| |_|a|g|p|s|t)|tp)|hu(aw|tc)|i\\-(20|go|ma)|i230|iac( |\\-|\\/)|ibro|idea|ig01|ikom|im1k|inno|ipaq|iris|ja(t|v)a|jbro|jemu|jigs|kddi|keji|kgt( |\\/)|klon|kpt |kwc\\-|kyo(c|k)|le(no|xi)|lg( g|\\/(k|l|u)|50|54|\\-[a-w])|libw|lynx|m1\\-w|m3ga|m50\\/|ma(te|ui|xo)|mc(01|21|ca)|m\\-cr|me(rc|ri)|mi(o8|oa|ts)|mmef|mo(01|02|bi|de|do|t(\\-| |o|v)|zz)|mt(50|p1|v )|mwbp|mywa|n10[0-2]|n20[2-3]|n30(0|2)|n50(0|2|5)|n7(0(0|1)|10)|ne((c|m)\\-|on|tf|wf|wg|wt)|nok(6|i)|nzph|o2im|op(ti|wv)|oran|owg1|p800|pan(a|d|t)|pdxg|pg(13|\\-([1-8]|c))|phil|pire|pl(ay|uc)|pn\\-2|po(ck|rt|se)|prox|psio|pt\\-g|qa\\-a|qc(07|12|21|32|60|\\-[2-7]|i\\-)|qtek|r380|r600|raks|rim9|ro(ve|zo)|s55\\/|sa(ge|ma|mm|ms|ny|va)|sc(01|h\\-|oo|p\\-)|sdk\\/|se(c(\\-|0|1)|47|mc|nd|ri)|sgh\\-|shar|sie(\\-|m)|sk\\-0|sl(45|id)|sm(al|ar|b3|it|t5)|so(ft|ny)|sp(01|h\\-|v\\-|v )|sy(01|mb)|t2(18|50)|t6(00|10|18)|ta(gt|lk)|tcl\\-|tdg\\-|tel(i|m)|tim\\-|t\\-mo|to(pl|sh)|ts(70|m\\-|m3|m5)|tx\\-9|up(\\.b|g1|si)|utst|v400|v750|veri|vi(rg|te)|vk(40|5[0-3]|\\-v)|vm40|voda|vulc|vx(52|53|60|61|70|80|81|83|85|98)|w3c(\\-| )|webc|whit|wi(g |nc|nw)|wmlb|wonu|x700|yas\\-|your|zeto|zte\\-", re.I | re.M)


# VIEWS AUXILIARES
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
        conteudo_pesquisado = self.request.GET.get("pesquisar", "")
        categoria_pesquisada = self.request.GET.get("categoria", "")
        subcategoria_pesquisada = self.request.GET.get("subcategoria", "")
        estados = Estado.objects.all()
        categorias = Categoria.objects.all()
        termos = []

        for card in context['cards']:
            avaliacoes_qtd = 0
            avaliacao_valor = 0
            avaliacoes = card.avaliacoes.all()  # Obtém todas as avaliações relacionadas ao card
            if avaliacoes.exists():
                for avaliacao in avaliacoes:
                    avaliacao_valor += avaliacao.valor
                    avaliacoes_qtd += 1
            else:
                avaliacoes_qtd = 1  # Para evitar divisão por zero
            
            avaliacao = math.ceil(avaliacao_valor / avaliacoes_qtd)
            card.avaliacao = avaliacao


        if conteudo_pesquisado:
            termos.append(conteudo_pesquisado)
        if categoria_pesquisada and categoria_pesquisada != '0':
            nome_categoria = Categoria.objects.get(id=categoria_pesquisada).nome
            termos.append(nome_categoria)
        if subcategoria_pesquisada and subcategoria_pesquisada != '0':
            nome_subcategoria = Subcategoria.objects.get(id=subcategoria_pesquisada).nome
            termos.append(nome_subcategoria)

        context['termos_pesquisados'] = ', em '.join(termos) if termos else None

        

        # context['termos_pesquisados'] = f'{conteudo_pesquisado} em {cat.nome} / {sub.nome}'
        
        context['range'] = range(1, 6)
        context['categorias'] = categorias
        context['subcategorias'] = Subcategoria.objects.filter(categoria=categorias.first())
        context['estados'] = estados
        context['municipios'] = Municipio.objects.filter(estado=estados.first())
        context['conteudo_pesquisado'] = conteudo_pesquisado
        return context

    def get_queryset(self):
        conteudo_pesquisado = self.request.GET.get("pesquisar")
        categoria = self.request.GET.get("categoria") if self.request.GET.get("categoria") != '0' else None
        subcategoria = self.request.GET.get("subcategoria") if self.request.GET.get("subcategoria") != '0' else None
        queryset = Card.objects.filter(publico=True)
        if conteudo_pesquisado and conteudo_pesquisado != 'None':
            conteudo_pesquisado_limpo = cleaner(conteudo_pesquisado)
            queryset = queryset.filter(conteudo_pesquisavel__contains=conteudo_pesquisado_limpo)
        if categoria and categoria != 'None':
            queryset = queryset.filter(categoria=categoria)
        if subcategoria and subcategoria != 'None':
            queryset = queryset.filter(subcategoria=subcategoria)

        return queryset


class Modelos(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    template_name = 'cards/modelos.html'

    def test_func(self):
        self.cartoes_pagos = 0
        usuario = self.request.user
        empresa = usuario.empresas.first()
        cards = empresa.cards.all() # cards criados
        if usuario.perfil.is_pj:
            cartoes_comprados = usuario.cartoespj.all()
        else:
            cartoes_comprados = usuario.cartoespf.all()

        if cartoes_comprados:    
            for cartao in cartoes_comprados:
                if cartao.status == 'paid':
                    self.cartoes_pagos += 1

        if len(cards) < self.cartoes_pagos:
            return True


    def handle_no_permission(self):
        if self.request.user.perfil.is_pj:
            if not self.cartoes_pagos:
                return render(self.request, 'cards/permissao-negada-nao-comprou-cartao-pj.html', status=403)
            else:    
                return render(self.request, 'cards/permissao-negada-cartoes-criados-atingiu-limite.html', status=403)
        else:
            return render(self.request, 'cards/permissao-negada-nao-comprou-cartao-pf.html', status=403)


class TrocarModelo(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    template_name = 'cards/trocar-modelo.html'

    def test_func(self):
        usuario = self.request.user
        self.comprou_cartao_pj = False
        self.comprou_cartao_pf = False

        if usuario.perfil.is_pj:
            cartoes_pj_comprados = usuario.cartoespj.all()
            for cartao in cartoes_pj_comprados:
                if cartao.status == 'paid':
                    self.comprou_cartao_pj = True
        else:
            cartoes_pf_comprados = usuario.cartoespf.all()
            for cartao in cartoes_pf_comprados:
                if cartao.status == 'paid':
                    self.comprou_cartao_pf = True

        if self.comprou_cartao_pj or self.comprou_cartao_pf:
            return True

    def handle_no_permission(self):
        if not self.comprou_cartao_pf:
            return render(self.request, 'cards/permissao-negada-nao-comprou-cartao-pf.html', status=403)
        if not self.comprou_cartao_pj:
            return render(self.request, 'cards/permissao-negada-nao-comprou-cartao-pj.html', status=403)
        

    def get_success_url(self, card):
        empresa = self.request.user.empresas.first()
        if self.request.user.perfil.is_pj:
            return reverse('core:detalhar-card-pj', kwargs={'empresa': empresa.slug, 'slug': card.slug})
        else:
            return reverse('core:detalhar-card-pf', kwargs={'empresa': empresa.slug, 'slug': card.slug})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        usuario = self.request.user
        card = usuario.cards.last()
        context['card'] = card
        return context

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        usuario = self.request.user
        card = usuario.cards.last()
        modelo = self.request.GET.get('modelo')
        if modelo:
            card.modelo = modelo
            card.save()
            return HttpResponseRedirect(self.get_success_url(card))
        return self.render_to_response(context)


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


class AvaliarCard(LoginRequiredMixin, View):
    
    def post(self, request, *args, **kwargs):
        card = Card.objects.get(slug=kwargs['slug'])
        usuario = request.user
        valor = request.POST.get('avaliacao')
        try:
            Avaliacao.objects.create(
                valor=valor,
                card=card,
                usuario=usuario
            )
            messages.success(request, 'Avaliação salva com sucesso.')
        except IntegrityError as e:
            messages.error(request, 'Erro ao salvar a avaliação.')
            print("Ocorreu um erro ao tentar salvar o objeto Avaliação:", e)

        return redirect('core:pesquisar')


# CARDS PF
class CriarCardPF(LoginRequiredMixin, UserPassesTestMixin, SuccessMessageMixin, CreateView):
    model = Card
    form_class = CardEditForm
    template_name = 'cards/criar-card-pf.html'
    success_message = 'Cartão criado com sucesso.'

    def test_func(self):
        cartoes_comprados = self.request.user.cartoespf.all()
        for cartao in cartoes_comprados:
            if cartao.status == 'paid':
                return True

    def handle_no_permission(self):
        return render(self.request, 'cards/permissao-negada-nao-comprou-cartao-pf.html', status=403)

    def get_success_url(self, card):
        empresa = self.request.user.empresas.first()
        return reverse('core:detalhar-card-pf', kwargs={'empresa': empresa.slug, 'slug': card.slug})

    def get_context_data(self, form=None):
        context = super().get_context_data()
        modelo = self.request.GET.get('modelo')
        estados = Estado.objects.all()
        municipios = Municipio.objects.all()
        categorias = Categoria.objects.all()
        subcategorias = Subcategoria.objects.all()
        user = self.request.user
        try:
            card = Card.objects.filter(proprietario=user)
            context['card'] = card
        except ObjectDoesNotExist as err:
            print(err)
            card = None
        context['modelo'] = modelo
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
        empresa_atual = proprietario.empresas.first()
        card.proprietario = proprietario
        card.usuario_do_card = proprietario
        card.empresa = empresa_atual
        publico = form.cleaned_data['publico']
        pasta_usuario = card.proprietario.id.hex
        modelo = form.cleaned_data['modelo']
        empresa = form.data['empresa']
        site = form.cleaned_data['site']
        cod_pais = form.cleaned_data['cod_pais']
        cod_pais_vcf = cod_pais.codigo
        whatsapp = form.cleaned_data['whatsapp']
        whatsapp_vcf = cleaner(cod_pais_vcf) + cleaner(whatsapp)
        facebook = form.cleaned_data['facebook']
        instagram = form.cleaned_data['instagram']
        linkedin = form.cleaned_data['linkedin']
        youtube = form.cleaned_data['youtube']
        tik_tok = form.cleaned_data['tik_tok']
        categoria = form.cleaned_data['categoria']
        subcategoria = form.cleaned_data['subcategoria']
        estado = form.cleaned_data['estado']
        municipio = form.cleaned_data['municipio']
        endereco = form.cleaned_data['endereco']
        img_perfil = form.cleaned_data.get('img_perfil')
        logotipo = form.cleaned_data.get('logotipo')
        largura_desejada = 500
        altura_desejada = 500
        # tamanho_maximo = 1 * 1024 * 1024  # 1 MB em bytes

        # VALIDA EXTENSAO E TAMANHO DE ARQUIVOS
        if img_perfil:

            if not img_perfil.name.endswith(('.jpg', '.jpeg', '.png', '.JPG', '.JPEG', '.PNG')):
                messages.error(self.request, 'Apenas arquivos JPG ou PNG são permitidos.')
                return self.form_invalid(form)


            extensao = slugify(os.path.splitext(img_perfil.name)[1])
            if extensao == 'jpg' or extensao == 'JPG':
                extensao = 'jpeg'

            # Redimensiona img_perfil se existe
            img_perfil_redimensionado, buffer_img_perfil = resize_image(img_perfil, largura_desejada, altura_desejada)

            # Cria in_memory_file para possibilitar associar ao card.img_perfil antes de salvar
            if img_perfil_redimensionado and buffer_img_perfil:
                in_memory_file = create_in_memory_file(buffer_img_perfil, img_perfil.name)
                card.img_perfil = in_memory_file

            # if img_perfil.size > tamanho_maximo:
            #     messages.error(
            #         self.request, 'O arquivo de foto excede o tamanho máximo permitido 1 MB.')
            #     return self.form_invalid(form)

        if logotipo:

            if not logotipo.name.endswith(('.jpg', '.jpeg', '.png', '.JPG', '.JPEG', '.PNG')):
                messages.error(self.request, 'Apenas arquivos JPG ou PNG são permitidos.')
                return self.form_invalid(form)

            extensao = slugify(os.path.splitext(logotipo.name)[1])
            if extensao == 'jpg' or extensao == 'JPG':
                extensao = 'jpeg'

            # Redimensiona logotipo se existe
            logotipo_redimensionado, buffer_logotipo = resize_image(logotipo, largura_desejada, altura_desejada)

            # Cria in_memory_file para possibilitar associar ao card.logotipo antes de salvar
            if logotipo_redimensionado and buffer_logotipo:
                in_memory_file = create_in_memory_file(buffer_logotipo, logotipo.name)
                card.logotipo = in_memory_file

            # tamanho_maximo = 1 * 1024 * 1024  # 1 MB em bytes
            # if logotipo.size > tamanho_maximo:
            #     messages.error(
            #         self.request, 'O arquivo de logotipo excede o tamanho máximo permitido 1 MB.')
            #     return self.form_invalid(form)

        if empresa:
            empresa_atual.nome_fantasia = empresa
            empresa_atual.slug = slugify(empresa)
            empresa_atual.save()
            perfil = self.request.user.perfil
            perfil.nome_fantasia = empresa
            perfil.save()
            card.empresa = empresa_atual

        #CRIA VCF
        vcf_content = make_vcf(proprietario.first_name, proprietario.last_name, empresa,
                               whatsapp_vcf, site, endereco, estado, municipio, proprietario.email)

        vcf_name = f'{uuid.uuid4().hex}.vcf'
        content = '\n'.join([str(line) for line in vcf_content])
        vcf_file = ContentFile(content)
        card.vcf.save(vcf_name, vcf_file)

        # CRIA QRCODE
        self.gera_qrcode(card)

        return HttpResponseRedirect(self.get_success_url(card))

    def form_invalid(self, form):
        response = super().form_invalid(form)
        for field, errors in form.errors.items():
            for error in errors:
                messages.error(self.request, f"{field}: {error}")

        modelo = self.request.POST.get('modelo', '')
        if modelo:
            response.context_data['modelo'] = modelo
        return response


class ListarCardPF(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = Card
    template_name = 'cards/listar-card-pf.html'
    context_object_name = 'cards'

    def test_func(self):
        cartoes_comprados = self.request.user.cartoespf.all()
        for cartao in cartoes_comprados:
            if cartao.status == 'paid':
                return True

    def handle_no_permission(self):
        return render(self.request, 'cards/permissao-negada-nao-comprou-cartao-pf.html', status=403)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        empresa = Empresa.objects.get(slug=self.kwargs['empresa'])
        ua = self.request.META['HTTP_USER_AGENT']
        queryset = Card.objects.filter(empresa__slug=empresa.slug)
        context['cards'] = queryset
        context['empresa'] = empresa
        return context


class EditarCardPF(LoginRequiredMixin, UserPassesTestMixin, SuccessMessageMixin, UpdateView):
    model = Card
    form_class = CardEditForm
    template_name = 'cards/editar-card-pf.html'
    success_message = 'Cartão atualizado com sucesso!'

    def test_func(self):
        cartoes_comprados = self.request.user.cartoespf.all()
        for cartao in cartoes_comprados:
            if cartao.status == 'paid':
                return True

    def handle_no_permission(self):
        return render(self.request, 'cards/permissao-negada-nao-comprou-cartao-pf.html', status=403)

    def get_success_url(self, card):
        usuario = self.request.user
        card = Card.objects.get(proprietario=usuario)
        empresa = usuario.empresas.first()
        return reverse('core:detalhar-card-pf', kwargs={'empresa': empresa.slug, 'slug': card.slug})

    def get_context_data(self, form=None):
       context = super().get_context_data()
       modelo = self.get_object().modelo
       estados = Estado.objects.all()
       categorias = Categoria.objects.all()
       subcategorias = Subcategoria.objects.all()
       categoria_atual = self.object.categoria
       subcategoria_atual = self.object.subcategoria
       estado_atual = self.object.estado
       municipio_atual = self.object.municipio
       empresa = self.get_object().empresa.nome_fantasia
       context['modelo'] = modelo
       context['categorias'] = categorias
       context['subcategorias'] = subcategorias
       context['estados'] = estados
       context['municipios'] = Municipio.objects.all()
       context['categoria_atual'] = categoria_atual
       context['subcategoria_atual'] = subcategoria_atual
       context['estado_atual'] = estado_atual
       context['municipio_atual'] = municipio_atual
       context['empresa'] = empresa
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
        empresa_atual = proprietario.empresas.first()
        card.proprietario = proprietario
        card.empresa = empresa_atual
        publico = form.cleaned_data['publico']
        empresa = form.data['empresa']
        modelo = form.cleaned_data['modelo']
        cor = form.cleaned_data['cor']
        nome_display = form.cleaned_data['nome_display']
        site = form.cleaned_data['site']
        cargo = form.cleaned_data['cargo']
        categoria = form.cleaned_data['categoria']
        subcategoria = form.cleaned_data['subcategoria']
        estado = form.cleaned_data['estado']
        municipio = form.cleaned_data['municipio']
        endereco = form.cleaned_data['endereco']
        cod_pais = form.cleaned_data['cod_pais']
        cod_pais_vcf = cod_pais.codigo
        whatsapp = form.cleaned_data['whatsapp']
        whatsapp_vcf = cleaner(cod_pais_vcf) + cleaner(whatsapp)
        facebook = form.cleaned_data['facebook']
        instagram = form.cleaned_data['instagram']
        linkedin = form.cleaned_data['linkedin']
        youtube = form.cleaned_data['youtube']
        tik_tok = form.cleaned_data['tik_tok']
        img_perfil = self.request.FILES['img_perfil'] if 'img_perfil' in self.request.FILES else ''
        logotipo = self.request.FILES['logotipo'] if 'logotipo' in self.request.FILES else ''
        largura_desejada = 500
        altura_desejada = 500
        # tamanho_maximo = 1 * 1024 * 1024

        # VALIDA TAMANHO DE ARQUIVOS
        # if img_perfil and img_perfil.size > tamanho_maximo:
        #     messages.error(
        #         self.request, 'O arquivo de foto excede o tamanho máximo permitido 1 MB.')
        #     return self.form_invalid(form)

        # if logotipo and logotipo.size > tamanho_maximo:
        #     messages.error(
        #         self.request, 'O arquivo de logotipo excede o tamanho máximo permitido 1 MB.')
        #     return self.form_invalid(form)

        # APAGA IMGAGEM PERFIL ANTIGA
        if img_perfil:

            if not img_perfil.name.endswith(('.jpg', '.jpeg', '.png', '.JPG', '.JPEG', '.PNG')):
                messages.error(self.request, 'Apenas arquivos JPG ou PNG são permitidos.')
                return self.form_invalid(form)

            if card.img_perfil:
                try:
                    os.remove(card.img_perfil.path)
                    card.img_perfil.delete()
                except FileNotFoundError as err:
                    print(err)

            extensao = slugify(os.path.splitext(img_perfil.name)[1])
            if extensao == 'jpg' or extensao == 'JPG':
                extensao = 'jpeg'

            # Redimensiona img_perfil se existe
            img_perfil_redimensionado, buffer_img_perfil = resize_image(img_perfil, largura_desejada, altura_desejada)

            # Cria in_memory_file para possibilitar associar ao card.img_perfil antes de salvar
            if img_perfil_redimensionado and buffer_img_perfil:
                in_memory_file = create_in_memory_file(buffer_img_perfil, img_perfil.name)
                card.img_perfil.save(name=img_perfil.name, content=in_memory_file)

        if 'sem_foto' in self.request.POST:
            if card.img_perfil:
                try:
                    os.remove(card.img_perfil.path)
                    card.img_perfil.delete()
                except FileNotFoundError as err:
                    print(err)


        # APAGA LOGOTIPO ANTIGO E SALVA NOVO
        if logotipo:
            if not logotipo.name.endswith(('.jpg', '.jpeg', '.png', '.JPG', '.JPEG', '.PNG')):
                messages.error(self.request, 'Apenas arquivos JPG ou PNG são permitidos.')
                return self.form_invalid(form)

            if card.logotipo:
                try:
                    os.remove(card.logotipo.path)
                    card.logotipo.delete()
                except FileNotFoundError as err:
                    print(err)

            extensao = slugify(os.path.splitext(logotipo.name)[1])
            if extensao == 'jpg' or extensao == 'JPG':
                extensao = 'jpeg'

            # Redimensiona logotipo se existe
            logotipo_redimensionado, buffer_logotipo  = resize_image(logotipo, largura_desejada, altura_desejada)

            if logotipo_redimensionado and buffer_logotipo:
                in_memory_file = create_in_memory_file(buffer_logotipo, logotipo.name)
                card.logotipo = in_memory_file
                card.logotipo.save(name=logotipo.name, content=in_memory_file)

        if 'sem_logo' in self.request.POST:
            if card.logotipo:
                try:
                    os.remove(card.logotipo.path)
                    card.logotipo.delete()
                except FileNotFoundError as err:
                    print(err)

        if empresa:
            empresa_atual.nome_fantasia = empresa
            empresa_atual.slug = slugify(empresa)
            empresa_atual.save()
            perfil = self.request.user.perfil
            perfil.nome_fantasia = empresa
            perfil.save()
            card.empresa = empresa_atual

        # APAGA VCF ANTIGO SALVA NOVO
        if card.vcf:
            try:
                os.remove(card.vcf.path)
                card.vcf.delete()
                vcf_content = make_vcf(proprietario.first_name, proprietario.last_name, empresa,
                                    whatsapp_vcf, site, endereco, estado, municipio, proprietario.email)

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
        card.publico = publico
        card.slug = slugify(nome_display)
        card.cor = cor
        card.site = site
        card.cargo = cargo
        card.categoria = categoria
        card.subcategoria = subcategoria
        card.estado = estado
        card.municipio = municipio
        card.cod_pais = cod_pais
        card.whatsapp = whatsapp
        card.facebook = facebook
        card.instagram = instagram
        card.linkedin = linkedin
        card.youtube = youtube
        card.tik_tok = tik_tok
        card.save()

        return HttpResponseRedirect(self.get_success_url(card))

    def form_invalid(self, form):
        for field, errors in form.errors.items():
            for error in errors:
                messages.error(self.request, f"{field}: {error}")

        return super().form_invalid(form)


class DetalharCardPF(DetailView):
    model = Card

    def chunk_list(self, lst):
        if len(lst) <= 4:
            return [lst]
        elif len(lst) in [5, 6]:
            return [lst[:3], lst[3:]]
        elif len(lst) in [7, 8]:
            return [lst[:4], lst[4:]]
        elif len(lst) == 9:
            return [lst[:3], lst[3:6], lst[6:]]
        else:
            return [lst[:4], lst[4:8], lst[8:]]

    def get_template_names(self):
        template_name = super().get_template_names()
        modelo = self.get_object().modelo
        template_name = [f'cards/modelo-{modelo}.html']
        return template_name

    def luminosidade(self, cor_de_fundo):
        # Converte a cor hexadecimal para RGB
        cor = cor_de_fundo.lstrip('#')
        rgb = tuple(int(cor[i:i+2], 16) for i in (0, 2, 4))
        
        # Fórmula de luminosidade para determinar o contraste
        luminosidade = (0.299 * rgb[0] + 0.587 * rgb[1] + 0.114 * rgb[2]) / 255
        
        # Retorna 'claro' se a luminosidade for maior que 0.5, senão 'escuro'
        return 'claro' if luminosidade > 0.5 else 'escuro'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        card = self.get_object()
        empresa = card.empresa
        avaliacoes = card.avaliacoes.all()
        cor_de_fundo = card.cor
        luminosidade = self.luminosidade(cor_de_fundo)
        card_atributos = card.__dict__
        anuncios = empresa.anuncios.all()
        avaliacao_valor = 0
        avaliacoes_qtd = 0
        produtos = []
        servicos = []
        portfolios = []
        promocoes = []
        cursos = []
        has_catalogo = False
        for anuncio in anuncios:
            if anuncio.tipo.nome == 'Produto':
                produtos.append(anuncio)
                has_catalogo = True
            if anuncio.tipo.nome == 'Serviço':
                servicos.append(anuncio)
                has_catalogo = True
            if anuncio.tipo.nome == 'Promoção':
                promocoes.append(anuncio)
                has_catalogo = True
            if anuncio.tipo.nome == 'Portfólio':
                portfolios.append(anuncio)
                has_catalogo = True
            if anuncio.tipo.nome == 'Curso':
                cursos.append(anuncio)
                has_catalogo = True

        nomes_atributos = ['telefone', 'vcf','endereco', 
                           'site', 'instagram', 'whatsapp', 'tik_tok', 
                           'linkedin', 'facebook', 'youtube',
                           ]
        atributos = ['email']
        for atributo in card_atributos:
            if atributo in nomes_atributos and card.__getattribute__(atributo):
                    atributos.append(atributo)
        if has_catalogo:
            atributos.append('catalogo')
        linhas = self.chunk_list(atributos)

        if avaliacoes:
            for avaliacao in avaliacoes:
                avaliacao_valor += avaliacao.valor
                avaliacoes_qtd += 1
        else:
            avaliacoes_qtd = 1
        
        context['range'] = range(1, 6)
        context['avaliacao'] = math.ceil(avaliacao_valor / avaliacoes_qtd)   
        context['produtos'] = produtos
        context['servicos'] = servicos
        context['portfolios'] = portfolios
        context['promocoes'] = promocoes
        context['cursos'] = cursos
        context['atributos'] = atributos
        context['linhas'] = linhas
        if luminosidade == 'escuro':
            context['cor_da_fonte'] = '#fff'
        else:
            context['cor_da_fonte'] = '#212529'

        return context


class ExcluirCardPF(LoginRequiredMixin, SuccessMessageMixin, DeleteView):

    model = Card
    success_message = 'Cartão apagado com sucesso!'
    template_name = 'cards/modelos.html'

    def get_success_url(self):
        return reverse('core:modelos')

    def post(self, request, *args, **kwargs):
        card = self.get_object()
        empresa = card.empresa
        anuncios = Anuncio.objects.filter(empresa=empresa)
        if anuncios:
            for anuncio in anuncios:
                anuncio.delete()

        # Apagar arquivos associados ao conteúdo
        path = os.path.join(settings.MEDIA_ROOT, self.request.user.id.hex)
        try:
            shutil.rmtree(path)
        except FileNotFoundError as err:
            print(err)

        return super().post(request, *args, **kwargs)



# ANUNCIOS PF
class CriarAnuncioPF(LoginRequiredMixin, UserPassesTestMixin, SuccessMessageMixin, CreateView):
    model = Anuncio
    form_class = AnuncioEditForm
    template_name = 'cards/criar-anuncio-pf.html'
    success_message = 'Anúncio criado com sucesso!'

    def test_func(self):
        self.comprou_ads = False
        self.criou_card = False
        usuario = self.request.user
        empresa = usuario.empresas.first()
        cards = empresa.cards.all()
        anuncios = empresa.anuncios.all()
        ads = usuario.ads.all()

        if ads:
            for ad in ads:
                if ad.status == 'paid':
                    self.comprou_ads = True

        if cards:
            self.criou_card = True

        if self.criou_card and self.comprou_ads and len(anuncios) < 10:
            return True

    def handle_no_permission(self):
        if not self.criou_card:
            return render(self.request, 'cards/permissao-negada-nao-criou-cartao.html', status=403)
        if not self.comprou_ads:
            return render(self.request, 'cards/permissao-negada-nao-comprou-anuncio.html', status=403)
        else:
            return render(self.request, 'cards/permissao-negada-anuncios-criados-atingiu-limite.html', status=403)

    def get_success_url(self):
        usuario = self.request.user
        card = usuario.cards.first()
        empresa = usuario.empresas.first()
        return reverse_lazy('core:listar-anuncio-pf', kwargs={'empresa': empresa.slug})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        usuario = self.request.user
        empresa = usuario.empresas.first()
        card = usuario.cards.first()
        anuncios = empresa.anuncios.all()
        quantidade_anuncios = len(anuncios)
        context['card'] = card
        context['anuncios'] = anuncios
        context['quantidade_anuncios'] = quantidade_anuncios
        return context

    def form_valid(self, form):
        anuncio = form.save(commit=False)
        usuario = self.request.user
        empresa = usuario.empresas.first()
        anuncio.empresa = empresa
        img = form.cleaned_data['img']
        largura_desejada = 300
        altura_desejada = 300
        # tamanho_maximo = 1 * 1024 * 1024

        if img:
            if not img.name.endswith(('.jpg', '.jpeg', '.png', '.JPG', '.JPEG', '.PNG')):
                messages.error(self.request, 'Apenas arquivos JPG ou PNG são permitidos.')
                return self.form_invalid(form)

            extensao = slugify(os.path.splitext(img.name)[1])
            if extensao == 'jpg' or extensao == 'JPG':
                extensao = 'jpeg'

            # Redimensiona imagem se existe
            img_redimensionada, buffer_img = resize_image(img, largura_desejada, altura_desejada)

            # Cria in_memory_file para possibilitar associar ao anuncio.img antes de salvar
            if img_redimensionada and buffer_img:
                in_memory_file = create_in_memory_file(buffer_img, img.name)
                anuncio.img = in_memory_file

            # Valida tamanho da imagem
            # if img.size > tamanho_maximo:
            #     messages.error(self.request, 'O arquivo excede o tamanho máximo permitido 1 MB.')
            #     return self.form_invalid(form)

        anuncio.save()

        return super().form_valid(form)

    def form_invalid(self, form):
        for field, errors in form.errors.items():
            for error in errors:
                messages.error(self.request, f"{field}: {error}")
        return super().form_invalid(form)


class ListarAnuncioPF(LoginRequiredMixin, UserPassesTestMixin, SuccessMessageMixin, ListView):
    model = Anuncio
    success_url = '.'
    template_name = 'cards/listar-anuncio-pf.html'

    def test_func(self):
        self.comprou_ads = False
        self.criou_card = False
        usuario = self.request.user
        empresa = usuario.empresas.first()
        cards = empresa.cards.all()
        ads = usuario.ads.all()

        if ads:
            for ad in ads:
                if ad.status == 'paid':
                    self.comprou_ads = True

        if cards:
            self.criou_card = True

        if self.criou_card and self.comprou_ads:
            return True

    def handle_no_permission(self):
        if not self.criou_card:
            return render(self.request, 'cards/permissao-negada-nao-criou-cartao.html', status=403)
        if not self.comprou_ads:
            return render(self.request, 'cards/permissao-negada-nao-comprou-anuncio.html', status=403)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        usuario = self.request.user
        empresa = usuario.empresas.first()
        card = usuario.cards.first()
        anuncios = empresa.anuncios.all()
        quantidade_anuncios = len(anuncios)
        context['card'] = card
        context['anuncios'] = anuncios
        context['quantidade_anuncios'] = quantidade_anuncios
        return context


class EditarAnuncioPF(LoginRequiredMixin, UserPassesTestMixin, SuccessMessageMixin, UpdateView):
    model = Anuncio
    form_class = AnuncioEditForm
    template_name = 'cards/editar-anuncio-pf.html'
    success_message = 'Anúncio atualizado com sucesso!'

    def test_func(self):
        self.comprou_ads = False
        self.criou_card = False
        usuario = self.request.user
        empresa = usuario.empresas.first()
        cards = empresa.cards.all()
        ads = usuario.ads.all()

        if ads:
            for ad in self.ads:
                if ad.status == 'paid':
                    self.comprou_ads = True

        if cards:
            self.criou_card = True

        if self.criou_card and self.comprou_ads:
            return True

    def handle_no_permission(self):
        if not self.criou_card:
            return render(self.request, 'cards/permissao-negada-nao-criou-cartao.html', status=403)
        if not self.comprou_ads:
            return render(self.request, 'cards/permissao-negada-nao-comprou-anuncio.html', status=403)

    def get_success_url(self):
        usuario = self.request.user
        card = usuario.cards.first()
        empresa = usuario.empresas.first()
        return reverse_lazy('core:listar-anuncio-pf', kwargs={'empresa': empresa.slug})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        usuario = self.request.user
        empresa = usuario.empresas.first()
        card = usuario.cards.first()
        anuncios = empresa.anuncios.all()
        quantidade_anuncios = len(anuncios)
        context['card'] = card
        context['anuncios'] = anuncios
        context['quantidade_anuncios'] = quantidade_anuncios
        return context

    def form_valid(self, form):
        anuncio = form.save(commit=False)
        usuario = self.request.user
        empresa = usuario.empresas.first()
        anuncio.empresa = empresa
        img = form.cleaned_data['img']
        largura_desejada = 300
        altura_desejada = 300
        # tamanho_maximo = 1 * 1024 * 1024

        if 'img' in form.changed_data:

            if not img.name.endswith(('.jpg', '.jpeg', '.png', '.JPG', '.JPEG', '.PNG')):
                messages.error(self.request, 'Apenas arquivos JPG ou PNG são permitidos.')
                return self.form_invalid(form)

            # APAGA IMGAGEM ANTIGA
            try:
                anuncio_anterior = Anuncio.objects.get(id=self.kwargs['pk'])
                imagem_anterior = anuncio_anterior.img
                os.remove(imagem_anterior.path)
                anuncio_anterior.img.delete()
            except FileNotFoundError as err:
                print(err)
            
            extensao = slugify(os.path.splitext(img.name)[1])
            if extensao == 'jpg' or extensao == 'JPG':
                extensao = 'jpeg'

            # Redimensiona imagem se existe
            img_redimensionada, buffer_img = resize_image(img, largura_desejada, altura_desejada)

            # Cria in_memory_file para possibilitar associar ao anuncio.img antes de salvar
            if img_redimensionada and buffer_img:
                in_memory_file = create_in_memory_file(buffer_img, img.name)
                anuncio.img.save(name=img.name, content=in_memory_file)

            # Valida tamanho da imagem
            # if img.size > tamanho_maximo:
            #     messages.error(self.request, 'O arquivo excede o tamanho máximo permitido 1 MB.')
            #     return self.form_invalid(form)
            

        anuncio.save()

        return super().form_valid(form)

    def form_invalid(self, form):
        for field, errors in form.errors.items():
            for error in errors:
                messages.error(self.request, f"{field}: {error}")
        return super().form_invalid(form)


class ExcluirAnuncioPF(LoginRequiredMixin, SuccessMessageMixin, DeleteView):
    model = Anuncio
    template_name = 'cards/criar-anuncio-pf.html'

    def get_success_url(self):
        usuario = self.request.user
        empresa = usuario.empresas.first()
        return reverse('core:criar-anuncio-pf', kwargs={'empresa': empresa.slug})

    def post(self, request, *args, **kwargs):
        anuncio = Anuncio.objects.filter(id=self.kwargs['pk']).first()
        path = anuncio.img.path

        # APAGA ARQUIVOS ANTIGOS E EXCLUI REGISTRO DO BANCO
        try:
            anuncio.delete()
            os.remove(path)
            messages.success(self.request, 'Anúncio excluído com sucesso!')
        except FileNotFoundError as err:
            print(err)
            messages.error(self.request, 'Erro ao deletar o anúncio: arquivo não encontrado.')

        return HttpResponseRedirect(self.get_success_url())


# RELATORIO PF
class RelatorioPF(LoginRequiredMixin, UserPassesTestMixin, SuccessMessageMixin, TemplateView):
    template_name = 'cards/relatorio-pf.html'

    def test_func(self):
        relatorios_comprados = self.request.user.relatorios.all()
        for relatorio in relatorios_comprados:
            if relatorio.status == 'paid':
                return True

    def handle_no_permission(self):
        return render(self.request, 'cards/permissao-negada-nao-comprou-relatorio.html', status=403)

    def get_success_url(self, card):
        empresa = self.request.user.empresas.first()
        return reverse('core:detalhar-card-pf', kwargs={'empresa': empresa.slug, 'slug': card.slug})

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
        pagina = f'/{self.request.user.empresas.first().slug}/relatorio-pf/{card.slug}/'
        data_city = analytics_data_api.run_report_city(property_id=None, pagina=pagina)
        data_session_origin = analytics_data_api.run_report_session_origin(property_id=None, pagina=pagina)

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


# CARDS PJ
class CriarCardPJ(LoginRequiredMixin, UserPassesTestMixin, SuccessMessageMixin, CreateView):
    model = Card
    form_class = CardEditFormPJ
    template_name = 'cards/criar-card-pj.html'
    success_message = 'Cartão criado com sucesso.'

    def test_func(self):
        self.comprou_cartao_pj = False
        self.assinatura_ativa = False
        self.cards_autorizados = 0
        usuario = self.request.user
        empresa = usuario.empresas.first()
        cartoes_pj = usuario.cartoespj.all()
        cards = empresa.cards.all()

        if len(cartoes_pj) > 0:
            self.comprou_cartao_pj = True
            for cartao_pj in cartoes_pj:
                if cartao_pj.status == 'paid':
                    self.assinatura_ativa = True
                    self.cards_autorizados += 1
                    
        if len(cards) < self.cards_autorizados:
            return True

    def handle_no_permission(self):
        if not self.assinatura_ativa:
            return render(self.request, 'cards/permissao-negada-nao-comprou-cartao-pj.html', status=403)
        else:
            return render(self.request, 'cards/permissao-negada-cartoes-criados-atingiu-limite.html', status=403)

    def get_success_url(self, card):
        empresa = self.request.user.empresas.first()
        return reverse('core:detalhar-card-pj', kwargs={'empresa': empresa.slug, 'slug': card.slug})

    def get_context_data(self, form=None):
        context = super().get_context_data()
        modelo = self.request.GET.get('modelo')
        estados = Estado.objects.all()
        municipios = Municipio.objects.all()
        categorias = Categoria.objects.all()
        subcategorias = Subcategoria.objects.all()
        user = self.request.user
        try:
            card = Card.objects.filter(proprietario=user)
            context['card'] = card
        except ObjectDoesNotExist as err:
            print(err)
            card = None
        context['modelo'] = modelo
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
        
        first_name = form.cleaned_data['first_name']
        last_name = form.cleaned_data['last_name']
        email = form.cleaned_data['email']
        username = slugify(f'{first_name}-{last_name}')

        password = make_password('(LaXX)((4s@Ls$lLt2')

        if email:
            email_existente = Usuario.objects.filter(email=email)
            if email_existente:
                messages.error(self.request, 'Já existe um usuário com o email informado.')
                return self.form_invalid(form)

        usuario = Usuario.objects.create(first_name=first_name, last_name=last_name, is_active=True, email=email, username=username, password=password)

        proprietario = self.request.user
        card.proprietario = proprietario
        card.usuario_do_card = usuario
        pasta_usuario = card.proprietario.id.hex
        modelo = form.cleaned_data['modelo']
        empresa = self.request.user.empresas.first()
        card.empresa = empresa
        publico = form.cleaned_data['publico']
        site = form.cleaned_data['site']
        cod_pais = form.cleaned_data['cod_pais']
        cod_pais_vcf = cod_pais.codigo
        whatsapp = form.cleaned_data['whatsapp']
        whatsapp_vcf = cleaner(cod_pais_vcf) + cleaner(whatsapp)
        facebook = form.cleaned_data['facebook']
        instagram = form.cleaned_data['instagram']
        linkedin = form.cleaned_data['linkedin']
        youtube = form.cleaned_data['youtube']
        tik_tok = form.cleaned_data['tik_tok']
        categoria = form.cleaned_data['categoria']
        subcategoria = form.cleaned_data['subcategoria']
        estado = form.cleaned_data['estado']
        municipio = form.cleaned_data['municipio']
        endereco = form.cleaned_data['endereco']
        img_perfil = form.cleaned_data.get('img_perfil')
        logotipo = form.cleaned_data.get('logotipo')
        largura_desejada = 500
        altura_desejada = 500
        # tamanho_maximo = 1 * 1024 * 1024  # 1 MB em bytes

        if img_perfil:

            if not img_perfil.name.endswith(('.jpg', '.jpeg', '.png', '.JPG', '.JPEG', '.PNG')):
                messages.error(self.request, 'Apenas arquivos JPG ou PNG são permitidos.')
                return self.form_invalid(form)

            extensao = slugify(os.path.splitext(img_perfil.name)[1])
            if extensao == 'jpg' or extensao == 'JPG':
                extensao = 'jpeg'

            # Redimensiona img_perfil se existe
            img_perfil_redimensionado, buffer_img_perfil = resize_image(img_perfil, largura_desejada, altura_desejada)

            # Cria in_memory_file para possibilitar associar ao card.img_perfil antes de salvar
            if img_perfil_redimensionado and buffer_img_perfil:
                in_memory_file = create_in_memory_file(buffer_img_perfil, img_perfil.name)
                card.img_perfil = in_memory_file

            # Valida tamanho de arquivo
            # if img_perfil.size > tamanho_maximo:
            #     messages.error(
            #         self.request, 'O arquivo de foto excede o tamanho máximo permitido 1 MB.')
            #     return self.form_invalid(form)


        if logotipo:

            if not logotipo.name.endswith(('.jpg', '.jpeg', '.png', '.JPG', '.JPEG', '.PNG')):
                messages.error(self.request, 'Apenas arquivos JPG ou PNG são permitidos.')
                return self.form_invalid(form)

            extensao = slugify(os.path.splitext(logotipo.name)[1])
            if extensao == 'jpg' or extensao == 'JPG':
                extensao = 'jpeg'

            # Redimensiona logotipo se existe
            logotipo_redimensionado, buffer_logotipo = resize_image(logotipo, largura_desejada, altura_desejada)

            # Cria in_memory_file para possibilitar associar ao card.logotipo antes de salvar
            if logotipo_redimensionado and buffer_logotipo:
                in_memory_file = create_in_memory_file(buffer_logotipo, logotipo.name)
                card.logotipo = in_memory_file

            # Valida tamanho de arquivos
            # tamanho_maximo = 1 * 1024 * 1024  # 1 MB em bytes
            # if logotipo.size > tamanho_maximo:
            #     messages.error(
            #         self.request, 'O arquivo de logotipo excede o tamanho máximo permitido 1 MB.')
            #     return self.form_invalid(form)


        #CRIA VCF
        vcf_content = make_vcf(first_name, last_name, empresa,
                               whatsapp, site, endereco, estado, municipio, email)

        vcf_name = f'{uuid.uuid4().hex}.vcf'
        content = '\n'.join([str(line) for line in vcf_content])
        vcf_file = ContentFile(content)
        card.vcf.save(vcf_name, vcf_file)

        # CRIA QRCODE
        self.gera_qrcode(card)

        return HttpResponseRedirect(self.get_success_url(card))

    def form_invalid(self, form):
        response = super().form_invalid(form)
        for field, errors in form.errors.items():
            for error in errors:
                messages.error(self.request, f"{field}: {error}")

        modelo = self.request.POST.get('modelo', '')
        if modelo:
            response.context_data['modelo'] = modelo
        return response


class ListarCardPJ(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = Card
    template_name = 'cards/listar-card-pj.html'
    context_object_name = 'cards'

    def test_func(self):
        usuario = self.request.user
        empresa = usuario.empresas.first()
        cartoes_pj = usuario.cartoespj.all()

        if cartoes_pj:
            for cartao_pj in cartoes_pj:
                if cartao_pj.status == 'paid':
                    return True
                    

    def handle_no_permission(self):
        return render(self.request, 'cards/permissao-negada-nao-comprou-cartao-pj.html', status=403)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        empresa = Empresa.objects.get(slug=self.kwargs['empresa'])
        ua = self.request.META['HTTP_USER_AGENT']
        cards = Card.objects.filter(empresa=empresa)
        context['cards'] = cards
        context['empresa'] = empresa
        return context


class DetalharCardPJ(DetailView):
    model = Card

    def chunk_list(self, lst):
        if len(lst) <= 4:
            return [lst]
        elif len(lst) in [5, 6]:
            return [lst[:3], lst[3:]]
        elif len(lst) in [7, 8]:
            return [lst[:4], lst[4:]]
        elif len(lst) == 9:
            return [lst[:3], lst[3:6], lst[6:]]
        else:
            return [lst[:4], lst[4:8], lst[8:]]

    def get_template_names(self):
        template_name = super().get_template_names()
        modelo = self.get_object().modelo
        template_name = [f'cards/modelo-{modelo}.html']
        return template_name

    def luminosidade(self, cor_de_fundo):
        # Converte a cor hexadecimal para RGB
        cor = cor_de_fundo.lstrip('#')
        rgb = tuple(int(cor[i:i+2], 16) for i in (0, 2, 4))
        
        # Fórmula de luminosidade para determinar o contraste
        luminosidade = (0.299 * rgb[0] + 0.587 * rgb[1] + 0.114 * rgb[2]) / 255
        
        # Retorna 'claro' se a luminosidade for maior que 0.5, senão 'escuro'
        return 'claro' if luminosidade > 0.5 else 'escuro'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        card = self.get_object()
        empresa = card.empresa
        avaliacoes = card.avaliacoes.all()
        cor_de_fundo = card.cor
        luminosidade = self.luminosidade(cor_de_fundo)
        card_atributos = card.__dict__
        anuncios = empresa.anuncios.all()
        avaliacao_valor = 0
        avaliacoes_qtd = 0
        produtos = []
        servicos = []
        portfolios = []
        promocoes = []
        cursos = []
        has_catalogo = False
        for anuncio in anuncios:
            if anuncio.tipo.nome == 'Produto':
                produtos.append(anuncio)
                has_catalogo = True
            if anuncio.tipo.nome == 'Serviço':
                servicos.append(anuncio)
                has_catalogo = True
            if anuncio.tipo.nome == 'Promoção':
                promocoes.append(anuncio)
                has_catalogo = True
            if anuncio.tipo.nome == 'Portfólio':
                portfolios.append(anuncio)
                has_catalogo = True
            if anuncio.tipo.nome == 'Curso':
                cursos.append(anuncio)
                has_catalogo = True

        nomes_atributos = ['telefone', 'vcf','endereco', 
                           'site', 'instagram', 'whatsapp', 'tik_tok', 
                           'linkedin', 'facebook', 'youtube',
                           ]
        atributos = ['email']
        for atributo in card_atributos:
            if atributo in nomes_atributos and card.__getattribute__(atributo):
                    atributos.append(atributo)
        if has_catalogo:
            atributos.append('catalogo')
        linhas = self.chunk_list(atributos)

        if avaliacoes:
            for avaliacao in avaliacoes:
                avaliacao_valor += avaliacao.valor
                avaliacoes_qtd += 1
        else:
            avaliacoes_qtd = 1

        context['range'] = range(1, 6)
        context['avaliacao'] = math.ceil(avaliacao_valor / avaliacoes_qtd) 
        context['produtos'] = produtos
        context['servicos'] = servicos
        context['portfolios'] = portfolios
        context['promocoes'] = promocoes
        context['cursos'] = cursos
        context['atributos'] = atributos
        context['linhas'] = linhas
        if luminosidade == 'escuro':
            context['cor_da_fonte'] = '#fff'
        else:
            context['cor_da_fonte'] = '#212529'

        return context


class EditarCardPJ(LoginRequiredMixin, UserPassesTestMixin, SuccessMessageMixin, UpdateView):
    model = Card
    form_class = CardEditFormPJ
    template_name = 'cards/editar-card-pj.html'
    success_message = 'Cartão atualizado com sucesso!'

    def test_func(self):
        self.comprou_cartao_pj = False
        self.assinatura_ativa = False
        self.criou_card = False
        usuario = self.request.user
        empresa = usuario.empresas.first()
        cartoes_pj = usuario.cartoespj.all()
        cards = empresa.cards.all()

        if len(cartoes_pj) > 0:
            self.comprou_cartao_pj = True
            for cartao_pj in cartoes_pj:
                if cartao_pj.status == 'paid':
                    self.assinatura_ativa = True
                    
        if cards:
            self.criou_card = True

        if self.assinatura_ativa and self.criou_card:
            return True

    def handle_no_permission(self):
        if not self.comprou_cartao_pj or not self.assinatura_ativa:
            return render(self.request, 'cards/permissao-negada-nao-comprou-cartao-pj.html', status=403)
        if not self.criou_card:
            return render(self.request, 'cards/permissao-negada-nao-criou-cartao.html', status=403)

    def get_success_url(self, card):
        usuario = self.request.user
        # card = Card.objects.get(usuario_do_card=user)
        empresa = usuario.empresas.first()
        return reverse('core:detalhar-card-pj', kwargs={'empresa': empresa.slug, 'slug': card.slug})

    def get_context_data(self, form=None):
       context = super().get_context_data()
       modelo = self.get_object().modelo
       estados = Estado.objects.all()
       categorias = Categoria.objects.all()
       subcategorias = Subcategoria.objects.all()
       categoria_atual = self.object.categoria
       subcategoria_atual = self.object.subcategoria
       estado_atual = self.object.estado
       municipio_atual = self.object.municipio
       empresa = self.get_object().empresa.nome_fantasia
       context['modelo'] = modelo
       context['categorias'] = categorias
       context['subcategorias'] = subcategorias
       context['estados'] = estados
       context['municipios'] = Municipio.objects.all()
       context['categoria_atual'] = categoria_atual
       context['subcategoria_atual'] = subcategoria_atual
       context['estado_atual'] = estado_atual
       context['municipio_atual'] = municipio_atual
       context['empresa'] = empresa
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

    def get_initial(self, **kwargs):
        initial = super().get_initial(**kwargs)
        card = self.get_object()
        initial['first_name'] = card.usuario_do_card.first_name
        initial['last_name'] = card.usuario_do_card.last_name
        initial['email'] = card.usuario_do_card.email
        return initial

    def form_valid(self, form):
        card = self.get_object()
        first_name = form.cleaned_data['first_name']
        last_name = form.cleaned_data['last_name']
        email = form.cleaned_data['email']
        username = slugify(f'{first_name}-{last_name}')
        usuario_do_card = card.usuario_do_card
        empresa = card.empresa
        publico = form.cleaned_data['publico']
        modelo = form.cleaned_data['modelo']
        cor = form.cleaned_data['cor']
        nome_display = form.cleaned_data['nome_display']
        site = form.cleaned_data['site']
        cargo = form.cleaned_data['cargo']
        categoria = form.cleaned_data['categoria']
        subcategoria = form.cleaned_data['subcategoria']
        estado = form.cleaned_data['estado']
        municipio = form.cleaned_data['municipio']
        endereco = form.cleaned_data['endereco']
        cod_pais = form.cleaned_data['cod_pais']
        cod_pais_vcf = cod_pais.codigo
        whatsapp = form.cleaned_data['whatsapp']
        whatsapp_vcf = cleaner(cod_pais_vcf) + cleaner(whatsapp)
        facebook = form.cleaned_data['facebook']
        instagram = form.cleaned_data['instagram']
        linkedin = form.cleaned_data['linkedin']
        youtube = form.cleaned_data['youtube']
        tik_tok = form.cleaned_data['tik_tok']
        img_perfil = self.request.FILES['img_perfil'] if 'img_perfil' in self.request.FILES else ''
        logotipo = self.request.FILES['logotipo'] if 'logotipo' in self.request.FILES else ''
        # tamanho_maximo = 1 * 1024 * 1024

        if 'email' in form.changed_data:
            email_existente = Usuario.objects.filter(email=email)
            if email_existente:
                messages.error(self.request, 'Já existe um usuário com o email informado.')
                return self.form_invalid(form)

        # VALIDA TAMANHO DE ARQUIVOS
        # if img_perfil and img_perfil.size > tamanho_maximo:
        #     messages.error(
        #         self.request, 'O arquivo de foto excede o tamanho máximo permitido 1 MB.')
        #     return self.form_invalid(form)


        # if logotipo and logotipo.size > tamanho_maximo:
        #     messages.error(
        #         self.request, 'O arquivo de logotipo excede o tamanho máximo permitido 1 MB.')
        #     return self.form_invalid(form)

        # APAGA IMGAGEM PERFIL ANTIGA
        if img_perfil:

            if not img_perfil.name.endswith(('.jpg', '.jpeg', '.png', '.JPG', '.JPEG', '.PNG')):
                messages.error(self.request, 'Apenas arquivos JPG ou PNG são permitidos.')
                return self.form_invalid(form)

            if card.img_perfil:
                try:
                    os.remove(card.img_perfil.path)
                    card.img_perfil.delete()
                except FileNotFoundError as err:
                    print(err)

            extensao = slugify(os.path.splitext(img_perfil.name)[1])
            if extensao == 'jpg' or extensao == 'JPG':
                extensao = 'jpeg'

            # Redimensiona img_perfil se existe
            img_perfil_redimensionado, buffer_img_perfil = resize_image(img_perfil, largura_desejada, altura_desejada)

            # Cria in_memory_file para possibilitar associar ao card.img_perfil antes de salvar
            if img_perfil_redimensionado and buffer_img_perfil:
                in_memory_file = create_in_memory_file(buffer_img_perfil, img_perfil.name)
                card.img_perfil.save(name=img_perfil.name, content=in_memory_file)


        if 'sem_foto' in self.request.POST:
            if card.img_perfil:
                try:
                    os.remove(card.img_perfil.path)
                    card.img_perfil.delete()
                except FileNotFoundError as err:
                    print(err)


        # APAGA LOGOTIPO ANTIGO E SALVA NOVO
        if logotipo:
            if not logotipo.name.endswith(('.jpg', '.jpeg', '.png', '.JPG', '.JPEG', '.PNG')):
                messages.error(self.request, 'Apenas arquivos JPG ou PNG são permitidos.')
                return self.form_invalid(form)

            if card.logotipo:
                try:
                    os.remove(card.logotipo.path)
                    card.logotipo.delete()
                except FileNotFoundError as err:
                    print(err)

            extensao = slugify(os.path.splitext(logotipo.name)[1])
            if extensao == 'jpg' or extensao == 'JPG':
                extensao = 'jpeg'

            # Redimensiona logotipo se existe
            logotipo_redimensionado, buffer_logotipo  = resize_image(logotipo, largura_desejada, altura_desejada)

            if logotipo_redimensionado and buffer_logotipo:
                in_memory_file = create_in_memory_file(buffer_logotipo, logotipo.name)
                card.logotipo = in_memory_file
                card.logotipo.save(name=logotipo.name, content=in_memory_file)


        if 'sem_logo' in self.request.POST:
            if card.logotipo:
                try:
                    os.remove(card.logotipo.path)
                    card.logotipo.delete()
                except FileNotFoundError as err:
                    print(err)


        # APAGA VCF ANTIGO SALVA NOVO
        if card.vcf:
            try:
                os.remove(card.vcf.path)
                card.vcf.delete()
                vcf_content = make_vcf(usuario_do_card.first_name, usuario_do_card.last_name, empresa,
                                    whatsapp_vcf, site, endereco, estado, municipio, usuario_do_card.email)

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

        usuario_do_card.email = email
        usuario_do_card.first_name = first_name
        usuario_do_card.last_name = last_name
        usuario_do_card.username = username
        usuario_do_card.save()

        card.publico = publico
        card.nome_display = nome_display
        card.slug = usuario_do_card.username
        card.cor = cor
        card.empresa = empresa
        card.site = site
        card.cargo = cargo
        card.categoria = categoria
        card.subcategoria = subcategoria
        card.estado = estado
        card.municipio = municipio
        card.cod_pais = cod_pais
        card.whatsapp = whatsapp
        card.facebook = facebook
        card.instagram = instagram
        card.linkedin = linkedin
        card.youtube = youtube
        card.tik_tok = tik_tok
        card.save()

        return HttpResponseRedirect(self.get_success_url(card))

    def form_invalid(self, form):
        for field, errors in form.errors.items():
            for error in errors:
                messages.error(self.request, f"{field}: {error}")
        return super().form_invalid(form)


class ExcluirCardPJ(LoginRequiredMixin, SuccessMessageMixin, DeleteView):

    model = Card
    success_message = 'Cartão excluído com sucesso!'

    def get_success_url(self, card):
        return reverse_lazy('core:listar-card-pj', kwargs={'empresa': card.empresa.slug})

    def post(self, request, *args, **kwargs):
        card = self.get_object()
        usuario_do_card = card.usuario_do_card

        # Apagar diretório associado ao card
        path = os.path.join(settings.MEDIA_ROOT, usuario_do_card.id.hex)
        try:
            shutil.rmtree(path)
        except FileNotFoundError as err:
            print(err)

        usuario_do_card.delete()

        return HttpResponseRedirect(self.get_success_url(card))


# ANUNCIOS PJ
class CriarAnuncioPJ(LoginRequiredMixin, UserPassesTestMixin, SuccessMessageMixin, CreateView):
    model = Anuncio
    form_class = AnuncioEditForm
    template_name = 'cards/criar-anuncio-pj.html'
    success_message = 'Anúncio criado com sucesso!'

    def test_func(self):
        self.comprou_ads = False
        self.assinatura_ativa = False
        self.criou_card = False
        usuario = self.request.user
        empresa = usuario.empresas.first()
        ads = usuario.ads.all()
        anuncios = empresa.anuncios.all()
        cards = empresa.cards.all()

        if len(ads) > 0:
            self.comprou_ads = True
            for ad in ads:
                if ad.status == 'paid':
                    self.assinatura_ativa = True

        if cards:
            self.criou_card = True

        if self.assinatura_ativa and len(anuncios) < 10 and self.criou_card:
            return True

    def handle_no_permission(self):
        if not self.comprou_cartao_pj or not self.assinatura_ativa:
            return render(self.request, 'cards/permissao-negada-nao-comprou-cartao-pj.html', status=403)
        elif not self.criou_card:
            return render(self.request, 'cards/permissao-negada-nao-criou-cartao.html', status=403)
        else:
            return render(self.request, 'cards/permissao-negada-anuncios-criados-atingiu-limite.html', status=403)

    def get_success_url(self):
        usuario = self.request.user
        card = usuario.cards.first()
        empresa = usuario.empresas.first()
        return reverse_lazy('core:listar-anuncio-pj', kwargs={'empresa': empresa.slug})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        usuario = self.request.user
        empresa = usuario.empresas.first()
        card = usuario.cards.first()
        anuncios = Anuncio.objects.filter(empresa=empresa)
        quantidade_anuncios = len(anuncios)
        context['card'] = card
        context['anuncios'] = anuncios
        context['quantidade_anuncios'] = quantidade_anuncios
        return context

    def form_valid(self, form):
        anuncio = form.save(commit=False)
        usuario = self.request.user
        empresa = usuario.empresas.first()
        anuncio.empresa = empresa
        img = form.cleaned_data['img']
        largura_desejada = 300
        altura_desejada = 300
        # tamanho_maximo = 1 * 1024 * 1024

        if img:
            if not img.name.endswith(('.jpg', '.jpeg', '.png', '.JPG', '.JPEG', '.PNG')):
                messages.error(self.request, 'Apenas arquivos JPG ou PNG são permitidos.')
                return self.form_invalid(form)

            
            extensao = slugify(os.path.splitext(img.name)[1])
            if extensao == 'jpg' or extensao == 'JPG':
                extensao = 'jpeg'

            # Redimensiona imagem se existe
            img_redimensionada, buffer_img = resize_image(img, largura_desejada, altura_desejada)

            # Cria in_memory_file para possibilitar associar ao anuncio.img antes de salvar
            if img_redimensionada and buffer_img:
                in_memory_file = create_in_memory_file(buffer_img, img.name)
                anuncio.img = in_memory_file

            # Valida tamanho da imagem
            # if img.size > tamanho_maximo:
            #     messages.error(self.request, 'A imagem excede o tamanho máximo permitido de 1 MB.')
            #     return self.form_invalid(form)

        anuncio.save()

        return super().form_valid(form)

    def form_invalid(self, form):
        for field, errors in form.errors.items():
            for error in errors:
                messages.error(self.request, f"{field}: {error}")
        return super().form_invalid(form)


class ListarAnuncioPJ(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = Anuncio
    success_url = '.'
    template_name = 'cards/listar-anuncio-pj.html'

    def test_func(self):
        self.comprou_ads = False
        self.assinatura_ativa = False
        self.criou_card = False
        usuario = self.request.user
        empresa = usuario.empresas.first()
        ads = usuario.ads.all()
        anuncios = empresa.anuncios.all()
        cards = empresa.cards.all()

        if len(ads) > 0:
            self.comprou_ads = True
            for ad in ads:
                if ad.status == 'paid':
                    self.assinatura_ativa = True

        if cards:
            self.criou_card = True

        if self.assinatura_ativa and len(anuncios) < 10 and self.criou_card:
            return True


    def handle_no_permission(self):
        if not self.comprou_cartao_pj or not self.assinatura_ativa:
            return render(self.request, 'cards/permissao-negada-nao-comprou-cartao-pj.html', status=403)
        if not self.criou_card:
            return render(self.request, 'cards/permissao-negada-nao-criou-cartao.html', status=403)


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        usuario = self.request.user
        empresa = usuario.empresas.first()
        card = usuario.cards.first()
        anuncios = Anuncio.objects.filter(empresa=empresa)
        context['card'] = card
        context['anuncios'] = anuncios
        return context


class EditarAnuncioPJ(LoginRequiredMixin, UserPassesTestMixin, SuccessMessageMixin, UpdateView):
    model = Anuncio
    form_class = AnuncioEditForm
    template_name = 'cards/editar-anuncio-pj.html'
    success_message = 'Anúncio atualizado com sucesso!'

    def test_func(self):
        self.comprou_ads = False
        self.assinatura_ativa = False
        self.criou_card = False
        usuario = self.request.user
        empresa = usuario.empresas.first()
        ads = usuario.ads.all()
        anuncios = empresa.anuncios.all()
        cards = empresa.cards.all()

        if len(ads) > 0:
            self.comprou_ads = True
            for ad in ads:
                if ad.status == 'paid':
                    self.assinatura_ativa = True

        if cards:
            self.criou_card = True

        if self.assinatura_ativa and len(anuncios) < 10 and self.criou_card:
            return True

    def handle_no_permission(self):
        if not self.comprou_cartao_pj or not self.assinatura_ativa:
            return render(self.request, 'cards/permissao-negada-nao-comprou-cartao-pj.html', status=403)
        if not self.criou_card:
            return render(self.request, 'cards/permissao-negada-nao-criou-cartao.html', status=403)

    def get_success_url(self):
        usuario = self.request.user
        card = usuario.cards.first()
        empresa = usuario.empresas.first()
        return reverse_lazy('core:listar-anuncio-pj', kwargs={'empresa': empresa.slug})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        usuario = self.request.user
        empresa = usuario.empresas.first()
        card = usuario.cards.first()
        anuncios = empresa.anuncios.all()
        quantidade_anuncios = len(anuncios)
        context['empresa'] = empresa
        context['card'] = card
        context['anuncios'] = anuncios
        context['quantidade_anuncios'] = quantidade_anuncios
        return context

    def form_valid(self, form):
        anuncio = form.save(commit=False)
        usuario = self.request.user
        empresa = usuario.empresas.first()
        anuncio.empresa = empresa
        img = form.cleaned_data['img']
        largura_desejada = 300
        altura_desejada = 300
        # tamanho_maximo = 1 * 1024 * 1024

        if 'img' in form.changed_data:

            if not img.name.endswith(('.jpg', '.jpeg', '.png', '.JPG', '.JPEG', '.PNG')):
                messages.error(self.request, 'Apenas arquivos JPG ou PNG são permitidos.')
                return self.form_invalid(form)

            # APAGA IMGAGEM ANTIGA
            try:
                anuncio_anterior = Anuncio.objects.get(id=self.kwargs['pk'])
                imagem_anterior = anuncio_anterior.img
                os.remove(imagem_anterior.path)
                anuncio_anterior.img.delete()
            except FileNotFoundError as err:
                print(err)
            
            extensao = slugify(os.path.splitext(img.name)[1])
            if extensao == 'jpg' or extensao == 'JPG':
                extensao = 'jpeg'

            # Redimensiona imagem se existe
            img_redimensionada, buffer_img = resize_image(img, largura_desejada, altura_desejada)

            # Cria in_memory_file para possibilitar associar ao anuncio.img antes de salvar
            if img_redimensionada and buffer_img:
                in_memory_file = create_in_memory_file(buffer_img, img.name)
                anuncio.img.save(name=img.name, content=in_memory_file)

            # Valida tamanho da imagem
            # if img.size > tamanho_maximo:
            #     messages.error(self.request, 'O arquivo excede o tamanho máximo permitido 1 MB.')
            #     return self.form_invalid(form)

        anuncio.save()

        return super().form_valid(form)

    def form_invalid(self, form):
        for field, errors in form.errors.items():
            for error in errors:
                messages.error(self.request, f"{field}: {error}")
        return super().form_invalid(form)


class ExcluirAnuncioPJ(LoginRequiredMixin, SuccessMessageMixin, DeleteView):
    model = Anuncio
    template_name = 'cards/listar-anuncio-pj.html'
    success_message = 'Anúncio excluído com sucesso!'
    success_url = '.'

    def get_success_url(self):
        usuario = self.request.user
        empresa = usuario.empresas.first()
        return reverse('core:listar-anuncio-pj', kwargs={'empresa': empresa.slug})

    def post(self, request, *args, **kwargs):
        anuncio = Anuncio.objects.filter(id=self.kwargs['pk']).first()
        path = anuncio.img.path

        # APAGA ARQUIVOS ANTIGOS E EXCLUI REGISTRO DO BANCO
        try:
            anuncio.delete()
            os.remove(path)
        except FileNotFoundError as err:
            print(err)

        return HttpResponseRedirect(self.get_success_url())


# RELATORIO PJ
class RelatorioPJ(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    template_name = 'cards/relatorio-pj.html'

    def test_func(self):
        self.comprou_relatorio = False
        self.assinatura_ativa = False
        self.criou_card = False
        usuario = self.request.user
        empresa = usuario.empresas.first()
        relatorios = usuario.relatorios.all()
        cards = empresa.cards.all()

        if len(relatorios) > 0:
            self.comprou_relatorio = True
            for relatorio in relatorios:
                if relatorio.status == 'paid':
                    self.assinatura_ativa = True
                    
        if cards:
            self.criou_card = True

        if self.assinatura_ativa and self.criou_card:
            return True

    def handle_no_permission(self):
        return render(self.request, 'cards/permissao-negada-nao-comprou-cartao-pj.html', status=403)


    def process_request(self):
        self.request.mobile = False
        if self.request.META['HTTP_USER_AGENT']:
            user_agent = self.request.META['HTTP_USER_AGENT']
            b = reg_b.search(user_agent)
            v = reg_v.search(user_agent[0:4])
            if b or v:
                return True


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.process_request():
            context['mobile'] = True
        empresa = Empresa.objects.get(slug=self.kwargs['empresa'])
        cards = Card.objects.filter(empresa=empresa)
        paginas = [f'/{empresa.slug}/relatorio-pj/{card.slug}/' for card in cards]
        # data_city = analytics_data_api.run_report_city(property_id=None, pagina=paginas)
        # data_session_origin = analytics_data_api.run_report_session_origin(property_id=None, pagina=pagina)
        data_page_path = analytics_data_api.run_report_page_path(property_id=None, pagina=paginas)
        data_source_traffic = analytics_data_api.run_report_source_traffic(property_id=None, pagina=paginas)

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
