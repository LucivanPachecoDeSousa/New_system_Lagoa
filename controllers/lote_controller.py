from database.connection import Database


class LoteController:
    def __init__(self):
        self.db = Database()

    def listar(self, apenas_ativos=False, tipo=None):
        conn = self.db.connect()
        cursor = conn.cursor()
        query = """
            SELECT l.*, e.razao_social AS entidade_nome,
                   a.nome AS tipo_adubo_nome,
                   c.nome AS tipo_calcario_nome
            FROM lotes l
            LEFT JOIN entidades e ON l.entidade_id = e.id
            LEFT JOIN adubo_tipos a ON l.tipo_adubo_id = a.id
            LEFT JOIN calcario_tipos c ON l.tipo_calcario_id = c.id
        """
        conds = []
        params = []
        if apenas_ativos:
            conds.append("l.ativo = 1")
        if tipo:
            if isinstance(tipo, (list, tuple)):
                placeholders = ",".join("?" for _ in tipo)
                conds.append(f"l.tipo IN ({placeholders})")
                params.extend(tipo)
            else:
                conds.append("l.tipo = ?")
                params.append(tipo)
        if conds:
            query += " WHERE " + " AND ".join(conds)
        query += " ORDER BY l.created_at DESC"
        cursor.execute(query, params)
        lotes = [dict(row) for row in cursor.fetchall()]
        for l in lotes:
            l["fazendas"] = self._listar_rateio(l["id"])
            l["talhoes"] = self._listar_talhoes(l["id"])
        return lotes

    def buscar_por_id(self, lote_id):
        conn = self.db.connect()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT l.*, e.razao_social AS entidade_nome,
                   a.nome AS tipo_adubo_nome,
                   c.nome AS tipo_calcario_nome
            FROM lotes l
            LEFT JOIN entidades e ON l.entidade_id = e.id
            LEFT JOIN adubo_tipos a ON l.tipo_adubo_id = a.id
            LEFT JOIN calcario_tipos c ON l.tipo_calcario_id = c.id
            WHERE l.id = ?
        """, (lote_id,))
        row = cursor.fetchone()
        if not row:
            return None
        lote = dict(row)
        lote["fazendas"] = self._listar_rateio(lote_id)
        lote["talhoes"] = self._listar_talhoes(lote_id)
        return lote

    def _listar_rateio(self, lote_id):
        conn = self.db.connect()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT lf.*, f.nome AS fazenda_nome
            FROM lote_fazendas lf
            JOIN fazendas f ON lf.fazenda_id = f.id
            WHERE lf.lote_id = ?
        """, (lote_id,))
        return [dict(row) for row in cursor.fetchall()]

    def _listar_talhoes(self, lote_id):
        conn = self.db.connect()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM lote_talhoes WHERE lote_id = ? ORDER BY id
        """, (lote_id,))
        return [dict(row) for row in cursor.fetchall()]

    def listar_talhoes(self, lote_id):
        return self._listar_talhoes(lote_id)

    def salvar(self, dados):
        conn = self.db.connect()
        cursor = conn.cursor()
        cursor.execute(
            """INSERT INTO lotes (tipo, entidade_id, nome_lote, tipo_adubo_id,
               tipo_calcario_id, quantidade_pedido, unidade, valor_unitario)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                dados["tipo"],
                dados.get("entidade_id"),
                dados["nome_lote"],
                dados.get("tipo_adubo_id"),
                dados.get("tipo_calcario_id"),
                dados.get("quantidade_pedido"),
                dados.get("unidade"),
                dados.get("valor_unitario", 0),
            ),
        )
        lote_id = cursor.lastrowid
        self._salvar_rateio(lote_id, dados.get("fazendas", []))
        self._salvar_talhoes(lote_id, dados.get("talhoes", []))
        conn.commit()
        return lote_id

    def atualizar(self, lote_id, dados):
        conn = self.db.connect()
        cursor = conn.cursor()
        cursor.execute(
            """UPDATE lotes
               SET tipo = ?, entidade_id = ?, nome_lote = ?,
                   tipo_adubo_id = ?, tipo_calcario_id = ?,
                   quantidade_pedido = ?, unidade = ?,
                   valor_unitario = ?, updated_at = CURRENT_TIMESTAMP
               WHERE id = ?""",
            (
                dados["tipo"],
                dados.get("entidade_id"),
                dados["nome_lote"],
                dados.get("tipo_adubo_id"),
                dados.get("tipo_calcario_id"),
                dados.get("quantidade_pedido"),
                dados.get("unidade"),
                dados.get("valor_unitario", 0),
                lote_id,
            ),
        )
        cursor.execute("DELETE FROM lote_fazendas WHERE lote_id = ?", (lote_id,))
        self._salvar_rateio(lote_id, dados.get("fazendas", []))
        cursor.execute("DELETE FROM lote_talhoes WHERE lote_id = ?", (lote_id,))
        self._salvar_talhoes(lote_id, dados.get("talhoes", []))
        conn.commit()
        return True

    def _salvar_rateio(self, lote_id, fazendas):
        conn = self.db.connect()
        cursor = conn.cursor()
        for f in fazendas:
            if f.get("quantidade", 0) > 0:
                cursor.execute(
                    "INSERT INTO lote_fazendas (lote_id, fazenda_id, quantidade) VALUES (?, ?, ?)",
                    (lote_id, f["fazenda_id"], f["quantidade"]),
                )

    def _salvar_talhoes(self, lote_id, talhoes):
        conn = self.db.connect()
        cursor = conn.cursor()
        for t in talhoes:
            nome = t.get("nome", "").strip()
            tamanho = t.get("tamanho", 0)
            if nome and tamanho > 0:
                cursor.execute(
                    "INSERT INTO lote_talhoes (lote_id, nome, tamanho) VALUES (?, ?, ?)",
                    (lote_id, nome, tamanho),
                )

    def remover(self, lote_id):
        conn = self.db.connect()
        cursor = conn.cursor()
        cursor.execute("UPDATE lotes SET ativo = 0 WHERE id = ?", (lote_id,))
        conn.commit()
        return cursor.rowcount > 0

    def reativar(self, lote_id):
        conn = self.db.connect()
        cursor = conn.cursor()
        cursor.execute("UPDATE lotes SET ativo = 1 WHERE id = ?", (lote_id,))
        conn.commit()
        return True

    def listar_entidades(self):
        conn = self.db.connect()
        cursor = conn.cursor()
        cursor.execute("SELECT id, razao_social, cnpj_cpf FROM entidades WHERE ativo = 1 ORDER BY razao_social")
        return [dict(row) for row in cursor.fetchall()]

    def listar_tipos_adubo(self):
        conn = self.db.connect()
        cursor = conn.cursor()
        cursor.execute("SELECT id, nome FROM adubo_tipos ORDER BY nome")
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

    def listar_tipos_calcario(self):
        conn = self.db.connect()
        cursor = conn.cursor()
        cursor.execute("SELECT id, nome FROM calcario_tipos ORDER BY nome")
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

    def listar_fazendas(self):
        conn = self.db.connect()
        cursor = conn.cursor()
        cursor.execute("SELECT id, nome FROM fazendas ORDER BY nome")
        return [dict(row) for row in cursor.fetchall()]
