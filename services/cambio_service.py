import json
from urllib.request import urlopen, Request
from urllib.error import URLError


def obter_cambio():
    try:
        url = "https://economia.awesomeapi.com.br/json/last/USD-BRL,EUR-BRL"
        req = Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urlopen(req, timeout=10) as resp:
            dados = json.loads(resp.read().decode())

        result = {}
        for moeda, key in [("USD", "USDBRL"), ("EUR", "EURBRL")]:
            if key in dados:
                result[moeda] = {
                    "bid": float(dados[key]["bid"]),
                    "pctChange": float(dados[key]["pctChange"]),
                }
        return result if result else None
    except (URLError, json.JSONDecodeError, KeyError, ValueError):
        return None
