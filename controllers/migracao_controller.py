import sqlite3
import hashlib
from pathlib import Path
from datetime import datetime
from database.connection import Database


class MigracaoController:
    def __init__(self):
        self.db = Database()

    def importar_backup(self, backup_path: str) -> dict:
        if not Path(backup_path).exists():
            return {"sucesso": False, "mensagem": "Arquivo de backup não encontrado."}

        conn_old = sqlite3.connect(backup_path)
        conn_new = self.db.connect()
        cursor_new = conn_new.cursor()

        relatorio = {
            "sucesso": True,
            "mensagem": "",
            "entidades_criadas": 0,
            "lotes_criados": 0,
            "adubo_tipos_criados": 0,
            "calcario_tipos_criados": 0,
            "material_tipos_criados": 0,
            "servico_tipos_criados": 0,
            "carregamentos_importados": 0,
            "entradas_adubo_importados": 0,
            "entradas_calcario_importados": 0,
            "manutencoes_importados": 0,
            "materiais_construcao_importados": 0,
            "vendas_importados": 0,
            "usuarios_importados": 0,
            "erros": [],
        }

        try:
            # ---- 1. Usuários ----
            try:
                old_users = conn_old.execute(
                    "SELECT usuario, senha FROM usuarios"
                ).fetchall()
                for username, senha in old_users:
                    existing = cursor_new.execute(
                        "SELECT id FROM usuarios WHERE username = ?", (username,)
                    ).fetchone()
                    if not existing:
                        password_hash = hashlib.sha256(
                            senha.encode()
                        ).hexdigest()
                        cursor_new.execute(
                            "INSERT INTO usuarios (username, password_hash, nome_completo, tipo) VALUES (?, ?, ?, ?)",
                            (username, password_hash, username, "operador"),
                        )
                        relatorio["usuarios_importados"] += 1
            except Exception as e:
                relatorio["erros"].append(f"Erro ao importar usuários: {e}")

            # ---- 2. Cache de entidades já criadas (nome -> id) ----
            cache_entidade = {}

            def _obter_entidade(nome: str) -> int | None:
                if not nome or not nome.strip():
                    return None
                nome = nome.strip().upper()
                if nome in cache_entidade:
                    return cache_entidade[nome]
                existing = cursor_new.execute(
                    "SELECT id FROM entidades WHERE cnpj_cpf = ?", (nome,)
                ).fetchone()
                if existing:
                    cache_entidade[nome] = existing[0]
                    return existing[0]
                cursor_new.execute(
                    "INSERT INTO entidades (cnpj_cpf, tipo_pessoa, razao_social, nome_fantasia) VALUES (?, ?, ?, ?)",
                    (nome, "juridica", nome, nome),
                )
                new_id = cursor_new.lastrowid
                cache_entidade[nome] = new_id
                relatorio["entidades_criadas"] += 1
                return new_id

            # ---- 3. Cache de adubo_tipos ----
            cache_adubo_tipo = {}

            def _obter_adubo_tipo(nome: str) -> int | None:
                if not nome or not nome.strip():
                    return None
                nome = nome.strip().upper()
                if nome in cache_adubo_tipo:
                    return cache_adubo_tipo[nome]
                existing = cursor_new.execute(
                    "SELECT id FROM adubo_tipos WHERE nome = ?", (nome,)
                ).fetchone()
                if existing:
                    cache_adubo_tipo[nome] = existing[0]
                    return existing[0]
                cursor_new.execute(
                    "INSERT INTO adubo_tipos (nome) VALUES (?)", (nome,)
                )
                new_id = cursor_new.lastrowid
                cache_adubo_tipo[nome] = new_id
                relatorio["adubo_tipos_criados"] += 1
                return new_id

            # ---- 4. Cache de calcario_tipos ----
            cache_calcario_tipo = {}

            def _obter_calcario_tipo(nome: str) -> int | None:
                if not nome or not nome.strip():
                    return None
                nome = nome.strip().upper()
                if nome in cache_calcario_tipo:
                    return cache_calcario_tipo[nome]
                existing = cursor_new.execute(
                    "SELECT id FROM calcario_tipos WHERE nome = ?", (nome,)
                ).fetchone()
                if existing:
                    cache_calcario_tipo[nome] = existing[0]
                    return existing[0]
                cursor_new.execute(
                    "INSERT INTO calcario_tipos (nome) VALUES (?)", (nome,)
                )
                new_id = cursor_new.lastrowid
                cache_calcario_tipo[nome] = new_id
                relatorio["calcario_tipos_criados"] += 1
                return new_id

            # ---- 5. Cache de material_construcao_tipos ----
            cache_material_tipo = {}

            def _obter_material_tipo(nome: str) -> int | None:
                if not nome or not nome.strip():
                    return None
                nome = nome.strip().upper()
                if nome in cache_material_tipo:
                    return cache_material_tipo[nome]
                existing = cursor_new.execute(
                    "SELECT id FROM material_construcao_tipos WHERE nome = ?",
                    (nome,),
                ).fetchone()
                if existing:
                    cache_material_tipo[nome] = existing[0]
                    return existing[0]
                cursor_new.execute(
                    "INSERT INTO material_construcao_tipos (nome) VALUES (?)",
                    (nome,),
                )
                new_id = cursor_new.lastrowid
                cache_material_tipo[nome] = new_id
                relatorio["material_tipos_criados"] += 1
                return new_id

            # ---- 6. Cache de servico_tipos ----
            cache_servico_tipo = {}

            def _obter_servico_tipo(nome: str) -> int | None:
                if not nome or not nome.strip():
                    return None
                nome = nome.strip().upper()
                if nome in cache_servico_tipo:
                    return cache_servico_tipo[nome]
                existing = cursor_new.execute(
                    "SELECT id FROM servico_tipos WHERE nome = ?", (nome,)
                ).fetchone()
                if existing:
                    cache_servico_tipo[nome] = existing[0]
                    return existing[0]
                cursor_new.execute(
                    "INSERT INTO servico_tipos (nome) VALUES (?)", (nome,)
                )
                new_id = cursor_new.lastrowid
                cache_servico_tipo[nome] = new_id
                relatorio["servico_tipos_criados"] += 1
                return new_id

            # ---- 7. Cache de lotes (nome_entidade + nome_lote -> lote_id) ----
            cache_lote = {}

            def _obter_lote(
                nome_entidade: str,
                nome_lote: str,
                tipo: str = "carregamento",
                quantidade_prevista: float = 0,
                unidade: str = "",
            ) -> int | None:
                if not nome_lote or not nome_lote.strip():
                    return None
                nome_lote = nome_lote.strip().upper()
                chave = f"{nome_entidade or ''}|{nome_lote}"
                if chave in cache_lote:
                    return cache_lote[chave]

                entidade_id = _obter_entidade(nome_entidade) if nome_entidade else None

                existing = cursor_new.execute(
                    "SELECT id FROM lotes WHERE nome_lote = ? AND (entidade_id = ? OR (entidade_id IS NULL AND ? IS NULL))",
                    (nome_lote, entidade_id, entidade_id),
                ).fetchone()
                if existing:
                    cache_lote[chave] = existing[0]
                    return existing[0]

                tipo_map = {
                    "CARREGAMENTO": "carregamento",
                    "ADUBO": "adubo",
                    "CALCARIO": "calcario",
                }
                tipo_norm = tipo_map.get(tipo.strip().upper(), "carregamento")

                cursor_new.execute(
                    "INSERT INTO lotes (tipo, entidade_id, nome_lote, quantidade_pedido, unidade) VALUES (?, ?, ?, ?, ?)",
                    (tipo_norm, entidade_id, nome_lote, quantidade_prevista, unidade),
                )
                new_id = cursor_new.lastrowid
                cache_lote[chave] = new_id
                relatorio["lotes_criados"] += 1
                return new_id

            # ---- 8. Cache de fazendas (nome -> id) ----
            cache_fazenda = {}
            fazendas_existentes = cursor_new.execute(
                "SELECT id, nome FROM fazendas"
            ).fetchall()
            for fid, fnome in fazendas_existentes:
                cache_fazenda[fnome.upper()] = fid

            def _obter_fazenda(nome: str) -> int | None:
                if not nome or not nome.strip():
                    return None
                nome = nome.strip().upper()
                if nome in cache_fazenda:
                    return cache_fazenda[nome]
                cursor_new.execute(
                    "INSERT INTO fazendas (nome) VALUES (?)", (nome,)
                )
                new_id = cursor_new.lastrowid
                cache_fazenda[nome] = new_id
                return new_id

            # ---- 9. Lotes do backup ----
            try:
                old_lotes = conn_old.execute(
                    "SELECT nome_entidade, nome_lote_contrato, tipo, quantidade_prevista, unidade FROM lotes"
                ).fetchall()
                for ent, lote, tipo, qtd, unid in old_lotes:
                    _obter_lote(ent, lote, tipo or "carregamento", qtd or 0, unid or "")
            except Exception as e:
                relatorio["erros"].append(f"Erro ao importar lotes: {e}")

            # ---- 10. Carregamentos ----
            try:
                old_carreg = conn_old.execute(
                    "SELECT data_carregamento, entidade, nome_lote_contrato, placa, "
                    "peso_bruto, peso_tara, peso_liquido_ticket, peso_liquido_nota, "
                    "numero_nf, valor_unitario, valor_total, chave_nf FROM carregamentos"
                ).fetchall()
                for (
                    data,
                    entidade,
                    lote_nome,
                    placa,
                    p_bruto,
                    p_tara,
                    p_ticket,
                    p_nf,
                    num_nf,
                    v_unit,
                    v_total,
                    chave,
                ) in old_carreg:
                    ent_id = _obter_entidade(entidade)
                    lote_id = _obter_lote(entidade, lote_nome)
                    if not ent_id:
                        continue
                    if p_bruto is None:
                        p_bruto = 0
                    if p_tara is None:
                        p_tara = 0
                    if p_ticket is None:
                        p_ticket = 0
                    if p_nf is None:
                        p_nf = 0
                    p_liquido = p_bruto - p_tara
                    cursor_new.execute(
                        "INSERT INTO carregamentos (data, entidade_id, lote_id, placa, "
                        "peso_bruto, tara, peso_liquido, peso_ticket, peso_nf, "
                        "numero_nf, chave_nf, valor_unitario, total_nota) "
                        "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                        (
                            data,
                            ent_id,
                            lote_id,
                            placa or "",
                            p_bruto,
                            p_tara,
                            p_liquido,
                            p_ticket,
                            p_nf,
                            num_nf or "",
                            chave or "",
                            v_unit or 0,
                            v_total or 0,
                        ),
                    )
                    relatorio["carregamentos_importados"] += 1
            except Exception as e:
                relatorio["erros"].append(f"Erro ao importar carregamentos: {e}")

            # ---- 11. Entradas de Adubo (recebimento_adubos) ----
            try:
                old_adubos = conn_old.execute(
                    "SELECT tipo_adubo, quantidade_bag, formulacao, placa_veiculo, "
                    "data_entrada, nome_motorista, transportadora, fornecedor, "
                    "numero_nf, peso_kg, lote_associado FROM recebimento_adubos"
                ).fetchall()
                for (
                    tipo,
                    qtd_bag,
                    formulacao,
                    placa,
                    data_ent,
                    motorista,
                    transportadora,
                    fornecedor,
                    num_nf,
                    peso_kg,
                    lote_assoc,
                ) in old_adubos:
                    tipo_id = _obter_adubo_tipo(tipo)
                    ent_id = _obter_entidade(fornecedor)
                    lote_id = _obter_lote(fornecedor, lote_assoc, "adubo")
                    if not tipo_id or not ent_id:
                        continue
                    cursor_new.execute(
                        "INSERT INTO entradas_adubo (data, adubo_tipo_id, lote_id, entidade_id, "
                        "quantidade_bag, peso_total_kg, placa, motorista, numero_nf, observacao) "
                        "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                        (
                            data_ent,
                            tipo_id,
                            lote_id,
                            ent_id,
                            qtd_bag or 0,
                            peso_kg or 0,
                            placa or "",
                            motorista or "",
                            num_nf or "",
                            f"Transportadora: {transportadora}" if transportadora else "",
                        ),
                    )
                    relatorio["entradas_adubo_importados"] += 1
            except Exception as e:
                relatorio["erros"].append(
                    f"Erro ao importar entradas de adubo: {e}"
                )

            # ---- 12. Entradas de Calcário (entradas) ----
            try:
                old_calc = conn_old.execute(
                    "SELECT tipo_calcario, quantidade, placa_veiculo, data_entrada, "
                    "nome_motorista, transportadora, fornecedor, numero_nf, "
                    "lote_associado FROM entradas"
                ).fetchall()
                for (
                    tipo,
                    quantidade,
                    placa,
                    data_ent,
                    motorista,
                    transportadora,
                    fornecedor,
                    num_nf,
                    lote_assoc,
                ) in old_calc:
                    tipo_id = _obter_calcario_tipo(tipo)
                    ent_id = _obter_entidade(fornecedor)
                    lote_id = _obter_lote(fornecedor, lote_assoc, "calcario")
                    if not tipo_id or not ent_id:
                        continue
                    cursor_new.execute(
                        "INSERT INTO entradas_calcario (data, calcario_tipo_id, lote_id, entidade_id, "
                        "quantidade_bag, peso_total_kg, placa, motorista, numero_nf, observacao) "
                        "VALUES (?, ?, ?, ?, 0, ?, ?, ?, ?, ?)",
                        (
                            data_ent,
                            tipo_id,
                            lote_id,
                            ent_id,
                            quantidade or 0,
                            placa or "",
                            motorista or "",
                            num_nf or "",
                            f"Transportadora: {transportadora}" if transportadora else "",
                        ),
                    )
                    relatorio["entradas_calcario_importados"] += 1
            except Exception as e:
                relatorio["erros"].append(
                    f"Erro ao importar entradas de calcário: {e}"
                )

            # ---- 13. Manutenções (manutencao_maquinas) ----
            try:
                old_manut = conn_old.execute(
                    "SELECT data_manutencao, veiculo_maquina, tipo_servico, descricao, "
                    "km_horimetro, fornecedor_mecanico FROM manutencao_maquinas"
                ).fetchall()
                for (
                    data_m,
                    veiculo,
                    servico,
                    descricao,
                    km_h,
                    responsavel,
                ) in old_manut:
                    servico_id = _obter_servico_tipo(servico)
                    cursor_new.execute(
                        "INSERT INTO manutencoes (data, veiculo, servico_tipo_id, "
                        "descricao_pecas, responsavel, kilometragem_horimetro) "
                        "VALUES (?, ?, ?, ?, ?, ?)",
                        (
                            data_m,
                            veiculo or "",
                            servico_id,
                            descricao or "",
                            responsavel or "",
                            int(km_h or 0),
                        ),
                    )
                    relatorio["manutencoes_importados"] += 1
            except Exception as e:
                relatorio["erros"].append(f"Erro ao importar manutenções: {e}")

            # ---- 14. Materiais de Construção (recebimento_materiais) ----
            try:
                old_mat = conn_old.execute(
                    "SELECT data_recebimento, material, empresa, transportadora, "
                    "peso_kg, metragem_m3 FROM recebimento_materiais"
                ).fetchall()
                for (
                    data_rec,
                    material,
                    empresa,
                    transportadora,
                    peso_kg,
                    metragem,
                ) in old_mat:
                    mat_id = _obter_material_tipo(material)
                    if not mat_id:
                        continue
                    cursor_new.execute(
                        "INSERT INTO materiais_construcao (data, material_id, "
                        "empresa_fornecedora, transportadora, peso_kg, metros_cubicos) "
                        "VALUES (?, ?, ?, ?, ?, ?)",
                        (
                            data_rec,
                            mat_id,
                            empresa or "",
                            transportadora or "",
                            peso_kg or 0,
                            metragem or 0,
                        ),
                    )
                    relatorio["materiais_construcao_importados"] += 1
            except Exception as e:
                relatorio["erros"].append(
                    f"Erro ao importar materiais de construção: {e}"
                )

            # ---- 15. Vendas (vendas_pequenas) ----
            try:
                old_vendas = conn_old.execute(
                    "SELECT data_venda, comprador, produto, quantidade, "
                    "valor_unitario, valor_total, status_pagamento FROM vendas_pequenas"
                ).fetchall()
                for (
                    data_v,
                    comprador,
                    produto,
                    quantidade,
                    v_unit,
                    v_total,
                    status,
                ) in old_vendas:
                    cursor_new.execute(
                        "INSERT INTO vendas (data, produto, quantidade_kg, comprador, "
                        "valor_unitario, valor_total, status_pagamento) "
                        "VALUES (?, ?, ?, ?, ?, ?, ?)",
                        (
                            data_v,
                            produto or "",
                            quantidade or 0,
                            comprador or "",
                            v_unit or 0,
                            v_total or 0,
                            status or "Pendente",
                        ),
                    )
                    relatorio["vendas_importados"] += 1
            except Exception as e:
                relatorio["erros"].append(f"Erro ao importar vendas: {e}")

            conn_new.commit()
            conn_old.close()

            partes = []
            for key, label in [
                ("usuarios_importados", "usuários"),
                ("entidades_criadas", "entidades"),
                ("lotes_criados", "lotes"),
                ("adubo_tipos_criados", "tipos de adubo"),
                ("calcario_tipos_criados", "tipos de calcário"),
                ("material_tipos_criados", "tipos de material"),
                ("servico_tipos_criados", "tipos de serviço"),
                ("carregamentos_importados", "carregamentos"),
                ("entradas_adubo_importados", "entradas de adubo"),
                ("entradas_calcario_importados", "entradas de calcário"),
                ("manutencoes_importados", "manutenções"),
                ("materiais_construcao_importados", "materiais de construção"),
                ("vendas_importados", "vendas"),
            ]:
                val = relatorio.get(key, 0)
                if val > 0:
                    partes.append(f"{val} {label}")

            relatorio["mensagem"] = (
                "Importação concluída.\n\nItens processados:\n" + "\n".join(partes)
            )
            if relatorio["erros"]:
                relatorio["mensagem"] += (
                    "\n\nAvisos:\n" + "\n".join(relatorio["erros"])
                )

        except Exception as e:
            conn_new.rollback()
            conn_old.close()
            relatorio["sucesso"] = False
            relatorio["mensagem"] = f"Erro durante a importação: {e}"

        return relatorio
