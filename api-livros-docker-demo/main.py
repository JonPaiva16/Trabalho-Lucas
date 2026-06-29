from fastapi import FastAPI, HTTPException, status
from models import Livro, LivroCriar, LivroAtualizar
from repository import RepositorioEmMemoria, RepositorioLivros


app = FastAPI(title="Catalogo de Livros", version="1.0.0")


# =========================================================
# SERVIÇO (AGORA RECRIÁVEL)
# =========================================================
class ServicoLivros:
    def __init__(self, repositorio: RepositorioLivros) -> None:
        self._repo = repositorio

    def listar(self) -> list[Livro]:
        return self._repo.listar()

    def buscar(self, livro_id: int) -> Livro | None:
        return self._repo.buscar_por_id(livro_id)

    def criar(self, dados: LivroCriar) -> Livro:
        return self._repo.adicionar(dados)

    def atualizar(self, livro_id: int, dados: LivroAtualizar) -> Livro | None:
        return self._repo.atualizar(livro_id, dados)

    def remover(self, livro_id: int) -> bool:
        return self._repo.remover(livro_id)


# =========================================================
# FUNÇÃO DE RESET (ESSENCIAL PARA OS TESTES)
# =========================================================
def criar_servico():
    return ServicoLivros(RepositorioEmMemoria())


# instância global inicial
servico = criar_servico()


# =========================================================
# ROTAS
# =========================================================

@app.get("/livros", response_model=list[Livro])
def listar_livros():
    return servico.listar()


@app.get("/livros/{livro_id}", response_model=Livro)
def buscar_livro(livro_id: int):
    livro = servico.buscar(livro_id)
    if livro is None:
        raise HTTPException(status_code=404, detail="Livro nao encontrado")
    return livro


@app.post("/livros", response_model=Livro, status_code=status.HTTP_201_CREATED)
def criar_livro(dados: LivroCriar):
    return servico.criar(dados)


@app.put("/livros/{livro_id}", response_model=Livro)
def atualizar_livro(livro_id: int, dados: LivroAtualizar):
    livro = servico.atualizar(livro_id, dados)
    if livro is None:
        raise HTTPException(status_code=404, detail="Livro nao encontrado")
    return livro


@app.delete("/livros/{livro_id}", status_code=200)
def remover_livro(livro_id: int):
    ok = servico.remover(livro_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Livro nao encontrado")

    return {"mensagem": "Livro removido com sucesso"}