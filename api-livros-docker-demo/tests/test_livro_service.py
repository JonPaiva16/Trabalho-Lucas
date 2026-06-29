"""Testes unitarios do service de livros."""

from datetime import date
from unittest.mock import patch

import pytest

from app.models import LivroCriar
from app.repository import RepositorioEmMemoria
from app.services.livro import AnoFuturoError, ISBNDuplicadoError, ServicoLivros


def criar_service():
    """Cria service isolado para testes unitarios."""
    return ServicoLivros(RepositorioEmMemoria())


@patch("app.services.livro.consultar_open_library")
def test_criar_livro_com_sucesso(mock_open_library):
    mock_open_library.return_value = None
    service = criar_service()
    dados = LivroCriar(titulo="Dom Casmurro", autor="Machado de Assis", ano=1899, isbn="123")

    livro = service.criar(dados)

    assert livro.id == 1
    assert livro.titulo == "Dom Casmurro"
    assert livro.isbn == "123"
    mock_open_library.assert_called_once_with("123")


@patch("app.services.livro.consultar_open_library")
def test_criar_livro_com_isbn_duplicado(mock_open_library):
    mock_open_library.return_value = None
    service = criar_service()
    dados = LivroCriar(titulo="Livro 1", autor="Autor", ano=2020, isbn="999")
    service.criar(dados)

    with pytest.raises(ISBNDuplicadoError, match="ISBN ja cadastrado"):
        service.criar(dados)


@patch("app.services.livro.consultar_open_library")
def test_criar_livro_com_ano_futuro(mock_open_library):
    mock_open_library.return_value = None
    service = criar_service()
    dados = LivroCriar(
        titulo="Livro Futuro",
        autor="Autor",
        ano=date.today().year + 1,
        isbn="456",
    )

    with pytest.raises(AnoFuturoError, match="Ano de publicacao nao pode ser futuro"):
        service.criar(dados)

    mock_open_library.assert_not_called()


@patch("app.services.livro.consultar_open_library")
def test_open_library_retornando_dados(mock_open_library):
    mock_open_library.return_value = {"title": "Dom Casmurro", "publish_date": "1899"}
    service = criar_service()
    dados = LivroCriar(titulo="Dom Casmurro", autor="Machado de Assis", ano=1899, isbn="321")

    livro = service.criar(dados)

    assert livro.isbn == "321"
    mock_open_library.assert_called_once_with("321")


@patch("app.services.livro.consultar_open_library")
def test_open_library_retornando_none(mock_open_library):
    mock_open_library.return_value = None
    service = criar_service()
    dados = LivroCriar(titulo="Livro sem retorno", autor="Autor", ano=2020, isbn="654")

    livro = service.criar(dados)

    assert livro.titulo == "Livro sem retorno"
    mock_open_library.assert_called_once_with("654")
