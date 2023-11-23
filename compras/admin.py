from django.contrib import admin
from .models import Relatorio, Cartao


class RelatorioAdmin(admin.ModelAdmin):
    list_display = ('id', 'usuario', 'assinatura_id', 'payer_id', 'date_created', 'valor', 'status')
    search_fields = ['usuario']

class CartaoAdmin(admin.ModelAdmin):
    list_display = ('id', 'usuario', 'pagamento_id', 'payer_id', 'date_created', 'valor', 'status')
    search_fields = ['usuario']

admin.site.register(Relatorio, RelatorioAdmin)
admin.site.register(Cartao, CartaoAdmin)
