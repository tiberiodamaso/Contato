from django.urls import path
from .views import Criar, Pagar


app_name = 'pedidos'

urlpatterns = [
    path('criar/', Criar.as_view(), name='criar'),
    path('pagar/', Pagar.as_view(), name='pagar'),
] 