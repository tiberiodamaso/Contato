import requests
from django.conf import settings
from django.shortcuts import render, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.views.generic import View
from django.http import JsonResponse
from .models import Pedido


class Criar(LoginRequiredMixin, View):

    def get(self, request):
        usuario = self.request.user
        pedido = Pedido.objects.create(usuario=usuario)    
        url_pagamento = 'https://www.mercadopago.com.br/subscriptions/checkout?preapproval_plan_id=2c93808488b118580188b2538a780088'    
        return redirect(url_pagamento)


class Pagar(LoginRequiredMixin, View):

    def get(self, request, *args, **kwargs):
        usuario = self.request.user
        contexto = {'usuario': usuario,}
        return render(request, 'pedidos/pagar.html', contexto)

    def post(self, request, *args, **kwargs):
        usuario = self.request.user
        # Defina a URL da API do MercadoPago
        url = 'https://api.mercadopago.com/preapproval/'

        # Defina o token de acesso
        access_token = settings.MERCADOPAGO_ACCESS_TOKEN

        # Defina o cabeçalho com o token de acesso e o tipo de conteúdo
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }

        # Defina os dados da solicitação em formato JSON
        data = {
            "reason": "Plano individual",
            "payer_email": usuario.email,
            "auto_recurring": {
                "frequency": 1,
                "frequency_type": "months",
                "repetitions": 12,
                "transaction_amount": 10,
                "currency_id": "BRL"
            },
            "payment_methods_allowed": {
                "payment_types": [{
                    "id": "credit_card",
                }],
                "payment_methods": [{}]
            },
            "back_url": "https://meucontato.pythonanywhere.com/",
            "status": "pending"
        }

        # Faça a solicitação POST para a API do MercadoPago
        response = requests.post(url, json=data, headers=headers)

        # Verifique se a solicitação foi bem-sucedida
        if response.status_code == 201:
            # Processar a resposta aqui, se necessário
            response_data = response.json()
            url_pagamento = response_data['init_point']
            return redirect(url_pagamento)
            # return JsonResponse(response_data)
        else:
            # Lidar com erros de solicitação, se necessário
            error_message = response.text
            return JsonResponse({'error': error_message}, status=response.status_code)

