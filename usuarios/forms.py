from django.contrib.auth.forms import AuthenticationForm, UserCreationForm, PasswordChangeForm, PasswordResetForm, SetPasswordForm
from django import forms
from .models import Usuario


class UsuarioAuthenticationForm(AuthenticationForm):
    username = forms.CharField(label='Usuário', widget=forms.TextInput(
        attrs={'autofocus': True, 'class': 'form-control'}))
    password = forms.CharField(
        label="Senha",
        strip=False,
        widget=forms.PasswordInput(
            attrs={'autocomplete': 'current-password', 'class': 'form-control'}),
    )


class UsuarioRegistrationForm(UserCreationForm):

    email = forms.EmailField(widget=forms.EmailInput(
        attrs={'class': 'form-control'}), help_text='Informe um e-mail válido')
    first_name = forms.CharField(max_length=50, label='Primeiro nome', widget=forms.TextInput(
        attrs={'class': 'form-control'}), help_text='Somente o primeiro nome do nome, mesmo que composto')
    last_name = forms.CharField(max_length=50, label='Último nome', widget=forms.TextInput(
        attrs={'class': 'form-control'}), help_text='Somente o último nome do sobrenome')
    # empresa = forms.CharField(max_length=50, label='Empresa', widget=forms.TextInput(
    #     attrs={'class': 'form-control'}), help_text='Empresa')

    class Meta:
        model = Usuario
        fields = ('email', 'username', 'first_name', 'last_name')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['username'].widget.attrs['class'] = 'form-control'
        self.fields['username'].label = 'Nome de usuário'
        self.fields['password1'].widget.attrs['class'] = 'form-control'
        self.fields['password2'].widget.attrs['class'] = 'form-control'


class TrocaSenhaForm(PasswordChangeForm):
    old_password = forms.CharField(label='Senha antiga', min_length=8,
                                   widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    new_password1 = forms.CharField(
        label='Nova senha', min_length=8, widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    new_password2 = forms.CharField(
        label='Confirmação', min_length=8, widget=forms.PasswordInput(attrs={'class': 'form-control'}))

    class Meta:
        model = Usuario
        fields = ['old_password', 'new_password1', 'new_password2']


class EsqueceuSenhaForm(PasswordResetForm):
    email = forms.EmailField(
        label=('Email'),
        max_length=254,
        widget=forms.EmailInput(attrs={"autocomplete": "email", 'class': 'form-control'}),
    )


class EsqueceuSenhaLinkForm(SetPasswordForm):
    new_password1 = forms.CharField(
        label=('Nova senha'),
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password', 'class': 'form-control'}),
        strip=False,
        # help_text=password_validation.password_validators_help_text_html(),
    )
    new_password2 = forms.CharField(
        label=('Confirmação'),
        strip=False,
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password', 'class': 'form-control'}),
    )