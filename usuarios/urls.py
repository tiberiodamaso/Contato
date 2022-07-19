from django.urls import path
from .views import UsuarioLoginView

app_name = 'usuarios'

urlpatterns = [
    path('login/', UsuarioLoginView.as_view(), name='login'),
]