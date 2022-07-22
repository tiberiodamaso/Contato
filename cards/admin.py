from django.contrib import admin
from .models import Empresa, Card


class EmpresaAdmin(admin.ModelAdmin):
    list_display = ['id', 'nome', 'criada']


class CardAdmin(admin.ModelAdmin):
    list_display = ['empresa', 'primeiro_nome', 'ultimo_nome', 'whatsapp', 'instagram', 'telefone']


admin.site.register(Empresa, EmpresaAdmin)
admin.site.register(Card, CardAdmin)