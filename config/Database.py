# database.py
# Configuração centralizada da conexão com o SQL Server.
# Todos os repositories importam get_conexao() daqui.

import pyodbc
from fastapi import HTTPException

SERVER   = "localhost\\SQLEXPRESS"
DATABASE = "bytebook"

def get_conexao():
    try:
        connection_string = (
            f"DRIVER={{ODBC Driver 17 for SQL Server}};"
            f"SERVER={SERVER};"
            f"DATABASE={DATABASE};"
            f"Trusted_Connection=yes;"
        )
        return pyodbc.connect(connection_string)
    except pyodbc.Error as e:
        raise HTTPException(status_code=503, detail=f"Erro ao conectar com o banco: {e}")