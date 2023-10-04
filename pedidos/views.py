import requests
import mercadopago
import json
from django.http import HttpResponseRedirect
from django.conf import settings
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.shortcuts import render, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.views.generic import View, CreateView
from django.http import JsonResponse
from .models import Pedido
from cards.views import Criar

class Criar(LoginRequiredMixin, View):

    def get(self, request):
        usuario = self.request.user
        pedido = Pedido.objects.create(usuario=usuario)    
        return redirect('pedidos:pagar')


@method_decorator(csrf_exempt, name='dispatch')
class Pagar(LoginRequiredMixin, SuccessMessageMixin, View):


    def get(self, request, *args, **kwargs):
        usuario = self.request.user
        contexto = {'usuario': usuario,}
        return render(request, 'pedidos/pagar.html', contexto)

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
            "back_url": "https://meucontato.pythonanywhere.com",
            "status": "authorized"
        }

        # Faça a solicitação POST para a API do MercadoPago
        response = requests.post(url, json=data, headers=headers)

        # Verifique se a solicitação foi bem-sucedida
        if response.status_code == 201:
            pedido = usuario.pedidos.last()
            pedido.status = 'Pago'
            pedido.save()
            messages.success(self.request, 'Pagamento realizado com sucesso!')
            # back_url = response.json()['back_url']
            # return redirect('core:home')
        else:
            # Lidar com erros de solicitação, se necessário
            error_message = response.text
            return JsonResponse({'error': error_message}, status=response.status_code)
