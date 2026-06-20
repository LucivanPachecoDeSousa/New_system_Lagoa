from database.connection import Database


class EntradaCalcarioController:
    def __init__(self):
        self.db = Database()

    def listar(self, apenas_ativos=True):
        conn = self.db.connect()
        cursor = conn.cursor()
        query = """
            SELECT e.*, c.nome AS calcario_nome, l.nome_lote,
                   ent.razao_social AS entidade_nome
            FROM entradas_calcario e
            JOIN calcario_tipos c ON e.calcario_tipo_id = c.id
            LEFT JOIN lotes l ON e.lote_id = l.id
            JOIN entidades ent ON e.entidade_id = ent.id
        """
        conds = []
        if apenas_ativos:
            conds.append("e.ativo = 1")
        if conds:
            query += " WHERE " + " AND ".join(conds)
        query += " ORDER BY e.data DESC, e.created_at DESC"
        cursor.execute(query)
        return [dict(row) for row in cursor.fetchall()]

    def buscar_por_id(self, registro_id):
        conn = self.db.connect()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT e.*, c.nome AS calcario_nome, l.nome_lote,
                   ent.razao_social AS entidade_nome
            FROM entradas_calcario e
            JOIN calcario_tipos c ON e.calcario_tipo_id = c.id
            LEFT JOIN lotes l ON e.lote_id = l.id
            JOIN entidades ent ON e.entidade_id = ent.id
            WHERE e.id = ?
        """, (registro_id,))
        row = cursor.fetchone()
        return dict(row) if row else None

    def salvar(self, dados):
        conn = self.db.connect()
        cursor = conn.cursor()
        cursor.execute(
            """INSERT INTO entradas_calcario
               (data, calcario_tipo_id, lote_id, entidade_id,
                quantidade_bag, peso_total_kg, placa, motorista,
                local_descarga, numero_nf, observacao)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                dados["data"],
                dados["calcario_tipo_id"],
                dados.get("lote_id"),
                dados["entidade_id"],
                dados.get("quantidade_bag", 0),
                dados.get("peso_total_kg", 0),
                dados.get("placa", ""),
                dados.get("motorista", ""),
                dados.get("local_descarga", ""),
                dados.get("numero_nf", ""),
                dados.get("observacao", ""),
            ),
        )
        conn.commit()
        return cursor.lastrowid

    def atualizar(self, registro_id, dados):
        conn = self.db.connect()
        cursor = conn.cursor()
        cursor.execute(
            """UPDATE entradas_calcario
               SET data = ?, calcario_tipo_id = ?, lote_id = ?, entidade_id = ?,
                   quantidade_bag = ?, peso_total_kg = ?, placa = ?, motorista = ?,
                   local_descarga = ?, numero_nf = ?, observacao = ?,
                   updated_at = CURRENT_TIMESTAMP
               WHERE id = ?""",
            (
                dados["data"],
                dados["calcario_tipo_id"],
                dados.get("lote_id"),
                dados["entidade_id"],
                dados.get("quantidade_bag", 0),
                dados.get("peso_total_kg", 0),
                dados.get("placa", ""),
                dados.get("motorista", ""),
                dados.get("local_descarga", ""),
                dados.get("numero_nf", ""),
                dados.get("observacao", ""),
                registro_id,
            ),
        )
        conn.commit()
        return cursor.rowcount > 0

    def remover(self, registro_id):
        conn = self.db.connect()
        cursor = conn.cursor()
        cursor.execute("UPDATE entradas_calcario SET ativo = 0 WHERE id = ?", (registro_id,))
        conn.commit()
        return cursor.rowcount > 0

    def listar_tipos_calcario(self):
        conn = self.db.connect()
        cursor = conn.cursor()
        cursor.execute("SELECT id, nome FROM calcario_tipos ORDER BY nome")
        return [dict(row) for row in cursor.fetchall()]

    def listar_lotes_calcario(self):
        conn = self.db.connect()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT l.id, l.nome_lote, e.razao_social AS entidade_nome
            FROM lotes l
            LEFT JOIN entidades e ON l.entidade_id = e.id
            WHERE l.tipo = 'calcario' AND l.ativo = 1
            ORDER BY l.nome_lote
        """)
        return [dict(row) for row in cursor.fetchall()]

    def listar_entidades(self):
        conn = self.db.connect()
        cursor = conn.cursor()
        cursor.execute("SELECT id, razao_social, cnpj_cpf FROM entidades WHERE ativo = 1 ORDER BY razao_social")
        return [dict(row) for row in cursor.fetchall()]

    def adicionar_tipo_calcario(self, nome):
        conn = self.db.connect()
        cursor = conn.cursor()
        nome = nome.strip().upper()
        cursor.execute("SELECT id FROM calcario_tipos WHERE nome = ?", (nome,))
        existing = cursor.fetchone()
        if existing:
            return existing["id"]
        cursor.execute("INSERT INTO calcario_tipos (nome) VALUES (?)", (nome,))
        conn.commit()
        return cursor.lastrowid

    def listar_locais(self):
        conn = self.db.connect()
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT local_descarga FROM entradas_calcario WHERE ativo = 1 AND local_descarga != '' ORDER BY local_descarga")
        return [row["local_descarga"] for row in cursor.fetchall()]

    def resumo_por_local(self, calcario_tipo_id=None):
        conn = self.db.connect()
        cursor = conn.cursor()
        query = """
            SELECT e.local_descarga,
                   SUM(e.peso_total_kg) AS total_peso_kg
            FROM entradas_calcario e
            WHERE e.ativo = 1 AND e.local_descarga != ''
        """
        params = []
        if calcario_tipo_id:
            query += " AND e.calcario_tipo_id = ?"
            params.append(calcario_tipo_id)
        query += " GROUP BY e.local_descarga ORDER BY e.local_descarga"
        cursor.execute(query, params)
        return [dict(row) for row in cursor.fetchall()]
