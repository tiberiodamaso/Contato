from django.urls import path
from .views import HomeView, Marcas, Bild, Perplan
from cards.views import CardEditView, CardListView, CardDashboardView, CardDetailView, AllCardsListView, CardCreateView, EmpresaDashboardView, EmpresaEditView

app_name = 'core'

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('<slug:empresa>/dashboard/', EmpresaDashboardView.as_view(), name='dashboard-empresa'),
    path('<slug:empresa>/dashboard/<slug:slug>/', CardDashboardView.as_view(), name='dashboard-card'),
    path('<slug:empresa>/cards/', CardListView.as_view(), name='lista'),
    path('card/criar/', CardCreateView.as_view(), name='criar'),
    path('<slug:empresa>/card/<slug:slug>/editar/', CardEditView.as_view(), name='editar'),
    path('<slug:empresa>/card/<slug:slug>/', CardDetailView.as_view(), name='detalhe'),
    path('<slug:empresa>/card/conteudo/<int:pk>/', EmpresaEditView.as_view(), name='conteudo'),
    path('all-cards/', AllCardsListView.as_view(), name='todos-cards'),


    # path('marcas/', Marcas.as_view(), name='marcas'),
    # path('marcas/bild/', Bild.as_view(), name='bild'),
    # path('marcas/perplan/', Perplan.as_view(), name='perplan'),
] 