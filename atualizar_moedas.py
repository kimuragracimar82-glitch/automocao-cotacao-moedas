import os
import requests
import time
from pyairtable import Api
from datetime import datetime

# Credenciais
AIRTABLE_TOKEN = os.environ.get("AIRTABLE_TOKEN")
BASE_ID = "app0lQPZ6LqMDhK3P"
TABLE_NAME = "Moedas"

# Conexão com Airtable
api = Api(AIRTABLE_TOKEN)
table = api.table(BASE_ID, TABLE_NAME)

# Buscar cotações com Headers para evitar bloqueio
headers = {'User-Agent': 'Mozilla/5.0'}

try:
    # 1. Dólar, Euro e Iene via API AwesomeAPI (com headers)
    url_cambio = "https://economia.awesomeapi.com.br/last/USD-BRL,EUR-BRL,JPY-BRL"
    req = requests.get(url_cambio, headers=headers)
    
    if req.status_code == 200:
        dados = req.json()
        usd = float(dados["USDBRL"]["bid"])
        eur = float(dados["EURBRL"]["bid"])
        jpy = float(dados["JPYBRL"]["bid"])
    else:
        # Valores de fallback caso a API limite
        usd, eur, jpy = 5.65, 6.15, 0.038

    # 2. Bitcoin via CoinGecko
    url_btc = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=brl"
    req_btc = requests.get(url_btc, headers=headers)
    
    if req_btc.status_code == 200:
        btc = float(req_btc.json()["bitcoin"]["brl"])
    else:
        btc = 330000.0

    cotacoes = {
        "Dólar": usd,
        "Euro": eur,
        "Bitcoin": btc,
        "Iene": jpy,
        "Real": 1.0
    }

    agora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Atualizar no Airtable
    registros = table.all()
    for reg in registros:
        moeda_nome = reg["fields"].get("Moeda")
        if moeda_nome in cotacoes:
            table.update(reg["id"], {
                "Valor": cotacoes[moeda_nome],
                "Última atualizacao": agora
            })
            print(f"Atualizado: {moeda_nome} -> R$ {cotacoes[moeda_nome]}")
            time.sleep(0.2) # Pausa leve entre requisições

    print("\n✅ Sucesso! Cheque seu Airtable.")

except Exception as e:
    print(f"❌ Erro ao processar: {e}")
