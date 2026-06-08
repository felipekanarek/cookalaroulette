"""Adaptador: GialloZafferano (Itália) — editorial/marca, via listagem de categorias.

giallozafferano.it é um portal ENORME (receitas, vídeos, blog de membros/creators,
magazine, ricerche, ricette-cat). Os sitemaps declarados no robots.txt só trazem
CATEGORIAS (`/ricette-cat/...`), BUSCAS (`/ricerca-ricette/...`), artigos, speciali e
creators — NÃO as receitas individuais. As receitas individuais ficam no subdomínio
`ricette.giallozafferano.it`, em path de segmento único terminando em `.html`
(ex.: https://ricette.giallozafferano.it/Tiramisu.html).

Estratégia: usar as páginas de categoria (`/ricette-cat/<Portata>/`) — acessíveis via
HTTP comum e listadas no sitemap `portate.xml` — como páginas de LISTAGEM, e extrair
delas os links de receita individual. `_e_receita` isola só o subdomínio `ricette.`,
path de UM segmento `.html`, descartando:
  - subcategorias do tipo `ricette.giallozafferano.it/ricette-con-la-Nutella/...` (2+ segmentos)
  - `#anchor` de comentários (fragmentos removidos antes do filtro)
  - vídeos, magazine, blog de creators e o resto do portal (outro path/host).

CHEF é a marca (site editorial). Coleta APENAS a URL — nunca o conteúdo (Princípio III).
Cloudflare está na frente, mas as categorias e as receitas respondem ao cliente HTTP
(200); se algum dia bloquear de vez, o helper de listagem cai para navegador sozinho.
"""
from __future__ import annotations

import re
from urllib.parse import urlparse

from . import base

CHEF = "GialloZafferano"
SITE = "giallozafferano.it"
TECNICAS = ["listagem"]

# Subdomínio onde vivem as receitas individuais.
_HOST_RECEITAS = "ricette.giallozafferano.it"

# Páginas de categoria (portate) usadas como listagem — vêm do sitemap portate.xml.
# Top-level apenas: cada uma traz dezenas de receitas; o helper deduplica entre elas.
_CATEGORIAS = [
    "Antipasti", "Primi", "Secondi-piatti", "Contorni", "Dolci-e-Desserts",
    "Carne", "Pesce", "Insalate", "Piatti-Unici", "Lievitati", "Torte-salate",
    "Verdura", "Vegetariani", "Uova", "Formaggio", "Salse-e-Sughi", "Fritti",
    "Al-forno", "Street-food", "Finger-food", "Sfiziosi", "facili-e-veloci",
]
_LISTAGENS = [f"https://www.giallozafferano.it/ricette-cat/{c}/" for c in _CATEGORIAS]


def _e_receita(url: str) -> bool:
    p = urlparse(url)
    # Receita individual SÓ no subdomínio ricette.
    if p.netloc.lower() != _HOST_RECEITAS:
        return False
    # As listagens trazem variantes com #anchor=gz-comments-anchor da MESMA receita; a
    # versão limpa também aparece, então rejeitamos a com fragmento p/ não duplicar
    # (o helper de listagem deduplica pela href crua, não normaliza o fragmento).
    if p.fragment or "#" in url:
        return False
    # Path de exatamente UM segmento terminando em .html (exclui subcategorias
    # como /ricette-con-la-Nutella/Dolci-e-Desserts/, que têm 2+ segmentos).
    partes = [s for s in p.path.split("/") if s]
    if len(partes) != 1:
        return False
    slug = partes[0]
    if not slug.lower().endswith(".html"):
        return False
    nome = slug[: -len(".html")]
    # Slug com letras/dígitos em kebab-case (evita lixo); precisa de ao menos uma letra.
    return bool(re.match(r"^[A-Za-z0-9]+(?:-[A-Za-z0-9]+)*$", nome)) and bool(
        re.search(r"[A-Za-z]", nome)
    )


def coletar(limite: int) -> list[dict]:
    return base.coletar_por_listagem(_LISTAGENS, CHEF, SITE, _e_receita, limite)
