from django.urls import path, re_path
from .views import UsusarioLoginView, RegistrarView, LogoutView, TrocarSenha, EsqueceuSenhaFormView, \
    EsqueceuSenhaLink, ReenviarEmailAtivacao, ativar_conta, MinhaConta, verificar_email, DesativarConta, PerfilPF, PerfilPJ, \
    MinhaContaPF, MinhaContaPJ

app_name = 'usuarios'

urlpatterns = [
    path('login/', UsusarioLoginView.as_view(), name='login'),
    path('registrar/', RegistrarView.as_view(), name='registrar'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('trocar-senha/', TrocarSenha.as_view(), name="trocar-senha"),
    path('esqueceu-senha-form/', EsqueceuSenhaFormView.as_view(), name="esqueceu-senha-form"),
    path('esqueceu-senha-link/<uidb64>/<token>/', EsqueceuSenhaLink.as_view(), name="esqueceu-senha-link"),
    path('ativar-conta/<uidb64>/<token>/', ativar_conta, name="ativar-conta"),
    path('reenviar-email-ativacao/', ReenviarEmailAtivacao.as_view(), name='reenviar-email-ativacao'),
    path('minha-conta/<str:username>/', MinhaConta.as_view(), name='minha-conta'),
    path('minha-conta-pf/<str:username>/', MinhaContaPF.as_view(), name='minha-conta-pf'),
    path('minha-conta-pj/<str:username>/', MinhaContaPJ.as_view(), name='minha-conta-pj'),
    path('verificar-email/', verificar_email, name='verificar-email'),
    path('desativar-conta/<str:id>/', DesativarConta.as_view(), name='desativar-conta'),
    path('perfil-pf/', PerfilPF.as_view(), name='perfil-pf'),
    path('perfil-pj/', PerfilPJ.as_view(), name='perfil-pj'),
]