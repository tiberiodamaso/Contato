from django import forms
from .models import Card, Conteudo, TipoConteudo

class CardEditForm(forms.ModelForm):

    class Meta:
        model = Card
        exclude = ['proprietario', 'vcf', 'qr_code']
        widgets = {
            'img_perfil': forms.FileInput(attrs={'class': 'form-control', 'label': 'Foto'}),
            'logotipo': forms.FileInput(attrs={'class': 'form-control', 'label': 'Logotipo'}),
            'cargo': forms.TextInput(attrs={'class': 'form-control'}),
            'endereco': forms.TextInput(attrs={'class': 'form-control'}),
            'cor': forms.TextInput(attrs={'class': 'form-control', 'type': 'color'}),
            'whatsapp': forms.TextInput(attrs={'class': 'form-control'}),
            'site': forms.URLInput(attrs={'class': 'form-control'}),
            'facebook': forms.URLInput(attrs={'class': 'form-control'}),
            'instagram': forms.URLInput(attrs={'class': 'form-control'}),
            'linkedin': forms.URLInput(attrs={'class': 'form-control'}),
            'telefone': forms.TextInput(attrs={'class': 'form-control'}),
            'youtube': forms.TextInput(attrs={'class': 'form-control'}),
            'tik_tok': forms.TextInput(attrs={'class': 'form-control'}),
            'nome_display': forms.TextInput(attrs={'class': 'form-control'}),
            'empresa': forms.TextInput(attrs={'class': 'form-control'}),
            'categoria': forms.Select(attrs={'class': 'form-select'}),
            'subcategoria': forms.Select(attrs={'class': 'form-select'}),
            'estado': forms.Select(attrs={'class': 'form-select'}),
            'municipio': forms.Select(attrs={'class': 'form-select'}),
        }


class ConteudoEditForm(forms.ModelForm):

    tipo = forms.ModelChoiceField(queryset=TipoConteudo.objects.all().order_by('nome'), widget=forms.Select(attrs={'class': 'form-select'}), empty_label=None)

    class Meta:
        model = Conteudo
        exclude = ['card']
        widgets = {
            'img': forms.FileInput(attrs={'class': 'form-control', 'required': 'required'}),
            'link': forms.URLInput(attrs={'class': 'form-control'}),
            'nome': forms.TextInput(attrs={'class': 'form-control'}),
            'descricao': forms.Textarea(attrs={'class': 'form-control', 'rows': '3'}),
        }