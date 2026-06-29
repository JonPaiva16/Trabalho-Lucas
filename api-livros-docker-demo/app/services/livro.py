"""Service de livros com regras de negocio."""

from datetime import date

from app.clients.open_library import consultar_open_library
from app.models import Livro, LivroAtualizar, LivroCriar
from app.repository import RepositorioLivros


class ISBNDuplicadoError(ValueError):
    """Erro para ISBN duplicado."""


class AnoFuturoError(ValueError):
    """Erro para ano de publicacao futuro."""


class ServicoLivros:
    """Camada de servico responsavel pelas regras de negocio."""

    def __init__(self, repositorio: RepositorioLivros) -> None:
        self._repo = repositorio

    def listar(self) -> list[Livro]:
        return self._repo.listar()

    def buscar(self, livro_id: int) -> Livro | None:
        return self._repo.buscar_por_id(livro_id)

    def criar(self, dados: LivroCriar) -> Livro:
        if self._repo.get_by_isbn(dados.isbn) is not None:
            raise ISBNDuplicadoError("ISBN ja cadastrado")

        if dados.ano > date.today().year:
            raise AnoFuturoError("Ano de publicacao nao pode ser futuro")

        consultar_open_library(dados.isbn)
        return self._repo.adicionar(dados)

    def atualizar(self, livro_id: int, dados: LivroAtualizar) -> Livro | None:
        return self._repo.atualizar(livro_id, dados)

    def remover(self, livro_id: int) -> bool:
        return self._repo.remover(livro_id)
