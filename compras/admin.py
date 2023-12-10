from django.contrib import admin
from .models import Relatorio, Cartao, Anuncio


class CartaoAdmin(admin.ModelAdmin):
    list_display = ('id', 'usuario', 'pagamento_id', 'payer_id', 'date_created', 'valor', 'status')
    search_fields = ['usuario']

class AnuncioAdmin(admin.ModelAdmin):
    list_display = ('id', 'usuario', 'pagamento_id', 'payer_id', 'date_created', 'valor', 'status')
    search_fields = ['usuario']
    
class RelatorioAdmin(admin.ModelAdmin):
    list_display = ('id', 'usuario', 'assinatura_id', 'payer_id', 'date_created', 'valor', 'status')
    search_fields = ['usuario']

admin.site.register(Cartao, CartaoAdmin)
admin.site.register(Anuncio, AnuncioAdmin)
admin.site.register(Relatorio, RelatorioAdmin)
