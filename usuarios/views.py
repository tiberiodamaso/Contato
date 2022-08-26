from django.contrib.auth.views import LoginView, LogoutView
from django.views.generic import CreateView, TemplateView
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth.views import PasswordChangeView, LogoutView, PasswordResetView, PasswordResetDoneView, PasswordResetConfirmView, PasswordResetCompleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.urls import reverse, reverse_lazy
from .forms import UsuarioAuthenticationForm, UsuarioRegistrationForm, TrocaSenhaForm, EsqueceuSenhaForm, EsqueceuSenhaLinkForm
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template.loader import render_to_string
from .tokens import account_activation_token
from django.core.mail import EmailMessage


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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        empresa = self.request.user.empresas.first()
        context['empresa'] = empresa
        return context


class TrocarSenha(LoginRequiredMixin, SuccessMessageMixin, PasswordChangeView):
    form_class = TrocaSenhaForm
    template_name = 'usuarios/trocar-senha.html'
    success_url = reverse_lazy('core:home')
    success_message = 'Senha alterada com sucesso'


class EsqueceuSenhaFormView(SuccessMessageMixin, PasswordResetView):
    template_name = 'usuarios/esqueceu-senha-form.html'
    form_class = EsqueceuSenhaForm
    email_template_name = 'usuarios/corpo-email-esqueceu-senha.html'
    from_email = 'tiberio.mendonca@meucontato.app.br'
    subject_template_name = "usuarios/assunto.txt"
    success_url = reverse_lazy('usuarios:login')
    success_message = 'Enviamos um e-mail com instruções para definir sua senha, se uma conta existe com o e-mail que você digitou você deve recebê-lo em breve.'


class EsqueceuSenhaLink(SuccessMessageMixin, PasswordResetConfirmView):
    form_class = EsqueceuSenhaLinkForm
    success_url = reverse_lazy("usuarios:login")
    template_name = "usuarios/esqueceu-senha-link.html"
    success_message = 'Sua senha foi definida. Você pode ir em frente e fazer login agora.'


def ativar_conta(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        usuario = Usuario.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, Usuario.DoesNotExist):
        usuario = None
    if usuario is not None and account_activation_token.check_token(usuario, token):
        usuario.is_active = True
        usuario.save()
        auth_login(request, usuario)
        return HttpResponse('Obrigado por confirmar seu e-mail. Agora você pode fazer login.')
    else:
        return HttpResponse('Link de ativação inválido!')