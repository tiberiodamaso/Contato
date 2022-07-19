from django.urls import path
from .views import Administracao, Card

app_name = 'nois_tricota'

urlpatterns = [
    path('admin/', Administracao.as_view(), name='nois_tricota_admin'),
    path('juliana-bonazone/', Card.as_view(), name='juliana_bonazone'),
    path('tiberio-mendonca/', Card.as_view(), name='tiberio_mendonca'),
]