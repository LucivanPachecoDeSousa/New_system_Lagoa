import sqlite3

conn = sqlite3.connect(r"L:\Projetos\Em Andamento\Sistema Campo Fertil\Sistema Campo Fertil\desktop_fazenda.db")
conn.row_factory = sqlite3.Row
c = conn.cursor()

c.execute("PRAGMA foreign_keys")
print("FK PRAGMA:", c.fetchone()[0])

c.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
tables = [r[0] for r in c.fetchall()]
print("TABLES:", tables)

c.execute("SELECT COUNT(*) FROM lote_talhoes")
print("lote_talhoes count:", c.fetchone()[0])

c.execute("SELECT COUNT(*) FROM entradas_feno")
print("entradas_feno count:", c.fetchone()[0])

c.execute("""
    SELECT lt.id, lt.lote_id, lt.nome, COUNT(ef.id) as refs
    FROM lote_talhoes lt
    LEFT JOIN entradas_feno ef ON ef.talhao_id = lt.id
    GROUP BY lt.id
    HAVING refs > 0
    ORDER BY refs DESC
""")
print("\nTalhoes com referencias em entradas_feno:")
for r in c.fetchall():
    print(f"  ID {r['id']}, lote {r['lote_id']}, nome '{r['nome']}', refs {r['refs']}")

c.execute("SELECT MIN(id) FROM lotes")
min_id = c.fetchone()[0]
if min_id:
    c.execute("SELECT id, nome, tamanho FROM lote_talhoes WHERE lote_id = ?", (min_id,))
    print(f"\nTalhoes do lote {min_id}:")
    for r in c.fetchall():
        c.execute("SELECT COUNT(*) FROM entradas_feno WHERE talhao_id = ?", (r["id"],))
        refs = c.fetchone()[0]
        print(f"  ID {r['id']}, nome '{r['nome']}', refs {refs}")

print("\n--- Lotes ---")
c.execute("SELECT id, nome_lote, tipo FROM lotes ORDER BY id")
for r in c.fetchall():
    print(f"  ID {r['id']}: {r['nome_lote']} ({r['tipo']})")

conn.close()
