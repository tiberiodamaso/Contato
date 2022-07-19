from django.contrib import admin
from .models import Usuario

class UsuarioAdmin(admin.ModelAdmin):
    list_display = ('id', 'username', 'first_name', 'last_name', 'is_active')
    list_filter = ('username', 'first_name', 'last_name')
    search_fields = ('id', 'username', 'first_name', 'last_name')
    
admin.site.register(Usuario, UsuarioAdmin)
