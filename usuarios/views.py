from django.contrib.auth.views import LoginView, LogoutView
from django.views.generic import CreateView, TemplateView
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth.views import PasswordChangeView, LogoutView, PasswordResetView, PasswordResetDoneView, PasswordResetConfirmView, PasswordResetCompleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.hashers import make_password
from django.contrib import auth, messages
from django.contrib.auth import login as auth_login
from django.urls import reverse, reverse_lazy
from .forms import UsuarioAuthenticationForm, UsuarioRegistrationForm, TrocaSenhaForm, EsqueceuSenhaForm, EsqueceuSenhaLinkForm
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template.loader import render_to_string
from .tokens import account_activation_token
from django.core.mail import EmailMessage
from django.template.defaultfilters import slugify
from .models import Usuario
from django.shortcuts import redirect
from cards.models import Card


class LoginView(LoginView):
    template_name = 'usuarios/login.html'
    form_class = UsuarioAuthenticationForm

    def get_success_url(self):
        user = self.request.user
        if user.is_staff:
            empresa = self.request.user.empresa_gerentes.first().slug
            return reverse('core:dashboard-empresa', kwargs={'empresa': empresa})
        else:
            empresa = self.request.user.empresa_vendedores.first().slug
            slug = self.request.user.cards.first().slug
            return reverse('core:dashboard-card', kwargs={'empresa': empresa, 'slug': slug})


class LogoutView(LogoutView):
    template_name = 'core/home.html'


class RegistrarView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = Usuario
    template_name = 'usuarios/registrar.html'
    success_url = reverse_lazy('usuarios:registrar')
    form_class = UsuarioRegistrationForm
    success_message = "Corretor cadastrado com sucesso! Um email foi enviado com instruções de acesso."

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        empresa = self.request.user.empresa_gerentes.first()
        context['empresa'] = empresa
        return context

    def form_valid(self, form):
        """If the form is valid, save the associated model."""
        novo_usuario = form.save()
        empresa = self.request.user.empresa_gerentes.first()
        empresa.vendedores.add(novo_usuario)
        empresa.save()

        # Envia email para ativação da conta com o password
        current_site = get_current_site(self.request)
        subject = 'Ative a sua conta'
        to = novo_usuario.email
        context = {'usuario': novo_usuario, 'dominio': current_site.domain, 'uid': urlsafe_base64_encode(force_bytes(novo_usuario.pk)),
                   'token': account_activation_token.make_token(novo_usuario), 'password': form.data['password1']}
        body = render_to_string('usuarios/email-ativacao.html', context=context)
        msg = EmailMessage(subject, body, to=[to])
        msg.content_subtype = "html"  # Main content is now text/html
        msg.send()

        return super().form_valid(form)


class TrocarSenha(LoginRequiredMixin, SuccessMessageMixin, PasswordChangeView):
    form_class = TrocaSenhaForm
    template_name = 'usuarios/trocar-senha.html'
    # success_url = reverse_lazy('core:editar')
    success_message = 'Senha alterada com sucesso!'

    # def get_context_data(self, **kwargs):
    #     context = super().get_context_data(**kwargs)
    #     usuario = self.request.user
    #     slug = usuario.cards.first().slug
    #     context['slug'] = slug
    #     return context

    def get_success_url(self):
        usuario = self.request.user
        empresa = usuario.empresa_vendedores.first().slug
        slug = usuario.cards.first().slug
        return reverse ('core:editar', kwargs={'empresa':empresa, 'slug':slug})


class EsqueceuSenhaFormView(SuccessMessageMixin, PasswordResetView):
    template_name = 'usuarios/esqueceu-senha-form.html'
    form_class = EsqueceuSenhaForm
    email_template_name = 'usuarios/corpo-email-esqueceu-senha.html'
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

        # Cria Card para o usuário que ativou a conta
        empresa = usuario.empresa_vendedores.first()
        card = Card.objects.create(empresa=empresa, whatsapp='16111111111', facebook='https://facebook.com/meunome',
        instagram='https://instagram.com/meunome', linkedin='https://linkedin/in/meunome', telefone='16111111111',
        usuario=usuario)

        auth_login(request, usuario)
        return redirect('usuarios:trocar-senha')
        # return HttpResponse('Obrigado por confirmar seu e-mail. Agora você pode fazer login.')
    else:
        return HttpResponse('Link de ativação inválido!')
