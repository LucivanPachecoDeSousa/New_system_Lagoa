from database.connection import Database
import hashlib

def criar_tabelas():
    db = Database()
    conn = db.connect()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            nome_completo TEXT NOT NULL,
            tipo TEXT NOT NULL DEFAULT 'operador'
                CHECK (tipo IN ('admin', 'operador')),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            ativo INTEGER DEFAULT 1
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS produtos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            descricao TEXT DEFAULT '',
            categoria TEXT NOT NULL DEFAULT 'outros'
                CHECK (categoria IN ('adubo', 'calcario', 'grao', 'insumo', 'outros')),
            unidade_medida TEXT NOT NULL DEFAULT 'kg',
            estoque_atual REAL NOT NULL DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            ativo INTEGER DEFAULT 1
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS entidades (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cnpj_cpf TEXT UNIQUE NOT NULL,
            tipo_pessoa TEXT NOT NULL DEFAULT 'juridica'
                CHECK (tipo_pessoa IN ('fisica', 'juridica')),
            razao_social TEXT NOT NULL,
            nome_fantasia TEXT DEFAULT '',
            logradouro TEXT DEFAULT '',
            numero TEXT DEFAULT '',
            complemento TEXT DEFAULT '',
            bairro TEXT DEFAULT '',
            cidade TEXT DEFAULT '',
            estado TEXT DEFAULT '',
            cep TEXT DEFAULT '',
            telefone TEXT DEFAULT '',
            email TEXT DEFAULT '',
            inscricao_estadual TEXT DEFAULT '',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            ativo INTEGER DEFAULT 1
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS adubo_tipos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT UNIQUE NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    adubos_padrao = [
        "CLORETO DE POTASSIO", "UREIA", "FORMULADO",
        "SUPERSIMPLES", "SULFATO DE AMONIO", "ES-MICROESSENTIALS",
    ]
    for nome in adubos_padrao:
        cursor.execute("SELECT id FROM adubo_tipos WHERE nome = ?", (nome,))
        if cursor.fetchone() is None:
            cursor.execute("INSERT INTO adubo_tipos (nome) VALUES (?)", (nome,))

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS lotes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tipo TEXT NOT NULL CHECK (tipo IN ('carregamento', 'adubo', 'calcario')),
            entidade_id INTEGER REFERENCES entidades(id),
            nome_lote TEXT NOT NULL,
            tipo_adubo_id INTEGER REFERENCES adubo_tipos(id),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            ativo INTEGER DEFAULT 1
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS fazendas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT UNIQUE NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    fazendas_padrao = ["LAGOA BONITA", "NS APARECIDA", "CAMPO GRANDE"]
    for nome in fazendas_padrao:
        cursor.execute("SELECT id FROM fazendas WHERE nome = ?", (nome,))
        if cursor.fetchone() is None:
            cursor.execute("INSERT INTO fazendas (nome) VALUES (?)", (nome,))

    for col, tipo in [("quantidade_pedido", "REAL"), ("unidade", "TEXT")]:
        try:
            cursor.execute(f"ALTER TABLE lotes ADD COLUMN {col} {tipo}")
        except Exception:
            pass

    try:
        cursor.execute("ALTER TABLE lotes ADD COLUMN valor_unitario REAL DEFAULT 0")
    except Exception:
        pass

    try:
        cursor.execute("ALTER TABLE lotes ADD COLUMN tipo_calcario_id INTEGER REFERENCES calcario_tipos(id)")
    except Exception:
        pass

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS lote_fazendas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            lote_id INTEGER NOT NULL REFERENCES lotes(id) ON DELETE CASCADE,
            fazenda_id INTEGER NOT NULL REFERENCES fazendas(id),
            quantidade REAL NOT NULL DEFAULT 0,
            UNIQUE(lote_id, fazenda_id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS carregamentos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            data DATE NOT NULL DEFAULT (date('now')),
            entidade_id INTEGER NOT NULL REFERENCES entidades(id),
            lote_id INTEGER NOT NULL REFERENCES lotes(id),
            placa TEXT NOT NULL DEFAULT '',
            peso_bruto REAL NOT NULL DEFAULT 0,
            tara REAL NOT NULL DEFAULT 0,
            peso_liquido REAL NOT NULL DEFAULT 0,
            peso_ticket REAL NOT NULL DEFAULT 0,
            peso_nf REAL NOT NULL DEFAULT 0,
            numero_nf TEXT NOT NULL DEFAULT '',
            chave_nf TEXT NOT NULL DEFAULT '',
            valor_unitario REAL NOT NULL DEFAULT 0,
            total_nota REAL NOT NULL DEFAULT 0,
            arquivo_nf TEXT DEFAULT '',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            ativo INTEGER DEFAULT 1
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS material_construcao_tipos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT UNIQUE NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS materiais_construcao (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            data DATE NOT NULL DEFAULT (date('now')),
            material_id INTEGER NOT NULL REFERENCES material_construcao_tipos(id),
            empresa_fornecedora TEXT NOT NULL DEFAULT '',
            transportadora TEXT NOT NULL DEFAULT '',
            peso_kg REAL NOT NULL DEFAULT 0,
            metros_cubicos REAL NOT NULL DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            ativo INTEGER DEFAULT 1
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS entradas_adubo (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            data DATE NOT NULL DEFAULT (date('now')),
            adubo_tipo_id INTEGER NOT NULL REFERENCES adubo_tipos(id),
            lote_id INTEGER REFERENCES lotes(id),
            entidade_id INTEGER NOT NULL REFERENCES entidades(id),
            quantidade_bag INTEGER NOT NULL DEFAULT 0,
            peso_total_kg REAL NOT NULL DEFAULT 0,
            placa TEXT NOT NULL DEFAULT '',
            motorista TEXT NOT NULL DEFAULT '',
            fazenda_id INTEGER REFERENCES fazendas(id),
            numero_nf TEXT NOT NULL DEFAULT '',
            observacao TEXT DEFAULT '',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            ativo INTEGER DEFAULT 1
        )
    """)

    for col, tipo in [
        ("quantidade_bag", "INTEGER"),
        ("peso_total_kg", "REAL"),
        ("placa", "TEXT"),
        ("motorista", "TEXT"),
        ("fazenda_id", "INTEGER"),
        ("numero_nf", "TEXT"),
    ]:
        try:
            cursor.execute(f"ALTER TABLE entradas_adubo ADD COLUMN {col} {tipo} DEFAULT 0")
        except Exception:
            pass
    try:
        cursor.execute("ALTER TABLE entradas_adubo ADD COLUMN fazenda_id INTEGER REFERENCES fazendas(id)")
    except Exception:
        pass

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS calcario_tipos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT UNIQUE NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS entradas_calcario (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            data DATE NOT NULL DEFAULT (date('now')),
            calcario_tipo_id INTEGER NOT NULL REFERENCES calcario_tipos(id),
            lote_id INTEGER REFERENCES lotes(id),
            entidade_id INTEGER NOT NULL REFERENCES entidades(id),
            quantidade_bag INTEGER NOT NULL DEFAULT 0,
            peso_total_kg REAL NOT NULL DEFAULT 0,
            placa TEXT NOT NULL DEFAULT '',
            motorista TEXT NOT NULL DEFAULT '',
            local_descarga TEXT DEFAULT '',
            numero_nf TEXT NOT NULL DEFAULT '',
            observacao TEXT DEFAULT '',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            ativo INTEGER DEFAULT 1
        )
    """)

    try:
        cursor.execute("ALTER TABLE entradas_calcario ADD COLUMN local_descarga TEXT DEFAULT ''")
    except Exception:
        pass

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS servico_tipos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT UNIQUE NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    servicos_padrao = ["TROCA DE OLEO", "PNEUS", "FILTRO", "OUTROS"]
    for nome in servicos_padrao:
        cursor.execute("SELECT id FROM servico_tipos WHERE nome = ?", (nome,))
        if cursor.fetchone() is None:
            cursor.execute("INSERT INTO servico_tipos (nome) VALUES (?)", (nome,))

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS manutencoes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            data DATE NOT NULL DEFAULT (date('now')),
            veiculo TEXT NOT NULL DEFAULT '',
            servico_tipo_id INTEGER REFERENCES servico_tipos(id),
            descricao_pecas TEXT DEFAULT '',
            responsavel TEXT NOT NULL DEFAULT '',
            kilometragem_horimetro INTEGER NOT NULL DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            ativo INTEGER DEFAULT 1
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS entradas_feno (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            data DATE NOT NULL DEFAULT (date('now')),
            tipo TEXT NOT NULL DEFAULT 'FENO'
                CHECK (tipo IN ('FENO', 'PRÉ-SECADO')),
            placa TEXT NOT NULL DEFAULT '',
            peso_bruto REAL NOT NULL DEFAULT 0,
            tara REAL NOT NULL DEFAULT 0,
            peso_liquido REAL NOT NULL DEFAULT 0,
            quantidade REAL NOT NULL DEFAULT 0,
            media_peso REAL NOT NULL DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            ativo INTEGER DEFAULT 1
        )
    """)

    conn.commit()

def seed_admin():
    db = Database()
    conn = db.connect()
    cursor = conn.cursor()

    cursor.execute("SELECT id FROM usuarios WHERE username = ?", ("admin",))
    if cursor.fetchone() is None:
        password_hash = hashlib.sha256("admin123".encode()).hexdigest()
        cursor.execute(
            "INSERT INTO usuarios (username, password_hash, nome_completo, tipo) VALUES (?, ?, ?, ?)",
            ("admin", password_hash, "Administrador", "admin"),
        )
        conn.commit()
