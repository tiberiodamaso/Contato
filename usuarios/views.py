from django.contrib.auth.views import LoginView, LogoutView
from django.views.generic import CreateView, TemplateView
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib import messages
from django.urls import reverse
from .forms import UsuarioAuthenticationForm, UsuarioRegistrationForm


class LoginView(LoginView):
    template_name = 'usuarios/login.html'
    form_class = UsuarioAuthenticationForm

    def get_success_url(self):
        url = self.get_redirect_url()
        empresa = self.request.user.empresas.all().first().slug
        return url or reverse('core:dashboard', kwargs={'empresa': empresa})


class LogoutView(LogoutView):
    template_name = 'core/home.html'


class RegistrarView(SuccessMessageMixin, CreateView):
    template_name = 'usuarios/registrar.html'
    success_url = '.'
    form_class = UsuarioRegistrationForm
    success_message = "Usuário criado com sucesso"
