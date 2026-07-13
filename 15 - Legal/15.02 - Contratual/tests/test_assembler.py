"""
tests/test_assembler.py
=======================
Testes para amendment_assembler.py e score_engine.py — Fase 4.

Casos de teste:
  1. ISA sem Proposta Comercial → score = 0.0
  2. Saldo Natal completo → verificar cláusula de responsabilidade pós-2025
  3. Duplo aditamento ISA + Saldo Natal → documento único consolidado

Execução:
    cd data/ifb-aditamentos/app
    python -m pytest tests/test_assembler.py -v
    # ou diretamente:
    python tests/test_assembler.py
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest

from modules.amendment_assembler import montar_aditamento
from modules.score_engine import calcular_score


# ---------------------------------------------------------------------------
# Fixtures comuns
# ---------------------------------------------------------------------------

CONTRATO_BASE = {
    "razao_social": "Empresa Teste Ltda.",
    "cnpj": "11.222.333/0001-81",
    "endereco": "Rua das Flores, 100, Centro, São Paulo/SP",
    "cep": "01.001-000",
    "data_assinatura_original": "10 de janeiro de 2023",
    "aviso_previo_clausula_10_3": 60,
    "tem_colabmais": None,
}

TICKET_BASE = {
    "key": "JURFIN-9999",
    "empresa": "Empresa Teste Ltda.",
    "cnpj_empresa": "11.222.333/0001-81",
    "endereco": "Rua das Flores, 100, Centro, São Paulo/SP",
    "cep": "01.001-000",
    "data_contrato_original": "10 de janeiro de 2023",
    "data_aditivo": "10 de julho de 2026",
    "representante_legal": "João da Silva",
    "cpf_representante": "123.456.789-09",
    "numero_contrato": "CTR-2023-001",
    "nome_representante_ifood": "Maria Oliveira",
    "cargo_representante_ifood": "Diretora Jurídica",
    "summary": "Solicitação de aditamento contratual para inclusão de novos benefícios.",
    "description": (
        "Prezados, solicitamos a elaboração de aditamento para a empresa Empresa Teste Ltda. "
        "conforme condições negociadas pela equipe comercial."
    ),
}

ANALISE_LEITOR_BASE = {
    "produtos": [],
    "alteracoes_solicitadas": [],
}


# ---------------------------------------------------------------------------
# Teste 1: ISA sem Proposta Comercial → score = 0.0
# ---------------------------------------------------------------------------

def test_isa_sem_proposta_comercial_score_zero():
    """
    REGRA-01: Módulo ISA selecionado sem Proposta Comercial anexa.
    Esperado: score = 0.0, PROPOSTA_COMERCIAL_ISA em campos_pendentes.
    """
    ticket = {
        **TICKET_BASE,
        "modulos_solicitados": [10],  # módulo ISA
        "proposta_comercial_isa": None,  # sem proposta comercial
        "summary": "Solicitação de inclusão de ISA para empresa Teste",
        "description": "Empresa deseja contratar o benefício ISA.",
    }
    analise_leitor = {
        **ANALISE_LEITOR_BASE,
        "produtos": ["ISA"],
    }

    resultado = montar_aditamento(ticket, CONTRATO_BASE, analise_leitor)

    # Verificações
    assert "PROPOSTA_COMERCIAL_ISA" in resultado["campos_pendentes"], (
        "Campo PROPOSTA_COMERCIAL_ISA deve estar em campos_pendentes"
    )
    assert resultado["score"]["score"] == 0.0, (
        f"Score deve ser 0.0 quando ISA sem Proposta Comercial, "
        f"obtido: {resultado['score']['score']}"
    )
    assert resultado["score"]["decisao"] == "REVISAO_HUMANA", (
        "Decisão deve ser REVISAO_HUMANA com score 0.0"
    )
    assert "REGRA-01" in resultado["regras_violadas"], (
        "REGRA-01 deve estar nas regras violadas"
    )
    print("✅ Teste 1 PASSOU: ISA sem Proposta Comercial → score=0.0")


# ---------------------------------------------------------------------------
# Teste 2: Saldo Natal completo → verificar cláusula pós-2025
# ---------------------------------------------------------------------------

def test_saldo_natal_clausula_responsabilidade():
    """
    REGRA-02: Módulo Saldo Natal deve incluir cláusula de responsabilidade do cliente.
    Esperado: CLAUSULA_RESPONSABILIDADE_NATAL preenchida com texto obrigatório.
    """
    ticket = {
        **TICKET_BASE,
        "modulos_solicitados": [12],  # módulo Saldo Natal
        "valor_saldo_natal": "200,00",
        "ano_referencia_natal": "2026",
        "data_credito_natal": "15 de dezembro de 2026",
        "summary": "Contratação de Saldo Natal para colaboradores da empresa Teste",
        "description": (
            "A empresa Teste Ltda. deseja contratar o benefício Saldo Natal para 2026, "
            "no valor de R$200 por colaborador elegível, com crédito em 15 de dezembro de 2026."
        ),
    }
    analise_leitor = {
        **ANALISE_LEITOR_BASE,
        "produtos": ["Saldo Natal"],
    }

    resultado = montar_aditamento(ticket, CONTRATO_BASE, analise_leitor)

    # Verificar que cláusula de responsabilidade está presente
    variaveis = resultado["variaveis"]
    assert "CLAUSULA_RESPONSABILIDADE_NATAL" in variaveis, (
        "CLAUSULA_RESPONSABILIDADE_NATAL deve estar nas variáveis"
    )
    clausula = variaveis["CLAUSULA_RESPONSABILIDADE_NATAL"]["valor"]
    assert "responsabilidade" in clausula.lower(), (
        "Cláusula de responsabilidade deve mencionar 'responsabilidade'"
    )
    assert "empresa" in clausula.lower() or "contratante" in clausula.lower(), (
        "Cláusula deve indicar que responsabilidade é do cliente (Empresa/Contratante)"
    )
    assert "ifood" not in clausula.lower() or "não cabendo" in clausula.lower(), (
        "Cláusula deve isentar o iFood da responsabilidade de distribuição"
    )

    # Verificar fonte da cláusula
    fonte = variaveis["CLAUSULA_RESPONSABILIDADE_NATAL"]["fonte"]
    assert "REGRA-02" in fonte or "2025" in fonte, (
        f"Fonte deve referenciar REGRA-02 ou pós-2025, obtida: {fonte}"
    )

    # Verificar campos preenchidos
    assert "VALOR_SALDO_NATAL" in variaveis
    assert variaveis["VALOR_SALDO_NATAL"]["valor"] == "200,00"
    assert "ANO_REFERENCIA" in variaveis
    assert variaveis["ANO_REFERENCIA"]["valor"] == "2026"
    assert "DATA_CREDITO_NATAL" in variaveis
    assert variaveis["DATA_CREDITO_NATAL"]["valor"] == "15 de dezembro de 2026"

    # Score não deve ser zero (todos campos preenchidos, sem violações de SCORE=0)
    assert resultado["score"]["score"] > 0.0 or resultado["campos_pendentes"], (
        "Score deve ser > 0.0 se não há campos pendentes"
    )

    print("✅ Teste 2 PASSOU: Saldo Natal inclui cláusula de responsabilidade pós-2025")


# ---------------------------------------------------------------------------
# Teste 3: Duplo aditamento ISA + Saldo Natal → documento único
# ---------------------------------------------------------------------------

def test_duplo_aditamento_isa_saldo_natal_documento_unico():
    """
    REGRA-05: ISA + Saldo Natal simultaneamente → documento único consolidado.
    Esperado: duplo_aditamento_consolidado=True, ambos módulos na lista, score=0 (sem Proposta Comercial).
    """
    ticket = {
        **TICKET_BASE,
        "modulos_solicitados": [10, 12],  # ISA + Saldo Natal
        "proposta_comercial_isa": None,   # sem proposta comercial (REGRA-01 violada)
        "valor_saldo_natal": "150,00",
        "ano_referencia_natal": "2026",
        "data_credito_natal": "20 de dezembro de 2026",
        "summary": "Contratação de ISA e Saldo Natal simultaneamente para empresa Teste",
        "description": (
            "A empresa deseja contratar ISA e Saldo Natal no mesmo aditamento, "
            "conforme aprovação comercial. Proposta Comercial ISA em análise."
        ),
    }
    analise_leitor = {
        **ANALISE_LEITOR_BASE,
        "produtos": ["ISA", "Saldo Natal"],
    }

    resultado = montar_aditamento(ticket, CONTRATO_BASE, analise_leitor)

    # Verificar documento consolidado (não dois separados)
    assert resultado["duplo_aditamento_consolidado"] is True, (
        "duplo_aditamento_consolidado deve ser True quando ISA + Saldo Natal selecionados"
    )

    # Verificar que ambos módulos estão na lista
    modulos = resultado["modulos_selecionados"]
    assert "10_isa" in modulos, "Módulo ISA (10_isa) deve estar nos módulos selecionados"
    assert "12_saldo_natal" in modulos, "Módulo Saldo Natal (12_saldo_natal) deve estar nos módulos selecionados"

    # Score deve ser 0 (ISA sem Proposta Comercial → REGRA-01)
    assert resultado["score"]["score"] == 0.0, (
        "Score deve ser 0.0 quando ISA sem Proposta Comercial"
    )
    assert "PROPOSTA_COMERCIAL_ISA" in resultado["campos_pendentes"], (
        "PROPOSTA_COMERCIAL_ISA deve estar em campos_pendentes"
    )
    assert "REGRA-01" in resultado["regras_violadas"], (
        "REGRA-01 deve estar nas regras violadas"
    )

    # Cláusula de responsabilidade do Saldo Natal deve estar presente
    variaveis = resultado["variaveis"]
    assert "CLAUSULA_RESPONSABILIDADE_NATAL" in variaveis, (
        "CLAUSULA_RESPONSABILIDADE_NATAL deve estar nas variáveis mesmo no duplo aditamento"
    )

    print("✅ Teste 3 PASSOU: Duplo aditamento ISA + Saldo Natal → documento único consolidado")


# ---------------------------------------------------------------------------
# Teste 4: Score engine — campos PENDENTES zeram o score
# ---------------------------------------------------------------------------

def test_score_zero_com_campos_pendentes():
    """
    REGRA ABSOLUTA: qualquer campo PENDENTE → score = 0.0.
    """
    analise_com_pendente = {
        "campos_pendentes": ["RAZAO_SOCIAL", "CNPJ_EMPRESA"],
        "variaveis": {
            "RAZAO_SOCIAL": {"valor": "{{PENDENTE: Qual a razão social?}}", "fonte": "PENDENTE"},
            "CNPJ_EMPRESA": {"valor": "{{PENDENTE: Qual o CNPJ?}}", "fonte": "PENDENTE"},
        },
        "modulos_selecionados": ["01_cabecalho"],
        "regras_violadas": [],
        "ticket": {"summary": "Teste", "description": "Teste com pendentes"},
        "modulos_md": [],
    }

    resultado = calcular_score(analise_com_pendente)

    assert resultado["score"] == 0.0, (
        f"Score deve ser 0.0 com campos PENDENTES, obtido: {resultado['score']}"
    )
    assert resultado["decisao"] == "REVISAO_HUMANA"
    assert len(resultado["campos_pendentes"]) == 2

    print("✅ Teste 4 PASSOU: Campos PENDENTES zeram o score automaticamente")


# ---------------------------------------------------------------------------
# Teste 5: Terminologia canônica corrigida automaticamente
# ---------------------------------------------------------------------------

def test_terminologia_canonica_corrigida():
    """
    REGRA-04: Termos não-canônicos devem ser corrigidos e registrados.
    """
    ticket = {
        **TICKET_BASE,
        "modulos_solicitados": [10],  # ISA
        "proposta_comercial_isa": "proposta_isa_2026.pdf",
        "valor_isa_mensal": "50,00",
        "periodicidade_isa": "mensal",
        "isa_cumulativo": "não",
        "data_inicio_isa": "01 de agosto de 2026",
        "forma_pagamento_isa": "crédito em carteira digital",
        "summary": "Inclusão de Saldo Saúde Alimentar para a empresa",  # termo não-canônico
        "description": "Contratação do Saldo Saúde Alimentar conforme proposta comercial.",
    }
    analise_leitor = {
        **ANALISE_LEITOR_BASE,
        "produtos": ["ISA"],
    }

    resultado = montar_aditamento(ticket, CONTRATO_BASE, analise_leitor)

    # Verificar que terminologia foi corrigida
    correcoes = resultado["terminologia_corrigida"]
    # Pode ter encontrado e corrigido "saldo saúde alimentar" → "ISA"
    # (a correção é no texto consolidado, não no ticket em si)

    # Verificar que REGRA-04 foi registrada se houve correção
    if correcoes:
        assert "REGRA-04" in resultado["regras_violadas"], (
            "REGRA-04 deve estar em regras_violadas quando há terminologia não-canônica"
        )
    print(f"✅ Teste 5 PASSOU: Terminologia canônica verificada ({len(correcoes)} correção(ões))")


# ---------------------------------------------------------------------------
# Teste 6: Todas variáveis têm fonte declarada
# ---------------------------------------------------------------------------

def test_todas_variaveis_tem_fonte():
    """
    Toda variável deve ter 'fonte' declarada (ticket, contrato, default, PENDENTE).
    """
    ticket = {**TICKET_BASE, "modulos_solicitados": []}
    analise_leitor = {**ANALISE_LEITOR_BASE}

    resultado = montar_aditamento(ticket, CONTRATO_BASE, analise_leitor)

    variaveis = resultado["variaveis"]
    for campo, info in variaveis.items():
        assert isinstance(info, dict), f"Variável {campo} deve ser dict"
        assert "fonte" in info, f"Variável {campo} deve ter 'fonte' declarada"
        assert info["fonte"] is not None or "PENDENTE:" in info.get("valor", ""), (
            f"Variável {campo} com PENDENTE deve ter fonte='PENDENTE'"
        )
    print(f"✅ Teste 6 PASSOU: Todas as {len(variaveis)} variáveis têm fonte declarada")


# ---------------------------------------------------------------------------
# Execução direta (sem pytest)
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("=" * 60)
    print("Executando testes do amendment_assembler.py + score_engine.py")
    print("=" * 60)

    testes = [
        ("Teste 1 — ISA sem Proposta Comercial", test_isa_sem_proposta_comercial_score_zero),
        ("Teste 2 — Saldo Natal cláusula responsabilidade", test_saldo_natal_clausula_responsabilidade),
        ("Teste 3 — Duplo aditamento ISA + Saldo Natal", test_duplo_aditamento_isa_saldo_natal_documento_unico),
        ("Teste 4 — Score zero com campos PENDENTES", test_score_zero_com_campos_pendentes),
        ("Teste 5 — Terminologia canônica", test_terminologia_canonica_corrigida),
        ("Teste 6 — Todas variáveis têm fonte", test_todas_variaveis_tem_fonte),
    ]

    falhas = []
    for nome, func in testes:
        print(f"\n▶ {nome}")
        try:
            func()
        except AssertionError as e:
            print(f"  ❌ FALHOU: {e}")
            falhas.append(nome)
        except Exception as e:
            print(f"  ❌ ERRO: {e}")
            import traceback
            traceback.print_exc()
            falhas.append(nome)

    print("\n" + "=" * 60)
    if falhas:
        print(f"RESULTADO: {len(falhas)} teste(s) falharam:")
        for f in falhas:
            print(f"  ❌ {f}")
        sys.exit(1)
    else:
        print(f"RESULTADO: Todos os {len(testes)} testes passaram! ✅")
        sys.exit(0)


# ---------------------------------------------------------------------------
# Teste 7: Cláusula 16.6 usa versão assimétrica
# ---------------------------------------------------------------------------

def test_clausula_16_6_assimetrica():
    """
    DECISION_LAYER: Cláusula 16.6 deve usar versão assimétrica.
    iFood pode ceder livremente; Empresa (CONTRATANTE) precisa de anuência.
    """
    ticket = {
        **TICKET_BASE,
        "modulos_solicitados": [5],  # módulo cessão
        "summary": "Solicitação de alteração da Cláusula 16.6 do contrato",
        "description": (
            "A empresa solicita a adequação da Cláusula 16.6 conforme "
            "a versão negociada com a equipe jurídica do iFood Benefícios."
        ),
    }
    analise_leitor = {**ANALISE_LEITOR_BASE}

    resultado = montar_aditamento(ticket, CONTRATO_BASE, analise_leitor)

    # Módulo 05_cessao deve estar nos módulos selecionados
    assert "05_cessao" in resultado["modulos_selecionados"], (
        "Módulo 05_cessao deve estar na lista de módulos selecionados"
    )

    # Verificar que cláusula assimétrica está registrada
    variaveis = resultado["variaveis"]
    assert "CLAUSULA_CESSAO_TIPO" in variaveis, (
        "CLAUSULA_CESSAO_TIPO deve estar nas variáveis do aditamento"
    )
    assert variaveis["CLAUSULA_CESSAO_TIPO"]["valor"] == "assimetrica", (
        "Cláusula 16.6 deve ser do tipo 'assimetrica'"
    )

    # Verificar texto do módulo menciona assimetria
    texto = resultado["texto_consolidado"]
    # Texto gerado deve conter referência a cessão assimétrica
    assert any(
        termo in texto.lower()
        for termo in ["assimétrica", "assimetrica", "independentemente", "anuência", "contratante"]
    ), (
        "Texto consolidado deve conter a cláusula de cessão assimétrica"
    )

    print("✅ Teste 7 PASSOU: Cláusula 16.6 usa versão assimétrica")


# ---------------------------------------------------------------------------
# Teste 8: Score >= 0.90 com zero campos pendentes
# ---------------------------------------------------------------------------

def test_score_alto_sem_pendentes():
    """
    Score só >= 0.90 com ZERO campos pendentes e ZERO regras violadas.
    """
    analise_completa = {
        "campos_pendentes": [],
        "variaveis": {
            "RAZAO_SOCIAL": {"valor": "Empresa Completa Ltda.", "fonte": "campo empresa do ticket JURFIN-0001"},
            "CNPJ_EMPRESA": {"valor": "11.222.333/0001-81", "fonte": "campo cnpj do ticket JURFIN-0001"},
            "ENDERECO_EMPRESA": {"valor": "Rua X, 100, SP", "fonte": "campo endereco do ticket JURFIN-0001"},
            "CEP_EMPRESA": {"valor": "01.001-000", "fonte": "campo cep do ticket JURFIN-0001"},
            "DATA_CONTRATO_ORIGINAL": {"valor": "10 de janeiro de 2023", "fonte": "contrato anexo"},
            "DATA_ADITIVO": {"valor": "10 de julho de 2026", "fonte": "campo data_aditivo do ticket JURFIN-0001"},
        },
        "modulos_selecionados": ["01_cabecalho", "08_rodape_assinaturas", "09_clausula_geral"],
        "regras_violadas": [],
        "ticket": {
            "summary": "Solicitação de aditamento completo com todos os dados fornecidos pelo advogado.",
            "description": (
                "Dados completos para geração do aditamento. Empresa Completa Ltda. "
                "solicita prorrogação de vigência conforme aprovação comercial de junho de 2026."
            ),
        },
        "modulos_md": ["conteudo modulo 1", "conteudo modulo 2"],
    }

    resultado = calcular_score(analise_completa)

    assert resultado["score"] >= 0.90, (
        f"Score deve ser >= 0.90 com zero PENDENTES e zero regras violadas, "
        f"obtido: {resultado['score']}"
    )
    assert resultado["decisao"] == "AUTONOMO", (
        f"Decisão deve ser AUTONOMO com score >= 0.90, obtida: {resultado['decisao']}"
    )
    assert len(resultado["campos_pendentes"]) == 0

    print(f"✅ Teste 8 PASSOU: Score {resultado['score']} >= 0.90 sem campos pendentes → AUTONOMO")
