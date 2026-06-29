from fastapi import FastAPI, HTTPException, status, Depends
from models import Livro, LivroCriar, LivroAtualizar
from repository import RepositorioEmMemoria, RepositorioLivros


app = FastAPI(title="Catalogo de Livros", version="1.0.0")


# =========================================================
# DEPENDÊNCIA (REPOSITÓRIO ÚNICO PARA TODA A APLICAÇÃO)
# =========================================================
# IMPORTANTE: o repositório precisa ser UMA ÚNICA instância
# compartilhada por todas as requisições. Se get_repo() criasse
# uma RepositorioEmMemoria() nova a cada chamada (como estava
# antes), cada requisição teria seu próprio dicionário vazio e
# os dados nunca persistiriam entre um POST e um GET, por exemplo.
_repositorio = RepositorioEmMemoria()


def get_repo():
    return _repositorio


def get_servico(repo: RepositorioLivros = Depends(get_repo)):
    return ServicoLivros(repo)


# =========================================================
# SERVIÇO
# =========================================================
class ServicoLivros:
    def __init__(self, repositorio: RepositorioLivros):
        self._repo = repositorio

    def listar(self):
        return self._repo.listar()

    def buscar(self, livro_id: int):
        return self._repo.buscar_por_id(livro_id)

    def criar(self, dados: LivroCriar):
        return self._repo.adicionar(dados)

    def atualizar(self, livro_id: int, dados: LivroAtualizar):
        return self._repo.atualizar(livro_id, dados)

    def remover(self, livro_id: int):
        return self._repo.remover(livro_id)


# =========================================================
# ROTAS (AGORA USANDO DEPENDS)
# =========================================================

@app.get("/livros", response_model=list[Livro])
def listar_livros(servico: ServicoLivros = Depends(get_servico)):
    return servico.listar()


@app.get("/livros/{livro_id}", response_model=Livro)
def buscar_livro(livro_id: int, servico: ServicoLivros = Depends(get_servico)):
    livro = servico.buscar(livro_id)
    if not livro:
        raise HTTPException(status_code=404, detail="Livro nao encontrado")
    return livro


@app.post("/livros", response_model=Livro, status_code=201)
def criar_livro(dados: LivroCriar, servico: ServicoLivros = Depends(get_servico)):
    return servico.criar(dados)


@app.put("/livros/{livro_id}", response_model=Livro)
def atualizar_livro(livro_id: int, dados: LivroAtualizar, servico: ServicoLivros = Depends(get_servico)):
    livro = servico.atualizar(livro_id, dados)
    if not livro:
        raise HTTPException(status_code=404, detail="Livro nao encontrado")
    return livro


@app.delete("/livros/{livro_id}", status_code=200)
def remover_livro(livro_id: int, servico: ServicoLivros = Depends(get_servico)):
    ok = servico.remover(livro_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Livro nao encontrado")
    return {"mensagem": "Livro removido com sucesso"}