from django.urls import path
from .views import Administracao, Dashboard, Cartao, DashboardVendedor

app_name = 'bild'

urlpatterns = [
    path('', Administracao.as_view(), name='bild_admin'),
    path('dashboard/', Dashboard.as_view(), name='dashboard'),
    path('dashboard/<int:pk>/', DashboardVendedor.as_view(), name='dashboard-vendedor'),
    path('guilherme-leal/', Cartao.as_view(), name='guilherme_leal'),
    path('juliana-costa/', Cartao.as_view(), name='juliana_costa'),
    path('tiberio-mendonca/', Cartao.as_view(), name='tiberio_mendonca'),
    path('vitoria-almeida/', Cartao.as_view(), name='vitoria_almeida'),
]