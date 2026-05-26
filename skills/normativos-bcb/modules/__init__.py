"""
Skill: normativos-bcb
Módulos para monitoramento, análise e notificação de normativos do Banco Central do Brasil.

Módulos disponíveis:
    captura         — Módulo 1: Captura RSS + íntegra da norma
    reasoning       — Módulo 2: Aplicação do reasoning layer + políticas
    avaliacao_risco — Módulo 3: Avaliação dos 5 pilares de risco
    resumo          — Módulo 4: Geração de resumo executivo
    responsaveis    — Módulo 5: Definição de áreas/times responsáveis
    persistencia    — Módulo 6: GitHub + memória semântica
    notificacao     — Módulo 7: Slack com blocos estruturados
"""

from .captura import capturar_normativos, Normativo
from .reasoning import classificar_normativo, ClassificacaoNormativo
from .avaliacao_risco import avaliar_risco, AvaliacaoRisco
from .resumo import gerar_resumo, ResumoExecutivo
from .responsaveis import mapear_responsaveis, Responsavel
from .persistencia import salvar_analise, push_github
from .notificacao import enviar_notificacao_slack

__all__ = [
    "capturar_normativos",
    "Normativo",
    "classificar_normativo",
    "ClassificacaoNormativo",
    "avaliar_risco",
    "AvaliacaoRisco",
    "gerar_resumo",
    "ResumoExecutivo",
    "mapear_responsaveis",
    "Responsavel",
    "salvar_analise",
    "push_github",
    "enviar_notificacao_slack",
]
