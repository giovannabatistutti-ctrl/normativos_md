"""
Módulo 1 — captura.py
Captura normativos do Banco Central do Brasil via RSS e busca a íntegra do texto.

Entradas:
    ano (int): Ano dos normativos a capturar. Padrão: ano atual.
    enviados (dict): Dicionário de normativos já processados (anti-duplicata).
    config (dict): Configurações carregadas do config.json.

Saídas:
    List[Normativo]: Lista de objetos Normativo com todos os campos incluindo texto_integral.

Uso:
    from modules.captura import capturar_normativos
    normativos = capturar_normativos(ano=2026, enviados={}, config=config)
"""

from __future__ import annotations

import re
import time
import warnings
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional

import requests
from bs4 import BeautifulSoup

warnings.filterwarnings("ignore")

BRASILIA = timezone(timedelta(hours=-3))


@dataclass
class Normativo:
    """Representa um normativo publicado pelo BCB."""

    # Campos do RSS
    id: str                          # ID único (ex: "normativos_52913")
    titulo: str                      # Título completo
    ementa: str                      # Ementa/resumo curto
    data_publicacao: str             # Data de publicação (ISO 8601)
    data_vigencia: Optional[str]     # Data de entrada em vigor
    link: str                        # URL da norma no site BCB
    tipo: str                        # Tipo: Resolução CMN, Resolução BCB, etc.
    numero: str                      # Número da norma
    ano_norma: str                   # Ano da norma

    # Campo adicional — íntegra
    texto_integral: str = field(default="")  # Texto completo da norma
    texto_fonte: str = field(default="")     # Fonte do texto (html, pdf, fallback)

    # Metadados de captura
    capturado_em: str = field(
        default_factory=lambda: datetime.now(BRASILIA).isoformat()
    )


def _carregar_config(config: Optional[Dict] = None) -> Dict:
    """Carrega configurações do config.json se não fornecidas."""
    if config:
        return config
    import json
    from pathlib import Path
    config_path = Path(__file__).parent.parent / "config.json"
    if config_path.exists():
        return json.loads(config_path.read_text(encoding="utf-8"))
    return {
        "bcb_feed": "https://www.bcb.gov.br/api/feed/app/normativos/normativos?ano={ano}",
        "bcb_headers": {"User-Agent": "Mozilla/5.0"},
    }


def _extrair_tipo_numero(titulo: str) -> tuple[str, str, str]:
    """
    Extrai tipo, número e ano de um título de normativo BCB.
    Exemplo: 'Resolução BCB nº 570, de 19 de maio de 2026' → ('Resolução BCB', '570', '2026')
    """
    tipo = "Normativo BCB"
    numero = ""
    ano = ""

    tipos_conhecidos = [
        "Instrução Normativa BCB",
        "Resolução Conjunta",
        "Resolução CMN",
        "Resolução BCB",
        "Circular BCB",
        "Carta Circular BCB",
        "Comunicado BCB",
        "Portaria BCB",
    ]
    for t in tipos_conhecidos:
        if t.lower() in titulo.lower():
            tipo = t
            break

    m = re.search(r"n[º°oa]?\s*\.?\s*(\d+[\./]?\d*)", titulo, re.IGNORECASE)
    if m:
        numero = m.group(1).strip("./")

    m_ano = re.search(r"\b(20\d{2})\b", titulo)
    if m_ano:
        ano = m_ano.group(1)

    return tipo, numero, ano


def _buscar_integra(link: str, headers: Dict, timeout: int = 15) -> tuple[str, str]:
    """
    Busca o texto integral de um normativo a partir do seu link no site BCB.

    Estratégias:
    1. Requisição HTTP ao link fornecido (página HTML BCB)
    2. Extração do texto via BeautifulSoup
    3. Se não encontrar conteúdo relevante, retorna ementa como fallback

    Retorna:
        (texto_integral, fonte): onde fonte é "html", "pdf" ou "fallback"
    """
    if not link:
        return "", "fallback"

    try:
        resp = requests.get(link, headers=headers, timeout=timeout, verify=False)
        if resp.status_code != 200:
            return "", "fallback"

        content_type = resp.headers.get("content-type", "")
        if "pdf" in content_type.lower():
            # PDF direto — retorna indicação para processamento futuro
            return f"[PDF disponível em: {link}]", "pdf"

        # HTML — extrair texto
        soup = BeautifulSoup(resp.text, "html.parser")

        # Remover scripts e estilos
        for tag in soup(["script", "style", "nav", "header", "footer"]):
            tag.decompose()

        # Tentar seletores específicos da página BCB de normativos
        seletores_bcb = [
            "div.conteudo-normativos",
            "div.normativos-detalhe",
            "div.conteudo-principal",
            "article",
            "main",
            "div#conteudo",
            "div.texto-norma",
            "div.norma-texto",
        ]
        texto = ""
        for seletor in seletores_bcb:
            elem = soup.select_one(seletor)
            if elem:
                texto = elem.get_text(separator="\n", strip=True)
                if len(texto) > 200:
                    break

        if not texto or len(texto) < 100:
            # Fallback: extrair texto do body inteiro
            body = soup.find("body")
            if body:
                texto = body.get_text(separator="\n", strip=True)

        # Limpeza básica
        linhas = [l.strip() for l in texto.splitlines() if l.strip()]
        texto_limpo = "\n".join(linhas)

        # Truncar se muito longo (máx 50.000 chars para segurança)
        if len(texto_limpo) > 50000:
            texto_limpo = texto_limpo[:50000] + "\n\n[texto truncado — ver íntegra em: " + link + "]"

        return texto_limpo, "html"

    except Exception as exc:
        return f"[Erro ao buscar íntegra: {exc}]", "fallback"


def _parse_rss_bcb(xml_content: str) -> List[Dict]:
    """Parseia o RSS do BCB e retorna lista de dicionários com campos básicos."""
    items = []
    try:
        root = ET.fromstring(xml_content)
        ns = {"atom": "http://www.w3.org/2005/Atom"}

        # Tentar formato Atom
        entries = root.findall(".//atom:entry", ns)
        if not entries:
            # Tentar formato RSS padrão
            entries = root.findall(".//item")
            for item in entries:
                def gt(tag):
                    el = item.find(tag)
                    return el.text.strip() if el is not None and el.text else ""

                items.append({
                    "id": gt("guid") or gt("link"),
                    "titulo": gt("title"),
                    "ementa": gt("description"),
                    "data_publicacao": gt("pubDate"),
                    "link": gt("link"),
                })
        else:
            for entry in entries:
                def ga(tag, ns=ns):
                    el = entry.find(f"atom:{tag}", ns)
                    return el.text.strip() if el is not None and el.text else ""

                link_el = entry.find("atom:link", ns)
                link = ""
                if link_el is not None:
                    link = link_el.get("href", "") or link_el.text or ""

                items.append({
                    "id": ga("id"),
                    "titulo": ga("title"),
                    "ementa": ga("summary") or ga("content"),
                    "data_publicacao": ga("published") or ga("updated"),
                    "link": link,
                })
    except ET.ParseError:
        # Tentar como JSON (BCB às vezes retorna JSON)
        import json
        try:
            data = json.loads(xml_content)
            if isinstance(data, list):
                items = data
            elif isinstance(data, dict) and "items" in data:
                items = data["items"]
        except Exception:
            pass

    return items


def _normalizar_id(raw_id: str) -> str:
    """Normaliza o ID de um normativo para uso como chave."""
    # Extrair somente dígitos de uma URL ou string de ID
    m = re.search(r"normativos[_/](\d+)", raw_id)
    if m:
        return f"normativos_{m.group(1)}"
    # Fallback: usar hash do ID completo
    return f"normativos_{abs(hash(raw_id)) % 100000}"


def capturar_normativos(
    ano: Optional[int] = None,
    enviados: Optional[Dict] = None,
    config: Optional[Dict] = None,
    buscar_integra: bool = True,
    delay_entre_requisicoes: float = 1.0,
) -> List[Normativo]:
    """
    Captura normativos BCB do RSS e opcionalmente busca a íntegra de cada norma.

    Entradas:
        ano (int): Ano a consultar. Padrão: ano atual em horário de Brasília.
        enviados (dict): Normativos já processados (anti-duplicata). Padrão: {}.
        config (dict): Configuração carregada do config.json. Se None, carrega automaticamente.
        buscar_integra (bool): Se True, busca o texto integral de cada norma. Padrão: True.
        delay_entre_requisicoes (float): Delay em segundos entre requisições à íntegra. Padrão: 1.0.

    Saídas:
        List[Normativo]: Lista de normativos novos (não presentes em `enviados`),
                         com todos os campos incluindo texto_integral.
    """
    cfg = _carregar_config(config)
    if enviados is None:
        enviados = {}
    if ano is None:
        ano = datetime.now(BRASILIA).year

    feed_url = cfg.get("bcb_feed", "").format(ano=ano)
    headers = cfg.get("bcb_headers", {"User-Agent": "Mozilla/5.0"})

    # Buscar RSS
    try:
        resp = requests.get(feed_url, headers=headers, timeout=30, verify=False)
        resp.raise_for_status()
    except Exception as exc:
        raise RuntimeError(f"Erro ao buscar RSS BCB ({feed_url}): {exc}") from exc

    raw_items = _parse_rss_bcb(resp.text)
    novos: List[Normativo] = []

    for raw in raw_items:
        norm_id = _normalizar_id(raw.get("id", ""))

        # Anti-duplicata
        if norm_id in enviados:
            continue

        titulo = raw.get("titulo", "").strip()
        ementa = raw.get("ementa", "").strip()
        link = raw.get("link", "").strip()
        data_pub = raw.get("data_publicacao", "").strip()

        tipo, numero, ano_norma = _extrair_tipo_numero(titulo)

        # Buscar íntegra
        texto_integral = ""
        texto_fonte = "fallback"
        if buscar_integra and link:
            time.sleep(delay_entre_requisicoes)
            texto_integral, texto_fonte = _buscar_integra(link, headers)
            if not texto_integral:
                texto_integral = ementa
                texto_fonte = "ementa"

        norm = Normativo(
            id=norm_id,
            titulo=titulo,
            ementa=ementa,
            data_publicacao=data_pub,
            data_vigencia=None,  # Será extraída do texto pelo módulo reasoning
            link=link,
            tipo=tipo,
            numero=numero,
            ano_norma=ano_norma,
            texto_integral=texto_integral,
            texto_fonte=texto_fonte,
        )
        novos.append(norm)

    return novos
