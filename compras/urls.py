from django.urls import path
from .views import ComprarRelatorio, CancelarRelatorio, AtualizarCartaoRelatorio, ComprarCartao, ComprarAnuncio


app_name = 'compras'

urlpatterns = [
    # path('criar-relatorio/', Criar-relatorioRelatorio.as_view(), name='criar-relatorio'),
    path('comprar-relatorio/', ComprarRelatorio.as_view(), name='comprar-relatorio'),
    path('cancelar-relatorio/<int:pk>/', CancelarRelatorio.as_view(), name='cancelar-relatorio'),
    path('atualizar-cartao-relatorio/<int:pk>/', AtualizarCartaoRelatorio.as_view(), name='atualizar-cartao-relatorio'),
    path('comprar-cartao/', ComprarCartao.as_view(), name='comprar-cartao'),
    path('comprar-anuncio/', ComprarAnuncio.as_view(), name='comprar-anuncio'),
] 