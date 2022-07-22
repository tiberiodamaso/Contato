from django.urls import path
from .views import UsuarioLoginView, UsuarioRegistrarView

app_name = 'usuarios'

urlpatterns = [
    path('login/', UsuarioLoginView.as_view(), name='login'),
    path('registrar/', UsuarioRegistrarView.as_view(), name='registrar'),
]