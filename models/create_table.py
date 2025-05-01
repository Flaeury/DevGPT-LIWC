import sqlite3


def conexao():
    conn = sqlite3.connect(database='extracao.db',
                           check_same_thread=False)

    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS conversas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_name TEXT,
            genero TEXT,
            ordem_mensagem INTEGER,
            texto_usuario TEXT,
            texto_ia TEXT,
            analytical_thinking REAL,
            clout REAL,
            authentic REAL,
            emotional_tone REAL
        )
    ''')
    conn.commit()
    conn.close()
    return conn


conn = conexao()
