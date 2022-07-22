from django.shortcuts import render
from django.contrib.auth.views import LoginView, LogoutView
from django.views.generic.edit import CreateView
from django.contrib.messages.views import SuccessMessageMixin
from .forms import UsuarioAuthenticationForm,UsuarioRegistrationForm
from django.contrib import messages


class UsuarioLoginView(LoginView):
    template_name = 'usuarios/login.html'
    form_class = UsuarioAuthenticationForm


# @login_required
# def registrar_usuario(request):
#     if request.method == 'POST':
#         form = UsuarioRegistrationForm(request.POST)
#         if form.is_valid():
#             form.save()
#             username = form.cleaned_data.get('username')
#             password = form.cleaned_data.get('password1')
#             messages.success(request, 'Usuário adicionado com sucesso!')
#             return redirect('usuarios:registrar')
#         else:
#             messages.error(request, 'Formulário inválido. Verifique se o CPF e o email estão corretos.')
#     else:
#         form = UsuarioRegistrationForm()
#     return render(request, 'usuarios/registrar.html', {'form': form})

class UsuarioRegistrarView(SuccessMessageMixin, CreateView):
  template_name = 'usuarios/registrar.html'
  success_url = 'usuarios:registrar'
  form_class = UsuarioRegistrationForm
  success_message = "Usuário criado com sucesso"

