import sqlite3
from database.connection import Database


class EntidadeController:
    def __init__(self):
        self.db = Database()

    def listar(self, apenas_ativos=True):
        conn = self.db.connect()
        cursor = conn.cursor()
        if apenas_ativos:
            cursor.execute("SELECT * FROM entidades WHERE ativo = 1 ORDER BY razao_social")
        else:
            cursor.execute("SELECT * FROM entidades ORDER BY razao_social")
        return [dict(row) for row in cursor.fetchall()]

    def buscar_por_id(self, entidade_id):
        conn = self.db.connect()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM entidades WHERE id = ?", (entidade_id,))
        row = cursor.fetchone()
        return dict(row) if row else None

    def buscar_por_cnpj_cpf(self, doc):
        conn = self.db.connect()
        cursor = conn.cursor()
        doc_limpo = ''.join(c for c in doc if c.isdigit())
        cursor.execute("SELECT * FROM entidades WHERE cnpj_cpf = ?", (doc_limpo,))
        row = cursor.fetchone()
        return dict(row) if row else None

    def salvar(self, dados):
        conn = self.db.connect()
        cursor = conn.cursor()

        doc = ''.join(c for c in dados["cnpj_cpf"] if c.isdigit())

        try:
            cursor.execute(
                """INSERT INTO entidades (
                    cnpj_cpf, tipo_pessoa, razao_social, nome_fantasia,
                    logradouro, numero, complemento, bairro,
                    cidade, estado, cep, telefone, email, inscricao_estadual
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    doc,
                    dados.get("tipo_pessoa", "juridica"),
                    dados["razao_social"],
                    dados.get("nome_fantasia", ""),
                    dados.get("logradouro", ""),
                    dados.get("numero", ""),
                    dados.get("complemento", ""),
                    dados.get("bairro", ""),
                    dados.get("cidade", ""),
                    dados.get("estado", ""),
                    dados.get("cep", ""),
                    dados.get("telefone", ""),
                    dados.get("email", ""),
                    dados.get("inscricao_estadual", ""),
                ),
            )
            conn.commit()
            return cursor.lastrowid
        except sqlite3.IntegrityError:
            raise ValueError(f"Já existe uma entidade cadastrada com o documento {doc}.")

    def atualizar(self, entidade_id, dados):
        conn = self.db.connect()
        cursor = conn.cursor()

        doc = ''.join(c for c in dados["cnpj_cpf"] if c.isdigit())

        try:
            cursor.execute(
                """UPDATE entidades SET
                    cnpj_cpf = ?, tipo_pessoa = ?, razao_social = ?, nome_fantasia = ?,
                    logradouro = ?, numero = ?, complemento = ?, bairro = ?,
                    cidade = ?, estado = ?, cep = ?, telefone = ?, email = ?,
                    inscricao_estadual = ?, updated_at = CURRENT_TIMESTAMP
                   WHERE id = ?""",
                (
                    doc,
                    dados.get("tipo_pessoa", "juridica"),
                    dados["razao_social"],
                    dados.get("nome_fantasia", ""),
                    dados.get("logradouro", ""),
                    dados.get("numero", ""),
                    dados.get("complemento", ""),
                    dados.get("bairro", ""),
                    dados.get("cidade", ""),
                    dados.get("estado", ""),
                    dados.get("cep", ""),
                    dados.get("telefone", ""),
                    dados.get("email", ""),
                    dados.get("inscricao_estadual", ""),
                    entidade_id,
                ),
            )
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            raise ValueError(f"Já existe outra entidade cadastrada com o documento {doc}.")

    def remover(self, entidade_id):
        conn = self.db.connect()
        cursor = conn.cursor()
        cursor.execute("UPDATE entidades SET ativo = 0 WHERE id = ?", (entidade_id,))
        conn.commit()
        return cursor.rowcount > 0

    def restaurar(self, entidade_id):
        conn = self.db.connect()
        cursor = conn.cursor()
        cursor.execute("UPDATE entidades SET ativo = 1 WHERE id = ?", (entidade_id,))
        conn.commit()
        return cursor.rowcount > 0
