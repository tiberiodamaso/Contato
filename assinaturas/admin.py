from django.contrib import admin
from .models import Assinatura


class AssinaturaAdmin(admin.ModelAdmin):
    list_display = ('id', 'usuario', 'assinatura_id', 'payer_id', 'date_created', 'valor', 'status')
    search_fields = ['usuario']

admin.site.register(Assinatura, AssinaturaAdmin)
