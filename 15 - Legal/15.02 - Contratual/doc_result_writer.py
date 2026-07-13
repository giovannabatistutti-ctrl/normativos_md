"""
doc_result_writer.py
====================
Helpers para o Planner salvar o resultado da geração do doc via MCP.
"""
import json
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
RESULTS_DIR = BASE_DIR / "data" / "doc_results"


def salvar_resultado(
    ticket_id: str,
    doc_id: str,
    doc_url: str,
    doc_nome: str,
    score: float = 0.0,
    decisao: str = "REVISAO_HUMANA",
    campos_pendentes: list = None,
) -> Path:
    """
    Chamado pelo Planner após gerar o documento via MCP.
    Salva doc_result_{ticket_id}.json para o pipeline continuar.
    """
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    resultado = {
        "ticket_id": ticket_id,
        "doc_id": doc_id,
        "doc_url": doc_url,
        "doc_nome": doc_nome,
        "score": score,
        "decisao": decisao,
        "campos_pendentes": campos_pendentes or [],
        "status": "gerado",
    }
    path = RESULTS_DIR / f"{ticket_id}_doc_result.json"
    path.write_text(json.dumps(resultado, ensure_ascii=False, indent=2))
    return path


def listar_pendentes() -> list:
    """
    Lista tickets com pending_doc ainda não processados pelo Planner.
    """
    pending_dir = BASE_DIR / "data" / "pending_docs"
    results_dir = RESULTS_DIR
    if not pending_dir.exists():
        return []
    pendentes = []
    for f in sorted(pending_dir.glob("*_pending_doc.json")):
        ticket_id = f.name.replace("_pending_doc.json", "")
        result = results_dir / f"{ticket_id}_doc_result.json"
        if not result.exists():
            pendentes.append(json.loads(f.read_text(encoding="utf-8")))
    return pendentes
