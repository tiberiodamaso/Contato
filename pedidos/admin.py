from django.contrib import admin
from .models import Pedido


class PedidoAdmin(admin.ModelAdmin):
    list_display = ('id', 'usuario', 'id_pgto_mercado_pago', 'status', 'criado')
    search_fields = ['usuario']

admin.site.register(Pedido, PedidoAdmin)
