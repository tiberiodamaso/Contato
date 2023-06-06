from django.urls import path
from .views import HomeView, Marcas, Bild, Perplan
from cards.views import CardEditView, CardListView, CardDashboardView, CardDetailView, TodosCardsListView, CardCreateView, EmpresaDashboardView, ConteudoCreateView, CardDeleteView
from core.views import GetMunicipios, GetSubcategorias


app_name = 'core'

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('<slug:empresa>/dashboard/', EmpresaDashboardView.as_view(), name='dashboard-empresa'),
    path('<slug:empresa>/dashboard/<slug:slug>/', CardDashboardView.as_view(), name='dashboard-card'),
    path('<slug:empresa>/cards/', CardListView.as_view(), name='lista'),
    path('card/criar/', CardCreateView.as_view(), name='criar'),
    path('<slug:empresa>/card/editar/<slug:slug>/', CardEditView.as_view(), name='editar'),
    path('<slug:empresa>/card/deletar/<slug:slug>/', CardDeleteView.as_view(), name='deletar'),
    path('<slug:empresa>/card/<slug:slug>/', CardDetailView.as_view(), name='detalhe'),
    path('<slug:empresa>/card/conteudo/<slug:slug>/', ConteudoCreateView.as_view(), name='conteudo'),
    path('todos-cards/', TodosCardsListView.as_view(), name='todos-cards'),

    # POPULAR FORMS
    path('get_municipios/', GetMunicipios.as_view(), name='get-municipios'),
    path('get_subcategorias/', GetSubcategorias.as_view(), name='get-subcategorias'),

    # path('marcas/', Marcas.as_view(), name='marcas'),
    # path('marcas/bild/', Bild.as_view(), name='bild'),
    # path('marcas/perplan/', Perplan.as_view(), name='perplan'),
] 