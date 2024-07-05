from django.urls import path
from .views import HomeView
from cards.views import EditarCardPF, ListarCardPF, RelatorioPF, DetalharCardPF, Todos, \
        CriarCardPF, Modelos, RelatorioPJ, CriarAnuncioPF, ListarAnuncioPF, ExcluirCardPF, Pesquisar, ExcluirAnuncioPF, \
        EditarAnuncioPF, TrocarModelo, ListarCardPJ, CriarCardPJ, DetalharCardPJ, ListarAnuncioPJ, EditarCardPJ, ExcluirCardPJ, CriarAnuncioPJ, EditarAnuncioPJ, \
        ExcluirAnuncioPJ, AvaliarCard
from core.views import GetMunicipios, GetSubcategorias, PoliticaDePrivacidade, TermosDeUso


app_name = 'core'

urlpatterns = [

    # VIEWS COMUNS
    path('', HomeView.as_view(), name='home'),
    path('todos-cards/', Todos.as_view(), name='todos-cards'),
    path('pesquisar/', Pesquisar.as_view(), name='pesquisar'),
    path('card/modelos/', Modelos.as_view(), name='modelos'),
    path('card/trocar-modelo/', TrocarModelo.as_view(), name='trocar-modelo'),
    path('<slug:empresa>/avaliar/<slug:slug>/', AvaliarCard.as_view(), name='avaliar-card'),

    # PRODUTOS PF
    path('<slug:empresa>/card-pf/criar/', CriarCardPF.as_view(), name='criar-card-pf'),
    path('<slug:empresa>/card-pf/', ListarCardPF.as_view(), name='lista-card-pf'),
    path('<slug:empresa>/card-pf/<slug:slug>/', DetalharCardPF.as_view(), name='detalhar-card-pf'),
    path('<slug:empresa>/card-pf/editar/<slug:slug>/', EditarCardPF.as_view(), name='editar-card-pf'),
    path('<slug:empresa>/card-pf/excluir/<slug:slug>/', ExcluirCardPF.as_view(), name='excluir-card-pf'),
    path('<slug:empresa>/relatorio-pf/<slug:slug>/', RelatorioPF.as_view(), name='relatorio-pf'),
    path('<slug:empresa>/card-pf/anuncio/criar/', CriarAnuncioPF.as_view(), name='criar-anuncio-pf'),
    path('<slug:empresa>/card-pf/anuncio/listar/', ListarAnuncioPF.as_view(), name='listar-anuncio-pf'),
    path('<slug:empresa>/card-pf/anuncio/editar/<int:pk>/', EditarAnuncioPF.as_view(), name='editar-anuncio-pf'),
    path('<slug:empresa>/card-pf/anuncio/excluir/<int:pk>/', ExcluirAnuncioPF.as_view(), name='excluir-anuncio-pf'),

    # PRODUTOS PJ
    path('<slug:empresa>/card-pj/criar/', CriarCardPJ.as_view(), name='criar-card-pj'),
    path('<slug:empresa>/card-pj/', ListarCardPJ.as_view(), name='listar-card-pj'),
    path('<slug:empresa>/card-pj/<slug:slug>/', DetalharCardPJ.as_view(), name='detalhar-card-pj'),
    path('<slug:empresa>/card-pj/editar/<slug:slug>/', EditarCardPJ.as_view(), name='editar-card-pj'),
    path('<slug:empresa>/card-pj/excluir/<slug:slug>/', ExcluirCardPJ.as_view(), name='excluir-card-pj'),
    path('<slug:empresa>/relatorio-pj/', RelatorioPJ.as_view(), name='relatorio-pj'),
    path('<slug:empresa>/card-pj/anuncio/criar/', CriarAnuncioPJ.as_view(), name='criar-anuncio-pj'),
    path('<slug:empresa>/card-pj/anuncio/listar/', ListarAnuncioPJ.as_view(), name='listar-anuncio-pj'),
    path('<slug:empresa>/card-pj/anuncio/editar/<int:pk>/', EditarAnuncioPJ.as_view(), name='editar-anuncio-pj'),
    path('<slug:empresa>/card-pj/anuncio/excluir/<int:pk>/', ExcluirAnuncioPJ.as_view(), name='excluir-anuncio-pj'),

    # POPULAR FORMS
    path('get-municipios/', GetMunicipios.as_view(), name='get-municipios'),
    path('get-subcategorias/', GetSubcategorias.as_view(), name='get-subcategorias'),

    # TERMOS
    path('termos-de-uso/', TermosDeUso.as_view(), name='termos-de-uso'),
    path('politica-de-privacidade/', PoliticaDePrivacidade.as_view(), name='politica-de-privacidade'),

] 