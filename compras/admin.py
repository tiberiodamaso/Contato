from django.contrib import admin
from .models import Relatorio, CartaoPF, Ad, CartaoPJ


class CartaoPFAdmin(admin.ModelAdmin):
    list_display = ('id', 'usuario', 'pagamento_id', 'valor', 'status', 'date_created')
    search_fields = ['usuario']

class AdAdmin(admin.ModelAdmin):
    list_display = ('id', 'usuario', 'pagamento_id', 'valor', 'status', 'date_created')
    search_fields = ['usuario']
    
class RelatorioAdmin(admin.ModelAdmin):
    list_display = ('id', 'usuario', 'assinatura_id', 'valor', 'status', 'date_created')
    search_fields = ['usuario']

class CartaoPJAdmin(admin.ModelAdmin):
    list_display = ('id', 'usuario', 'assinatura_id', 'valor', 'status', 'date_created')
    search_fields = ['usuario']

class PagamentoAdmin(admin.ModelAdmin):
    list_display = ('id', 'stripe_session_id', 'customer_email', 'amount', 'status', 'created_at', 'updated_at')
    search_fields = ['customer_email']

admin.site.register(CartaoPF, CartaoPFAdmin)
admin.site.register(Ad, AdAdmin)
admin.site.register(Relatorio, RelatorioAdmin)
admin.site.register(CartaoPJ, CartaoPJAdmin)
# admin.site.register(Pagamento, PagamentoAdmin)
