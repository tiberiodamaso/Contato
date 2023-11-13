import json, os, requests
import hmac
import hashlib

from datetime import datetime
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse, HttpResponseBadRequest
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


from .models import Assinatura
from cards.views import Criar

class Criar(LoginRequiredMixin, View):

    def get(self, request):
        usuario = self.request.user
        return redirect('assinaturas:pagar')


@method_decorator(csrf_exempt, name='dispatch')
class Pagar(LoginRequiredMixin, SuccessMessageMixin, View):


    def get(self, request, *args, **kwargs):
        print('Entrou na views PAGAR')
        usuario = self.request.user
        contexto = {'usuario': usuario,}
        return render(request, 'assinaturas/pagar.html', contexto)

    def post(self, request, *args, **kwargs):
        print('Entrou no método POST de PAGAR')
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
            assinatura = Assinatura.objects.create(
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
class Cancelar(LoginRequiredMixin, SuccessMessageMixin, TemplateView):

    template_name = 'usuarios/minha-conta.html'

    def render_to_response(self, context, **response_kwargs):
        response_kwargs.setdefault('content_type', self.content_type)
        return self.response_class(request=self.request, template=self.get_template_names(), context=context, using=self.template_engine, **response_kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context['assinaturas'] = self.request.user.assinaturas.all()
        return context

    def get(self, request, *args, **kwargs):    
        # usuario = self.request.user
        assinatura = Assinatura.objects.get(id=self.kwargs['pk'])
        assinatura_id = assinatura.assinatura_id
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
            assinatura.status = data['status']
            assinatura.save()
            messages.success(self.request, 'Assinatura cancelada com sucesso!')
            return self.render_to_response(context=context)
        else:
            # Lidar com erros de solicitação, se necessário
            error_message = response.text
            return JsonResponse({'error': error_message}, status=response.status_code)


@method_decorator(csrf_exempt, name='dispatch')
class AtualizarCartao(LoginRequiredMixin, SuccessMessageMixin, View):


    def get(self, request, *args, **kwargs):
        usuario = self.request.user
        assinatura = Assinatura.objects.get(id=self.kwargs['pk'])
        assinatura_id = assinatura.assinatura_id
        pk = assinatura.id
        card = usuario.cards.all().first()
        contexto = {'usuario': usuario, 'pk': pk, 'card': card}
        return render(request, 'assinaturas/atualizar-cartao.html', contexto)

    def post(self, request, *args, **kwargs):
        usuario = self.request.user
        assinatura = Assinatura.objects.get(id=self.kwargs['pk'])
        assinatura_id = assinatura.assinatura_id
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
                # "frequency": 1,
                # "frequency_type": "months",
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
