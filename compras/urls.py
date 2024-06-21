from django.urls import path
from .views import ComprarRelatorio, CancelarRelatorio, AtualizarCartaoRelatorio, ComprarCartaoPF, ComprarAnuncio, \
    ComprarCartaoPJ, stripe_webhook, gerenciar_assinaturas


app_name = 'compras'

urlpatterns = [
    path('comprar-relatorio/', ComprarRelatorio.as_view(), name='comprar-relatorio'),
    path('cancelar-relatorio/<int:pk>/', CancelarRelatorio.as_view(), name='cancelar-relatorio'),
    path('atualizar-cartao-relatorio/<int:pk>/', AtualizarCartaoRelatorio.as_view(), name='atualizar-cartao-relatorio'),
    path('comprar-cartao-pf/', ComprarCartaoPF.as_view(), name='comprar-cartao-pf'),
    path('comprar-anuncio/', ComprarAnuncio.as_view(), name='comprar-anuncio'),
    path('comprar-cartao-pj/', ComprarCartaoPJ.as_view(), name='comprar-cartao-pj'),
    path('stripe_webhook/', stripe_webhook, name='stripe_webhook'),
    path('gerenciar-assinaturas/', gerenciar_assinaturas, name='gerenciar-assinaturas'),
] 