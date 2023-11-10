from django.urls import path
from .views import HomeView
from cards.views import Editar, Listar, Dashboard, Detalhar, Todos, \
    Criar, DashboardEmpresa, ConteudoCriar, Deletar, Pesquisar, ConteudoExcluir, ConteudoEditarNome, ConteudoEditarDescricao
from core.views import GetMunicipios, GetSubcategorias, PoliticaDePrivacidade, TermosDeUso, Pagamento


app_name = 'core'

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('<slug:empresa>/dashboard/', DashboardEmpresa.as_view(), name='dashboard-empresa'),
    path('<slug:empresa>/dashboard/<slug:slug>/', Dashboard.as_view(), name='dashboard-card'),
    path('<slug:empresa>/cards/', Listar.as_view(), name='lista'),
    path('card/criar/', Criar.as_view(), name='criar'),
    path('<slug:empresa>/card/editar/<slug:slug>/', Editar.as_view(), name='editar'),
    path('<slug:empresa>/card/deletar/<slug:slug>/', Deletar.as_view(), name='deletar'),
    path('<slug:empresa>/card/<slug:slug>/', Detalhar.as_view(), name='detalhe'),
    path('<slug:empresa>/card/conteudo/<slug:slug>/', ConteudoCriar.as_view(), name='conteudo-criar'),
    path('<slug:empresa>/card/conteudo/excluir/<int:pk>/', ConteudoExcluir.as_view(), name='conteudo-excluir'),
    path('<slug:empresa>/card/conteudo/editar/nome/<int:pk>/', ConteudoEditarNome.as_view(), name='conteudo-editar-nome'),
    path('<slug:empresa>/card/conteudo/editar/descricao/<int:pk>/', ConteudoEditarDescricao.as_view(), name='conteudo-editar-descricao'),
    path('todos-cards/', Todos.as_view(), name='todos-cards'),
    path('pesquisar/', Pesquisar.as_view(), name='pesquisar'),
    path('pagamento/', Pagamento.as_view(), name='pagamento'),

    # POPULAR FORMS
    path('get_municipios/', GetMunicipios.as_view(), name='get-municipios'),
    path('get_subcategorias/', GetSubcategorias.as_view(), name='get-subcategorias'),

    # TERMOS
    path('termos-de-uso/', TermosDeUso.as_view(), name='termos-de-uso'),
    path('politica-de-privacidade/', PoliticaDePrivacidade.as_view(), name='politica-de-privacidade'),

    # PAGAMENTO
    # path('pagamento/', Pagamento.as_view(), name='pagamento'),
] 