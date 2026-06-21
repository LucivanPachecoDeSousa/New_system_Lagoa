from database.connection import Database


class EntradaAduboController:
    def __init__(self):
        self.db = Database()

    def listar(self, apenas_ativos=True):
        conn = self.db.connect()
        cursor = conn.cursor()
        query = """
            SELECT e.*, a.nome AS adubo_nome, l.nome_lote,
                   ent.razao_social AS entidade_nome,
                   f.nome AS fazenda_nome
            FROM entradas_adubo e
            JOIN adubo_tipos a ON e.adubo_tipo_id = a.id
            LEFT JOIN lotes l ON e.lote_id = l.id
            JOIN entidades ent ON e.entidade_id = ent.id
            LEFT JOIN fazendas f ON e.fazenda_id = f.id
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
            SELECT e.*, a.nome AS adubo_nome, l.nome_lote,
                   ent.razao_social AS entidade_nome,
                   f.nome AS fazenda_nome
            FROM entradas_adubo e
            JOIN adubo_tipos a ON e.adubo_tipo_id = a.id
            LEFT JOIN lotes l ON e.lote_id = l.id
            JOIN entidades ent ON e.entidade_id = ent.id
            LEFT JOIN fazendas f ON e.fazenda_id = f.id
            WHERE e.id = ?
        """, (registro_id,))
        row = cursor.fetchone()
        return dict(row) if row else None

    def salvar(self, dados):
        conn = self.db.connect()
        cursor = conn.cursor()
        cursor.execute(
            """INSERT INTO entradas_adubo
               (data, adubo_tipo_id, lote_id, entidade_id,
                quantidade_bag, peso_total_kg, placa, motorista,
                fazenda_id, numero_nf, observacao)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                dados["data"],
                dados["adubo_tipo_id"],
                dados.get("lote_id"),
                dados["entidade_id"],
                dados.get("quantidade_bag", 0),
                dados.get("peso_total_kg", 0),
                dados.get("placa", ""),
                dados.get("motorista", ""),
                dados.get("fazenda_id"),
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
            """UPDATE entradas_adubo
               SET data = ?, adubo_tipo_id = ?, lote_id = ?, entidade_id = ?,
                   quantidade_bag = ?, peso_total_kg = ?, placa = ?, motorista = ?,
                   fazenda_id = ?, numero_nf = ?, observacao = ?,
                   updated_at = CURRENT_TIMESTAMP
               WHERE id = ?""",
            (
                dados["data"],
                dados["adubo_tipo_id"],
                dados.get("lote_id"),
                dados["entidade_id"],
                dados.get("quantidade_bag", 0),
                dados.get("peso_total_kg", 0),
                dados.get("placa", ""),
                dados.get("motorista", ""),
                dados.get("fazenda_id"),
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
        cursor.execute("UPDATE entradas_adubo SET ativo = 0 WHERE id = ?", (registro_id,))
        conn.commit()
        return cursor.rowcount > 0

    def listar_tipos_adubo(self):
        conn = self.db.connect()
        cursor = conn.cursor()
        cursor.execute("SELECT id, nome FROM adubo_tipos ORDER BY nome")
        return [dict(row) for row in cursor.fetchall()]

    def listar_lotes_adubo(self, adubo_tipo_id=None, fazenda_id=None):
        conn = self.db.connect()
        cursor = conn.cursor()
        # Only show lotes that actually have entries in entradas_adubo matching the filters
        query = """
            SELECT DISTINCT l.id, l.nome_lote, e.razao_social AS entidade_nome
            FROM lotes l
            LEFT JOIN entidades e ON l.entidade_id = e.id
            JOIN entradas_adubo ea ON ea.lote_id = l.id
            WHERE l.tipo = 'adubo' AND l.ativo = 1
        """
        params = []
        if adubo_tipo_id:
            query += " AND ea.adubo_tipo_id = ?"
            params.append(adubo_tipo_id)
        if fazenda_id:
            query += " AND ea.fazenda_id = ?"
            params.append(fazenda_id)
        query += " ORDER BY l.nome_lote"
        cursor.execute(query, params)
        return [dict(row) for row in cursor.fetchall()]

    def listar_entidades(self):
        conn = self.db.connect()
        cursor = conn.cursor()
        cursor.execute("SELECT id, razao_social, cnpj_cpf FROM entidades WHERE ativo = 1 ORDER BY razao_social")
        return [dict(row) for row in cursor.fetchall()]

    def listar_fazendas(self):
        conn = self.db.connect()
        cursor = conn.cursor()
        cursor.execute("SELECT id, nome FROM fazendas ORDER BY nome")
        return [dict(row) for row in cursor.fetchall()]

    def adicionar_tipo_adubo(self, nome):
        conn = self.db.connect()
        cursor = conn.cursor()
        nome = nome.strip().upper()
        cursor.execute("SELECT id FROM adubo_tipos WHERE nome = ?", (nome,))
        existing = cursor.fetchone()
        if existing:
            return existing["id"]
        cursor.execute("INSERT INTO adubo_tipos (nome) VALUES (?)", (nome,))
        conn.commit()
        return cursor.lastrowid

    def resumo_saldo_fazendas(self, adubo_tipo_id=None):
        conn = self.db.connect()
        cursor = conn.cursor()
        query = """
            SELECT lf.fazenda_id, f.nome AS fazenda_nome,
                   SUM(lf.quantidade) AS esperado_bag
            FROM lote_fazendas lf
            JOIN lotes l ON lf.lote_id = l.id
            JOIN fazendas f ON lf.fazenda_id = f.id
            WHERE l.tipo = 'adubo' AND l.ativo = 1
        """
        params = []
        if adubo_tipo_id:
            query += " AND l.tipo_adubo_id = ?"
            params.append(adubo_tipo_id)
        query += " GROUP BY lf.fazenda_id"
        cursor.execute(query, params)
        esperado = {row["fazenda_id"]: {"fazenda_nome": row["fazenda_nome"], "bags": row["esperado_bag"]} for row in cursor.fetchall()}

        entregue_query = """
            SELECT e.fazenda_id, f.nome AS fazenda_nome,
                   SUM(e.quantidade_bag) AS entregue_bag
            FROM entradas_adubo e
            JOIN fazendas f ON e.fazenda_id = f.id
            WHERE e.ativo = 1 AND e.fazenda_id IS NOT NULL
        """
        params2 = []
        if adubo_tipo_id:
            entregue_query += " AND e.adubo_tipo_id = ?"
            params2.append(adubo_tipo_id)
        entregue_query += " GROUP BY e.fazenda_id"
        cursor.execute(entregue_query, params2)
        entregue = {row["fazenda_id"]: {"fazenda_nome": row["fazenda_nome"], "bags": row["entregue_bag"]} for row in cursor.fetchall()}

        todas = set(list(esperado.keys()) + list(entregue.keys()))
        resultado = []
        for fid in sorted(todas):
            e = esperado.get(fid) or entregue.get(fid) or {"fazenda_nome": "", "bags": 0}
            en = entregue.get(fid) or esperado.get(fid) or {"fazenda_nome": "", "bags": 0}
            resultado.append({
                "fazenda_nome": e.get("fazenda_nome") or en.get("fazenda_nome", ""),
                "esperado": e.get("bags", 0) or 0,
                "entregue": en.get("bags", 0) or 0,
                "saldo": (e.get("bags", 0) or 0) - (en.get("bags", 0) or 0),
            })
        return resultado
