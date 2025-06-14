from django.contrib.auth.forms import AuthenticationForm, UserCreationForm, PasswordChangeForm, PasswordResetForm, SetPasswordForm
from django import forms
from .models import Usuario, Perfil
from django.template.defaultfilters import slugify


class UsuarioAuthenticationForm(AuthenticationForm):
    username = forms.CharField(label='E-mail', widget=forms.TextInput(attrs={'autofocus': True, 'class': 'form-control'}))
    password = forms.CharField(label="Senha", strip=False, widget=forms.PasswordInput(
            attrs={'autocomplete': 'current-password', 'class': 'form-control'}),
    )


class UsuarioRegistrationForm(UserCreationForm):

    class Meta:
        model = Usuario
        fields = ('email', 'first_name', 'last_name')

    error_messages = {
        'password_mismatch': 'As senhas não coincidem.',
        'email_taken': 'Este email já está em uso.',
        'required': 'Este campo é obrigatório. Por favor, preencha.',
        'invalid': 'Por favor, insira um endereço de e-mail válido.',
        'unique': 'Este endereço de e-mail já está em uso. Por favor, escolha outro.',
        'password_too_similar': 'A senha é muito parecida com Primeiro nome',     
        'password_too_short': 'Sua senha deve ter pelo menos 8 caracteres.',
        'password_too_common': 'Escolha uma senha mais segura. Evite senhas comuns.',
        'password_entirely_numeric': 'Esta senha é inteiramente numérica.',
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['email'].widget.attrs.update({'class': 'form-control', 'placeholder': 'será o email do cartão', 'hx-trigger': 'change', 'hx-get': '/usuarios/verificar-email', 'hx-target': '#verificar_email'})
        self.fields['first_name'].widget.attrs.update({'class': 'form-control'})
        self.fields['last_name'].widget.attrs.update({'class': 'form-control'})
        self.fields['password1'].widget.attrs.update({'class': 'form-control'})
        self.fields['password2'].widget.attrs.update({'class': 'form-control'})

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        user.is_active = False
        if commit:
            user.save()
        return user


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
        label=('E-mail'),
        max_length=254,
        widget=forms.EmailInput(
            attrs={"autocomplete": "email", 'class': 'form-control'}),
    )


class EsqueceuSenhaLinkForm(SetPasswordForm):
    new_password1 = forms.CharField(
        label=('Nova senha'),
        widget=forms.PasswordInput(
            attrs={'autocomplete': 'new-password', 'class': 'form-control'}),
        strip=False,
        # help_text=password_validation.password_validators_help_text_html(),
    )
    new_password2 = forms.CharField(
        label=('Confirmação'),
        strip=False,
        widget=forms.PasswordInput(
            attrs={'autocomplete': 'new-password', 'class': 'form-control'}),
    )


class PerfilFormPJ(forms.ModelForm):

    class Meta:
        model = Perfil
        fields = ('cnpj_cpf', 'nome_fantasia')
        widgets = {
            'cnpj_cpf': forms.TextInput(attrs={'class': 'form-control'}),
            'nome_fantasia': forms.TextInput(attrs={'class': 'form-control'}),
        }


class PerfilFormPF(forms.ModelForm):

    class Meta:
        model = Perfil
        fields = ('cnpj_cpf',)
        widgets = {
            'cnpj_cpf': forms.TextInput(attrs={'class': 'form-control'}),
        }
