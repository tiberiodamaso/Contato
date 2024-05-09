from django.urls import path
from .views import HomeView
from cards.views import Editar, Listar, Dashboard, Detalhar, Todos, \
    Criar, Modelos, RelatorioPJ, CriarAnuncioPF, ListarAnuncioPF, Deletar, Pesquisar, ExcluirAnuncioPF, \
    EditarAnuncioPF, TrocarModelo, ListarCardsPJ, CriarCardPJ, DetalharCardPJ, ListarAnuncioPJ, EditarCardPJ, ExcluirCardPJ, CriarAnuncioPJ, EditarAnuncioPJ
from core.views import GetMunicipios, GetSubcategorias, PoliticaDePrivacidade, TermosDeUso


app_name = 'core'

urlpatterns = [

    # VIEWS COMUNS
    path('', HomeView.as_view(), name='home'),
    path('todos-cards/', Todos.as_view(), name='todos-cards'),
    path('pesquisar/', Pesquisar.as_view(), name='pesquisar'),
    path('card/modelos/', Modelos.as_view(), name='modelos'),
    path('card/trocar-modelo/', TrocarModelo.as_view(), name='trocar-modelo'),

    # CARDS PF
    path('card-pf/criar/', Criar.as_view(), name='criar'),
    path('<slug:empresa>/card-pf/', Listar.as_view(), name='lista'),
    path('<slug:empresa>/card-pf/<slug:slug>/', Detalhar.as_view(), name='detalhe'),
    path('<slug:empresa>/card-pf/editar/<slug:slug>/', Editar.as_view(), name='editar'),
    path('<slug:empresa>/card-pf/deletar/<slug:slug>/', Deletar.as_view(), name='deletar'),
    path('<slug:empresa>/card-pf/dashboard/<slug:slug>/', Dashboard.as_view(), name='dashboard-card'),
    path('<slug:empresa>/card-pf/anuncio/criar/<slug:slug>/', CriarAnuncioPF.as_view(), name='criar-anuncio-pf'),
    path('<slug:empresa>/card-pf/anuncio/listar/<slug:slug>/', ListarAnuncioPF.as_view(), name='listar-anuncio-pf'),
    path('<slug:empresa>/card-pf/anuncio/editar/<int:pk>/', EditarAnuncioPF.as_view(), name='editar-anuncio-pf'),
    path('<slug:empresa>/card-pf/anuncio/excluir/<int:pk>/', ExcluirAnuncioPF.as_view(), name='excluir-anuncio-pf'),

    # CARDS PJ
    path('card-pj/criar/', CriarCardPJ.as_view(), name='criar-card-pj'),
    path('<slug:empresa>/card-pj/<slug:slug>/', DetalharCardPJ.as_view(), name='detalhar-card-pj'),
    path('<slug:empresa>/card-pj/', ListarCardsPJ.as_view(), name='listar-cards-pj'),
    path('<slug:empresa>/card-pj/editar/<slug:slug>/', EditarCardPJ.as_view(), name='editar-card-pj'),
    path('<slug:empresa>/card-pj/excluir/<slug:slug>/', ExcluirCardPJ.as_view(), name='excluir-card-pj'),
    path('<slug:empresa>/card-pj/anuncio/criar/', CriarAnuncioPJ.as_view(), name='criar-anuncio-pj'),
    path('<slug:empresa>/card-pj/anuncio/listar/', ListarAnuncioPJ.as_view(), name='listar-anuncio-pj'),
    path('<slug:empresa>/card-pj/anuncio/editar/<slug:slug>/', EditarAnuncioPJ.as_view(), name='editar-anuncio-pj'),
    path('<slug:empresa>/relatorio-pj/', RelatorioPJ.as_view(), name='relatorio-pj'),

    # POPULAR FORMS
    path('get-municipios/', GetMunicipios.as_view(), name='get-municipios'),
    path('get-subcategorias/', GetSubcategorias.as_view(), name='get-subcategorias'),

    # TERMOS
    path('termos-de-uso/', TermosDeUso.as_view(), name='termos-de-uso'),
    path('politica-de-privacidade/', PoliticaDePrivacidade.as_view(), name='politica-de-privacidade'),

] 