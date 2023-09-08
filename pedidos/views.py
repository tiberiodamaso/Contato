from django.shortcuts import render, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.views.generic import View
from .models import Pedido


class Criar(LoginRequiredMixin, View):

    def get(self, request):
        usuario = self.request.user
        pedido = Pedido.objects.create(usuario=usuario)    
        url_pagamento = 'https://www.mercadopago.com.br/subscriptions/checkout?preapproval_plan_id=2c93808488b118580188b2538a780088'    
        return redirect(url_pagamento)

