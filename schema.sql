-- ============================================================
-- ByteBook — Script de Criação do Banco de Dados
-- Execute no SQL Server Management Studio (SSMS)
-- Servidor: localhost\SQLEXPRESS | Banco: bytebook
-- ============================================================

IF NOT EXISTS (SELECT name FROM sys.databases WHERE name = 'bytebook')
    CREATE DATABASE bytebook;
GO

USE bytebook;
GO

-- ============================================================
-- TABELA: autor
-- ============================================================
IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='autor' AND xtype='U')
BEGIN
    CREATE TABLE autor (
        id_autor_pk  INT IDENTITY(1,1) PRIMARY KEY,
        nome         NVARCHAR(255)     NOT NULL,
        dt_nasc      DATE              NULL
    );
    PRINT 'Tabela autor criada.';
END
GO

-- ============================================================
-- TABELA: Livro
-- quantidade = total de exemplares físicos no estoque
-- ============================================================
IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='Livro' AND xtype='U')
BEGIN
    CREATE TABLE Livro (
        id_livro       INT IDENTITY(1,1) PRIMARY KEY,
        nome           NVARCHAR(255)     NOT NULL,
        isbn           NVARCHAR(13)      NULL UNIQUE,
        quantidade     INT               NOT NULL DEFAULT 0,
        dt_lancamento  DATE              NULL,
        editora        NVARCHAR(255)     NULL,
        genero         NVARCHAR(100)     NULL,
        id_autor_fk    INT               NULL,

        CONSTRAINT FK_Livro_Autor FOREIGN KEY (id_autor_fk)
            REFERENCES autor(id_autor_pk)
    );
    PRINT 'Tabela Livro criada.';
END
GO

-- ============================================================
-- TABELA: cliente
-- ============================================================
IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='cliente' AND xtype='U')
BEGIN
    CREATE TABLE cliente (
        id_cliente_pk  INT IDENTITY(1,1) PRIMARY KEY,
        nome           NVARCHAR(255)     NOT NULL,
        endereco       NVARCHAR(500)     NULL,
        email          NVARCHAR(255)     NULL UNIQUE,
        cpf            NVARCHAR(14)      NULL UNIQUE,
        telefone       NVARCHAR(20)      NULL
    );
    PRINT 'Tabela cliente criada.';
END
GO

-- ============================================================
-- TABELA: emprestimo
-- ============================================================
IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='emprestimo' AND xtype='U')
BEGIN
    CREATE TABLE emprestimo (
        id_emprestimo_pk   INT IDENTITY(1,1) PRIMARY KEY,
        id_livro_fk        INT           NOT NULL,
        id_cliente_fk      INT           NOT NULL,
        dt_emprestimo      DATE          NOT NULL DEFAULT CAST(GETDATE() AS DATE),
        dt_devolucao_prev  DATE          NOT NULL,
        dt_devolucao_real  DATE          NULL,
        status             NVARCHAR(20)  NOT NULL DEFAULT 'ativo'
                           CHECK (status IN ('ativo', 'devolvido')),

        CONSTRAINT FK_Emprestimo_Livro    FOREIGN KEY (id_livro_fk)   REFERENCES Livro(id_livro),
        CONSTRAINT FK_Emprestimo_Cliente  FOREIGN KEY (id_cliente_fk) REFERENCES cliente(id_cliente_pk)
    );
    PRINT 'Tabela emprestimo criada.';
END
GO

PRINT '============================';
PRINT 'ByteBook — Banco configurado!';
PRINT '============================';
