import requests

url = "https://sandbox.api.pagseguro.com/oauth2/authorize?client_id=a7ed5fb0-91ac-4122-8fb3-38bb36fd415d&response_type=code&redirect_uri=https%3A%2F%2Fmeucontato.app.br&scope=payments.read%2Bpayments.create%2Bpayments.refund%2Bcheckout.create%2Bcheckout.view%2Bcheckout.update&state=17EF6776A7C84F75A8BD485BC36BC1CB"

headers = {
    "accept": "text/plain",
    "Authorization": "17EF6776A7C84F75A8BD485BC36BC1CB",
    }

response = requests.get(url, headers=headers)

print(response.text)