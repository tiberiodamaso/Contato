from django.contrib import admin
from .models import Empresa, Card


class EmpresaAdmin(admin.ModelAdmin):
    list_display = ['id', 'nome', 'slug', 'criada', 'get_gerentes', 'get_vendedores']
    
    def get_gerentes(self, obj):
        return [gerente for gerente in obj.gerentes.all()]

    def get_vendedores(self, obj):
        return [vendedor for vendedor in obj.vendedores.all()]


class CardAdmin(admin.ModelAdmin):
    list_display = ['empresa', 'usuario', 'slug', 'whatsapp', 'instagram', 'telefone', 'get_staff']

    def get_staff(self, obj):
        return obj.usuario.is_staff


admin.site.register(Empresa, EmpresaAdmin)
admin.site.register(Card, CardAdmin)