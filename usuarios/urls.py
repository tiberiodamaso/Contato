from django.urls import path
from .views import LoginView, RegistrarView, LogoutView, TrocarSenha, EsqueceuSenhaFormView, EsqueceuSenhaLink, ativar_conta

app_name = 'usuarios'

urlpatterns = [
    path('login/', LoginView.as_view(), name='login'),
    path('registrar/', RegistrarView.as_view(), name='registrar'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('trocar-senha/', TrocarSenha.as_view(), name="trocar-senha"),
    # resetar senha
    path('esqueceu-senha-form/', EsqueceuSenhaFormView.as_view(), name="esqueceu-senha-form"),
    path('esqueceu-senha-link/<uidb64>/<token>/', EsqueceuSenhaLink.as_view(), name="esqueceu-senha-link"),

    path(r'^ativar-conta/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        ativar_conta, name='ativar-conta'),
]