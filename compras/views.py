import json, os, requests
import hmac
import hashlib
import stripe
import shutil
from datetime import datetime
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse, HttpResponseBadRequest
from django.urls import reverse, reverse_lazy
from django.conf import settings
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.utils.decorators import method_decorator
from django.db.utils import DatabaseError, IntegrityError, OperationalError
from django.shortcuts import render, redirect
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.views.generic.base import TemplateResponseMixin
from django.views.generic.edit import DeletionMixin
from django.views.generic import View, CreateView, UpdateView, TemplateView
from django.http import JsonResponse
from .models import Relatorio, Ad, CartaoPF, CartaoPJ
from cards.views import CriarCardPF
from usuarios.models import Usuario

stripe.api_key = settings.STRIPE_SECRET_KEY


@method_decorator(csrf_exempt, name='dispatch')
class ComprarRelatorio(LoginRequiredMixin, UserPassesTestMixin, SuccessMessageMixin, View):

    def test_func(self):
        # Verifica se já comprou um Cartão PF
        cartoes = self.request.user.cartoespf.all()
        cards = self.request.user.cards.all()
        for cartao in cartoes:
            if cartao.status == 'paid':
                return True


    def handle_no_permission(self):
            return render(self.request, 'cards/permissao-negada-nao-comprou-cartao-pf.html', status=403)


    def get(self, request, *args, **kwargs):
        context = {}
        usuario = self.request.user
        email_usuario = usuario.email
        first_name = usuario.first_name
        last_name = usuario.last_name
        compra = usuario.relatorios.last()
        card = usuario.cards.all().first()
        context['usuario'] = usuario
        context['card'] = card
        context['compra'] = compra
        context['email_usuario'] = email_usuario
        return render(request, 'compras/comprar-relatorio.html', context=context)


# @method_decorator(csrf_exempt, name='dispatch')
# class CancelarRelatorio(LoginRequiredMixin, SuccessMessageMixin, TemplateView):

#     template_name = 'usuarios/minha-conta.html'

#     def render_to_response(self, context, **response_kwargs):
#         response_kwargs.setdefault('content_type', self.content_type)
#         return self.response_class(request=self.request, template=self.get_template_names(), context=context, using=self.template_engine, **response_kwargs)

#     def get_context_data(self, **kwargs):
#         context = super().get_context_data()
#         context['relatorios'] = self.request.user.relatorios.all()
#         return context

#     def get(self, request, *args, **kwargs):    
#         usuario = self.request.user
#         relatorio = Relatorio.objects.get(id=self.kwargs['pk'])
#         assinatura_id = relatorio.assinatura_id
#         access_token = settings.MERCADOPAGO_ACCESS_TOKEN_RELATORIO

#         # Defina a URL da API do MercadoPago
#         url = f'https://api.mercadopago.com/preapproval/{assinatura_id}'

#         # Defina o cabeçalho com o token de acesso e o tipo de conteúdo
#         headers = {
#             'Authorization': f'Bearer {access_token}',
#             'Content-Type': 'application/json'
#         }

#         # Defina os dados da solicitação em formato JSON
#         data = {
#             "status": "cancelled",
#         }

#         # Faça a solicitação PUT para a API do MercadoPago
#         response = requests.put(url, json=data, headers=headers)

#         # Verifique se a solicitação foi bem-sucedida
#         if response.status_code == 200:
#             data = response.json()
#             context = self.get_context_data(**kwargs)
#             formato_da_string = "%Y-%m-%dT%H:%M:%S.%f%z"
#             relatorio.status = data['status']
#             relatorio.last_modified = datetime.strptime(data['last_modified'], formato_da_string)
#             relatorio.save()
#             messages.success(self.request, 'Assinatura cancelada com sucesso!')
#             return self.render_to_response(context=context)
#         else:
#             # Lidar com erros de solicitação, se necessário
#             error_message = response.text
#             return JsonResponse({'error': error_message}, status=response.status_code)


# @method_decorator(csrf_exempt, name='dispatch')
# class AtualizarCartaoRelatorio(LoginRequiredMixin, SuccessMessageMixin, View):


#     def get(self, request, *args, **kwargs):
#         usuario = self.request.user
#         relatorio = Relatorio.objects.get(id=self.kwargs['pk'])
#         assinatura_id = relatorio.assinatura_id
#         pk = relatorio.id
#         card = usuario.cards.all().last()
#         contexto = {'usuario': usuario, 'pk': pk, 'card': card}
#         return render(request, 'compras/atualizar-cartao-relatorio.html', contexto)

#     def post(self, request, *args, **kwargs):
#         usuario = self.request.user
#         relatorio = Relatorio.objects.get(id=self.kwargs['pk'])
#         assinatura_id = relatorio.assinatura_id
#         access_token = settings.MERCADOPAGO_ACCESS_TOKEN_RELATORIO
#         form_data = json.loads(self.request.body.decode('utf-8'))

#         # Defina a URL da API do MercadoPago
#         url = f'https://api.mercadopago.com/preapproval/{assinatura_id}'

#         # Defina o cabeçalho com o token de acesso e o tipo de conteúdo
#         headers = {
#             'Authorization': f'Bearer {access_token}',
#             'Content-Type': 'application/json'
#         }

#         # Defina os dados da solicitação em formato JSON
#         data = {
#             "reason": "Plano individual",
#             "back_url": "https://meucontato.pythonanywhere.com",
#             "auto_recurring": {
#                 "transaction_amount": 9.90,
#                 "currency_id": "BRL"
#             },
#             "card_token_id": form_data.get('token'),
#             "status": "authorized",
#         }

#         # Faça a solicitação POST para a API do MercadoPago
#         response = requests.put(url, json=data, headers=headers)

#         # Verifique se a solicitação foi bem-sucedida
#         if response.status_code == 200:
            
#             mensagem = 'Cartão atualizado com sucesso!'
#             messages.success(self.request, mensagem)
#             response_data = {
#                 'status_code': response.status_code,
#                 'message': mensagem,
#             }
#             return JsonResponse(response_data, status=response.status_code)
#         else:
#             # Lidar com erros de solicitação, se necessário
#             error_message = response.text
#             return JsonResponse({'error': error_message}, status=response.status_code)


@method_decorator(csrf_exempt, name='dispatch')
class ComprarCartaoPF(LoginRequiredMixin, SuccessMessageMixin, View):


    def get(self, request, *args, **kwargs):
        context = {}
        usuario = self.request.user
        email_usuario = usuario.email

        try:
            perfil = usuario.perfil
        except:
            return redirect(reverse_lazy('usuarios:perfil-pf'))

        comprou_cartao_pf = False
        cartoes_pf = usuario.cartoespf.all()
        for cartao_pf in cartoes_pf:
            if cartao_pf.status == 'paid':
                comprou_cartao_pf = True

        card = usuario.cards.all().first()
        context['email_usuario'] = email_usuario
        context['comprou_cartao_pf'] = comprou_cartao_pf
        context['card'] = card
        return render(request, 'compras/comprar-cartao-pf.html', context)


@method_decorator(csrf_exempt, name='dispatch')
class ComprarAnuncio(LoginRequiredMixin, UserPassesTestMixin, SuccessMessageMixin, View):

    def test_func(self):
        # Verifica se já comprou um Cartão PF
        cartoes = self.request.user.cartoespf.all()
        for cartao in cartoes:
            if cartao.status == 'paid':
                return True

    def handle_no_permission(self):
        return render(self.request, 'cards/permissao-negada-nao-comprou-cartao-pf.html', status=403)

    def get(self, request, *args, **kwargs):
        context = {}
        usuario = self.request.user
        email_usuario = usuario.email
        empresa = usuario.empresas.first()
        comprou_ads = usuario.ads.last()
        card = usuario.cards.all().first()
        anuncios = empresa.anuncios.all()
        context['email_usuario'] = email_usuario
        context['empresa'] = empresa
        context['comprou_ads'] = comprou_ads
        context['card'] = card
        context['anuncios'] = anuncios
        return render(request, 'compras/comprar-anuncio.html', context)


@method_decorator(csrf_exempt, name='dispatch')
class ComprarCartaoPJ(LoginRequiredMixin, UserPassesTestMixin, SuccessMessageMixin, View):

    def test_func(self):
        # Verifica se já comprou um Cartão PF
        cartoes = self.request.user.cartoespf.all()
        if not cartoes:
            return True

    def handle_no_permission(self):
        return render(self.request, 'cards/permissao-negada-comprou-cartao-pf.html', status=403)


    def get(self, request, *args, **kwargs):
        context = {}
        usuario = self.request.user
        email_usuario = usuario.email
        comprou_cartao_pj = False
        nova_compra = request.GET.get('nova_compra')

        try:
            perfil = usuario.perfil
        except:
            return redirect(reverse_lazy('usuarios:perfil-pj'))

        cartoes_pj = usuario.cartoespj.all()
        for cartao_pj in cartoes_pj:
            if cartao_pj.status == 'paid':
                comprou_cartao_pj = True

        card = usuario.cards.all()
        context['email_usuario'] = email_usuario
        context['usuario'] = usuario
        context['card'] = card
        context['comprou_cartao_pj'] = comprou_cartao_pj
        context['nova_compra'] = nova_compra
        return render(request, 'compras/comprar-cartao-pj.html', context)



# STRIPE
@csrf_exempt
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META['HTTP_STRIPE_SIGNATURE']
    # Local
    # endpoint_secret = 'whsec_de06a86430dc9c76f4097be20ebe6fb84f596936734543fb5bcb7ffacd9fff5d'

    # Online
    endpoint_secret = 'whsec_CouEVPKqgTvMMxMcABCK5azmE5Xmdn2Y'

    try:
        event = stripe.Webhook.construct_event(payload, sig_header, endpoint_secret)
    except ValueError as e:
        # Invalid payload
        print('Error parsing payload: {}'.format(str(e)))
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        print('Error verifying webhook signature: {}'.format(str(e)))
        return HttpResponse(status=400)

    # Handle the event
    if event.type == 'checkout.session.completed':
        email_usuario = event.data.object.customer_email
        usuario = Usuario.objects.get(email=email_usuario)
        valor = event.data.object.amount_total / 100.0
        status = event.data.object.payment_status
        stripe_customer = event.data.object.customer
        if event.data.object.subscription:
            stripe_id = event.data.object.subscription
        elif event.data.object.payment_intent:
            stripe_id = event.data.object.payment_intent
        else:
            stripe_id = None

        # Cria Relatório
        if event.data.object.metadata.produto == 'relatorio':
            try:
                relatorio = Relatorio.objects.create(
                    usuario = usuario,
                    stripe_id = stripe_id,
                    valor = valor,
                    status = status,
                    stripe_customer=stripe_customer
                )
            except DatabaseError as e:
                print(f'DatabaseError {e}')

        # Cria Cartão PF
        if event.data.object.metadata.produto == 'cartao_pf':
            try:
                cartao_pf = CartaoPF.objects.create(
                    usuario = usuario,
                    stripe_id = stripe_id,
                    valor = valor,
                    status = status,
                )
            except DatabaseError as e:
                print(f'DatabaseError {e}')

        # Cria Ad
        if event.data.object.metadata.produto == 'ad':
            try:
                ad = Ad.objects.create(
                    usuario = usuario,
                    stripe_id = stripe_id,
                    valor = valor,
                    status = status,
                )
            except DatabaseError as e:
                print(f'DatabaseError {e}')

        # Cria Cartão PJ, Relatório e Ad
        if event.data.object.metadata.produto == 'cartao_pj':
            try:
                cartao_pj = CartaoPJ.objects.create(
                    usuario = usuario,
                    stripe_id = stripe_id,
                    valor = valor,
                    status = status,
                    stripe_customer=stripe_customer
                )

                relatorio = Relatorio.objects.create(
                    usuario = usuario,
                    stripe_id = stripe_id,
                    valor = 0,
                    status = status,
                    stripe_customer=stripe_customer
                )

                ad = Ad.objects.create(
                    usuario = usuario,
                    stripe_id = stripe_id,
                    valor = 0,
                    status = status,
                )                
            except DatabaseError as e:
                print(f'DatabaseError {e}')

    if event.type == 'customer.subscription.updated':
        stripe_id = event.data.object.id
        cancelamento = event.data.object.cancel_at if event.data.object.cancel_at else None
        if cancelamento:
            if event.data.object.plan.product == 'prod_QKrz38Vn9as8Ak':
                try:
                    cartao_pj = CartaoPJ.objects.get(stripe_id=stripe_id)
                    cartao_pj.cancelamento = datetime.fromtimestamp(cancelamento).date()
                    cartao_pj.save()
                    relatorio = Relatorio.objects.get(stripe_id=stripe_id)
                    relatorio.cancelamento = datetime.fromtimestamp(cancelamento).date()
                    relatorio.save()
                    ad = Ad.objects.get(stripe_id=stripe_id)
                    ad.cancelamento = datetime.fromtimestamp(cancelamento).date()
                    ad.save()
                except OperationalError as e:
                    print(f'Erro ao salvar data de cancelamento no banco de dados {e}')
            else:
                try:
                    relatorio = Relatorio.objects.get(stripe_id=stripe_id)
                    relatorio.cancelamento = datetime.fromtimestamp(cancelamento).date()
                    relatorio.save()
                except OperationalError as e:
                    print(f'Erro ao salvar data de cancelamento no banco de dados {e}')

        if not event.data.object.cancel_at_period_end:
            if event.data.object.plan.product == 'prod_QKrz38Vn9as8Ak':
                try:
                    cartao_pj = CartaoPJ.objects.get(stripe_id=stripe_id)
                    cartao_pj.cancelamento = None
                    cartao_pj.save()
                    relatorio = Relatorio.objects.get(stripe_id=stripe_id)
                    relatorio.cancelamento = None
                    relatorio.save()
                    ad = Ad.objects.get(stripe_id=stripe_id)
                    ad.cancelamento = None
                    ad.save()
                except OperationalError as e:
                    print(f'Erro ao salvar data de cancelamento no banco de dados {e}')
            else:
                try:
                    relatorio = Relatorio.objects.get(stripe_id=stripe_id)
                    relatorio.cancelamento = None
                    relatorio.save()
                except OperationalError as e:
                    print(f'Erro ao salvar data de cancelamento no banco de dados {e}')
            
    if event.type == 'customer.subscription.deleted':
        stripe_id = event.data.object.id
        status = event.data.object.status
        if event.data.object.plan.product == 'prod_QKrz38Vn9as8Ak':
            try:
                cartao_pj = CartaoPJ.objects.get(stripe_id=stripe_id)
                cartao_pj.status = status
                cartao_pj.save()
                relatorio = Relatorio.objects.get(stripe_id=stripe_id)
                relatorio.status = status
                relatorio.save()
                ad = Ad.objects.get(stripe_id=stripe_id)
                ad.status = status
                ad.save()

                usuario = cartao_pj.usuario
                empresa = usuario.empresas.first()
                cards = empresa.cards.all()
                anuncios = empresa.anuncios.all()

                if cards:
                    for card in cards:
                        usuario_do_card = card.usuario_do_card
                        path = os.path.join(settings.MEDIA_ROOT, usuario_do_card.id.hex)
                        try:
                            card.delete()
                            usuario_do_card.delete()
                            shutil.rmtree(path)
                        except FileNotFoundError as err:
                            print(err)

                if anuncios:
                    for anuncio in anuncios:
                        path = anuncio.img.path
                        try:
                            anuncio.delete()
                            shutil.rmtree(path)
                        except FileNotFoundError as err:
                            print(err)

            except OperationalError as e:
                print(f'Erro ao salvar informações do status no banco de dados {e}')
        else:
            try:
                relatorio = Relatorio.objects.get(stripe_id=stripe_id)
                relatorio.status = status
                relatorio.save()
            except OperationalError as e:
                print(f'Erro ao salvar informações do status no banco de dados {e}')


    # Passed signature verification
    return HttpResponse(status=200)


def gerenciar_assinaturas(request):
    email_usuario = request.user.email
    stripe_customer = request.POST.get('stripe_customer')
    if request.method == 'POST':
        portal = stripe.billing_portal.Session.create(
            customer=stripe_customer,
            return_url="http://localhost:8000",
        )
        url = portal.url
        return HttpResponseRedirect(url)