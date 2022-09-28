from django.core.exceptions import ValidationError
import os

def validate_file_extension(value):
    ext = os.path.splitext(value.name)[1]  # [0] returns path & filename
    valid_extensions = ['.jpg', '.png', '.jpeg', '.svg'] # populate with the extensions that you allow / want
    if not ext.lower() in valid_extensions:
        raise ValidationError('Tipo de imagem não suportado. Tente imagens do tipo JPG, JEPG, PNG ou SVG.')