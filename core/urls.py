from django.urls import path
from .views import HomeView, DashboardView, Marcas, Bild, Perplan
from cards.views import CardEditView, CardListView, CardDashboardView

app_name = 'core'

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('<slug:empresa>/dashboard/', DashboardView.as_view(), name='dashboard'),
    path('<slug:empresa>/dashboard/<slug:slug>/', CardDashboardView.as_view(), name='detalhe'),
    path('<slug:empresa>/cards/', CardListView.as_view(), name='lista'),
    path('<slug:empresa>/card/editar/<slug:slug>/', CardEditView.as_view(), name='editar'),


    path('marcas/', Marcas.as_view(), name='marcas'),
    path('marcas/bild/', Bild.as_view(), name='bild'),
    path('marcas/perplan/', Perplan.as_view(), name='perplan'),
] 