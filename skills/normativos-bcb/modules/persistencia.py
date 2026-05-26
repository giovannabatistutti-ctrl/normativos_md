"""
Módulo 6 — persistencia.py
Persiste a análise completa de um normativo:
  - Salva JSON local em data/normativos-bcb/{data}/{codigo}.json (memória semântica)
  - Faz push para GitHub (repo: giovannabatistutti-ctrl/normativos_md)
  - Atualiza README.md do repo com o normativo
  - Atualiza enviados.json (anti-duplicata)

Entradas:
    normativo (Normativo): Normativo capturado.
    classificacao (ClassificacaoNormativo): Resultado do reasoning.
    avaliacao (AvaliacaoRisco): Resultado da avaliação de risco.
    resumo (ResumoExecutivo): Resumo executivo gerado.
    responsaveis (List[Responsavel]): Lista de responsáveis.
    config (dict): Configuração do config.json.

Saídas:
    dict: Resultado da persistência com status de cada operação.

Uso:
    from modules.persistencia import salvar_analise, push_github
    resultado = salvar_analise(normativo, classificacao, avaliacao, resumo, responsaveis)
"""

from __future__ import annotations

import base64
import json
import re
import time
import warnings
from dataclasses import asdict
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Dict, List, Optional

import requests

from .captura import Normativo
from .reasoning import ClassificacaoNormativo
from .avaliacao_risco import AvaliacaoRisco
from .resumo import ResumoExecutivo
from .responsaveis import Responsavel

warnings.filterwarnings("ignore")

BRASILIA = timezone(timedelta(hours=-3))


def _carregar_config(config: Optional[Dict] = None) -> Dict:
    if config:
        return config
    config_path = Path(__file__).parent.parent / "config.json"
    if config_path.exists():
        return json.loads(config_path.read_text(encoding="utf-8"))
    return {}


def _dataclass_to_dict(obj) -> Dict:
    """Converte dataclass para dict recursivamente."""
    try:
        return asdict(obj)
    except Exception:
        if hasattr(obj, "__dict__"):
            return obj.__dict__
        return str(obj)


def _sanitizar_nome_arquivo(titulo: str) -> str:
    """Sanitiza título para uso como nome de arquivo."""
    nome = re.sub(r"[^\w\s\-]", "", titulo.lower())
    nome = re.sub(r"\s+", "_", nome.strip())
    nome = re.sub(r"_+", "_", nome)
    return nome[:80]


def _load_enviados(enviados_path: Path) -> Dict:
    """Carrega enviados.json."""
    if enviados_path.exists():
        try:
            return json.loads(enviados_path.read_text(encoding="utf-8"))
        except Exception:
            return {}
    return {}


def _save_enviados(enviados_path: Path, data: Dict) -> None:
    """Salva enviados.json."""
    enviados_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def _gh_get(github_api: str, github_repo: str, path: str) -> requests.Response:
    """GET de um arquivo no GitHub (sem headers manuais — proxy injeta Bearer)."""
    url = f"{github_api}/repos/{github_repo}/contents/{path}"
    return requests.get(url, verify=False, timeout=30)


def _gh_put(
    github_api: str,
    github_repo: str,
    path: str,
    message: str,
    content_b64: str,
    branch: str,
    sha: Optional[str] = None,
) -> requests.Response:
    """PUT de um arquivo no GitHub."""
    url = f"{github_api}/repos/{github_repo}/contents/{path}"
    payload: Dict = {"message": message, "content": content_b64, "branch": branch}
    if sha:
        payload["sha"] = sha
    return requests.put(url, json=payload, verify=False, timeout=30)


def push_github(
    remote_path: str,
    content: str,
    commit_msg: str,
    config: Dict,
) -> Dict:
    """
    Faz push de um arquivo para o GitHub.

    Entradas:
        remote_path (str): Caminho no repositório GitHub.
        content (str): Conteúdo do arquivo (texto).
        commit_msg (str): Mensagem de commit.
        config (dict): Configuração com github_repo, github_api, branch.

    Saídas:
        dict: {"success": bool, "sha": str, "error": str}
    """
    github_api = config.get("github_api", "https://api.github.com")
    github_repo = config.get("github_repo", "")
    branch = config.get("branch", "main")

    if not github_repo:
        return {"success": False, "sha": None, "error": "github_repo não configurado"}

    content_b64 = base64.b64encode(content.encode("utf-8")).decode("utf-8")
    sha = None

    # Verificar se arquivo já existe
    r_get = _gh_get(github_api, github_repo, remote_path)
    if r_get.status_code == 200:
        try:
            sha = r_get.json().get("sha")
        except Exception:
            pass

    r_put = _gh_put(github_api, github_repo, remote_path, commit_msg, content_b64, branch, sha)

    if r_put.status_code in (200, 201):
        try:
            new_sha = r_put.json().get("content", {}).get("sha", "")
        except Exception:
            new_sha = ""
        return {"success": True, "sha": new_sha, "error": ""}
    else:
        return {
            "success": False,
            "sha": None,
            "error": f"HTTP {r_put.status_code}: {r_put.text[:300]}",
        }


def _atualizar_readme(
    normativo: Normativo,
    classificacao: ClassificacaoNormativo,
    avaliacao: AvaliacaoRisco,
    config: Dict,
) -> Dict:
    """Atualiza README.md do repositório GitHub com o novo normativo."""
    github_api = config.get("github_api", "https://api.github.com")
    github_repo = config.get("github_repo", "")
    branch = config.get("branch", "main")

    # Buscar README atual
    r = _gh_get(github_api, github_repo, "README.md")
    readme_atual = ""
    sha = None
    if r.status_code == 200:
        try:
            data = r.json()
            sha = data.get("sha")
            readme_atual = base64.b64decode(data.get("content", "")).decode("utf-8")
        except Exception:
            pass

    # Linha nova para o normativo
    data_br = datetime.now(BRASILIA).strftime("%Y-%m-%d")
    emoji = {"APLICÁVEL": "🔴", "MONITORAR": "🟡", "NÃO APLICÁVEL": "🟢"}.get(
        classificacao.classificacao, "⚪"
    )
    nova_linha = (
        f"| {data_br} | [{normativo.tipo} nº {normativo.numero}]({normativo.link}) | "
        f"{emoji} {classificacao.classificacao} | {avaliacao.score_consolidado} |"
    )

    # Inserir após cabeçalho da tabela ou no início
    marcador = "<!-- NORMATIVOS_TABLE -->"
    if marcador in readme_atual:
        readme_novo = readme_atual.replace(marcador, f"{marcador}\n{nova_linha}")
    else:
        readme_novo = readme_atual + f"\n\n{nova_linha}\n"

    return push_github("README.md", readme_novo, f"docs: adicionar {normativo.tipo} nº {normativo.numero}", config)


def salvar_analise(
    normativo: Normativo,
    classificacao: ClassificacaoNormativo,
    avaliacao: AvaliacaoRisco,
    resumo: ResumoExecutivo,
    responsaveis: List[Responsavel],
    config: Optional[Dict] = None,
) -> Dict:
    """
    Persiste análise completa do normativo local e no GitHub.

    Operações realizadas:
      1. Salva JSON completo em data/normativos-bcb/{data}/{codigo}.json
      2. Salva markdown em data/normativos-bcb/{data}/{codigo}.md
      3. Push JSON para GitHub em normativos/{data}/{codigo}.json
      4. Push markdown para GitHub em normativos/{data}/{codigo}.md
      5. Atualiza README.md do GitHub
      6. Atualiza enviados.json (anti-duplicata)

    Entradas:
        normativo (Normativo): Normativo capturado.
        classificacao (ClassificacaoNormativo): Resultado do reasoning.
        avaliacao (AvaliacaoRisco): Resultado da avaliação de risco.
        resumo (ResumoExecutivo): Resumo executivo.
        responsaveis (List[Responsavel]): Lista de responsáveis.
        config (dict): Configuração. Se None, carrega do config.json.

    Saídas:
        dict: {
            "local_json": str,      # Caminho do JSON local
            "local_md": str,        # Caminho do markdown local
            "github_json": dict,    # Resultado push JSON
            "github_md": dict,      # Resultado push markdown
            "github_readme": dict,  # Resultado atualização README
            "enviados_atualizado": bool,
        }
    """
    cfg = _carregar_config(config)

    data_br = datetime.now(BRASILIA).strftime("%Y-%m-%d")
    nome_arquivo = _sanitizar_nome_arquivo(normativo.titulo)
    codigo = normativo.id

    # Diretórios locais
    memoria_path = Path(cfg.get("memoria_path", "data/normativos-bcb"))
    local_dir = memoria_path / data_br
    local_dir.mkdir(parents=True, exist_ok=True)

    # ── 1. Salvar JSON local ──────────────────────────────────────────────────
    analise_completa = {
        "normativo": _dataclass_to_dict(normativo),
        "classificacao": _dataclass_to_dict(classificacao),
        "avaliacao": _dataclass_to_dict(avaliacao),
        "resumo": _dataclass_to_dict(resumo),
        "responsaveis": [_dataclass_to_dict(r) for r in responsaveis],
        "metadata": {
            "pipeline": "normativos-bcb",
            "versao": "2.0",
            "data_analise": datetime.now(BRASILIA).isoformat(),
        },
    }
    json_path = local_dir / f"{codigo}.json"
    json_path.write_text(
        json.dumps(analise_completa, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    # ── 2. Salvar markdown local ──────────────────────────────────────────────
    md_path = local_dir / f"{nome_arquivo}.md"
    md_path.write_text(resumo.markdown, encoding="utf-8")

    # ── 3 & 4. Push para GitHub ───────────────────────────────────────────────
    github_json = {"success": False, "error": "GitHub não configurado"}
    github_md = {"success": False, "error": "GitHub não configurado"}
    github_readme = {"success": False, "error": "GitHub não configurado"}

    if cfg.get("github_repo"):
        github_json = push_github(
            f"normativos/{data_br}/{codigo}.json",
            json.dumps(analise_completa, ensure_ascii=False, indent=2),
            f"feat: análise {normativo.tipo} nº {normativo.numero} ({data_br})",
            cfg,
        )
        time.sleep(0.5)

        github_md = push_github(
            f"normativos/{data_br}/{nome_arquivo}.md",
            resumo.markdown,
            f"docs: resumo {normativo.tipo} nº {normativo.numero} ({data_br})",
            cfg,
        )
        time.sleep(0.5)

        # ── 5. Atualizar README ───────────────────────────────────────────────
        try:
            github_readme = _atualizar_readme(normativo, classificacao, avaliacao, cfg)
        except Exception as exc:
            github_readme = {"success": False, "error": str(exc)}

    # ── 6. Atualizar enviados.json ────────────────────────────────────────────
    enviados_path = Path(cfg.get("enviados_path", "data/normativos-bcb/enviados.json"))
    enviados = _load_enviados(enviados_path)
    enviados[codigo] = {
        "date": data_br,
        "filename": md_path.name,
        "titulo": normativo.titulo,
        "classificacao": classificacao.classificacao,
        "score": avaliacao.score_consolidado,
        "status": "analisado",
    }
    _save_enviados(enviados_path, enviados)

    return {
        "local_json": str(json_path),
        "local_md": str(md_path),
        "github_json": github_json,
        "github_md": github_md,
        "github_readme": github_readme,
        "enviados_atualizado": True,
    }


def push_planilha(config: dict) -> dict:
    """Gera planilha atualizada e faz push para GitHub.

    1. Executa gerar_planilha.py para atualizar normativos_radar.xlsx.
    2. Lê o .xlsx gerado e faz push base64 para
       planilha/normativos_radar.xlsx no repositório GitHub.

    Entradas:
        config (dict): Configuração com github_repo, github_api, branch.

    Saídas:
        dict: {"status": "ok"|"erro", "http": int, "msg": str}
    """
    import subprocess
    from pathlib import Path as _Path

    # 1. Gerar planilha atualizada
    subprocess.run(
        ["python3", "data/normativos-bcb/gerar_planilha.py"],
        check=False,
    )

    # 2. Verificar se planilha existe
    planilha_path = _Path("data/normativos-bcb/normativos_radar.xlsx")
    if not planilha_path.exists():
        return {"status": "erro", "http": 0, "msg": "planilha não encontrada após geração"}

    conteudo_b64 = base64.b64encode(planilha_path.read_bytes()).decode()
    remote_path = "planilha/normativos_radar.xlsx"

    github_api = config.get("github_api", "https://api.github.com")
    github_repo = config.get("github_repo", "")
    branch = config.get("branch", "main")

    if not github_repo:
        return {"status": "erro", "http": 0, "msg": "github_repo não configurado"}

    # 3. Checar SHA existente
    r = _gh_get(github_api, github_repo, remote_path)
    sha = r.json().get("sha") if r.status_code == 200 else None

    payload: dict = {
        "message": "chore: atualiza planilha normativos_radar.xlsx",
        "content": conteudo_b64,
        "branch": branch,
    }
    if sha:
        payload["sha"] = sha

    r2 = requests.put(
        f"{github_api}/repos/{github_repo}/contents/{remote_path}",
        json=payload,
        verify=False,
        timeout=60,
    )

    if r2.status_code in (200, 201):
        return {"status": "ok", "http": r2.status_code, "msg": "planilha enviada ao GitHub"}
    else:
        return {
            "status": "erro",
            "http": r2.status_code,
            "msg": r2.text[:300],
        }
