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
]