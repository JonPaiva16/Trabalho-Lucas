"""Modelos Pydantic da API de catalogo de livros."""

from pydantic import BaseModel, Field


class LivroCriar(BaseModel):
    """Dados enviados para criar um livro."""

    titulo: str = Field(..., min_length=1, description="Titulo do livro")
    autor: str = Field(..., min_length=1, description="Nome do autor")
    ano: int = Field(..., ge=0, description="Ano de publicacao")
    isbn: str = Field(..., min_length=1, description="Codigo ISBN")


class LivroAtualizar(BaseModel):
    """Dados enviados para atualizar um livro."""

    titulo: str = Field(..., min_length=1)
    autor: str = Field(..., min_length=1)
    ano: int = Field(..., ge=0)
    isbn: str = Field(..., min_length=1)


class Livro(BaseModel):
    """Livro completo devolvido pela API."""

    id: int
    titulo: str
    autor: str
    ano: int
    isbn: str
