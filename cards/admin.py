from django.contrib import admin
from .models import Conteudo, Categoria, Estado, Municipio, Empresa, Card


class ConteudoAdmin(admin.ModelAdmin):
  list_display = ['id','site']

  def save_model(self, request, obj, form, change):
        # Atribui o usuário logado ao atributo "user" do objeto
        obj.user = request.user
        # Salva o objeto
        obj.save()


class CategoriaAdmin(admin.ModelAdmin):
  list_display = ['id', 'nome']


class EstadoAdmin(admin.ModelAdmin):
  list_display = ['id', 'sigla', 'nome']


class MunicipioAdmin(admin.ModelAdmin):
  list_display = ['id', 'estado', 'nome']


class EmpresaAdmin(admin.ModelAdmin):
    list_display = ['id', 'nome', 'cnpj', 'slug', 'criada']

    def save_model(self, request, obj, form, change):
      # Atribui o usuário logado ao atributo "user" do objeto
      obj.user = request.user
      # Salva o objeto
      obj.save()


class CardAdmin(admin.ModelAdmin):
    list_display = ['id', 'nome_display', 'slug', 'cargo', 'telefone', 'whatsapp', 'facebook', 'instagram']

    def save_model(self, request, obj, form, change):
      # Atribui o usuário logado ao atributo "user" do objeto
      obj.usuario = request.user
      # Salva o objeto
      obj.save()


admin.site.register(Conteudo, ConteudoAdmin)
admin.site.register(Categoria, CategoriaAdmin)
admin.site.register(Estado, EstadoAdmin)
admin.site.register(Municipio, MunicipioAdmin)
admin.site.register(Empresa, EmpresaAdmin)
admin.site.register(Card, CardAdmin)