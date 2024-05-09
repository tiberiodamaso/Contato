from django.contrib import admin
from .models import Relatorio, CartaoPF, Ad, CartaoPJ


class CartaoPFAdmin(admin.ModelAdmin):
    list_display = ('id', 'usuario', 'pagamento_id', 'payer_id', 'date_created', 'valor', 'status')
    search_fields = ['usuario']

class AdAdmin(admin.ModelAdmin):
    list_display = ('id', 'usuario', 'pagamento_id', 'payer_id', 'date_created', 'valor', 'status')
    search_fields = ['usuario']
    
class RelatorioAdmin(admin.ModelAdmin):
    list_display = ('id', 'usuario', 'assinatura_id', 'payer_id', 'date_created', 'valor', 'status')
    search_fields = ['usuario']

class CartaoPJAdmin(admin.ModelAdmin):
    list_display = ('id', 'usuario', 'assinatura_id', 'payer_id', 'date_created', 'valor', 'status')
    search_fields = ['usuario']

admin.site.register(CartaoPF, CartaoPFAdmin)
admin.site.register(Ad, AdAdmin)
admin.site.register(Relatorio, RelatorioAdmin)
admin.site.register(CartaoPJ, CartaoPJAdmin)
