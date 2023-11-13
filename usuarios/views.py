import requests
from typing import Any, Dict
from datetime import datetime
from django.contrib.auth.views import LoginView, LogoutView
from django.views.generic import CreateView, TemplateView, View, ListView
from django.views.generic.base import TemplateResponseMixin
from django.conf import settings
from django.http import HttpResponseRedirect, JsonResponse
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
from assinaturas.models import Assinatura

class UsusarioLoginView(LoginView):
    template_name = 'usuarios/login.html'
    form_class = UsuarioAuthenticationForm

    def get_success_url(self):
        usuario = self.request.user
        card = usuario.cards.first()
        return reverse('core:home')

    def verifica_status_assinatura(self, usuario):
        # usuario = self.request.user
        assinatura = usuario.assinaturas.all().last()

        if not assinatura:
            return 'pendente'

        assinatura_id = assinatura.assinatura_id
        access_token = settings.MERCADOPAGO_ACCESS_TOKEN

        # Defina a URL da API do MercadoPago
        url = f'https://api.mercadopago.com/preapproval/{assinatura_id}'

        # Defina o cabeçalho com o token de acesso e o tipo de conteúdo
        headers = {
            'Authorization': f'Bearer {access_token}',
        }

        if assinatura:
            # Faça a solicitação GET para a API do MercadoPago
            response = requests.get(url, headers=headers)

        # Verifique se a solicitação foi bem-sucedida
            if response.status_code == 200:
                data = response.json()
                context = {}
                assinatura.status = data['status']
                assinatura.save()
                return assinatura.status
                # return self.render_to_response(context=context)
            else:
                # Lidar com erros de solicitação, se necessário
                error_message = response.text
                return JsonResponse({'error': error_message}, status=response.status_code)
    
    def post(self, request):

        # recupera formulário
        form = self.get_form()

        # recupera usuário no banco de dados com base no e-mail inserido no formulário
        usuario = Usuario.objects.filter(email=form['username'].value())
        if usuario:
            usuario = usuario[0]
            status = self.verifica_status_assinatura(usuario)
        else:
            messages.error(self.request, "e-mail não encontrado.")
            super().form_invalid(form)

        # se usuário existe e não está ativo, chama tela de reenviar email de ativação
        if usuario and not usuario.is_active:
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

    def form_invalid(self, form):
        # Acesse os erros do formulário
        errors = form.errors.as_data()

        # Crie uma lista para armazenar mensagens de erro personalizadas
        error_messages = []

        # Itere sobre os erros e adicione mensagens personalizadas
        for field, error_list in errors.items():
             # Adicione mensagens de erro personalizadas
                if field == 'email' and 'unique' in errors['email'][0].code:
                    error_messages.append(form.error_messages['email_taken'])
                elif field == 'password2' and 'password_mismatch' in errors['password2'][0].code:
                    error_messages.append(form.error_messages['password_mismatch'])
                else:
                    # Adicione outras mensagens de erro conforme necessário
                    error_messages.append(f"Campo '{form.fields[field].label}' é inválido: {error.message}")

        return self.render_to_response(self.get_context_data(form=form, error_messages=error_messages))


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


class MinhaConta(LoginRequiredMixin, ListView):

    template_name = 'usuarios/minha-conta.html'
    model = Assinatura
    context_object_name = 'assinaturas'


    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context['assinaturas'] = []
        assinaturas = self.request.user.assinaturas.all()
        access_token = settings.MERCADOPAGO_ACCESS_TOKEN

        # Defina o cabeçalho com o token de acesso do 
        headers = {
            'Authorization': f'Bearer {access_token}',
        }

        for assinatura in assinaturas:
            url = f'https://api.mercadopago.com/preapproval/{assinatura.assinatura_id}'

            # Faça a solicitação GET para a API do MercadoPago
            response = requests.get(url, headers=headers)

            # Verifique se a solicitação foi bem-sucedida
            if response.status_code == 200:
                data = response.json()
                formato_da_string = "%Y-%m-%dT%H:%M:%S.%f%z"
                assinatura.status = data['status']
                assinatura.start_date = datetime.strptime(data['date_created'], formato_da_string)
                assinatura.next_payment_date = datetime.strptime(data['next_payment_date'], formato_da_string)
                assinatura.save()
                context['assinaturas'].append(assinatura)
            else:
                # Lidar com erros de solicitação, se necessário
                error_message = response.text
                return JsonResponse({'error': error_message}, status=response.status_code)
        
        return context
        

def ativar_conta(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        usuario = Usuario.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, Usuario.DoesNotExist):
        usuario = None
    if usuario is not None and account_activation_token.check_token(usuario, token):
        usuario.is_active = True
        usuario.save()
        return render(request, 'usuarios/sucesso-ativacao.html')
    else:
        return render(request, 'usuarios/falha-ativacao.html')


def verificar_email(request):
    usuario = request.user
    email = request.GET.get('email', None)

    if email and Usuario.objects.filter(email=email).exists():
        return HttpResponse('Já existe uma conta com esse email')
    else:
        return HttpResponse('')