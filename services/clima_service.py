import json
from urllib.request import urlopen, Request
from urllib.error import URLError

WEATHER_CODES = {
    0: "Céu limpo", 1: "Predom. limpo", 2: "Parcialmente nublado",
    3: "Encoberto", 45: "Nevoeiro", 48: "Nevoeiro c/ geada",
    51: "Garoa fraca", 53: "Garoa", 55: "Garoa forte",
    61: "Chuva fraca", 63: "Chuva", 65: "Chuva forte",
    71: "Neve fraca", 73: "Neve", 75: "Neve forte",
    80: "Pancada fraca", 81: "Pancada", 82: "Pancada forte",
    95: "Tempestade", 96: "Tempestade c/ granizo", 99: "Tempestade c/ granizo forte",
}

WEATHER_ICONS = {
    0: "☀️", 1: "🌤️", 2: "⛅", 3: "☁️",
    45: "🌫️", 48: "🌫️",
    51: "🌦️", 53: "🌦️", 55: "🌦️",
    61: "🌧️", 63: "🌧️", 65: "🌧️",
    71: "❄️", 73: "❄️", 75: "❄️",
    80: "🌦️", 81: "🌧️", 82: "🌧️",
    95: "⛈️", 96: "⛈️", 99: "⛈️",
}

DIAS_SEMANA = ["Seg", "Ter", "Qua", "Qui", "Sex", "Sáb", "Dom"]


def obter_localizacao():
    try:
        req = Request("http://ip-api.com/json/?fields=lat,lon,city,region", headers={"User-Agent": "Mozilla/5.0"})
        with urlopen(req, timeout=10) as resp:
            dados = json.loads(resp.read().decode())
        if dados.get("lat") and dados.get("lon"):
            return dados["lat"], dados["lon"], dados.get("city", "Desconhecida"), dados.get("region", "")
        return None, None, "Desconhecida", ""
    except (URLError, json.JSONDecodeError):
        return None, None, "Desconhecida", ""


def obter_clima(lat, lon):
    try:
        url = (
            f"https://api.open-meteo.com/v1/forecast?"
            f"latitude={lat}&longitude={lon}"
            f"&current=temperature_2m,relative_humidity_2m,weather_code"
            f"&daily=temperature_2m_max,temperature_2m_min,weather_code"
            f"&timezone=America%2FSao_Paulo"
            f"&forecast_days=14"
        )
        req = Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urlopen(req, timeout=10) as resp:
            dados = json.loads(resp.read().decode())
        current = dados.get("current", {})
        code = current.get("weather_code", 0)

        daily = dados.get("daily", {})
        previsao_semanal = []
        datas = daily.get("time", [])
        maxs = daily.get("temperature_2m_max", [])
        mins = daily.get("temperature_2m_min", [])
        codes = daily.get("weather_code", [])

        from datetime import datetime as dt
        for i in range(len(datas)):
            data = dt.strptime(datas[i], "%Y-%m-%d")
            nome_dia = DIAS_SEMANA[data.weekday()] if i > 0 else "Hoje"
            if i == 1:
                nome_dia = "Amanhã"
            previsao_semanal.append({
                "dia": nome_dia,
                "dia_mes": data.day,
                "mes": data.month,
                "data": datas[i],
                "temp_max": maxs[i] if i < len(maxs) else None,
                "temp_min": mins[i] if i < len(mins) else None,
                "icone": WEATHER_ICONS.get(codes[i], "❓"),
                "descricao": WEATHER_CODES.get(codes[i], "Desconhecido"),
            })

        return {
            "temperatura": current.get("temperature_2m"),
            "umidade": current.get("relative_humidity_2m"),
            "icone": WEATHER_ICONS.get(code, "❓"),
            "descricao": WEATHER_CODES.get(code, "Desconhecido"),
            "previsao_semanal": previsao_semanal,
        }
    except (URLError, json.JSONDecodeError):
        return None
