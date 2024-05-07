from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Usuario, Perfil


class PerfilInline(admin.StackedInline):
    model = Perfil
    can_delete = False
    verbose_name_plural = "Perfis"


class UsuarioAdmin(UserAdmin):
    list_display = ('id', 'username', 'email', 'first_name', 'last_name', 'date_joined', 'is_active')
    list_filter = ('username', 'first_name', 'last_name')
    search_fields = ('id', 'username', 'email', 'first_name', 'last_name')
    inlines = [PerfilInline]

class PerfilAdmin(admin.ModelAdmin):
    list_display = ('id', 'usuario' ,'cnpj_cpf', 'nome_fantasia', 'is_pj')

admin.site.register(Usuario, UsuarioAdmin)
admin.site.register(Perfil, PerfilAdmin)
