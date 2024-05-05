from django import forms
from .models import Card, Conteudo, TipoConteudo

class CardEditForm(forms.ModelForm):

    class Meta:
        model = Card
        exclude = ['proprietario', 'vcf', 'qr_code', 'empresa']
        widgets = {
            'img_perfil': forms.FileInput(attrs={'class': 'form-control', 'label': 'Foto', 'accept': 'image/jpeg, image/png'}),
            'logotipo': forms.FileInput(attrs={'class': 'form-control', 'label': 'Logotipo', 'accept': 'image/jpeg, image/png'}),
            'cargo': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Seu cargo'}),
            'endereco': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Logradouro, número, CEP 00000000'}),
            'cor': forms.TextInput(attrs={'class': 'form-control', 'type': 'color'}),
            'cod_pais': forms.Select(attrs={'class': 'form-select'}),
            'whatsapp': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '(11) 98754-3210'}),
            'site': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://seusite.com.br/'}),
            'facebook': forms.URLInput(attrs={'class': 'form-control', 'placeholder': '@seu-perfil'}),
            'instagram': forms.URLInput(attrs={'class': 'form-control', 'placeholder': '@seu-perfil'}),
            'linkedin': forms.URLInput(attrs={'class': 'form-control', 'placeholder': '@seu-perfil'}),
            'youtube': forms.URLInput(attrs={'class': 'form-control', 'placeholder': '@seu-perfil'}),
            'tik_tok': forms.URLInput(attrs={'class': 'form-control', 'placeholder': '@seu-perfil'}),
            'nome_display': forms.TextInput(attrs={'class': 'form-control'}),
            'categoria': forms.Select(attrs={'class': 'form-select'}),
            'subcategoria': forms.Select(attrs={'class': 'form-select'}),
            'estado': forms.Select(attrs={'class': 'form-select'}),
            'municipio': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['cod_pais'].empty_label = 'Selecione uma opção'


class ConteudoEditForm(forms.ModelForm):

    tipo = forms.ModelChoiceField(queryset=TipoConteudo.objects.all().order_by('nome'), widget=forms.Select(attrs={'class': 'form-select'}), empty_label=None)

    class Meta:
        model = Conteudo
        exclude = ['card']
        widgets = {
            'img': forms.FileInput(attrs={'class': 'form-control', 'required': 'required', 'accept': 'image/jpeg, image/png'}),
            'link': forms.URLInput(attrs={'class': 'form-control'}),
            'nome': forms.TextInput(attrs={'class': 'form-control'}),
            'descricao': forms.Textarea(attrs={'class': 'form-control', 'rows': '3'}),
        }