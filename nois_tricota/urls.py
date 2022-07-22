from django.urls import path
from .views import Administracao, Cartao

app_name = 'nois_tricota'

urlpatterns = [
    path('', Administracao.as_view(), name='admin'),
    path('juliana-bonazone/', Cartao.as_view(), name='juliana_bonazone'),
    path('tiberio-mendonca/', Cartao.as_view(), name='tiberio_mendonca'),
]