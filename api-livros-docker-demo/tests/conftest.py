"""Configuracao dos testes."""

import pytest
from fastapi.testclient import TestClient

import main
from app.repository import RepositorioEmMemoria
from app.services.livro import ServicoLivros


@pytest.fixture(autouse=True)
def limpar_repositorio():
    """Garante que cada teste comece com repositorio vazio."""
    main.servico = ServicoLivros(RepositorioEmMemoria())
    yield


@pytest.fixture
def client():
    """Cliente de testes da API FastAPI."""
    return TestClient(main.app)


@pytest.fixture
def livro_payload():
    """Payload padrao para cadastro de livro."""
    return {
        "titulo": "Dom Casmurro",
        "autor": "Machado de Assis",
        "ano": 1899,
        "isbn": "9788535910663",
    }
