"""Testes de integracao das rotas de livros."""

from datetime import date
from unittest.mock import patch


@patch("app.services.livro.consultar_open_library")
def test_post_livros_sucesso(mock_open_library, client, livro_payload):
    mock_open_library.return_value = None

    resposta = client.post("/livros", json=livro_payload)

    assert resposta.status_code == 201
    corpo = resposta.json()
    assert corpo["id"] == 1
    assert corpo["titulo"] == livro_payload["titulo"]
    assert corpo["isbn"] == livro_payload["isbn"]


@patch("app.services.livro.consultar_open_library")
def test_post_livros_isbn_duplicado(mock_open_library, client, livro_payload):
    mock_open_library.return_value = None
    client.post("/livros", json=livro_payload)

    resposta = client.post("/livros", json=livro_payload)

    assert resposta.status_code == 409
    assert resposta.json()["detail"] == "ISBN ja cadastrado"


@patch("app.services.livro.consultar_open_library")
def test_post_livros_ano_futuro(mock_open_library, client, livro_payload):
    mock_open_library.return_value = None
    livro_payload["ano"] = date.today().year + 1

    resposta = client.post("/livros", json=livro_payload)

    assert resposta.status_code == 400
    assert resposta.json()["detail"] == "Ano de publicacao nao pode ser futuro"
    mock_open_library.assert_not_called()


@patch("app.services.livro.consultar_open_library")
def test_get_livros(mock_open_library, client, livro_payload):
    mock_open_library.return_value = None
    client.post("/livros", json=livro_payload)

    resposta = client.get("/livros")

    assert resposta.status_code == 200
    assert resposta.json()[0]["isbn"] == livro_payload["isbn"]


def test_get_livro_inexistente_retorna_404(client):
    resposta = client.get("/livros/999")

    assert resposta.status_code == 404
    assert resposta.json()["detail"] == "Livro nao encontrado"


def test_post_livros_payload_invalido_retorna_422(client):
    resposta = client.post("/livros", json={"titulo": "", "autor": "Autor"})

    assert resposta.status_code == 422
