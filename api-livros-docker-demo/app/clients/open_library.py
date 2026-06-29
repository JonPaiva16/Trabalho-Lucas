"""Cliente simples para consultar livros na Open Library."""

import json
from urllib.error import URLError
from urllib.request import urlopen


def consultar_open_library(isbn: str) -> dict | None:
    """Consulta a Open Library por ISBN e retorna dados basicos quando existir."""
    url = f"https://openlibrary.org/isbn/{isbn}.json"
    try:
        with urlopen(url, timeout=5) as resposta:  # nosec B310 - URL publica controlada pela aplicacao
            if resposta.status != 200:
                return None
            return json.loads(resposta.read().decode("utf-8"))
    except (URLError, TimeoutError, json.JSONDecodeError):
        return None
