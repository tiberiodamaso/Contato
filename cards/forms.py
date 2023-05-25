from django import forms
from .models import Card, Conteudo

class CardEditForm(forms.ModelForm):

    class Meta:
        model = Card
        exclude = ['proprietario', 'vcf', 'qr_code']
        widgets = {
            'img_perfil': forms.FileInput(attrs={'class': 'form-control', 'label': 'Foto'}),
            'logotipo': forms.FileInput(attrs={'class': 'form-control', 'label': 'Logotipo'}),
            'cargo': forms.TextInput(attrs={'class': 'form-control'}),
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
            'estado': forms.Select(attrs={'class': 'form-select'}),
            'municipio': forms.Select(attrs={'class': 'form-select'}),
        }


class ConteudoEditForm(forms.ModelForm):

    class Meta:
        model = Conteudo
        fields = '__all__'
        widgets = {
            'site': forms.URLInput(attrs={'class': 'form-control'}),
            'youtube': forms.Textarea(attrs={'class': 'form-control'}),
            'telefone': forms.TextInput(attrs={'class': 'form-control'}),
            'promo1': forms.FileInput(attrs={'class': 'form-control'}),
            'promo1_link': forms.URLInput(attrs={'class': 'form-control'}),
            'promo2': forms.FileInput(attrs={'class': 'form-control'}),
            'promo2_link': forms.URLInput(attrs={'class': 'form-control'}),
            'promo3': forms.FileInput(attrs={'class': 'form-control'}),
            'promo3_link': forms.URLInput(attrs={'class': 'form-control'}),
            'produto1': forms.FileInput(attrs={'class': 'form-control'}),
            'produto1_link': forms.URLInput(attrs={'class': 'form-control'}),
            'produto2': forms.FileInput(attrs={'class': 'form-control'}),
            'produto2_link': forms.URLInput(attrs={'class': 'form-control'}),
            'produto3': forms.FileInput(attrs={'class': 'form-control'}),
            'produto3_link': forms.URLInput(attrs={'class': 'form-control'}),
            'servico1': forms.FileInput(attrs={'class': 'form-control'}),
            'servico1_link': forms.URLInput(attrs={'class': 'form-control'}),
            'servico2': forms.FileInput(attrs={'class': 'form-control'}),
            'servico2_link': forms.URLInput(attrs={'class': 'form-control'}),
            'servico3': forms.FileInput(attrs={'class': 'form-control'}),
            'servico3_link': forms.URLInput(attrs={'class': 'form-control'}),
            'portfolio1': forms.FileInput(attrs={'class': 'form-control'}),
            'portfolio1_link': forms.URLInput(attrs={'class': 'form-control'}),
            'portfolio2': forms.FileInput(attrs={'class': 'form-control'}),
            'portfolio2_link': forms.URLInput(attrs={'class': 'form-control'}),
            'portfolio3': forms.FileInput(attrs={'class': 'form-control'}),
            'portfolio3_link': forms.URLInput(attrs={'class': 'form-control'}),
        }