from django.shortcuts import render
from django.contrib.auth.views import LoginView, LogoutView
from .forms import UsuarioAuthenticationForm


class UsuarioLoginView(LoginView):
    template_name = 'usuarios/login.html'
    form_class = UsuarioAuthenticationForm