from django.contrib import admin

from .models import Card, Categoria, Subcategoria, Conteudo, Estado, Municipio, TipoConteudo


class CategoriaAdmin(admin.ModelAdmin):
    list_display = ['id', 'nome']


class SubcategoriaAdmin(admin.ModelAdmin):
    list_display = ['id', 'categoria', 'nome']


class EstadoAdmin(admin.ModelAdmin):
    list_display = ['id', 'sigla', 'nome']


class MunicipioAdmin(admin.ModelAdmin):
    list_display = ['id', 'estado', 'nome']


# class EmpresaAdmin(admin.ModelAdmin):
#     list_display = ['id', 'nome', 'cnpj', 'slug', 'criada']

#     def save_model(self, request, obj, form, change):
#       # Atribui o usuário logado ao atributo "user" do objeto
#       obj.user = request.user
#       # Salva o objeto
#       obj.save()


class CardAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'nome_display',
        'slug',
        'cargo',
        'proprietario',
        'telefone',
        'empresa',
        'slug_empresa',
        'conteudo_pesquisavel',
    ]

    def save_model(self, request, obj, form, change):
        # Atribui o usuário logado ao atributo "user" do objeto
        obj.proprietario = request.user
        # Salva o objeto
        obj.save()


class TipoConteudoAdmin(admin.ModelAdmin):
    list_display = ['id', 'nome']


class ConteudoAdmin(admin.ModelAdmin):
    list_display = ['id', 'card', 'img', 'tipo', 'link', 'nome']


admin.site.register(Categoria, CategoriaAdmin)
admin.site.register(Subcategoria, SubcategoriaAdmin)
admin.site.register(Estado, EstadoAdmin)
admin.site.register(Municipio, MunicipioAdmin)
# admin.site.register(Empresa, EmpresaAdmin)
admin.site.register(Card, CardAdmin)
admin.site.register(TipoConteudo, TipoConteudoAdmin)
admin.site.register(Conteudo, ConteudoAdmin)
