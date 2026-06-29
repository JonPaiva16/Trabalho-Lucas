"""
Testes de integração da API de catálogo de livros.

Rodam contra o TestClient do FastAPI (não precisam de servidor rodando).
Cobrem todos os endpoints e casos de erro.
"""

import pytest
from fastapi.testclient import TestClient

from main import app, get_repo
from repository import RepositorioEmMemoria


@pytest.fixture
def client():
    """
    Cria um TestClient com repositório novo e isolado para cada teste.

    A aplicação usa um repositório único (singleton) durante sua execução
    normal, então aqui sobrescrevemos a dependência get_repo para que cada
    teste receba sua própria RepositorioEmMemoria() vazia, sem interferir
    nos outros testes.
    """
    repo_de_teste = RepositorioEmMemoria()
    app.dependency_overrides[get_repo] = lambda: repo_de_teste
    yield TestClient(app)
    app.dependency_overrides.clear()


# ── Dados de exemplo ──────────────────────────────────────────────

LIVRO_VALIDO = {
    "titulo": "Dom Casmurro",
    "autor": "Machado de Assis",
    "ano": 1899,
    "isbn": "978-85-7232-001-0",
}

LIVRO_VALIDO_2 = {
    "titulo": "O Alquimista",
    "autor": "Paulo Coelho",
    "ano": 1988,
    "isbn": "978-85-7542-001-1",
}


# ── Testes do GET /livros ────────────────────────────────────────

class TestListarLivros:
    def test_lista_vazia(self, client):
        """API recém-criada deve retornar lista vazia."""
        resp = client.get("/livros")
        assert resp.status_code == 200
        assert resp.json() == []

    def test_lista_com_livros(self, client):
        """Após criar livros, a lista deve contê-los."""
        client.post("/livros", json=LIVRO_VALIDO)
        client.post("/livros", json=LIVRO_VALIDO_2)
        resp = client.get("/livros")
        assert resp.status_code == 200
        assert len(resp.json()) == 2


# ── Testes do POST /livros ───────────────────────────────────────

class TestCriarLivro:
    def test_criar_livro_valido(self, client):
        """Criar um livro com dados válidos deve retornar 201."""
        resp = client.post("/livros", json=LIVRO_VALIDO)
        assert resp.status_code == 201
        data = resp.json()
        assert data["id"] == 1
        assert data["titulo"] == LIVRO_VALIDO["titulo"]
        assert data["autor"] == LIVRO_VALIDO["autor"]
        assert data["ano"] == LIVRO_VALIDO["ano"]
        assert data["isbn"] == LIVRO_VALIDO["isbn"]

    def test_criar_livro_sem_titulo(self, client):
        """Título vazio deve ser rejeitado (validação Pydantic)."""
        dados = {**LIVRO_VALIDO, "titulo": ""}
        resp = client.post("/livros", json=dados)
        assert resp.status_code == 422

    def test_criar_livro_ano_negativo(self, client):
        """Ano negativo deve ser rejeitado."""
        dados = {**LIVRO_VALIDO, "ano": -1}
        resp = client.post("/livros", json=dados)
        assert resp.status_code == 422

    def test_criar_livro_ano_futuro(self, client):
        """Ano acima de 2100 deve ser rejeitado."""
        dados = {**LIVRO_VALIDO, "ano": 3000}
        resp = client.post("/livros", json=dados)
        assert resp.status_code == 422

    def test_ids_sequenciais(self, client):
        """IDs devem ser sequenciais (1, 2, 3...)."""
        r1 = client.post("/livros", json=LIVRO_VALIDO)
        r2 = client.post("/livros", json=LIVRO_VALIDO_2)
        assert r1.json()["id"] == 1
        assert r2.json()["id"] == 2


# ── Testes do GET /livros/{id} ───────────────────────────────────

class TestBuscarLivro:
    def test_buscar_livro_existente(self, client):
        """Buscar por ID existente deve retornar o livro."""
        client.post("/livros", json=LIVRO_VALIDO)
        resp = client.get("/livros/1")
        assert resp.status_code == 200
        assert resp.json()["titulo"] == LIVRO_VALIDO["titulo"]

    def test_buscar_livro_inexistente(self, client):
        """Buscar por ID inexistente deve retornar 404."""
        resp = client.get("/livros/999")
        assert resp.status_code == 404


# ── Testes do PUT /livros/{id} ───────────────────────────────────

class TestAtualizarLivro:
    def test_atualizar_livro_existente(self, client):
        """Atualizar livro existente deve modificar os campos."""
        client.post("/livros", json=LIVRO_VALIDO)
        dados_atualizados = {**LIVRO_VALIDO, "titulo": "Dom Casmurro - Edição Especial"}
        resp = client.put("/livros/1", json=dados_atualizados)
        assert resp.status_code == 200
        assert resp.json()["titulo"] == "Dom Casmurro - Edição Especial"

    def test_atualizar_livro_inexistente(self, client):
        """Atualizar livro inexistente deve retornar 404."""
        resp = client.put("/livros/999", json=LIVRO_VALIDO)
        assert resp.status_code == 404


# ── Testes do DELETE /livros/{id} ────────────────────────────────

class TestRemoverLivro:
    def test_remover_livro_existente(self, client):
        """Remover livro existente deve retornar mensagem de sucesso."""
        client.post("/livros", json=LIVRO_VALIDO)
        resp = client.delete("/livros/1")
        assert resp.status_code == 200
        assert resp.json()["mensagem"] == "Livro removido com sucesso"

    def test_remover_livro_inexistente(self, client):
        """Remover livro inexistente deve retornar 404."""
        resp = client.delete("/livros/999")
        assert resp.status_code == 404

    def test_remover_e_listar(self, client):
        """Após remover, o livro não deve aparecer na listagem."""
        client.post("/livros", json=LIVRO_VALIDO)
        client.delete("/livros/1")
        resp = client.get("/livros")
        assert resp.json() == []