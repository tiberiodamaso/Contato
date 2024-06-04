import json, os, requests
import hmac
import hashlib
import stripe
from datetime import datetime
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse, HttpResponseBadRequest
from django.urls import reverse, reverse_lazy
from django.conf import settings
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.utils.decorators import method_decorator
from django.shortcuts import render, redirect
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.views.generic.base import TemplateResponseMixin
from django.views.generic.edit import DeletionMixin
from django.views.generic import View, CreateView, UpdateView, TemplateView
from django.http import JsonResponse
from .models import Relatorio, Ad, CartaoPF, CartaoPJ
from cards.views import CriarCardPF

stripe.api_key = settings.STRIPE_SECRET_KEY


@method_decorator(csrf_exempt, name='dispatch')
class ComprarRelatorio(LoginRequiredMixin, UserPassesTestMixin, SuccessMessageMixin, View):

    def test_func(self):
        cartoes = self.request.user.cartoespf.all()
        for cartao in cartoes:
            if cartao.status == 'approved':
                return True

    def handle_no_permission(self):
        return render(self.request, 'cards/permissao-negada-nao-criou-cartao.html', status=403)


    def get(self, request, *args, **kwargs):
        usuario = self.request.user
        compra = usuario.relatorios.last()
        card = usuario.cards.all().first()
        contexto = {'usuario': usuario, 'card': card, 'compra': compra}
        return render(request, 'compras/comprar-relatorio.html', contexto)

    def post(self, request, *args, **kwargs):
        usuario = self.request.user
        access_token = settings.MERCADOPAGO_ACCESS_TOKEN_RELATORIO
        form_data = json.loads(self.request.body.decode('utf-8'))

        # Defina a URL da API do MercadoPago
        url = 'https://api.mercadopago.com/preapproval/'

        # Defina o cabeçalho com o token de acesso e o tipo de conteúdo
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }

        # Defina os dados da solicitação em formato JSON
        data = {
            "auto_recurring": {
                "frequency": 1,
                "frequency_type": "months",
                "transaction_amount": 9.90,
                "currency_id": "BRL"
            },
            "back_url": "https://meucontato.pythonanywhere.com/",
            "card_token_id": form_data.get('token'),
            "payer_email": form_data.get('payer')['email'],
            "preapproval_plan_id": "2c9380848c885e45018c88639c710001",
            "reason": "Plano individual",
            "status": "authorized"
        }

        # Faça a solicitação POST para a API do MercadoPago
        response = requests.post(url, json=data, headers=headers)

        # Verifique se a solicitação foi bem-sucedida
        if response.status_code == 201:
            data = response.json()
            formato_da_string = "%Y-%m-%dT%H:%M:%S.%f%z"
            relatorio = Relatorio.objects.create(
                usuario=usuario,
                assinatura_id = data['id'],
                payer_id = data['payer_id'],
                date_created = datetime.strptime(data['date_created'], formato_da_string),
                valor = float(data['auto_recurring']['transaction_amount']),
                status = data['status'],
                start_date = datetime.strptime(data['date_created'], formato_da_string),
                next_payment_date = datetime.strptime(data['next_payment_date'], formato_da_string),
                last_modified = datetime.strptime(data['last_modified'], formato_da_string),
            )
            messages.success(self.request, 'Pagamento realizado com sucesso!')
            mensagem = 'Pagamento realizado com sucesso!'
            response_data = {
                'status_code': response.status_code,
                'message': mensagem,
            }
            return JsonResponse(response_data, status=response.status_code)
        else:
            # Lidar com erros de solicitação, se necessário
            error_message = response.text
            print(f'response.status_code != 201, error_message = {error_message}')
            return JsonResponse({'error': error_message}, status=response.status_code)


@method_decorator(csrf_exempt, name='dispatch')
class CancelarRelatorio(LoginRequiredMixin, SuccessMessageMixin, TemplateView):

    template_name = 'usuarios/minha-conta.html'

    def render_to_response(self, context, **response_kwargs):
        response_kwargs.setdefault('content_type', self.content_type)
        return self.response_class(request=self.request, template=self.get_template_names(), context=context, using=self.template_engine, **response_kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context['relatorios'] = self.request.user.relatorios.all()
        return context

    def get(self, request, *args, **kwargs):    
        usuario = self.request.user
        relatorio = Relatorio.objects.get(id=self.kwargs['pk'])
        assinatura_id = relatorio.assinatura_id
        access_token = settings.MERCADOPAGO_ACCESS_TOKEN_RELATORIO

        # Defina a URL da API do MercadoPago
        url = f'https://api.mercadopago.com/preapproval/{assinatura_id}'

        # Defina o cabeçalho com o token de acesso e o tipo de conteúdo
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }

        # Defina os dados da solicitação em formato JSON
        data = {
            "status": "cancelled",
        }

        # Faça a solicitação PUT para a API do MercadoPago
        response = requests.put(url, json=data, headers=headers)

        # Verifique se a solicitação foi bem-sucedida
        if response.status_code == 200:
            data = response.json()
            context = self.get_context_data(**kwargs)
            formato_da_string = "%Y-%m-%dT%H:%M:%S.%f%z"
            relatorio.status = data['status']
            relatorio.last_modified = datetime.strptime(data['last_modified'], formato_da_string)
            relatorio.save()
            messages.success(self.request, 'Assinatura cancelada com sucesso!')
            return self.render_to_response(context=context)
        else:
            # Lidar com erros de solicitação, se necessário
            error_message = response.text
            return JsonResponse({'error': error_message}, status=response.status_code)


@method_decorator(csrf_exempt, name='dispatch')
class AtualizarCartaoRelatorio(LoginRequiredMixin, SuccessMessageMixin, View):


    def get(self, request, *args, **kwargs):
        usuario = self.request.user
        relatorio = Relatorio.objects.get(id=self.kwargs['pk'])
        assinatura_id = relatorio.assinatura_id
        pk = relatorio.id
        card = usuario.cards.all().last()
        contexto = {'usuario': usuario, 'pk': pk, 'card': card}
        return render(request, 'compras/atualizar-cartao-relatorio.html', contexto)

    def post(self, request, *args, **kwargs):
        usuario = self.request.user
        relatorio = Relatorio.objects.get(id=self.kwargs['pk'])
        assinatura_id = relatorio.assinatura_id
        access_token = settings.MERCADOPAGO_ACCESS_TOKEN_RELATORIO
        form_data = json.loads(self.request.body.decode('utf-8'))

        # Defina a URL da API do MercadoPago
        url = f'https://api.mercadopago.com/preapproval/{assinatura_id}'

        # Defina o cabeçalho com o token de acesso e o tipo de conteúdo
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }

        # Defina os dados da solicitação em formato JSON
        data = {
            "reason": "Plano individual",
            "back_url": "https://meucontato.pythonanywhere.com",
            "auto_recurring": {
                "transaction_amount": 9.90,
                "currency_id": "BRL"
            },
            "card_token_id": form_data.get('token'),
            "status": "authorized",
        }

        # Faça a solicitação POST para a API do MercadoPago
        response = requests.put(url, json=data, headers=headers)

        # Verifique se a solicitação foi bem-sucedida
        if response.status_code == 200:
            
            mensagem = 'Cartão atualizado com sucesso!'
            messages.success(self.request, mensagem)
            response_data = {
                'status_code': response.status_code,
                'message': mensagem,
            }
            return JsonResponse(response_data, status=response.status_code)
        else:
            # Lidar com erros de solicitação, se necessário
            error_message = response.text
            return JsonResponse({'error': error_message}, status=response.status_code)


@method_decorator(csrf_exempt, name='dispatch')
class ComprarCartaoPFMP(LoginRequiredMixin, SuccessMessageMixin, View):


    def get(self, request, *args, **kwargs):
        usuario = self.request.user
        try:
            perfil = usuario.perfil
        except:
            return redirect(reverse_lazy('usuarios:perfil-pf'))
        compra = usuario.cartoespf.last()
        card = usuario.cards.all().first()
        contexto = {'usuario': usuario, 'card': card, 'compra': compra}
        return render(request, 'compras/comprar-cartao-pf.html', contexto)

    def post(self, request, *args, **kwargs):
        usuario = self.request.user
        access_token = settings.MERCADOPAGO_ACCESS_TOKEN
        form_data = json.loads(self.request.body.decode('utf-8'))

        # Defina a URL da API do MercadoPago
        url = 'https://api.mercadopago.com/v1/payments'

        # Defina o cabeçalho com o token de acesso e o tipo de conteúdo
        headers = {
            'Content-Type': 'application/json',
            'X-Idempotency-Key': '0d5020ed-1af6-469c-ae06-c3bec19954bb',
            'Authorization': f'Bearer {access_token}',
        }

        # Defina os dados da solicitação em formato JSON
        data = {
            "description": "Cartão de visitas virtual individual",
            "installments": 1,
            "issuer_id": form_data.get('issuer_id'),
            "payer": {
                "entity_type": "individual",
                "type": "customer",
                "email": form_data.get('payer')['email'],
                "identification": {
                    "type": form_data.get('payer')['identification']['type'],
                    "number": form_data.get('payer')['identification']['number']
                }
            },
            "payment_method_id": form_data.get('payment_method_id'),
            "token": form_data.get('token'),
            "transaction_amount": form_data.get('transaction_amount')
        }

        # Faça a solicitação POST para a API do MercadoPago
        response = requests.post(url, json=data, headers=headers)

        # Verifique se a solicitação foi bem-sucedida
        if response.status_code == 200 or response.status_code == 201:
            data = response.json()
            formato_da_string = "%Y-%m-%dT%H:%M:%S.%f%z"
            cartao = CartaoPF.objects.create(
                usuario=usuario,
                pagamento_id = data['id'],
                payer_id = data['payer']['id'],
                date_created = datetime.strptime(data['date_created'], formato_da_string),
                valor = float(data['transaction_amount']),
                authorization_code = data['authorization_code'],
                status = data['status'],
            )
            messages.success(self.request, 'Pagamento realizado com sucesso!')
            mensagem = 'Pagamento realizado com sucesso!'
            response_data = {
                'status_code': response.status_code,
                'message': mensagem,
            }
            return JsonResponse(response_data, status=response.status_code)
        else:
            # Lidar com erros de solicitação, se necessário
            error_message = response.text
            print(f'response.status_code != 201, error_message = {error_message}')
            return JsonResponse({'error': error_message}, status=response.status_code)


@method_decorator(csrf_exempt, name='dispatch')
class ComprarCartaoPF(LoginRequiredMixin, SuccessMessageMixin, View):


    def get(self, request, *args, **kwargs):

        # session = stripe.checkout.Session.retrieve(request.args.get('session_id'))

        # return jsonify(status=session.status, customer_email=session.customer_details.email)

        usuario = self.request.user
        username = usuario.username
        try:
            perfil = usuario.perfil
        except:
            return redirect(reverse_lazy('usuarios:perfil-pf'))
        compra = usuario.cartoespf.last()
        card = usuario.cards.all().first()
        contexto = {'usuario': usuario, 'username': username, 'card': card, 'compra': compra}
        return render(request, 'compras/comprar-cartao-pf.html', contexto)


    def post(self, request, *args, **kwargs):
        usuario = self.request.user
        data_atual = datetime.now()
        formato_da_string = "%Y-%m-%d %H:%M:%S"
        data_atual_formatada = data_atual.strftime(formato_da_string)

        try:
            data = json.loads(request.body)
            intent = stripe.PaymentIntent.create(
                amount=2990,
                currency='brl',
                automatic_payment_methods={'enabled': True,},
            )

            cartao = CartaoPF.objects.create(
                usuario=usuario,
                pagamento_id = intent.id,
                payer_id = 1,
                date_created = datetime.now().strptime(data_atual_formatada, formato_da_string),
                valor = 29.90,
                authorization_code = 1,
                status = 'pendente',
            )

            return JsonResponse({
                'clientSecret': intent['client_secret']
            })
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=403)



@method_decorator(csrf_exempt, name='dispatch')
class ComprarAnuncio(LoginRequiredMixin, UserPassesTestMixin, SuccessMessageMixin, View):

    def test_func(self):
        cartoes = self.request.user.cartoespf.all()
        for cartao in cartoes:
            if cartao.status == 'approved':
                return True

    def handle_no_permission(self):
        return render(self.request, 'cards/permissao-negada-nao-criou-cartao.html', status=403)


    def get(self, request, *args, **kwargs):
        usuario = self.request.user
        empresa = usuario.empresas.first()
        compra = usuario.ads.last()
        card = usuario.cards.all().first()
        anuncios = empresa.anuncios.all()
        contexto = {'usuario': usuario, 'card': card, 'compra': compra, 'anuncios': anuncios}
        return render(request, 'compras/comprar-anuncio.html', contexto)

    def post(self, request, *args, **kwargs):
        usuario = self.request.user
        access_token = settings.MERCADOPAGO_ACCESS_TOKEN
        form_data = json.loads(self.request.body.decode('utf-8'))

        # Defina a URL da API do MercadoPago
        url = 'https://api.mercadopago.com/v1/payments'

        # Defina o cabeçalho com o token de acesso e o tipo de conteúdo
        headers = {
            'Content-Type': 'application/json',
            'X-Idempotency-Key': '0d5020ed-1af6-469c-ae06-c3bec19954bb',
            'Authorization': f'Bearer {access_token}',
        }

        # Defina os dados da solicitação em formato JSON
        data = {
            "description": "Cartão de visitas virtual individual",
            "installments": 1,
            "issuer_id": form_data.get('issuer_id'),
            "payer": {
                "entity_type": "individual",
                "type": "customer",
                "email": form_data.get('payer')['email'],
                "identification": {
                    "type": form_data.get('payer')['identification']['type'],
                    "number": form_data.get('payer')['identification']['number']
                }
            },
            "payment_method_id": form_data.get('payment_method_id'),
            "token": form_data.get('token'),
            "transaction_amount": form_data.get('transaction_amount')
        }

        # Faça a solicitação POST para a API do MercadoPago
        response = requests.post(url, json=data, headers=headers)

        # Verifique se a solicitação foi bem-sucedida
        if response.status_code == 200:
            data = response.json()
            formato_da_string = "%Y-%m-%dT%H:%M:%S.%f%z"
            ad = Ad.objects.create(
                usuario=usuario,
                pagamento_id = data['id'],
                payer_id = data['payer']['id'],
                date_created = datetime.strptime(data['date_created'], formato_da_string),
                valor = float(data['transaction_amount']),
                authorization_code = data['authorization_code'],
                status = data['status'],
            )
            messages.success(self.request, 'Pagamento realizado com sucesso!')
            mensagem = 'Pagamento realizado com sucesso!'
            response_data = {
                'status_code': response.status_code,
                'message': mensagem,
            }
            return JsonResponse(response_data, status=response.status_code)
        else:
            # Lidar com erros de solicitação, se necessário
            error_message = response.text
            print(f'response.status_code != 201, error_message = {error_message}')
            return JsonResponse({'error': error_message}, status=response.status_code)


@method_decorator(csrf_exempt, name='dispatch')
class ComprarCartaoPJ(LoginRequiredMixin, SuccessMessageMixin, View):


    def get(self, request, *args, **kwargs):
        usuario = self.request.user
        nova_compra = request.GET.get('nova_compra')
        try:
            perfil = usuario.perfil
        except:
            return redirect(reverse_lazy('usuarios:perfil-pj'))
        compra = usuario.cartoespj.last()
        card = usuario.cards.all()
        contexto = {'usuario': usuario, 'card': card, 'compra': compra, 'nova_compra': nova_compra}
        return render(request, 'compras/comprar-cartao-pj.html', contexto)

    def post(self, request, *args, **kwargs):
        usuario = self.request.user
        access_token = settings.MERCADOPAGO_ACCESS_TOKEN_RELATORIO
        form_data = json.loads(self.request.body.decode('utf-8'))

        # Defina a URL da API do MercadoPago
        url = 'https://api.mercadopago.com/preapproval/'

        # Defina o cabeçalho com o token de acesso e o tipo de conteúdo
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }

        # Defina os dados da solicitação em formato JSON
        data = {
            "auto_recurring": {
                "frequency": 1,
                "frequency_type": "months",
                "transaction_amount": 49.90,
                "currency_id": "BRL"
            },
            "back_url": "https://meucontato.pythonanywhere.com/",
            "card_token_id": form_data.get('token'),
            "payer_email": form_data.get('payer')['email'],
            "preapproval_plan_id": "2c9380848f1b8ed3018f2c3b458e0795",
            "reason": "Plano empresarial",
            "status": "authorized"
        }

        # Faça a solicitação POST para a API do MercadoPago
        response = requests.post(url, json=data, headers=headers)

        # Verifique se a solicitação foi bem-sucedida
        if response.status_code == 200 or response.status_code == 201:
            data = response.json()
            formato_da_string = "%Y-%m-%dT%H:%M:%S.%f%z"
            cartao = CartaoPJ.objects.create(
                usuario=usuario,
                assinatura_id = data['id'],
                payer_id = data['payer_id'],
                date_created = datetime.strptime(data['date_created'], formato_da_string),
                valor = float(data['auto_recurring']['transaction_amount']),
                status = data['status'],
                start_date = datetime.strptime(data['date_created'], formato_da_string),
                next_payment_date = datetime.strptime(data['next_payment_date'], formato_da_string),
                last_modified = datetime.strptime(data['last_modified'], formato_da_string),
            )

            # TODO Verificar se ao comprar um novo cartão PJ precisa criar novo objeto relatório e novo objeto anúncio
            relatorio = Relatorio.objects.create(
                usuario=usuario,
                assinatura_id = 'empresarial',
                payer_id = data['payer_id'],
                date_created = datetime.strptime(data['date_created'], formato_da_string),
                valor = 0,
                status = data['status'],
                start_date = datetime.strptime(data['date_created'], formato_da_string),
                next_payment_date = datetime.strptime(data['next_payment_date'], formato_da_string),
                last_modified = datetime.strptime(data['last_modified'], formato_da_string),
            )

            ad = Ad.objects.create(
                usuario=usuario,
                pagamento_id = 'empresarial',
                payer_id = data['payer_id'],
                date_created = datetime.strptime(data['date_created'], formato_da_string),
                valor = 0,
                authorization_code = 'empresarial',
                status = data['status'],
            )

            messages.success(self.request, 'Pagamento realizado com sucesso!')
            mensagem = 'Pagamento realizado com sucesso!'
            response_data = {
                'status_code': response.status_code,
                'message': mensagem,
            }
            return JsonResponse(response_data, status=response.status_code)
        else:
            # Lidar com erros de solicitação, se necessário
            error_message = response.text
            print(f'response.status_code != 201, error_message = {error_message}')
            return JsonResponse({'error': error_message}, status=response.status_code)


# STRIPE

# @csrf_exempt
# def create_checkout_session(request):

#     if request.method == 'POST':
#         try:
#             domain_url = request.build_absolute_uri('/')[:-1]
#             success_url = str(reverse_lazy('core:modelos'))
#             session = stripe.checkout.Session.create(
#                 ui_mode='embedded',
#                 locale='pt',
#                 line_items=[
#                     {
#                         # Provide the exact Price ID (for example, pr_1234) of the product you want to sell
#                         'price': 'price_1PLA0lEfa8nOJrr9DfWMLery',
#                         'quantity': 1,
#                     }, 
#                 ],
#                 mode='payment',
#                 return_url=f"{domain_url}{success_url}?session_id={{CHECKOUT_SESSION_ID}}",
#             )
#             return JsonResponse({'clientSecret': session.client_secret})
#         except Exception as e:
#             return JsonResponse({'error': str(e)}, status=400)
#     else:
#         return JsonResponse({'error': 'Invalid request method'}, status=405)


# @csrf_exempt
# def session_status(request):

#     session_id = request.GET.get('session_id')
#     if session_id:
#         try:
#             session = stripe.checkout.Session.retrieve(session_id)
#             response_data = {
#                 'status': session.status,
#                 'customer_email': session.customer_details.email,
#             }
#             return JsonResponse(response_data)
#         except Exception as e:
#             return JsonResponse({'error': str(e)}, status=400)
#     else:
#         return JsonResponse({'error': 'session_id parameter is required'}, status=400)


@csrf_exempt
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META['HTTP_STRIPE_SIGNATURE']
    event = None
    endpoint_secret = 'whsec_de06a86430dc9c76f4097be20ebe6fb84f596936734543fb5bcb7ffacd9fff5d'

    try:
        event = stripe.Webhook.construct_event(payload, sig_header, endpoint_secret)
    except ValueError as e:
        # Invalid payload
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        return HttpResponse(status=400)

    # Passed signature verification
    return HttpResponse(status=200)


@csrf_exempt
@require_POST
def create_payment(request):
    try:
        data = json.loads(request.body)
        intent = stripe.PaymentIntent.create(
            amount=2990,
            currency='brl',
            automatic_payment_methods={'enabled': True,},
        )
        return JsonResponse({
            'clientSecret': intent['client_secret']
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=403)