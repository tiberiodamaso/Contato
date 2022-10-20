from django import forms
from .models import Card

class CardEditForm(forms.ModelForm):

    class Meta:
        model = Card
        exclude = ['empresa', 'usuario', 'vcard', 'qr_code']
        widgets = {
            'img_perfil': forms.FileInput(attrs={'class': 'form-control', 'label': 'Foto'}),
            'whatsapp': forms.TextInput(attrs={'class': 'form-control'}),
            'facebook': forms.URLInput(attrs={'class': 'form-control'}),
            'instagram': forms.URLInput(attrs={'class': 'form-control'}),
            'linkedin': forms.URLInput(attrs={'class': 'form-control'}),
            'youtube': forms.Textarea(attrs={'class': 'form-control'}),
            'telefone': forms.TextInput(attrs={'class': 'form-control'}),
            'slide1': forms.FileInput(attrs={'class': 'form-control', 'label': 'Slide 1'}),
            'slide1_link': forms.URLInput(attrs={'class': 'form-control'}),
            'slide2': forms.FileInput(attrs={'class': 'form-control', 'label': 'Slide 2'}),
            'slide2_link': forms.URLInput(attrs={'class': 'form-control'}),
            'slide3': forms.FileInput(attrs={'class': 'form-control', 'label': 'Slide 3'}),
            'slide3_link': forms.URLInput(attrs={'class': 'form-control'}),
            'produtos': forms.FileInput(attrs={'class': 'form-control', 'label': 'Produtos'}),
            'produtos_link': forms.URLInput(attrs={'class': 'form-control'}),
            'servicos': forms.FileInput(attrs={'class': 'form-control', 'label': 'Serviços'}),
            'servicos_link': forms.URLInput(attrs={'class': 'form-control'}),
            'promocoes': forms.FileInput(attrs={'class': 'form-control', 'label': 'Promoções'}),
            'promocoes_link': forms.URLInput(attrs={'class': 'form-control'}),
        }