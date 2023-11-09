"""
Exemplo de como utilizar webhook do mercadopago

- criar uma views para tratar as requisições POST MercadoPagoWebhook (abaixo) 

- criar rota para receber as requisições, ex:
    path('webhook/', MercadoPagoWebhook.as_view(), name='webhook')

- adicionar no corpo das requisições o endpoint para receber notificações:
    "back_url": "https://meucontato.pythonanywhere.com/assinaturas/webhook/",

- configurar no MercadoPago o endpoint de teste e de produção, bem como os tipos de eventos

exemplos de payloads Recebidos:
# pagamento:
# payload 1
payload = {
    'action': 'payment.created', 
    'api_version': 'v1', 
    'data': {
        'id': '692...18'  # id do pagamento
        }, 
    'date_created': '2023-11-09T14:14:45Z', 
    'id': 1085...337, # id da notificação
    'live_mode': True, 
    'type': 'payment',
    'user_id': '148...83'
    }

#payload2
payload = {
    'action': 'updated', 
    'application_id': 665..6406, # id da aplicação do vendedor
    'data': {
        'id': '2c38088b...6f79c04f5' # id da alteração
        }, 
    'date': '2023-11-09T14:14:46Z', 
    'entity': 'preapproval', 
    'id': 108..34, # id da notificação
    'type': 'subscription_preapproval', 
    'version': 1
    }

# cancelamento
payload = {
    'action': 'updated', 
    'application_id': 6673..06, 
    'data': {
        'id': '2c98048...46f79c04f5'  # id da alteração
        }, 
    'date': '2023-11-09T14:28:59Z', 
    'entity': 'preapproval', 
    'id': 108...8673, # id da notificação
    'type': 'subscription_preapproval', 
    'version': 2
    }
"""

# copiar o conteúdo abaixo para o arquivo views.py
import json, os
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import View
from mercadopago.sdk import SDK


@method_decorator(csrf_exempt, name='dispatch')
class MercadoPagoWebhook(View):

    def post(self, request, *args, **kwargs):
        # autenticação no SDK
        mercado_pago = SDK(access_token=os.getenv('MERCADOPAGO_ACCESS_TOKEN'))

        # recupera dados do payload da requisição
        try:
            payload = json.loads(request.body)
        except json.JSONDecodeError as err:
            # melhorar o tratamento do erro
            print(f'Erro ao extrair json.loads(request.body). Erro: {str(err)}')

        try:
            notification_type = payload.get("type")
        except Exception as err:
            # melhorar o tratamento do erro
            print(f'Erro ao recuperar chave payload.get("type"). Erro: {str(err)}')

        if notification_type:
            if notification_type == "payment":
                resultado_consulta = mercado_pago.subscription().get('<id do pagamento>')
                # alterar BD conforme necessário
            elif notification_type == "subscription_preapproval":
                resultado_consulta = mercado_pago.subscription().get('<id da alteração>')
                # alterar BD conforme necessário
            # analisar cada caso conforme documentação

        # resposta para webhook 
        return JsonResponse({'status': 'ok'})

"""
exemplo do resultado_consulta:

{'status': 200,
 'response': {'id': '2c938...c04f5',
  'payer_id': 14...059,
  'payer_email': '',
  'back_url': 'https://meucontato.pythonanywhere.com',
  'collector_id': 148...3,
  'application_id': 6657...406,
  'status': 'authorized',
  'reason': 'Individual',
  'date_created': '2023-11-09T10:14:46.170-04:00',
  'last_modified': '2023-11-09T11:00:15.753-04:00',
  'init_point': 'https://www.mercadopago.com.br/subscriptions/checkout?preapproval_id=2c9...04f5',
  'preapproval_plan_id': '2c93...310',
  'auto_recurring': {'frequency': 1,
   'frequency_type': 'months',
   'transaction_amount': 10.0,
   'currency_id': 'BRL',
   'start_date': '2023-11-09T10:14:46.171-04:00',
   'billing_day_proportional': False,
   'has_billing_day': False,
   'free_trial': None},
  'summarized': {'quotas': None,
   'charged_quantity': None,
   'pending_charge_quantity': None,
   'charged_amount': None,
   'pending_charge_amount': None,
   'semaphore': None,
   'last_charged_date': None,
   'last_charged_amount': None},
  'next_payment_date': '2023-12-09T10:14:46.000-04:00',
  'payment_method_id': 'master',
  'card_id': '92...3',
  'first_invoice_offset': None}}
"""