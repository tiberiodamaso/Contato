from django.urls import path
from .views import Card

app_name = 'nois_tricota'

urlpatterns = [
    path('juliana-bonazone/', Card.as_view(), name='juliana-bonazone'),
    path('tiberio-mendonca/', Card.as_view(), name='tiberio-mendonca'),
]