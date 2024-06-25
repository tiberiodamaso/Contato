import os, re, io, sys
from PIL import Image
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import InMemoryUploadedFile

def validate_file_extension(value):
    ext = os.path.splitext(value.name)[1]  # [0] returns path & filename
    valid_extensions = ['.jpg', '.png', '.jpeg', '.svg'] # populate with the extensions that you allow / want
    if not ext.lower() in valid_extensions:
        raise ValidationError('Tipo de imagem não suportado. Tente imagens do tipo JPG, JEPG, PNG ou SVG.')

# def make_vcf(first_name, last_name, empresa, telefone, whatsapp, facebook, instagram, linkedin, email, youtube, tik_tok):
def make_vcf(first_name, last_name, empresa, telefone, site, endereco, estado, municipio, email):

    
    return [
        'BEGIN:VCARD',
        'VERSION:3.0',
        f'N:{last_name};{first_name}',
        f'FN:{first_name} {last_name}',
        f'ORG:{empresa}',
        f'TEL;type=WORK;type=VOICE:{telefone}',
        f'item1.URL;type=pref:{site}',
        f'item1.X-ABLabel:Site',
        f'item1.ADR;type=OTHER;type=pref:{endereco} - {municipio}/{estado}',
        f'item1.X-ABADR:br',
        f'item1.URL;type=pref:{site}',
        f'item1.X-ABLabel:Site',
        # f'item1.URL;type=pref:https://api.whatsapp.com/send?phone=55{whatsapp}&text=oi',
        # f'item1.X-ABLabel:Whatsapp',
        # f'item2.URL;type=pref:{instagram}',
        # f'item2.X-ABLabel:Instagram',
        # f'item3.URL;type=pref:{facebook}',
        # f'item3.X-ABLabel:Facebook',
        # f'item4.URL;type=pref:{linkedin}',
        # f'item4.X-ABLabel:Linkedin',
        # f'item5.URL;type=pref:{youtube}',
        # f'item5.X-ABLabel:Youtube',
        # f'item6.URL;type=pref:{tik_tok}',
        # f'item6.X-ABLabel:Tik Tok',
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

def resize_image(imagem, largura_desejada, altura_desejada):
    try:
        with Image.open(imagem) as imagem:

            largura_atual, altura_atual = imagem.size

            if largura_atual <= largura_desejada and altura_atual <= altura_desejada:
                # Não é necessário redimensionar a imagem
                buffer = io.BytesIO()
                imagem.save(buffer, format=imagem.format)
                buffer.seek(0)
                return imagem, buffer

            proporcao_largura = largura_desejada / largura_atual
            proporcao_altura = altura_desejada / altura_atual

            if proporcao_largura < proporcao_altura:
                nova_largura = largura_desejada
                nova_altura = int(altura_atual * proporcao_largura)
            else:
                nova_largura = int(largura_atual * proporcao_altura)
                nova_altura = altura_desejada

            img_redimensionada = imagem.resize((nova_largura, nova_altura))

            buffer = io.BytesIO()
            img_redimensionada.save(buffer, format=imagem.format)
            buffer.seek(0)

            return img_redimensionada, buffer


    except Exception as e:
        print(f"Erro ao redimensionar a imagem: {e}")
        return None

def cleaner(text: str) -> str:
    """
    Função utilizada para limpar texto substituindo caracteres acentuados e removendo o que não é letra

    :param text: texto que será tratado

    :returns: texto processado
    """
    text = text.lower()

    # substituir caracteres acentuados por não acentuados
    text = re.sub(r'[áàâãä]', 'a', text)
    text = re.sub(r'[éèêë]', 'e', text)
    text = re.sub(r'[íìîï]', 'i', text)
    text = re.sub(r'[óòôõö]', 'o', text)
    text = re.sub(r'[úùûü]', 'u', text)
    text = re.sub('ç', 'c', text)

    # remover todos os caracteres que não são números e não são letras (caracter de linha, de parágrafo etc)
    text = re.sub(r'[^a-z0-9]', '', text)

    return text

def create_in_memory_file(buffer, filename):
    try:
        # Extrair a extensão do formato do buffer
        buffer.seek(0)
        img_format = Image.open(buffer).format.lower()
        if img_format in ['jpeg', 'jpg']:
            content_type = 'image/jpeg'
        elif img_format == 'png':
            content_type = 'image/png'
        else:
            content_type = f'image/{img_format}'

        in_memory_file = InMemoryUploadedFile(
            buffer,
            None,
            filename,
            content_type,
            buffer.getbuffer().nbytes,
            None
        )
        return in_memory_file

    except Exception as e:
        print(f"Ocorreu um erro ao criar InMemoryUploadedFile: {e}")
        return None
