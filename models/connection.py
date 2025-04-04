import sqlite3


def conexao():
    conn = sqlite3.connect(database='NOME.db', check_same_thread=False)
    # flash("Abrindo conexão")
    return conn


conn = conexao()
