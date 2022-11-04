from django.core.exceptions import ValidationError
import os

def validate_file_extension(value):
    ext = os.path.splitext(value.name)[1]  # [0] returns path & filename
    valid_extensions = ['.jpg', '.png', '.jpeg', '.svg'] # populate with the extensions that you allow / want
    if not ext.lower() in valid_extensions:
        raise ValidationError('Tipo de imagem não suportado. Tente imagens do tipo JPG, JEPG, PNG ou SVG.')


def make_vcard(first_name, last_name, empresa, telefone, whatsapp, facebook, instagram, linkedin, email):

    
    return [
        'BEGIN:VCARD',
        'VERSION:3.0',
        f'N:{last_name};{first_name}',
        f'FN:{first_name} {last_name}',
        f'ORG:{empresa}',
        f'TEL;type=WORK;type=VOICE:{telefone}',
        f'item1.URL;type=pref:https://api.whatsapp.com/send?phone=55{whatsapp}&text=oi',
        f'item1.X-ABLabel:Whatsapp',
        f'item2.URL;type=pref:{instagram}',
        f'item2.X-ABLabel:Instagram',
        f'item3.URL;type=pref:{facebook}',
        f'item3.X-ABLabel:Facebook',
        f'item4.URL;type=pref:{linkedin}',
        f'item4.X-ABLabel:Linkedin',
        f'EMAIL;type=INTERNET;type=WORK:{email}',
        'END:VCARD'
    ]


# def write_vcard(f, vcard):
#     with open(f, 'w') as f:
#         f.writelines([l + '\n' for l in vcard])
#     print(f)
#     return f


