from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Usuario

class UsuarioAdmin(UserAdmin):
    list_display = ('id', 'username', 'email', 'first_name', 'last_name', 'date_joined', 'is_active')
    list_filter = ('username', 'first_name', 'last_name')
    search_fields = ('id', 'username', 'email', 'first_name', 'last_name')

admin.site.register(Usuario, UsuarioAdmin)
