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

admin.site.register(Usuario, UsuarioAdmin)
