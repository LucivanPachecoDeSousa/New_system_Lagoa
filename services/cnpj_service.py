import json
from urllib.request import urlopen, Request
from urllib.error import URLError, HTTPError


def consultar_cnpj(cnpj: str) -> tuple:
    cnpj_limpo = ''.join(c for c in cnpj if c.isdigit())
    if len(cnpj_limpo) != 14:
        return False, "CNPJ deve ter 14 dígitos."

    url = f"https://brasilapi.com.br/api/cnpj/v1/{cnpj_limpo}"
    try:
        req = Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urlopen(req, timeout=10) as resp:
            dados = json.loads(resp.read().decode())
    except HTTPError as e:
        if e.code == 429:
            return False, "Muitas consultas seguidas. Aguarde alguns instantes e tente novamente."
        return False, f"Erro ao consultar: {str(e)}"
    except URLError as e:
        return False, f"Erro ao consultar: {str(e)}"
    except json.JSONDecodeError:
        return False, "Resposta inválida da API."

    if not dados or "razao_social" not in dados:
        return False, "CNPJ não encontrado."

    return True, {
        "cnpj_cpf": cnpj_limpo,
        "tipo_pessoa": "juridica",
        "razao_social": dados.get("razao_social", ""),
        "nome_fantasia": dados.get("nome_fantasia", ""),
        "logradouro": dados.get("logradouro", ""),
        "numero": dados.get("numero", ""),
        "complemento": dados.get("complemento", ""),
        "bairro": dados.get("bairro", ""),
        "cidade": dados.get("municipio", ""),
        "estado": dados.get("uf", ""),
        "cep": dados.get("cep", ""),
        "telefone": dados.get("ddd_telefone_1", ""),
        "email": dados.get("email", ""),
        "inscricao_estadual": dados.get("inscricao_estadual", ""),
        "inscricoes_estaduais": dados.get("inscricoes_estaduais", []),
    }
