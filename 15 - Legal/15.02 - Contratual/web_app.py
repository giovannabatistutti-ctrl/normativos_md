"""
web_app.py — Interface web do Pipeline 15-Aditamentos iFood Benefícios

Endpoints:
  GET  /           → Formulário de disparo com campo Ticket ID + opção dry-run
  POST /processar  → Executa pipeline, retorna resultado formatado
  GET  /historico  → Últimas 20 entradas do DECISION_AUDIT.csv
  GET  /health     → {"status": "ok", "app": "15-aditamentos"}
"""

import csv
import json
import os
import sys
from pathlib import Path
from datetime import datetime

from flask import Flask, request, jsonify, Response

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
BASE_DIR = Path(__file__).parent
AUDIT_PATH = BASE_DIR / "data" / "audit" / "DECISION_AUDIT.csv"

# Ensure pipeline can import its modules
sys.path.insert(0, str(BASE_DIR))

app = Flask(__name__)

# ---------------------------------------------------------------------------
# HTML templates (inline, sem CDN externo, sem Google Fonts)
# ---------------------------------------------------------------------------

HTML_BASE = """<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>15-Aditamentos — iFood Benefícios</title>
  <style>
    *, *::before, *::after {{ box-sizing: border-box; }}
    body {{
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Arial, sans-serif;
      background: #f5f5f5;
      margin: 0;
      padding: 24px;
      color: #212121;
    }}
    .container {{
      max-width: 760px;
      margin: 0 auto;
    }}
    h1 {{
      font-size: 1.4rem;
      font-weight: 700;
      color: #c8001e;
      margin: 0 0 4px 0;
    }}
    .subtitle {{
      font-size: 0.85rem;
      color: #666;
      margin: 0 0 28px 0;
    }}
    .card {{
      background: #fff;
      border: 1px solid #e0e0e0;
      border-radius: 8px;
      padding: 24px;
      margin-bottom: 20px;
    }}
    label {{
      display: block;
      font-size: 0.875rem;
      font-weight: 600;
      margin-bottom: 6px;
      color: #333;
    }}
    input[type="text"] {{
      width: 100%;
      padding: 10px 12px;
      border: 1px solid #ccc;
      border-radius: 6px;
      font-size: 0.95rem;
      outline: none;
      transition: border-color 0.15s;
    }}
    input[type="text"]:focus {{ border-color: #c8001e; }}
    .check-row {{
      display: flex;
      align-items: center;
      gap: 8px;
      margin: 14px 0 20px 0;
    }}
    input[type="checkbox"] {{ width: 16px; height: 16px; accent-color: #c8001e; }}
    .check-row span {{ font-size: 0.875rem; color: #444; }}
    button[type="submit"] {{
      background: #c8001e;
      color: #fff;
      border: none;
      padding: 11px 24px;
      border-radius: 6px;
      font-size: 0.95rem;
      font-weight: 600;
      cursor: pointer;
      transition: background 0.15s;
    }}
    button[type="submit"]:hover {{ background: #a5001a; }}
    .nav {{
      display: flex;
      gap: 16px;
      margin-bottom: 20px;
    }}
    .nav a {{
      color: #c8001e;
      text-decoration: none;
      font-size: 0.875rem;
      font-weight: 500;
    }}
    .nav a:hover {{ text-decoration: underline; }}
    .result-box {{
      background: #f9f9f9;
      border-left: 4px solid #c8001e;
      border-radius: 4px;
      padding: 16px 20px;
      margin-top: 20px;
    }}
    .result-box h2 {{ font-size: 1rem; margin: 0 0 12px 0; }}
    .result-row {{ margin: 6px 0; font-size: 0.875rem; }}
    .result-row b {{ min-width: 140px; display: inline-block; }}
    .badge {{
      display: inline-block;
      padding: 2px 10px;
      border-radius: 12px;
      font-size: 0.8rem;
      font-weight: 600;
    }}
    .badge-green {{ background: #e6f4ea; color: #1e7e34; }}
    .badge-orange {{ background: #fff3e0; color: #e65100; }}
    .badge-red {{ background: #fce8e6; color: #c5221f; }}
    .error-box {{
      background: #fce8e6;
      border-left: 4px solid #c5221f;
      border-radius: 4px;
      padding: 16px 20px;
      margin-top: 20px;
      font-size: 0.875rem;
      color: #c5221f;
    }}
    table {{
      width: 100%;
      border-collapse: collapse;
      font-size: 0.83rem;
    }}
    th, td {{
      text-align: left;
      padding: 8px 10px;
      border-bottom: 1px solid #eee;
    }}
    th {{ background: #fafafa; font-weight: 600; color: #555; }}
    tr:hover {{ background: #f5f5f5; }}
    .hint {{ font-size: 0.78rem; color: #999; margin-top: 6px; }}
  </style>
</head>
<body>
<div class="container">
  <h1>Pipeline 15-Aditamentos</h1>
  <p class="subtitle">iFood Benefícios — Automação de Aditivos Contratuais</p>
  <div class="nav">
    <a href="/">&#8962; Processar</a>
    <a href="/historico">&#128203; Histórico</a>
  </div>
  {BODY}
</div>
</body>
</html>"""


FORM_BODY = """
<div class="card">
  <form method="POST" action="/processar">
    <label for="ticket_id">Ticket Jira</label>
    <input type="text" id="ticket_id" name="ticket_id"
           placeholder="JURFIN-1234 ou MOCK-001 para teste"
           autocomplete="off" required>
    <p class="hint">Use prefixo <b>MOCK-</b> (ex: MOCK-001) para executar sem chamar APIs externas.</p>
    <div class="check-row">
      <input type="checkbox" id="dry_run" name="dry_run" value="1">
      <span><b>Dry-run</b> — montar aditamento sem gerar documento / notificar Slack</span>
    </div>
    <button type="submit">&#9654; Processar Aditamento</button>
  </form>
</div>
{RESULT}
"""


def _badge(decisao: str) -> str:
    if decisao == "AUTONOMO":
        return '<span class="badge badge-green">AUTÔNOMO ✓</span>'
    elif decisao == "REVISAO_HUMANA":
        return '<span class="badge badge-orange">REVISÃO HUMANA</span>'
    return f'<span class="badge badge-red">{decisao}</span>'


def _render_result(resultado: dict) -> str:
    score_info = resultado.get("score", {})
    if isinstance(score_info, dict):
        score_val = score_info.get("score", 0.0)
        decisao = score_info.get("decisao", "REVISAO_HUMANA")
    else:
        score_val = float(score_info or 0.0)
        decisao = "AUTONOMO" if score_val >= 0.90 else "REVISAO_HUMANA"

    campos_pend = resultado.get("campos_pendentes", [])
    modulos = resultado.get("modulos_selecionados", [])
    doc_url = resultado.get("doc_url") or ""
    status = resultado.get("status", "")
    dry_run = resultado.get("dry_run", False)

    doc_link = (
        f'<a href="{doc_url}" target="_blank" rel="noopener">Abrir documento</a>'
        if doc_url
        else "(não gerado — dry-run ou erro)"
    )

    pend_html = ""
    if campos_pend:
        items = "".join(f"<li>{c}</li>" for c in campos_pend)
        pend_html = f"<ul style='margin:4px 0 0 16px;font-size:0.82rem;color:#c5221f'>{items}</ul>"
    else:
        pend_html = '<span style="color:#1e7e34;font-size:0.82rem">Nenhum campo pendente ✓</span>'

    modulos_str = ", ".join(modulos) if modulos else "(nenhum)"

    return f"""
<div class="result-box">
  <h2>Resultado — {resultado.get('ticket', '')}
    {'<span style="font-size:0.75rem;font-weight:400;color:#888;margin-left:8px">[DRY-RUN]</span>' if dry_run else ''}
  </h2>
  <div class="result-row"><b>Empresa:</b> {resultado.get('empresa', '—')}</div>
  <div class="result-row"><b>Decisão:</b> {_badge(decisao)}</div>
  <div class="result-row"><b>Score:</b> {score_val:.2%}</div>
  <div class="result-row"><b>Módulos:</b> {modulos_str}</div>
  <div class="result-row"><b>Status:</b> {status}</div>
  <div class="result-row"><b>Documento:</b> {doc_link}</div>
  <div class="result-row"><b>Campos pendentes:</b><br>{pend_html}</div>
</div>
"""


def _render_error(msg: str) -> str:
    return f'<div class="error-box"><b>Erro:</b> {msg}</div>'


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.get("/health")
def health():
    return jsonify({"status": "ok", "app": "15-aditamentos"})


@app.get("/")
def index():
    body = HTML_BASE.replace("{BODY}", FORM_BODY.replace("{RESULT}", ""))
    return Response(body, mimetype="text/html")


@app.post("/processar")
def processar():
    ticket_id = (request.form.get("ticket_id") or "").strip().upper()
    dry_run = bool(request.form.get("dry_run"))

    result_html = ""
    if not ticket_id:
        result_html = _render_error("Informe o Ticket ID.")
    else:
        try:
            from pipeline_aditamentos import processar_ticket
            resultado = processar_ticket(ticket_id, dry_run=dry_run)
            if "erro" in resultado or resultado.get("status", "").startswith("erro"):
                result_html = _render_error(
                    resultado.get("erro") or resultado.get("status", "Erro desconhecido")
                )
            else:
                result_html = _render_result(resultado)
        except Exception as exc:
            result_html = _render_error(str(exc))

    body = HTML_BASE.replace("{BODY}", FORM_BODY.replace("{RESULT}", result_html))
    return Response(body, mimetype="text/html")


@app.get("/historico")
def historico():
    rows = []
    if AUDIT_PATH.exists():
        try:
            with open(AUDIT_PATH, encoding="utf-8") as f:
                reader = csv.DictReader(f)
                rows = list(reader)
            rows = rows[-20:]
            rows.reverse()
        except Exception:
            rows = []

    if rows:
        headers = list(rows[0].keys())
        thead = "".join(f"<th>{h}</th>" for h in headers)
        tbody_rows = []
        for r in rows:
            tds = "".join(f"<td>{r.get(h, '')}</td>" for h in headers)
            tbody_rows.append(f"<tr>{tds}</tr>")
        table_html = f"""
<div class="card" style="overflow-x:auto">
  <h2 style="font-size:1rem;margin-top:0">Últimas entradas de auditoria</h2>
  <table>
    <thead><tr>{thead}</tr></thead>
    <tbody>{''.join(tbody_rows)}</tbody>
  </table>
</div>"""
    else:
        table_html = '<div class="card"><p style="color:#666;font-size:0.9rem">Nenhuma entrada no histórico ainda.</p></div>'

    body = HTML_BASE.replace("{BODY}", table_html)
    return Response(body, mimetype="text/html")


# ---------------------------------------------------------------------------
# Entrypoint
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port, debug=False)
