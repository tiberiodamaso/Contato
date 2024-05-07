from django.urls import path
from .views import HomeView
from cards.views import Editar, Listar, Dashboard, Detalhar, Todos, \
    Criar, Modelos, RelatorioPJ, CriarAnuncioPF, ListarAnuncioPF, Deletar, Pesquisar, ExcluirAnuncioPF, \
    EditarAnuncioPF, TrocarModelo, ListarCardsPJ, CriarCardPJ, DetalharCardPJ, ListarAnunciosPJ
from core.views import GetMunicipios, GetSubcategorias, PoliticaDePrivacidade, TermosDeUso


app_name = 'core'

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('<slug:empresa>/dashboard/<slug:slug>/', Dashboard.as_view(), name='dashboard-card'),
    path('<slug:empresa>/cards-pf/', Listar.as_view(), name='lista'),
    path('card-pf/criar/', Criar.as_view(), name='criar'),
    path('card/modelos/', Modelos.as_view(), name='modelos'),
    path('card/trocar-modelo/', TrocarModelo.as_view(), name='trocar-modelo'),
    path('<slug:empresa>/card/editar/<slug:slug>/', Editar.as_view(), name='editar'),
    path('<slug:empresa>/card/deletar/<slug:slug>/', Deletar.as_view(), name='deletar'),
    path('<slug:empresa>/card/<slug:slug>/', Detalhar.as_view(), name='detalhe'),
    path('<slug:empresa>/card/anuncio/criar/<slug:slug>/', CriarAnuncioPF.as_view(), name='criar-anuncio-pf'),
    path('<slug:empresa>/card/anuncio/listar/<slug:slug>/', ListarAnuncioPF.as_view(), name='listar-anuncio-pf'),
    path('<slug:empresa>/card/anuncio/excluir/<int:pk>/', ExcluirAnuncioPF.as_view(), name='excluir-anuncio-pf'),
    path('<slug:empresa>/card/anuncio/editar/<int:pk>/', EditarAnuncioPF.as_view(), name='editar-anuncio-pf'),
    path('todos-cards/', Todos.as_view(), name='todos-cards'),
    path('pesquisar/', Pesquisar.as_view(), name='pesquisar'),

    # CARDS PJ
    path('card-pj/criar/', CriarCardPJ.as_view(), name='criar-card-pj'),
    path('<slug:empresa>/card-pj/<slug:slug>/', DetalharCardPJ.as_view(), name='detalhar-card-pj'),
    path('<slug:empresa>/relatorio-pj/', RelatorioPJ.as_view(), name='relatorio-pj'),
    path('<slug:empresa>/cards-pj/', ListarCardsPJ.as_view(), name='listar-cards-pj'),
    path('<slug:empresa>/anuncios-pj/', ListarAnunciosPJ.as_view(), name='listar-anuncios-pj'),

    # POPULAR FORMS
    path('get-municipios/', GetMunicipios.as_view(), name='get-municipios'),
    path('get-subcategorias/', GetSubcategorias.as_view(), name='get-subcategorias'),

    # TERMOS
    path('termos-de-uso/', TermosDeUso.as_view(), name='termos-de-uso'),
    path('politica-de-privacidade/', PoliticaDePrivacidade.as_view(), name='politica-de-privacidade'),

] 