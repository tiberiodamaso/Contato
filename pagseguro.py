import requests

url = "https://sandbox.api.pagseguro.com/oauth2/application"

payload = {
    "name": "Meu contato",
    "description": "Aplicação",
    "site": "https://meucontato.app.br",
    "redirect_uri": "https://meucontato.app.br",
    # "logo": "logotipo.png"
}
headers = {
    "accept": "application/json",
    "Authorization": "17EF6776A7C84F75A8BD485BC36BC1CB",
    "content-type": "application/json"
}

response = requests.post(url, json=payload, headers=headers)

print(response.text)