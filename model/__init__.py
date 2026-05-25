# model/__init__.py
# Exporta todos os models de um lugar só.
# Permite importar assim:  from model import AutorModel, LivroResponse, ..

from model.AutorModel      import AutorModel, AutorResponse
from model.LivroModel      import LivroModel, LivroResponse, ConfirmarLivroISBN, ResultadoISBN
from model.ClienteModel    import ClienteModel, ClienteResponse
from model.EmprestimoModel import EmprestimoModel, DevolucaoModel, EmprestimoResponse