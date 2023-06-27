from typing import Any, Dict
from django.contrib.auth.views import LoginView, LogoutView
from django.views.generic import CreateView, TemplateView, View
from django.http import HttpResponseRedirect
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth.views import PasswordChangeView, LogoutView, PasswordResetView, PasswordResetDoneView, PasswordResetConfirmView, PasswordResetCompleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.hashers import make_password
from django.contrib import auth, messages
from django.contrib.auth import login as auth_login
from django.urls import reverse, reverse_lazy
from django.http import HttpResponse
from .forms import UsuarioAuthenticationForm, UsuarioRegistrationForm, TrocaSenhaForm, EsqueceuSenhaForm, EsqueceuSenhaLinkForm
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template.loader import render_to_string
from .tokens import account_activation_token
from django.core.mail import EmailMessage
from django.template.defaultfilters import slugify
from .models import Usuario
from django.shortcuts import redirect, render
from cards.models import Card


class UsusarioLoginView(LoginView):
    template_name = 'usuarios/login.html'
    form_class = UsuarioAuthenticationForm

    def get_success_url(self):
        user = self.request.user
        card = user.cards.first()
        if card:
          return reverse('core:detalhe', kwargs={'empresa': card.slug_empresa, 'slug': card.slug})
        else:
          return reverse('core:criar')
    
    def post(self, request):
        # recupera formulário
        form = self.get_form()
        # recupera usuário no banco de dados com base no e-mail inserido no formulário
        usuario = Usuario.objects.filter(email=form['username'].value())
        # se usuário existe e não está ativo, chama tela de reenviar email de ativação
        if usuario and not usuario[0].is_active:
            return HttpResponseRedirect(reverse('usuarios:reenviar-email-ativacao', kwargs={'username': usuario[0].username}))
        return super().post(self.request)


class LogoutView(LogoutView):
    template_name = 'core/home.html'


class RegistrarView(SuccessMessageMixin, CreateView):
    model = Usuario
    template_name = 'usuarios/registrar.html'
    success_url = reverse_lazy('usuarios:login')
    form_class = UsuarioRegistrationForm
    success_message = "Usuário cadastrado com sucesso! Um email foi enviado com instruções de acesso."


    def form_valid(self, form):
        novo_usuario = form.save()

        # Envia email para ativação da conta com o password
        current_site = get_current_site(self.request)
        subject = 'Ative a sua conta'
        to = novo_usuario.email
        context = {'usuario': novo_usuario, 'dominio': current_site.domain, 'uid': urlsafe_base64_encode(force_bytes(novo_usuario.pk)),
                   'token': account_activation_token.make_token(novo_usuario)}
        body = render_to_string(
            'usuarios/email-ativacao.html', context=context)
        msg = EmailMessage(subject, body, to=[to])
        msg.content_subtype = "html"  # Main content is now text/html
        msg.send()

        return super().form_valid(form)


class TrocarSenha(LoginRequiredMixin, SuccessMessageMixin, PasswordChangeView):
    form_class = TrocaSenhaForm
    template_name = 'usuarios/trocar-senha.html'
    success_message = 'Senha alterada com sucesso!'

    def get_success_url(self):
        usuario = self.request.user
        card = Card.objects.filter(proprietario=usuario)
        return reverse('core:detalhe', kwargs={'empresa': card.slug_empresa, 'slug': card.slug})


class EsqueceuSenhaFormView(SuccessMessageMixin, PasswordResetView):
    template_name = 'usuarios/esqueceu-senha-form.html'
    form_class = EsqueceuSenhaForm
    email_template_name = 'usuarios/corpo-email-esqueceu-senha.html'
    html_email_template_name = 'usuarios/corpo-email-esqueceu-senha.html'
    subject_template_name = "usuarios/assunto.txt"
    success_url = reverse_lazy('usuarios:login')
    success_message = 'Enviamos um e-mail com instruções para redefinir sua senha, se uma conta existe com o e-mail que você digitou você deve recebê-lo em breve.'


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
        # return HttpResponse('Seu card foi ativado com sucesso!')
        return redirect(reverse('usuarios:login'))
    else:
        return render(request, 'usuarios/falha-ativacao.html')


class ReenviarEmailAtivacao(TemplateView):
    template_name = 'usuarios/reenviar-email-ativacao.html'
    
    def get_success_url(self):
        return HttpResponseRedirect(reverse('usuarios:login'))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['username'] = kwargs['username']
        return context

    def post(self, request, **kwargs):
        username = kwargs['username']
        
        usuario = Usuario.objects.get(username=username)

        # Envia email para ativação da conta com o password
        current_site = get_current_site(self.request)
        subject = 'Ative a sua conta'
        to = usuario.email
        context = {'usuario': usuario, 'dominio': current_site.domain, 'uid': urlsafe_base64_encode(force_bytes(usuario.pk)),
                   'token': account_activation_token.make_token(usuario)}
        body = render_to_string(
            'usuarios/email-ativacao.html', context=context)
        msg = EmailMessage(subject, body, to=[to])
        msg.content_subtype = "html"  # Main content is now text/html
        msg.send()

        return self.get_success_url()
