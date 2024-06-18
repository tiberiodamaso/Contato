import requests
from typing import Any, Dict
from datetime import datetime
from django.contrib.auth.views import LoginView, LogoutView
from django.views.generic import CreateView, TemplateView, View, ListView, DeleteView
from django.views.generic.base import TemplateResponseMixin
from django.conf import settings
from django.http import HttpResponseRedirect, JsonResponse
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth.views import PasswordChangeView, LogoutView, PasswordResetView, PasswordResetDoneView, PasswordResetConfirmView, PasswordResetCompleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.hashers import make_password
from django.contrib import auth, messages
from django.contrib.auth import login as auth_login
from django.urls import reverse, reverse_lazy
from django.http import HttpResponse
from .forms import UsuarioAuthenticationForm, UsuarioRegistrationForm, TrocaSenhaForm, EsqueceuSenhaForm, EsqueceuSenhaLinkForm, PerfilFormPF, PerfilFormPJ
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template.loader import render_to_string
from .tokens import account_activation_token
from django.core.mail import EmailMessage
from django.core.exceptions import ObjectDoesNotExist
from django.template.defaultfilters import slugify
from .models import Usuario, Perfil
from cards.models import Empresa, Card
from django.shortcuts import redirect, render
from compras.models import Relatorio, CartaoPF, CartaoPJ, Ad
from django.contrib.auth.hashers import check_password


class UsusarioLoginView(LoginView):
    template_name = 'usuarios/login.html'
    form_class = UsuarioAuthenticationForm

    def get_success_url(self):
        usuario = self.request.user
        card = usuario.cards.first()
        return reverse('usuarios:minha-conta', kwargs={'username': usuario.username})

    def post(self, request, *args, **kwargs):
        # Obtendo os dados do formulário de login
        email = request.POST.get('username')
        password = request.POST.get('password')
        recaptcha_token = request.POST.get('recaptcha_token')

        # Verificar o token do reCAPTCHA
        recaptcha_response = requests.post('https://www.google.com/recaptcha/api/siteverify', data={
            'secret': settings.RECAPTCHA_PRIVATE_KEY,
            'response': recaptcha_token
        })
        recaptcha_data = recaptcha_response.json()
        if recaptcha_data['success']:
            # Verificando se o usuário com o email existe
            try:
                user = Usuario.objects.get(email=email)
                # Verifica se senha está correta
                if not check_password(password, user.password):
                    messages.error(request, 'Falha na autenticação - Senha incorreta')
                    return HttpResponseRedirect(reverse('usuarios:login'))
                
                #verifica se usuario não é ativo para redirecionar para reenviar e-mail
                if not user.is_active:
                    # Se o usuário existe, mas não está ativo
                    # Redirecionar para o template de reenvio de email de ativação
                    request.session['email'] = email
                    return HttpResponseRedirect(reverse('usuarios:reenviar-email-ativacao'))
                    # return HttpResponseRedirect(reverse('usuarios:reenviar-email-ativacao', kwargs={'username': user.username}))
                    # return TemplateResponse(request, 'resend_activation_email.html')

                # Se o usuário existe e está ativo, tentar fazer login
                return super().post(request, *args, **kwargs)
            except Usuario.DoesNotExist:
                # Se o usuário não existe, retornar mensagem de erro
                messages.error(self.request, "Usuário não encontrado. Por favor, verifique o email.")
                return HttpResponseRedirect(reverse('usuarios:login'))
        else:
            messages.error(self.request, "Por favor, complete o reCAPTCHA.")


class LogoutView(LogoutView):
    template_name = 'core/home.html'


class RegistrarView(SuccessMessageMixin, CreateView):
    model = Usuario
    template_name = 'usuarios/registrar.html'
    success_url = reverse_lazy('usuarios:login')
    form_class = UsuarioRegistrationForm
    success_message = "Conta criada com sucesso! Um email foi enviado com instruções de acesso."


    def form_valid(self, form):
        recaptcha_token = self.request.POST.get('recaptcha_token')

        # Verificar o token do reCAPTCHA
        recaptcha_response = requests.post('https://www.google.com/recaptcha/api/siteverify', data={
            'secret': settings.RECAPTCHA_PRIVATE_KEY,
            'response': recaptcha_token
        })
        recaptcha_data = recaptcha_response.json()
        if recaptcha_data['success']:
            novo_usuario = form.save()

            # Envia email para ativação da conta com o password
            current_site = get_current_site(self.request)
            subject = 'Meu contato - ative a sua conta'
            to = novo_usuario.email
            context = {'usuario': novo_usuario, 'dominio': current_site.domain, 'uid': urlsafe_base64_encode(force_bytes(novo_usuario.pk)),
                    'token': account_activation_token.make_token(novo_usuario)}
            body = render_to_string(
                'usuarios/email-ativacao.html', context=context)
            msg = EmailMessage(subject, body, to=[to])
            msg.content_subtype = "html"  # Main content is now text/html
            msg.send()
        else:
            messages.error(self.request, "Por favor, complete o reCAPTCHA.")

        return super().form_valid(form)

    def form_invalid(self, form):
        # Acesse os erros do formulário
        errors = form.errors.as_data()

        # Crie uma lista para armazenar mensagens de erro personalizadas
        error_messages = []

        # Itere sobre os erros e adicione mensagens personalizadas
        for field, error_list in errors.items():
            for error in error_list:
                if error.code in form.error_messages.keys():
                    error_messages.append(form.error_messages[error.code])
                else:
                    error_messages.append(f"Campo '{form.fields[field].label}' é inválido.")

        return self.render_to_response(self.get_context_data(form=form, error_messages=error_messages))


class TrocarSenha(LoginRequiredMixin, SuccessMessageMixin, PasswordChangeView):
    form_class = TrocaSenhaForm
    template_name = 'usuarios/trocar-senha.html'
    success_message = 'Senha alterada com sucesso!'

    def get_success_url(self):
        usuario = self.request.user
        card = Card.objects.filter(proprietario=usuario)
        return reverse('usuarios:minha-conta', kwargs={'username': usuario.username})

    def form_valid(self, form):
        recaptcha_token = self.request.POST.get('recaptcha_token')

        # Verificar o token do reCAPTCHA
        recaptcha_response = requests.post('https://www.google.com/recaptcha/api/siteverify', data={
            'secret': settings.RECAPTCHA_PRIVATE_KEY,
            'response': recaptcha_token
        })
        recaptcha_data = recaptcha_response.json()
        if recaptcha_data['success']:
            form.save()
        else:
            messages.error(self.request, "Por favor, complete o reCAPTCHA.")
        return super().form_valid(form)


class EsqueceuSenhaFormView(SuccessMessageMixin, PasswordResetView):
    template_name = 'usuarios/esqueceu-senha-form.html'
    form_class = EsqueceuSenhaForm
    email_template_name = 'usuarios/corpo-email-esqueceu-senha.html'
    html_email_template_name = 'usuarios/corpo-email-esqueceu-senha.html'
    subject_template_name = "usuarios/assunto.txt"
    success_url = reverse_lazy('usuarios:login')
    success_message = 'Enviamos um e-mail com instruções para redefinir sua senha, se uma conta existe com o e-mail que você digitou você deve recebê-lo em breve.'

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        if form.is_valid():
            recaptcha_token = self.request.POST.get('recaptcha_token')

            # Verificar o token do reCAPTCHA
            recaptcha_response = requests.post('https://www.google.com/recaptcha/api/siteverify', data={
                'secret': settings.RECAPTCHA_PRIVATE_KEY,
                'response': recaptcha_token
            })
            recaptcha_data = recaptcha_response.json()
            if recaptcha_data['success']:
                return super().post(request, *args, **kwargs)
            else:
                messages.error(self.request, "Por favor, complete o reCAPTCHA.")
        else:
            return self.form_invalid(form)


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
        # context['username'] = kwargs['username']
        return context

    def post(self, request, **kwargs):
        email = request.session.pop('email')
        
        # Verifique se o usuário existe no banco de dados
        try:
            usuario = Usuario.objects.get(email=email)
        except Usuario.DoesNotExist:
            # Usuário não encontrado
            messages.error(request, 'Usuário não encontrado')
            return self.render_to_response(self.get_context_data())

        except Usuario.MultipleObjectsReturned:
            # Mais de um usuário encontrado
            messages.error(request, 'Mais de um usuário encontrado. Entre em contato com o suporte.')
            return self.render_to_response(self.get_context_data())


        # Envia email para ativação da conta com o password
        current_site = get_current_site(self.request)
        subject = 'Meu Contato - ative a sua conta'
        to = usuario.email
        context = {'usuario': usuario, 'dominio': current_site.domain, 'uid': urlsafe_base64_encode(force_bytes(usuario.pk)),
                   'token': account_activation_token.make_token(usuario)}
        body = render_to_string(
            'usuarios/email-ativacao.html', context=context)
        msg = EmailMessage(subject, body, to=[to])
        msg.content_subtype = "html"  # Main content is now text/html
        msg.send()

        messages.success(request, 'E-mail enviado com sucesso')
        return self.get_success_url()


class MinhaConta(LoginRequiredMixin, ListView):

    model = Usuario

    def get_template_names(self):
        try:
            perfil = self.request.user.perfil
            if self.request.user.perfil.is_pj:
                return 'usuarios/minha-conta-pj.html'
            else:
                return 'usuarios/minha-conta-pf.html'
        except:
            return 'usuarios/minha-conta.html'


    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        usuario = self.request.user
        empresa = usuario.empresas.first()
        card = Card.objects.filter(proprietario=usuario).first()
        anuncios_criados = empresa.anuncios.all() if empresa else None
        produtos = []
        pgto_cartao_pf = False
        try:
            comprou_cartao_pf = usuario.cartoespf.all() # cartoes comprados pf
            comprou_cartao_pj = usuario.cartoespj.all() # cartoes comprados pj
            comprou_anuncio = usuario.ads.all() # anuncios comprados
            comprou_relatorio = usuario.relatorios.all() # relatorios comprados
            cards_criados = usuario.cards.all() # cards criados pelo usuário depois de pagar pela compra
            anuncio = comprou_anuncio
            relatorio = comprou_relatorio

            if comprou_cartao_pf:
                for cartao_pf in comprou_cartao_pf:
                    produtos.append(cartao_pf)
                    if cartao_pf.status == 'Aprovado':
                        pgto_cartao_pf = True

            if comprou_cartao_pj:
                for cartao_pj in comprou_cartao_pj:
                    produtos.append(cartao_pj)

            if comprou_anuncio:
                for ad in comprou_anuncio:
                    produtos.append(ad)

            if comprou_relatorio:
                for rel in comprou_relatorio:
                    produtos.append(rel)

            context['usuario'] = usuario
            context['comprou_cartao_pf'] = comprou_cartao_pf
            context['comprou_cartao_pj'] = comprou_cartao_pj
            context['comprou_anuncio'] = comprou_anuncio
            context['anuncio'] = anuncio
            context['cards_criados'] = cards_criados
            context['card'] = card
            context['anuncios_criados'] = anuncios_criados
            context['comprou_relatorio'] = comprou_relatorio
            context['relatorio'] = relatorio
            context['numero_cards_criados'] = len(cards_criados)
            context['numero_anuncios_criados'] = len(anuncios_criados) if anuncios_criados else 0
            context['numero_cartoes_pj'] = len(comprou_cartao_pj)
            context['produtos'] = produtos
            context['pgto_cartao_pf'] = pgto_cartao_pf
        except ObjectDoesNotExist as err:
            print(err)
            card = None
        
        return context
        

class DesativarConta(LoginRequiredMixin, DeleteView):
    model = Usuario

    def get_template_names(self):
        try:
            perfil = self.request.user.perfil
            if self.request.user.perfil.is_pj:
                return 'usuarios/minha-conta-pj.html'
            else:
                return 'usuarios/minha-conta-pf.html'
        except:
            return 'usuarios/minha-conta.html'

    def get(self, request, *args, **kwargs):
        usuario = Usuario.objects.get(id=kwargs['id'])
        usuario.is_active = False
        usuario.save()
        return redirect(reverse_lazy('usuarios:logout'))


class PerfilPF(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = Perfil
    form_class = PerfilFormPF
    template_name = 'usuarios/perfil-pf.html'
    success_url = reverse_lazy('compras:comprar-cartao-pf')
    success_message = "Informações salvas com sucesso."

    def form_valid(self, form):
        perfil = form.save(commit=False)
        perfil.usuario = self.request.user
        perfil.is_pj = False
        perfil.nome_fantasia = self.request.user.get_full_name()
        perfil.save()

        Empresa.objects.create(
            nome_fantasia = perfil.nome_fantasia,
            cnpj_cpf = form.cleaned_data['cnpj_cpf'],
            proprietario = self.request.user,
            slug = slugify(perfil.nome_fantasia)
        )

        return super().form_valid(form)


class PerfilPJ(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = Perfil
    form_class = PerfilFormPJ
    template_name = 'usuarios/perfil-pj.html'
    success_url = reverse_lazy('compras:comprar-cartao-pj')
    success_message = "Informações salvas com sucesso."

    def form_valid(self, form):
        perfil = form.save(commit=False)
        perfil.usuario = self.request.user
        perfil.is_pj = True
        perfil.nome_fantasia = form.cleaned_data['nome_fantasia']
        perfil.save()

        Empresa.objects.create(
            nome_fantasia = perfil.nome_fantasia,
            cnpj_cpf = form.cleaned_data['cnpj_cpf'],
            proprietario = self.request.user,
            slug = slugify(perfil.nome_fantasia)
        )

        return super().form_valid(form)


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