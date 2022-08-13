from django.urls import path
from .views import Card

app_name = 'bild'

urlpatterns = [
    path('guilherme-leal/', Card.as_view(), name='guilherme_leal'),
    path('juliana-costa/', Card.as_view(), name='juliana_costa'),
    path('tiberio-mendonca/', Card.as_view(), name='tiberio_mendonca'),
    path('vitoria-almeida/', Card.as_view(), name='vitoria_almeida'),
]