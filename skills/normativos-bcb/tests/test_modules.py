"""
Suite de testes — Skill normativos-bcb
Testa importação e funcionalidade básica de todos os 7 módulos.

Uso:
    python3 -m pytest skills/normativos-bcb/tests/ -v
    python3 skills/normativos-bcb/tests/test_modules.py
"""

from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

# Adicionar path da skill ao sys.path
SKILL_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(SKILL_DIR))


class TestImportacaoModulos(unittest.TestCase):
    """Testa que todos os 7 módulos podem ser importados corretamente."""

    def test_importar_modulo_captura(self):
        """Módulo 1 — captura.py deve importar sem erros."""
        from modules.captura import capturar_normativos, Normativo
        self.assertTrue(callable(capturar_normativos))
        self.assertTrue(hasattr(Normativo, "__dataclass_fields__"))

    def test_importar_modulo_reasoning(self):
        """Módulo 2 — reasoning.py deve importar sem erros."""
        from modules.reasoning import classificar_normativo, ClassificacaoNormativo
        self.assertTrue(callable(classificar_normativo))
        self.assertTrue(hasattr(ClassificacaoNormativo, "__dataclass_fields__"))

    def test_importar_modulo_avaliacao_risco(self):
        """Módulo 3 — avaliacao_risco.py deve importar sem erros."""
        from modules.avaliacao_risco import avaliar_risco, AvaliacaoRisco, PilarAvaliacao
        self.assertTrue(callable(avaliar_risco))
        self.assertTrue(hasattr(AvaliacaoRisco, "__dataclass_fields__"))
        self.assertTrue(hasattr(PilarAvaliacao, "__dataclass_fields__"))

    def test_importar_modulo_resumo(self):
        """Módulo 4 — resumo.py deve importar sem erros."""
        from modules.resumo import gerar_resumo, ResumoExecutivo
        self.assertTrue(callable(gerar_resumo))
        self.assertTrue(hasattr(ResumoExecutivo, "__dataclass_fields__"))

    def test_importar_modulo_responsaveis(self):
        """Módulo 5 — responsaveis.py deve importar sem erros."""
        from modules.responsaveis import mapear_responsaveis, Responsavel
        self.assertTrue(callable(mapear_responsaveis))
        self.assertTrue(hasattr(Responsavel, "__dataclass_fields__"))

    def test_importar_modulo_persistencia(self):
        """Módulo 6 — persistencia.py deve importar sem erros."""
        from modules.persistencia import salvar_analise, push_github
        self.assertTrue(callable(salvar_analise))
        self.assertTrue(callable(push_github))

    def test_importar_modulo_notificacao(self):
        """Módulo 7 — notificacao.py deve importar sem erros."""
        from modules.notificacao import enviar_notificacao_slack
        self.assertTrue(callable(enviar_notificacao_slack))

    def test_importar_init_modulos(self):
        """modules/__init__.py deve exportar todos os símbolos principais."""
        import modules
        for simbolo in [
            "capturar_normativos", "Normativo",
            "classificar_normativo", "ClassificacaoNormativo",
            "avaliar_risco", "AvaliacaoRisco",
            "gerar_resumo", "ResumoExecutivo",
            "mapear_responsaveis", "Responsavel",
            "salvar_analise", "push_github",
            "enviar_notificacao_slack",
        ]:
            self.assertTrue(hasattr(modules, simbolo), f"modules.{simbolo} não encontrado")


class TestNormativoDataclass(unittest.TestCase):
    """Testa o dataclass Normativo."""

    def test_criar_normativo_basico(self):
        """Deve criar um Normativo com campos básicos."""
        from modules.captura import Normativo
        n = Normativo(
            id="normativos_12345",
            titulo="Resolução BCB nº 570, de 19 de maio de 2026",
            ementa="Altera normas sobre instituições de pagamento.",
            data_publicacao="2026-05-19T00:00:00-03:00",
            data_vigencia=None,
            link="https://www.bcb.gov.br/normativos/12345",
            tipo="Resolução BCB",
            numero="570",
            ano_norma="2026",
        )
        self.assertEqual(n.id, "normativos_12345")
        self.assertEqual(n.texto_integral, "")
        self.assertEqual(n.texto_fonte, "")
        self.assertIsNotNone(n.capturado_em)

    def test_criar_normativo_com_integra(self):
        """Deve criar Normativo com texto integral."""
        from modules.captura import Normativo
        n = Normativo(
            id="normativos_99999",
            titulo="Resolução CMN nº 5.306",
            ementa="Dispõe sobre tarifas de instituições de pagamento.",
            data_publicacao="2026-05-20",
            data_vigencia="2026-08-01",
            link="https://www.bcb.gov.br/normativos/99999",
            tipo="Resolução CMN",
            numero="5306",
            ano_norma="2026",
            texto_integral="Art. 1° Esta resolução dispõe sobre as tarifas cobradas pelas instituições de pagamento...",
            texto_fonte="html",
        )
        self.assertIn("Art. 1°", n.texto_integral)
        self.assertEqual(n.texto_fonte, "html")


class TestCaptura(unittest.TestCase):
    """Testa funções do módulo captura."""

    def test_extrair_tipo_numero_resolucao_bcb(self):
        """Deve extrair tipo e número de uma Resolução BCB."""
        from modules.captura import _extrair_tipo_numero
        tipo, numero, ano = _extrair_tipo_numero("Resolução BCB nº 570, de 19 de maio de 2026")
        self.assertEqual(tipo, "Resolução BCB")
        self.assertEqual(numero, "570")
        self.assertEqual(ano, "2026")

    def test_extrair_tipo_numero_resolucao_cmn(self):
        """Deve extrair tipo e número de uma Resolução CMN."""
        from modules.captura import _extrair_tipo_numero
        tipo, numero, ano = _extrair_tipo_numero("Resolução CMN nº 5.306, de 20 de maio de 2026")
        self.assertEqual(tipo, "Resolução CMN")
        self.assertIn("5", numero)
        self.assertEqual(ano, "2026")

    def test_normalizar_id(self):
        """Deve normalizar IDs de normativos corretamente."""
        from modules.captura import _normalizar_id
        self.assertEqual(_normalizar_id("normativos_12345"), "normativos_12345")
        self.assertEqual(_normalizar_id("https://bcb.gov.br/normativos/12345"), "normativos_12345")
        id_hash = _normalizar_id("algum-id-estranho")
        self.assertTrue(id_hash.startswith("normativos_"))


class TestReasoning(unittest.TestCase):
    """Testa funções do módulo reasoning."""

    def _criar_normativo_ifood(self) -> "Normativo":
        from modules.captura import Normativo
        return Normativo(
            id="normativos_test",
            titulo="Resolução BCB nº 999 — Instituições de Pagamento",
            ementa="Altera normas sobre conta de pagamento e Pix para instituições de pagamento.",
            data_publicacao="2026-05-20",
            data_vigencia=None,
            link="https://bcb.gov.br/99999",
            tipo="Resolução BCB",
            numero="999",
            ano_norma="2026",
            texto_integral=(
                "Art. 1° Esta resolução aplica-se às instituições de pagamento. "
                "Art. 2° As instituições de pagamento devem adequar seus sistemas de conta de pagamento. "
                "Art. 3° Os participantes do Pix devem observar as regras."
            ),
        )

    def test_classificar_aplicavel(self):
        """Normativo sobre IPs e Pix deve ser classificado como APLICÁVEL."""
        from modules.reasoning import classificar_normativo
        config = {
            "reasoning_layer_path": "data/normativos-bcb/REASONING_LAYER.md",
            "politicas_path": "data/normativos-bcb/REASONING_LAYER_POLITICAS.md",
            "feedback_path": "data/normativos-bcb/FEEDBACK.md",
            "keywords_aplicavel": [
                "pagamento", "pix", "instituição de pagamento", "conta de pagamento"
            ],
            "keywords_monitorar": ["banco", "risco"],
        }
        normativo = self._criar_normativo_ifood()
        resultado = classificar_normativo(normativo, config=config)
        self.assertIn(resultado.classificacao, ["APLICÁVEL", "MONITORAR"])
        self.assertIsNotNone(resultado.justificativa)
        self.assertIsNotNone(resultado.passo1_tipo)

    def test_classificar_nao_aplicavel(self):
        """Normativo sobre câmbio não deve ser APLICÁVEL."""
        from modules.captura import Normativo
        from modules.reasoning import classificar_normativo
        n = Normativo(
            id="normativos_cambio",
            titulo="Resolução BCB nº 888 — Operações de Câmbio",
            ementa="Regula exclusivamente operações de câmbio e câmbio manual.",
            data_publicacao="2026-05-01",
            data_vigencia=None,
            link="https://bcb.gov.br/888",
            tipo="Resolução BCB",
            numero="888",
            ano_norma="2026",
            texto_integral="Art. 1° Esta resolução regula câmbio, operações de câmbio e câmbio manual exclusivamente.",
        )
        config = {
            "reasoning_layer_path": "data/normativos-bcb/REASONING_LAYER.md",
            "politicas_path": "data/normativos-bcb/REASONING_LAYER_POLITICAS.md",
            "feedback_path": "data/normativos-bcb/FEEDBACK.md",
            "keywords_aplicavel": ["pagamento", "pix", "instituição de pagamento"],
            "keywords_monitorar": ["banco", "risco"],
        }
        resultado = classificar_normativo(n, config=config)
        self.assertIsNotNone(resultado.classificacao)


class TestAvaliacaoRisco(unittest.TestCase):
    """Testa funções do módulo avaliacao_risco."""

    def _criar_fixture(self):
        from modules.captura import Normativo
        from modules.reasoning import ClassificacaoNormativo, PoliticaImpactada
        n = Normativo(
            id="normativos_risco",
            titulo="Resolução BCB nº 570 — Segurança Cibernética",
            ementa="Altera regras de segurança cibernética e proteção ao consumidor.",
            data_publicacao="2026-05-19",
            data_vigencia="2026-09-01",
            link="https://bcb.gov.br/570",
            tipo="Resolução BCB",
            numero="570",
            ano_norma="2026",
            texto_integral=(
                "Art. 1° As instituições de pagamento devem implementar procedimentos de "
                "segurança cibernética. Art. 2° É obrigatório o monitoramento de fraudes. "
                "Art. 3° As multas aplicáveis são de até R$ 2.000.000,00."
            ),
        )
        c = ClassificacaoNormativo(
            normativo_id="normativos_risco",
            normativo_titulo=n.titulo,
            classificacao="APLICÁVEL",
            confianca="ALTA",
            justificativa="Norma sobre IPs com segurança cibernética.",
            passo1_tipo="Resolução BCB nº 570",
            passo2_atinge_ifood=True,
            passo2_razoes=["instituição de pagamento"],
            passo3_temas=["[APLICÁVEL] segurança cibernética", "[APLICÁVEL] pagamento"],
            passo4_classificacao="APLICÁVEL",
            passo5_politicas=[],
        )
        return n, c

    def test_avaliar_risco_retorna_5_pilares(self):
        """Avaliação deve retornar objeto com 5 pilares preenchidos."""
        from modules.avaliacao_risco import avaliar_risco, SCORE_CRITICO, SCORE_ALTO, SCORE_MEDIO, SCORE_BAIXO
        n, c = self._criar_fixture()
        resultado = avaliar_risco(n, c)
        self.assertIsNotNone(resultado.pilar_operacional)
        self.assertIsNotNone(resultado.pilar_regulatorio)
        self.assertIsNotNone(resultado.pilar_financeiro)
        self.assertIsNotNone(resultado.pilar_clientes)
        self.assertIsNotNone(resultado.pilar_estrategico)
        self.assertIn(resultado.score_consolidado, [SCORE_CRITICO, SCORE_ALTO, SCORE_MEDIO, SCORE_BAIXO])

    def test_score_numerico_valido(self):
        """Score numérico deve estar entre 1 e 4."""
        from modules.avaliacao_risco import avaliar_risco
        n, c = self._criar_fixture()
        resultado = avaliar_risco(n, c)
        self.assertGreaterEqual(resultado.score_numerico, 1.0)
        self.assertLessEqual(resultado.score_numerico, 4.0)


class TestResumo(unittest.TestCase):
    """Testa funções do módulo resumo."""

    def test_gerar_resumo_markdown(self):
        """Resumo deve gerar markdown não vazio."""
        from modules.captura import Normativo
        from modules.reasoning import ClassificacaoNormativo
        from modules.avaliacao_risco import avaliar_risco
        from modules.resumo import gerar_resumo

        n = Normativo(
            id="normativos_resumo",
            titulo="Resolução CMN nº 5.306 — Tarifas de IPs",
            ementa="Altera tarifas cobradas por instituições de pagamento.",
            data_publicacao="2026-05-20",
            data_vigencia="2026-08-01",
            link="https://bcb.gov.br/5306",
            tipo="Resolução CMN",
            numero="5306",
            ano_norma="2026",
            texto_integral="Art. 1° As instituições de pagamento devem observar os limites de tarifas.",
        )
        c = ClassificacaoNormativo(
            normativo_id=n.id,
            normativo_titulo=n.titulo,
            classificacao="APLICÁVEL",
            confianca="MÉDIA",
            justificativa="Norma sobre tarifas de IPs.",
            passo1_tipo="Resolução CMN nº 5.306",
            passo2_atinge_ifood=True,
            passo2_razoes=["instituição de pagamento"],
            passo3_temas=["[APLICÁVEL] tarifas", "[APLICÁVEL] pagamento"],
            passo4_classificacao="APLICÁVEL",
            passo5_politicas=[],
        )
        av = avaliar_risco(n, c)
        resumo = gerar_resumo(n, c, av)

        self.assertNotEqual(resumo.markdown, "")
        self.assertIn("iFood Pago", resumo.markdown)
        self.assertIn(n.tipo, resumo.markdown)
        self.assertIsInstance(resumo.acoes_requeridas, list)
        self.assertGreater(len(resumo.acoes_requeridas), 0)


class TestResponsaveis(unittest.TestCase):
    """Testa funções do módulo responsaveis."""

    def test_mapear_responsaveis_pld(self):
        """Normativo sobre PLD deve incluir time PLD/FT."""
        from modules.captura import Normativo
        from modules.reasoning import ClassificacaoNormativo
        from modules.avaliacao_risco import avaliar_risco
        from modules.responsaveis import mapear_responsaveis

        n = Normativo(
            id="normativos_pld",
            titulo="Circular BCB nº 3.978 — PLD",
            ementa="Altera procedimentos de prevenção à lavagem de dinheiro.",
            data_publicacao="2026-05-01",
            data_vigencia=None,
            link="https://bcb.gov.br/pld",
            tipo="Circular BCB",
            numero="3978",
            ano_norma="2026",
            texto_integral=(
                "Art. 1° As instituições de pagamento devem reforçar os procedimentos de "
                "prevenção à lavagem de dinheiro e financiamento ao terrorismo (PLD/FT)."
            ),
        )
        c = ClassificacaoNormativo(
            normativo_id=n.id,
            normativo_titulo=n.titulo,
            classificacao="APLICÁVEL",
            confianca="ALTA",
            justificativa="Norma PLD/FT para IPs.",
            passo1_tipo="Circular BCB nº 3978",
            passo2_atinge_ifood=True,
            passo2_razoes=["instituição de pagamento"],
            passo3_temas=["[APLICÁVEL] pld", "[APLICÁVEL] prevenção à lavagem"],
            passo4_classificacao="APLICÁVEL",
            passo5_politicas=[],
        )
        av = avaliar_risco(n, c)
        responsaveis = mapear_responsaveis(n, c, av)

        self.assertGreater(len(responsaveis), 0)
        times = [r.time for r in responsaveis]
        areas = [r.area for r in responsaveis]
        # Compliance ou PLD/FT deve estar presente
        self.assertTrue(
            any("PLD" in t or "Compliance" in a for t, a in zip(times, areas)),
            f"PLD/FT não encontrado. Times: {times}, Áreas: {areas}"
        )

    def test_responsavel_tem_todos_campos(self):
        """Cada Responsavel deve ter área, time, ação, prioridade e segmento."""
        from modules.responsaveis import Responsavel
        r = Responsavel(
            area="Compliance",
            time="PLD/FT",
            acao="Revisar política PLD",
            prioridade="ALTA",
            segmento="B2C",
        )
        self.assertEqual(r.area, "Compliance")
        self.assertEqual(r.prioridade, "ALTA")
        self.assertEqual(r.segmento, "B2C")


class TestNotificacao(unittest.TestCase):
    """Testa funções do módulo notificacao."""

    def test_construir_blocos_slack(self):
        """Deve construir blocos Slack válidos."""
        from modules.captura import Normativo
        from modules.reasoning import ClassificacaoNormativo
        from modules.avaliacao_risco import avaliar_risco
        from modules.resumo import gerar_resumo
        from modules.responsaveis import mapear_responsaveis
        from modules.notificacao import _construir_blocos_slack

        n = Normativo(
            id="normativos_slack",
            titulo="Resolução BCB nº 999",
            ementa="Altera normas sobre pagamentos.",
            data_publicacao="2026-05-20",
            data_vigencia=None,
            link="https://bcb.gov.br/999",
            tipo="Resolução BCB",
            numero="999",
            ano_norma="2026",
            texto_integral="Art. 1° As instituições de pagamento devem...",
        )
        c = ClassificacaoNormativo(
            normativo_id=n.id,
            normativo_titulo=n.titulo,
            classificacao="APLICÁVEL",
            confianca="ALTA",
            justificativa="Norma sobre IPs.",
            passo1_tipo="Resolução BCB nº 999",
            passo2_atinge_ifood=True,
            passo2_razoes=["instituição de pagamento"],
            passo3_temas=["[APLICÁVEL] pagamento"],
            passo4_classificacao="APLICÁVEL",
            passo5_politicas=[],
        )
        av = avaliar_risco(n, c)
        resp = mapear_responsaveis(n, c, av)
        resumo = gerar_resumo(n, c, av, resp)

        blocos = _construir_blocos_slack(n, c, av, resumo, resp)

        self.assertIsInstance(blocos, list)
        self.assertGreater(len(blocos), 0)
        # Verificar que há um header
        tipos = [b.get("type") for b in blocos]
        self.assertIn("header", tipos)
        self.assertIn("section", tipos)

    def test_nao_aplicavel_suprimido(self):
        """Notificação NÃO APLICÁVEL deve ser suprimida."""
        from modules.captura import Normativo
        from modules.reasoning import ClassificacaoNormativo
        from modules.avaliacao_risco import avaliar_risco
        from modules.resumo import gerar_resumo
        from modules.responsaveis import mapear_responsaveis
        from modules.notificacao import enviar_notificacao_slack

        n = Normativo(
            id="normativos_nao_ap",
            titulo="Resolução sobre câmbio",
            ementa="Câmbio exclusivamente.",
            data_publicacao="2026-05-01",
            data_vigencia=None,
            link="https://bcb.gov.br/nao_ap",
            tipo="Resolução BCB",
            numero="001",
            ano_norma="2026",
        )
        c = ClassificacaoNormativo(
            normativo_id=n.id,
            normativo_titulo=n.titulo,
            classificacao="NÃO APLICÁVEL",
            confianca="ALTA",
            justificativa="Câmbio fora do escopo.",
            passo1_tipo="Resolução BCB nº 001",
            passo2_atinge_ifood=False,
            passo2_razoes=[],
            passo3_temas=[],
            passo4_classificacao="NÃO APLICÁVEL",
            passo5_politicas=[],
        )
        av = avaliar_risco(n, c)
        resp = mapear_responsaveis(n, c, av)
        resumo = gerar_resumo(n, c, av, resp)

        config = {"slack_webhook": "https://hooks.slack.com/fake", "github_repo": ""}
        resultado = enviar_notificacao_slack(n, c, av, resumo, resp, config=config)
        self.assertTrue(resultado.get("skipped"), "NÃO APLICÁVEL deve ser suprimido")


class TestConfigJson(unittest.TestCase):
    """Testa que config.json existe e tem os campos obrigatórios."""

    def test_config_json_existe(self):
        """config.json deve existir na raiz da skill."""
        config_path = SKILL_DIR / "config.json"
        self.assertTrue(config_path.exists(), f"config.json não encontrado em {config_path}")

    def test_config_campos_obrigatorios(self):
        """config.json deve ter todos os campos obrigatórios."""
        config_path = SKILL_DIR / "config.json"
        config = json.loads(config_path.read_text(encoding="utf-8"))

        campos_obrigatorios = [
            "github_repo",
            "slack_webhook",
            "bcb_feed",
            "reasoning_layer_path",
            "politicas_path",
            "feedback_path",
            "enviados_path",
            "branch",
        ]
        for campo in campos_obrigatorios:
            self.assertIn(campo, config, f"Campo obrigatório ausente: {campo}")

    def test_config_github_repo(self):
        """github_repo deve ter o valor correto."""
        config_path = SKILL_DIR / "config.json"
        config = json.loads(config_path.read_text(encoding="utf-8"))
        self.assertEqual(config["github_repo"], "giovannabatistutti-ctrl/normativos_md")


if __name__ == "__main__":
    print("=" * 60)
    print("🧪 Executando suite de testes — skill normativos-bcb")
    print("=" * 60)
    unittest.main(verbosity=2)
