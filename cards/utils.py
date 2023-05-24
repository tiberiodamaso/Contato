from django.core.exceptions import ValidationError
import os, re

def validate_file_extension(value):
    ext = os.path.splitext(value.name)[1]  # [0] returns path & filename
    valid_extensions = ['.jpg', '.png', '.jpeg', '.svg'] # populate with the extensions that you allow / want
    if not ext.lower() in valid_extensions:
        raise ValidationError('Tipo de imagem não suportado. Tente imagens do tipo JPG, JEPG, PNG ou SVG.')

def make_vcf(first_name, last_name, empresa, telefone, whatsapp, facebook, instagram, linkedin, email, youtube, tik_tok):

    
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
        f'item5.URL;type=pref:{youtube}',
        f'item5.X-ABLabel:Youtube',
        f'item6.URL;type=pref:{tik_tok}',
        f'item6.X-ABLabel:Tik Tok',
        f'EMAIL;type=INTERNET;type=WORK:{email}',
        'END:VCARD'
    ]

def valida_cnpj(cnpj:str) -> bool:
  """
  Valida o CNPJ e dígitos verificadores.
  :param cnpj: número cnpj que será validado
  """

  # Remover caracteres não numéricos
  cnpj = re.sub(r'\D', '', cnpj)

  # Verificar se o CNPJ possui 14 dígitos
  if len(cnpj) != 14:
      return False

  # Verificar se todos os dígitos são iguais
  if cnpj == cnpj[0] * 14:
      return False

  # Calcular o primeiro dígito verificador
  soma = 0
  peso = 5
  for i in range(12):
      soma += int(cnpj[i]) * peso
      peso -= 1 if peso > 2 else -8
  digito1 = str((11 - (soma % 11)) % 10)

  # Calcular o segundo dígito verificador
  soma = 0
  peso = 6
  for i in range(13):
      soma += int(cnpj[i]) * peso
      peso -= 1 if peso > 2 else -8
  digito2 = str((11 - (soma % 11)) % 10)

  # Verificar se os dígitos verificadores são válidos
  if cnpj[-2:] != digito1 + digito2:
      return False

  return True





