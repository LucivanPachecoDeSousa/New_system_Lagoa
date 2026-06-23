from database.connection import Database


class MaterialConstrucaoController:
    def __init__(self):
        self.db = Database()

    def listar(self, apenas_ativos=True):
        conn = self.db.connect()
        cursor = conn.cursor()
        query = """
            SELECT m.*, t.nome AS material_nome
            FROM materiais_construcao m
            JOIN material_construcao_tipos t ON m.material_id = t.id
        """
        conds = []
        if apenas_ativos:
            conds.append("m.ativo = 1")
        if conds:
            query += " WHERE " + " AND ".join(conds)
        query += " ORDER BY m.data DESC, m.created_at DESC"
        cursor.execute(query)
        return [dict(row) for row in cursor.fetchall()]

    def buscar_por_id(self, registro_id):
        conn = self.db.connect()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT m.*, t.nome AS material_nome
            FROM materiais_construcao m
            JOIN material_construcao_tipos t ON m.material_id = t.id
            WHERE m.id = ?
        """, (registro_id,))
        row = cursor.fetchone()
        return dict(row) if row else None

    def salvar(self, dados):
        conn = self.db.connect()
        cursor = conn.cursor()
        material_id = self._obter_material_id(dados["material"])
        cursor.execute(
            """INSERT INTO materiais_construcao
               (data, material_id, empresa_fornecedora, transportadora, peso_kg, metros_cubicos, unidade)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (
                dados["data"],
                material_id,
                dados.get("empresa_fornecedora", ""),
                dados.get("transportadora", ""),
                dados.get("peso_kg", 0),
                dados.get("metros_cubicos", 0),
                dados.get("unidade", "M³"),
            ),
        )
        conn.commit()
        return cursor.lastrowid

    def atualizar(self, registro_id, dados):
        conn = self.db.connect()
        cursor = conn.cursor()
        material_id = self._obter_material_id(dados["material"])
        cursor.execute(
            """UPDATE materiais_construcao
               SET data = ?, material_id = ?, empresa_fornecedora = ?,
                   transportadora = ?, peso_kg = ?, metros_cubicos = ?,
                   unidade = ?, updated_at = CURRENT_TIMESTAMP
               WHERE id = ?""",
            (
                dados["data"],
                material_id,
                dados.get("empresa_fornecedora", ""),
                dados.get("transportadora", ""),
                dados.get("peso_kg", 0),
                dados.get("metros_cubicos", 0),
                dados.get("unidade", "M³"),
                registro_id,
            ),
        )
        conn.commit()
        return cursor.rowcount > 0

    def remover(self, registro_id):
        conn = self.db.connect()
        cursor = conn.cursor()
        cursor.execute("UPDATE materiais_construcao SET ativo = 0 WHERE id = ?", (registro_id,))
        conn.commit()
        return cursor.rowcount > 0

    def _obter_material_id(self, nome_material):
        conn = self.db.connect()
        cursor = conn.cursor()
        nome = nome_material.strip().upper()
        cursor.execute("SELECT id FROM material_construcao_tipos WHERE nome = ?", (nome,))
        row = cursor.fetchone()
        if row:
            return row["id"]
        cursor.execute("INSERT INTO material_construcao_tipos (nome) VALUES (?)", (nome,))
        conn.commit()
        return cursor.lastrowid

    def listar_tipos_material(self):
        conn = self.db.connect()
        cursor = conn.cursor()
        cursor.execute("SELECT id, nome FROM material_construcao_tipos ORDER BY nome")
        return [dict(row) for row in cursor.fetchall()]

    def listar_entidades(self):
        conn = self.db.connect()
        cursor = conn.cursor()
        cursor.execute("SELECT id, razao_social, cnpj_cpf FROM entidades WHERE ativo = 1 ORDER BY razao_social")
        return [dict(row) for row in cursor.fetchall()]
