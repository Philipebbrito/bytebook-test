# model/__init__.py
# Exporta todos os models de um lugar só.
# Permite importar assim:  from model import AutorModel, LivroResponse, ..

from model.autor_model      import AutorModel, AutorResponse
from model.livro_model      import LivroModel, LivroResponse, ConfirmarLivroISBN, ResultadoISBN
from model.cliente_model    import ClienteModel, ClienteResponse
from model.emprestimo_model import EmprestimoModel, DevolucaoModel, EmprestimoResponse