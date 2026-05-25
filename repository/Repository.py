# repository.py
# Camada de acesso ao banco de dados.
# Contém todas as classes Repository do sistema — SQL puro via pyodbc.
# Equivalente ao @Repository do Spring Boot.

import pyodbc
from fastapi import HTTPException
from model.ClienteModel import (ClienteModel, ClienteResponse)
from model.AutorModel import (AutorModel, AutorResponse)
from model.EmprestimoModel import (EmprestimoModel, EmprestimoResponse,DevolucaoModel)
from model.LivroModel import (LivroModel, LivroResponse, ConfirmarLivroISBN, ResultadoISBN)


# ══════════════════════════════════════════════════════════════
# AUTOR
# ══════════════════════════════════════════════════════════════

class AutorRepository:

    def __init__(self, conn: pyodbc.Connection):
        self.conn = conn

    def criar_autor(self, autor: AutorModel) -> AutorResponse:
        """Insere um novo autor e retorna com ID gerado pelo banco."""
        sql = """
            INSERT INTO autor (nome, dt_nasc)
            OUTPUT INSERTED.id_autor_pk
            VALUES (?, ?)
        """
        try:
            cursor = self.conn.cursor()
            cursor.execute(sql, autor.nome, autor.dt_nasc)
            row = cursor.fetchone()
            self.conn.commit()
            return AutorResponse(id_autor=row[0], nome=autor.nome, dt_nasc=autor.dt_nasc)
        except pyodbc.Error as e:
            self.conn.rollback()
            raise HTTPException(status_code=500, detail=f"Erro ao criar autor: {e}")
        finally:
            cursor.close()
            self.conn.close()

    def listar_autores(self) -> list[AutorResponse]:
        """Retorna todos os autores cadastrados."""
        sql = "SELECT id_autor_pk, nome, dt_nasc FROM autor ORDER BY nome"
        try:
            cursor = self.conn.cursor()
            cursor.execute(sql)
            return [
                AutorResponse(id_autor=r[0], nome=r[1], dt_nasc=str(r[2]) if r[2] else None)
                for r in cursor.fetchall()
            ]
        except pyodbc.Error as e:
            raise HTTPException(status_code=500, detail=f"Erro ao listar autores: {e}")
        finally:
            cursor.close()
            self.conn.close()

    def ver_autor(self, id_autor: int) -> AutorResponse:
        """Busca um autor pelo ID."""
        sql = "SELECT id_autor_pk, nome, dt_nasc FROM autor WHERE id_autor_pk = ?"
        try:
            cursor = self.conn.cursor()
            cursor.execute(sql, id_autor)
            r = cursor.fetchone()
            if not r:
                raise HTTPException(status_code=404, detail=f"Autor ID {id_autor} não encontrado.")
            return AutorResponse(id_autor=r[0], nome=r[1], dt_nasc=str(r[2]) if r[2] else None)
        except HTTPException:
            raise
        except pyodbc.Error as e:
            raise HTTPException(status_code=500, detail=f"Erro ao buscar autor: {e}")
        finally:
            cursor.close()
            self.conn.close()


# ══════════════════════════════════════════════════════════════
# LIVRO
# ══════════════════════════════════════════════════════════════

class LivroRepository:

    def __init__(self, conn: pyodbc.Connection):
        self.conn = conn

    def confirmar_ou_adicionar(self, dados: ConfirmarLivroISBN) -> ResultadoISBN:
        """
        Decisão automática baseada no ISBN:
        - ISBN novo      → cria o livro com quantidade = 1
        - ISBN existente → soma +1 na quantidade do livro já cadastrado
        """
        try:
            cursor = self.conn.cursor()

            cursor.execute(
                "SELECT id_livro, nome, isbn, quantidade, dt_lancamento, editora, genero, id_autor_fk FROM Livro WHERE isbn = ?",
                dados.isbn
            )
            livro_existente = cursor.fetchone()

            if livro_existente:
                # ISBN já cadastrado — incrementa quantidade
                nova_qtd = livro_existente[3] + 1
                cursor.execute("UPDATE Livro SET quantidade = ? WHERE id_livro = ?", nova_qtd, livro_existente[0])
                self.conn.commit()

                nome_autor = self._buscar_nome_autor(cursor, livro_existente[7])
                livro_resp = LivroResponse(
                    id_livro=livro_existente[0], nome=livro_existente[1], isbn=livro_existente[2],
                    quantidade=nova_qtd, dt_lancamento=str(livro_existente[4]) if livro_existente[4] else None,
                    editora=livro_existente[5], genero=livro_existente[6],
                    id_autor_fk=livro_existente[7], nome_autor=nome_autor
                )
                return ResultadoISBN(
                    mensagem=f"Livro já cadastrado. Estoque atualizado: {nova_qtd} exemplar(es).",
                    acao="exemplar_adicionado", livro=livro_resp, quantidade=nova_qtd
                )

            else:
                # ISBN novo — cadastra o livro
                cursor.execute(
                    """
                    INSERT INTO Livro (nome, isbn, quantidade, dt_lancamento, editora, genero, id_autor_fk)
                    OUTPUT INSERTED.id_livro
                    VALUES (?, ?, 1, ?, ?, ?, ?)
                    """,
                    dados.nome, dados.isbn, dados.dt_lancamento, dados.editora, dados.genero, dados.id_autor_fk
                )
                id_livro = cursor.fetchone()[0]
                self.conn.commit()

                nome_autor = self._buscar_nome_autor(cursor, dados.id_autor_fk)
                livro_resp = LivroResponse(
                    id_livro=id_livro, nome=dados.nome, isbn=dados.isbn, quantidade=1,
                    dt_lancamento=dados.dt_lancamento, editora=dados.editora,
                    genero=dados.genero, id_autor_fk=dados.id_autor_fk, nome_autor=nome_autor
                )
                return ResultadoISBN(
                    mensagem="Livro cadastrado com sucesso.",
                    acao="livro_criado", livro=livro_resp, quantidade=1
                )

        except HTTPException:
            self.conn.rollback()
            raise
        except pyodbc.Error as e:
            self.conn.rollback()
            raise HTTPException(status_code=500, detail=f"Erro ao salvar livro: {e}")
        finally:
            cursor.close()
            self.conn.close()

    def criar_livro(self, livro: LivroModel) -> LivroResponse:
        """Cadastro manual. Rejeita ISBN duplicado."""
        try:
            cursor = self.conn.cursor()

            if livro.isbn:
                cursor.execute("SELECT id_livro FROM Livro WHERE isbn = ?", livro.isbn)
                if cursor.fetchone():
                    raise HTTPException(
                        status_code=409,
                        detail=f"ISBN '{livro.isbn}' já cadastrado. Use POST /livros/isbn/confirmar para adicionar exemplar."
                    )

            cursor.execute(
                """
                INSERT INTO Livro (nome, isbn, quantidade, dt_lancamento, editora, genero, id_autor_fk)
                OUTPUT INSERTED.id_livro
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                livro.nome, livro.isbn, livro.quantidade,
                livro.dt_lancamento, livro.editora, livro.genero, livro.id_autor_fk
            )
            id_livro = cursor.fetchone()[0]
            self.conn.commit()

            nome_autor = self._buscar_nome_autor(cursor, livro.id_autor_fk)
            return LivroResponse(
                id_livro=id_livro, nome=livro.nome, isbn=livro.isbn, quantidade=livro.quantidade,
                dt_lancamento=livro.dt_lancamento, editora=livro.editora,
                genero=livro.genero, id_autor_fk=livro.id_autor_fk, nome_autor=nome_autor
            )
        except HTTPException:
            self.conn.rollback()
            raise
        except pyodbc.Error as e:
            self.conn.rollback()
            raise HTTPException(status_code=500, detail=f"Erro ao criar livro: {e}")
        finally:
            cursor.close()
            self.conn.close()

    def listar_livros(self) -> list[LivroResponse]:
        """Lista todos os livros com nome do autor via JOIN."""
        sql = """
            SELECT l.id_livro, l.nome, l.isbn, l.quantidade,
                   l.dt_lancamento, l.editora, l.genero,
                   l.id_autor_fk, a.nome AS nome_autor
            FROM Livro l
            LEFT JOIN autor a ON a.id_autor_pk = l.id_autor_fk
            ORDER BY l.nome
        """
        try:
            cursor = self.conn.cursor()
            cursor.execute(sql)
            return [
                LivroResponse(
                    id_livro=r[0], nome=r[1], isbn=r[2], quantidade=r[3],
                    dt_lancamento=str(r[4]) if r[4] else None,
                    editora=r[5], genero=r[6], id_autor_fk=r[7], nome_autor=r[8]
                )
                for r in cursor.fetchall()
            ]
        except pyodbc.Error as e:
            raise HTTPException(status_code=500, detail=f"Erro ao listar livros: {e}")
        finally:
            cursor.close()
            self.conn.close()

    def _buscar_nome_autor(self, cursor, id_autor_fk) -> str | None:
        if not id_autor_fk:
            return None
        try:
            cursor.execute("SELECT nome FROM autor WHERE id_autor_pk = ?", id_autor_fk)
            row = cursor.fetchone()
            return row[0] if row else None
        except:
            return None


# ══════════════════════════════════════════════════════════════
# CLIENTE
# ══════════════════════════════════════════════════════════════

class ClienteRepository:

    def __init__(self, conn: pyodbc.Connection):
        self.conn = conn

    def criar_cliente(self, cliente: ClienteModel) -> ClienteResponse:
        """Insere novo cliente e retorna com ID gerado pelo banco."""
        sql = """
            INSERT INTO cliente (nome, endereco, email, cpf, telefone)
            OUTPUT INSERTED.id_cliente_pk
            VALUES (?, ?, ?, ?, ?)
        """
        try:
            cursor = self.conn.cursor()
            cursor.execute(sql, cliente.nome, cliente.endereco, cliente.email, cliente.cpf, cliente.telefone)
            row = cursor.fetchone()
            self.conn.commit()
            return ClienteResponse(
                id_cliente=row[0], nome=cliente.nome, endereco=cliente.endereco,
                email=cliente.email, cpf=cliente.cpf, telefone=cliente.telefone
            )
        except pyodbc.IntegrityError as e:
            self.conn.rollback()
            msg = str(e).lower()
            if "email" in msg:
                raise HTTPException(status_code=409, detail="E-mail já cadastrado.")
            if "cpf" in msg:
                raise HTTPException(status_code=409, detail="CPF já cadastrado.")
            raise HTTPException(status_code=409, detail="Dado duplicado.")
        except pyodbc.Error as e:
            self.conn.rollback()
            raise HTTPException(status_code=500, detail=f"Erro ao criar cliente: {e}")
        finally:
            cursor.close()
            self.conn.close()

    def listar_clientes(self) -> list[ClienteResponse]:
        """Retorna todos os clientes cadastrados."""
        sql = "SELECT id_cliente_pk, nome, endereco, email, cpf, telefone FROM cliente ORDER BY nome"
        try:
            cursor = self.conn.cursor()
            cursor.execute(sql)
            return [
                ClienteResponse(id_cliente=r[0], nome=r[1], endereco=r[2], email=r[3], cpf=r[4], telefone=r[5])
                for r in cursor.fetchall()
            ]
        except pyodbc.Error as e:
            raise HTTPException(status_code=500, detail=f"Erro ao listar clientes: {e}")
        finally:
            cursor.close()
            self.conn.close()

    def ver_cliente(self, id_cliente: int) -> ClienteResponse:
        """Busca um cliente pelo ID."""
        sql = "SELECT id_cliente_pk, nome, endereco, email, cpf, telefone FROM cliente WHERE id_cliente_pk = ?"
        try:
            cursor = self.conn.cursor()
            cursor.execute(sql, id_cliente)
            r = cursor.fetchone()
            if not r:
                raise HTTPException(status_code=404, detail=f"Cliente ID {id_cliente} não encontrado.")
            return ClienteResponse(id_cliente=r[0], nome=r[1], endereco=r[2], email=r[3], cpf=r[4], telefone=r[5])
        except HTTPException:
            raise
        except pyodbc.Error as e:
            raise HTTPException(status_code=500, detail=f"Erro ao buscar cliente: {e}")
        finally:
            cursor.close()
            self.conn.close()


# ══════════════════════════════════════════════════════════════
# EMPRESTIMO
# ══════════════════════════════════════════════════════════════

class EmprestimoRepository:

    def __init__(self, conn: pyodbc.Connection):
        self.conn = conn

    def novo_emprestimo(self, emprestimo: EmprestimoModel) -> EmprestimoResponse:
        """
        Registra empréstimo e reduz 1 do estoque do livro.
        Valida: livro com quantidade > 0 e cliente existe.
        """
        try:
            cursor = self.conn.cursor()

            cursor.execute("SELECT nome, quantidade FROM Livro WHERE id_livro = ?", emprestimo.id_livro_fk)
            livro = cursor.fetchone()
            if not livro:
                raise HTTPException(status_code=404, detail=f"Livro ID {emprestimo.id_livro_fk} não encontrado.")
            if livro[1] <= 0:
                raise HTTPException(status_code=409, detail=f"Livro '{livro[0]}' sem exemplares disponíveis.")

            cursor.execute("SELECT nome FROM cliente WHERE id_cliente_pk = ?", emprestimo.id_cliente_fk)
            cliente = cursor.fetchone()
            if not cliente:
                raise HTTPException(status_code=404, detail=f"Cliente ID {emprestimo.id_cliente_fk} não encontrado.")

            cursor.execute(
                """
                INSERT INTO emprestimo (id_livro_fk, id_cliente_fk, dt_devolucao_prev, status)
                OUTPUT INSERTED.id_emprestimo_pk, INSERTED.dt_emprestimo
                VALUES (?, ?, ?, 'ativo')
                """,
                emprestimo.id_livro_fk, emprestimo.id_cliente_fk, emprestimo.dt_devolucao_prev
            )
            row = cursor.fetchone()
            id_emp, dt_emp = row[0], row[1]

            cursor.execute("UPDATE Livro SET quantidade = quantidade - 1 WHERE id_livro = ?", emprestimo.id_livro_fk)
            self.conn.commit()

            return EmprestimoResponse(
                id_emprestimo=id_emp, id_livro_fk=emprestimo.id_livro_fk,
                id_cliente_fk=emprestimo.id_cliente_fk,
                dt_emprestimo=str(dt_emp) if dt_emp else None,
                dt_devolucao_prev=str(emprestimo.dt_devolucao_prev),
                status="ativo", nome_cliente=cliente[0], nome_livro=livro[0]
            )
        except HTTPException:
            self.conn.rollback()
            raise
        except pyodbc.Error as e:
            self.conn.rollback()
            raise HTTPException(status_code=500, detail=f"Erro ao registrar empréstimo: {e}")
        finally:
            cursor.close()
            self.conn.close()

    def encerrar_emprestimo(self, id_emprestimo: int) -> EmprestimoResponse:
        """
        Registra devolução: status → 'devolvido', preenche dt_devolucao_real
        e restaura +1 no estoque do livro.
        """
        try:
            cursor = self.conn.cursor()

            cursor.execute(
                """
                UPDATE emprestimo
                SET status = 'devolvido', dt_devolucao_real = CAST(GETDATE() AS DATE)
                OUTPUT INSERTED.id_emprestimo_pk, INSERTED.id_livro_fk, INSERTED.id_cliente_fk,
                       INSERTED.dt_emprestimo, INSERTED.dt_devolucao_prev,
                       INSERTED.dt_devolucao_real, INSERTED.status
                WHERE id_emprestimo_pk = ? AND status = 'ativo'
                """,
                id_emprestimo
            )
            row = cursor.fetchone()
            if not row:
                raise HTTPException(
                    status_code=404,
                    detail=f"Empréstimo ID {id_emprestimo} não encontrado ou já devolvido."
                )

            cursor.execute("UPDATE Livro SET quantidade = quantidade + 1 WHERE id_livro = ?", row[1])
            self.conn.commit()

            return EmprestimoResponse(
                id_emprestimo=row[0], id_livro_fk=row[1], id_cliente_fk=row[2],
                dt_emprestimo=str(row[3]) if row[3] else None,
                dt_devolucao_prev=str(row[4]) if row[4] else None,
                dt_devolucao_real=str(row[5]) if row[5] else None,
                status=row[6]
            )
        except HTTPException:
            self.conn.rollback()
            raise
        except pyodbc.Error as e:
            self.conn.rollback()
            raise HTTPException(status_code=500, detail=f"Erro ao encerrar empréstimo: {e}")
        finally:
            cursor.close()
            self.conn.close()

    def listar_emprestimos(self) -> list[EmprestimoResponse]:
        """Lista todos os empréstimos com nome do cliente e título do livro."""
        sql = """
            SELECT e.id_emprestimo_pk, e.id_livro_fk, e.id_cliente_fk,
                   e.dt_emprestimo, e.dt_devolucao_prev, e.dt_devolucao_real, e.status,
                   c.nome AS nome_cliente, l.nome AS nome_livro
            FROM emprestimo e
            INNER JOIN cliente c ON c.id_cliente_pk = e.id_cliente_fk
            INNER JOIN Livro   l ON l.id_livro      = e.id_livro_fk
            ORDER BY e.dt_emprestimo DESC
        """
        try:
            cursor = self.conn.cursor()
            cursor.execute(sql)
            return [
                EmprestimoResponse(
                    id_emprestimo=r[0], id_livro_fk=r[1], id_cliente_fk=r[2],
                    dt_emprestimo=str(r[3]) if r[3] else None,
                    dt_devolucao_prev=str(r[4]) if r[4] else None,
                    dt_devolucao_real=str(r[5]) if r[5] else None,
                    status=r[6], nome_cliente=r[7], nome_livro=r[8]
                )
                for r in cursor.fetchall()
            ]
        except pyodbc.Error as e:
            raise HTTPException(status_code=500, detail=f"Erro ao listar empréstimos: {e}")
        finally:
            cursor.close()
            self.conn.close()