from django.urls import path
from .views import Criar


app_name = 'pedidos'

urlpatterns = [
    path('criar/', Criar.as_view(), name='criar'),
] 