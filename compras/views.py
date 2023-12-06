import json, os, requests
import hmac
import hashlib

from datetime import datetime
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse, HttpResponseBadRequest
from django.urls import reverse, reverse_lazy
from django.conf import settings
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.shortcuts import render, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.views.generic.base import TemplateResponseMixin
from django.views.generic.edit import DeletionMixin
from django.views.generic import View, CreateView, UpdateView, TemplateView
from django.http import JsonResponse

from .models import Relatorio, Cartao
from cards.views import Criar

# class CriarRelatorio(LoginRequiredMixin, View):

#     def get(self, request):
#         usuario = self.request.user
#         return redirect('compras:comprar-relatorio')


@method_decorator(csrf_exempt, name='dispatch')
class ComprarRelatorio(LoginRequiredMixin, SuccessMessageMixin, View):


    def get(self, request, *args, **kwargs):
        usuario = self.request.user
        card = usuario.cards.all().first()
        contexto = {'usuario': usuario, 'card': card}
        return render(request, 'compras/comprar-relatorio.html', contexto)

    def post(self, request, *args, **kwargs):
        usuario = self.request.user
        access_token = settings.MERCADOPAGO_ACCESS_TOKEN
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
            "preapproval_plan_id": "2c9380848af2eac7018af6be15ce0310",
            "reason": "Plano individual",
            "payer_email": form_data.get('payer')['email'],
            "card_token_id": form_data.get('token'),
            "auto_recurring": {
                "frequency": 1,
                "frequency_type": "months",
                "transaction_amount": 10,
                "currency_id": "BRL"
            },
            "back_url": "https://meucontato.pythonanywhere.com/",
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
                start_date = datetime.strptime(data['auto_recurring']['start_date'], formato_da_string),
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
        # usuario = self.request.user
        relatorio = Relatorio.objects.get(id=self.kwargs['pk'])
        assinatura_id = relatorio.assinatura_id
        access_token = settings.MERCADOPAGO_ACCESS_TOKEN

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
        pk = assinatura.id
        card = usuario.cards.all().first()
        contexto = {'usuario': usuario, 'pk': pk, 'card': card}
        return render(request, 'compras/atualizar-cartao-relatorio.html', contexto)

    def post(self, request, *args, **kwargs):
        usuario = self.request.user
        relatorio = Relatorio.objects.get(id=self.kwargs['pk'])
        assinatura_id = relatorio.assinatura_id
        access_token = settings.MERCADOPAGO_ACCESS_TOKEN
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
                "transaction_amount": 10,
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
class ComprarCartao(LoginRequiredMixin, SuccessMessageMixin, View):


    def get(self, request, *args, **kwargs):
        usuario = self.request.user
        card = usuario.cards.all().first()
        contexto = {'usuario': usuario, 'card': card}
        return render(request, 'compras/comprar-cartao.html', contexto)

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
            cartao = Cartao.objects.create(
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
            # return JsonResponse(response_data, status=response.status_code)
            return HttpResponseRedirect(reverse('core:criar'))
        else:
            # Lidar com erros de solicitação, se necessário
            error_message = response.text
            print(f'response.status_code != 201, error_message = {error_message}')
            return JsonResponse({'error': error_message}, status=response.status_code)