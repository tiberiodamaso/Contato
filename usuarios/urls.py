from django.urls import path, re_path
from .views import LoginView, RegistrarView, LogoutView, TrocarSenha, EsqueceuSenhaFormView, EsqueceuSenhaLink, ativar_conta

app_name = 'usuarios'

urlpatterns = [
    path('login/', LoginView.as_view(), name='login'),
    path('registrar/', RegistrarView.as_view(), name='registrar'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('trocar-senha/', TrocarSenha.as_view(), name="trocar-senha"),
    path('esqueceu-senha-form/', EsqueceuSenhaFormView.as_view(), name="esqueceu-senha-form"),
    path('esqueceu-senha-link/<uidb64>/<token>/', EsqueceuSenhaLink.as_view(), name="esqueceu-senha-link"),
    path('ativar-conta/<uidb64>/<token>/', ativar_conta, name="ativar-conta"),

    # re_path(r'^ativar-conta/[0-9A-Za-z_\-]+/[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20}/',
    #     ativar_conta, name='ativar-conta'),
    # re_path(r'^ativar-conta/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/',
    #     ativar_conta, name='ativar-conta'),
]