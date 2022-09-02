from django.urls import path
from .views import HomeView, DashboardView, Marcas, Bild, Perplan

app_name = 'core'

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('dashboard/<str:empresa>/', DashboardView.as_view(), name='dashboard'),
    path('marcas/', Marcas.as_view(), name='marcas'),
    path('marcas/bild/', Bild.as_view(), name='bild'),
    path('marcas/perplan/', Perplan.as_view(), name='perplan'),
] 