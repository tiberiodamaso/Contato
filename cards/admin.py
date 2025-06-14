from django.contrib import admin

from .models import Card, Categoria, Subcategoria, Anuncio, Estado, Municipio, TipoAnuncio, CodigoPais, Empresa, Avaliacao


class CategoriaAdmin(admin.ModelAdmin):
    list_display = ['id', 'nome']


class SubcategoriaAdmin(admin.ModelAdmin):
    list_display = ['id', 'categoria', 'nome']


class EstadoAdmin(admin.ModelAdmin):
    list_display = ['id', 'sigla', 'nome']


class MunicipioAdmin(admin.ModelAdmin):
    list_display = ['id', 'estado', 'nome']


class CodigoPaisAdmin(admin.ModelAdmin):
    list_display = ['id', 'codigo', 'pais']


class EmpresaAdmin(admin.ModelAdmin):
    list_display = ['id', 'nome_fantasia', 'cnpj_cpf', 'slug', 'criada']


class CardAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'empresa',
        'modelo',
        'nome_display',
        'slug',
        'cargo',
        'proprietario',
        'cod_pais',
        'whatsapp',
        'publico',
    ]

    readonly_fields = ['conteudo_pesquisavel']

    def save_model(self, request, obj, form, change):
        # Atribui o usuário logado ao atributo "user" do objeto
        obj.proprietario = request.user
        # Salva o objeto
        obj.save()


class TipoAnuncioAdmin(admin.ModelAdmin):
    list_display = ['id', 'nome']


class AnuncioAdmin(admin.ModelAdmin):
    list_display = ['id', 'empresa', 'img', 'tipo', 'link', 'nome', 'ativo']


class AvaliacaoAdmin(admin.ModelAdmin):
    list_display = ['id', 'valor', 'card', 'usuario']


admin.site.register(Categoria, CategoriaAdmin)
admin.site.register(Subcategoria, SubcategoriaAdmin)
admin.site.register(Estado, EstadoAdmin)
admin.site.register(Municipio, MunicipioAdmin)
admin.site.register(CodigoPais, CodigoPaisAdmin)
admin.site.register(Empresa, EmpresaAdmin)
admin.site.register(Card, CardAdmin)
admin.site.register(TipoAnuncio, TipoAnuncioAdmin)
admin.site.register(Anuncio, AnuncioAdmin)
admin.site.register(Avaliacao, AvaliacaoAdmin)
