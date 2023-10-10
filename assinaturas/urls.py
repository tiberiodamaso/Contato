from django.urls import path
from .views import Criar, Pagar, Cancelar


app_name = 'assinaturas'

urlpatterns = [
    path('criar/', Criar.as_view(), name='criar'),
    path('pagar/', Pagar.as_view(), name='pagar'),
    path('cancelar/<int:pk>/', Cancelar.as_view(), name='cancelar'),
] 