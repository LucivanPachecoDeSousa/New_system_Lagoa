from database.connection import Database


class CarregamentoController:
    def __init__(self):
        self.db = Database()

    def listar(self, busca="", entidade_id=None, lote_id=None, data_inicio=None, data_fim=None, apenas_ativos=True):
        conn = self.db.connect()
        cursor = conn.cursor()
        query = """
            SELECT c.*, e.razao_social AS entidade_nome, l.nome_lote
            FROM carregamentos c
            JOIN entidades e ON c.entidade_id = e.id
            JOIN lotes l ON c.lote_id = l.id
        """
        params = []
        conds = []
        if apenas_ativos:
            conds.append("c.ativo = 1")
        if entidade_id:
            conds.append("c.entidade_id = ?")
            params.append(entidade_id)
        if lote_id:
            conds.append("c.lote_id = ?")
            params.append(lote_id)
        if data_inicio:
            conds.append("c.data >= ?")
            params.append(data_inicio)
        if data_fim:
            conds.append("c.data <= ?")
            params.append(data_fim)
        if busca:
            conds.append("(e.razao_social LIKE ? OR l.nome_lote LIKE ? OR c.placa LIKE ? OR c.numero_nf LIKE ?)")
            params.extend([f"%{busca}%"] * 4)
        if conds:
            query += " WHERE " + " AND ".join(conds)
        query += " ORDER BY c.data DESC, c.created_at DESC"
        cursor.execute(query, params)
        return [dict(row) for row in cursor.fetchall()]

    def buscar_por_id(self, carregamento_id):
        conn = self.db.connect()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT c.*, e.razao_social AS entidade_nome, l.nome_lote
            FROM carregamentos c
            JOIN entidades e ON c.entidade_id = e.id
            JOIN lotes l ON c.lote_id = l.id
            WHERE c.id = ?
        """, (carregamento_id,))
        row = cursor.fetchone()
        return dict(row) if row else None

    def salvar(self, dados):
        conn = self.db.connect()
        cursor = conn.cursor()
        cursor.execute(
            """INSERT INTO carregamentos
               (data, entidade_id, lote_id, placa, peso_bruto, tara, peso_liquido,
                peso_ticket, peso_nf, numero_nf, chave_nf, valor_unitario, total_nota)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                dados["data"],
                dados["entidade_id"],
                dados["lote_id"],
                dados.get("placa", ""),
                dados.get("peso_bruto", 0),
                dados.get("tara", 0),
                dados.get("peso_liquido", 0),
                dados.get("peso_ticket", 0),
                dados.get("peso_nf", 0),
                dados.get("numero_nf", ""),
                dados.get("chave_nf", ""),
                dados.get("valor_unitario", 0),
                dados.get("total_nota", 0),
            ),
        )
        carregamento_id = cursor.lastrowid
        conn.commit()
        return carregamento_id

    def atualizar(self, carregamento_id, dados):
        conn = self.db.connect()
        cursor = conn.cursor()
        cursor.execute(
            """UPDATE carregamentos
               SET data = ?, entidade_id = ?, lote_id = ?, placa = ?,
                   peso_bruto = ?, tara = ?, peso_liquido = ?,
                   peso_ticket = ?, peso_nf = ?, numero_nf = ?,
                   chave_nf = ?, valor_unitario = ?, total_nota = ?,
                   updated_at = CURRENT_TIMESTAMP
               WHERE id = ?""",
            (
                dados["data"],
                dados["entidade_id"],
                dados["lote_id"],
                dados.get("placa", ""),
                dados.get("peso_bruto", 0),
                dados.get("tara", 0),
                dados.get("peso_liquido", 0),
                dados.get("peso_ticket", 0),
                dados.get("peso_nf", 0),
                dados.get("numero_nf", ""),
                dados.get("chave_nf", ""),
                dados.get("valor_unitario", 0),
                dados.get("total_nota", 0),
                carregamento_id,
            ),
        )
        conn.commit()
        return True

    def remover(self, carregamento_id):
        conn = self.db.connect()
        cursor = conn.cursor()
        cursor.execute("UPDATE carregamentos SET ativo = 0 WHERE id = ?", (carregamento_id,))
        conn.commit()
        return cursor.rowcount > 0

    def listar_entidades(self):
        conn = self.db.connect()
        cursor = conn.cursor()
        cursor.execute("SELECT id, razao_social, cnpj_cpf FROM entidades WHERE ativo = 1 ORDER BY razao_social")
        return [dict(row) for row in cursor.fetchall()]

    def listar_clientes_carregamento(self):
        conn = self.db.connect()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT DISTINCT e.id, e.razao_social, e.cnpj_cpf
            FROM entidades e
            JOIN carregamentos c ON c.entidade_id = e.id
            WHERE e.ativo = 1
            ORDER BY e.razao_social
        """)
        return [dict(row) for row in cursor.fetchall()]

    def listar_lotes_carregamento(self, entidade_id=None, apenas_ativos=True):
        conn = self.db.connect()
        cursor = conn.cursor()
        query = """
            SELECT l.id, l.nome_lote, l.valor_unitario,
                   l.entidade_id, l.ativo,
                   e.razao_social AS entidade_nome
            FROM lotes l
            LEFT JOIN entidades e ON l.entidade_id = e.id
            WHERE l.tipo = 'carregamento'
        """
        params = []
        if apenas_ativos:
            query += " AND l.ativo = 1"
        if entidade_id:
            query += " AND l.entidade_id = ?"
            params.append(entidade_id)
        query += " ORDER BY l.ativo DESC, l.nome_lote"
        cursor.execute(query, params)
        return [dict(row) for row in cursor.fetchall()]


