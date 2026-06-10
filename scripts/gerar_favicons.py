#!/usr/bin/env python3
"""gerar_favicons.py — gera os favicons da raiz a partir de assets/favicon.svg.

Build-time apenas (não faz parte do site/runtime). Renderiza o SVG via Playwright em
vários tamanhos PNG e empacota um favicon.ico válido (header ICO + PNG embedado, formato
suportado por Windows Vista+ e todos os browsers modernos).

Uso:  python3 scripts/gerar_favicons.py

Por que tudo isso? O Google, ao decidir qual ícone mostrar no snippet de busca, segue uma
ordem: primeiro tenta `/favicon.ico` na raiz; depois lê o `<link rel="icon">` do HTML;
prefere ICO/PNG a SVG quando há ambiguidade. Servir vários formatos na raiz com paths
absolutos é o caminho mais robusto.
"""
from __future__ import annotations

import pathlib
import struct

from playwright.sync_api import sync_playwright

RAIZ = pathlib.Path(__file__).resolve().parent.parent
SVG = RAIZ / "assets" / "favicon.svg"

# Tamanhos a gerar (nome do arquivo na raiz → lado em px).
TAMANHOS = {
    "favicon-16x16.png":   16,
    "favicon-32x32.png":   32,
    "favicon-48x48.png":   48,    # tamanho recomendado pelo Google p/ search snippets
    "apple-touch-icon.png": 180,  # iOS home screen
    "favicon-192x192.png": 192,   # PWA / Android
    "favicon-512x512.png": 512,   # PWA maior
}

HTML_TPL = """<!doctype html><html><head><meta charset="utf-8">
<style>html,body{margin:0;padding:0;background:transparent;}
.box{width:{size}px;height:{size}px;display:flex;align-items:center;justify-content:center;}
.box svg{width:100%;height:100%;}</style></head>
<body><div class="box">{svg}</div></body></html>"""


def renderizar_png(svg_text: str, lado: int, saida: pathlib.Path) -> None:
    """Renderiza o SVG em PNG quadrado de `lado` px via Chromium headless."""
    html = HTML_TPL.replace("{size}", str(lado)).replace("{svg}", svg_text)
    with sync_playwright() as pw:
        nav = pw.chromium.launch(headless=True)
        pg = nav.new_page(viewport={"width": lado, "height": lado})
        pg.set_content(html, wait_until="networkidle")
        pg.screenshot(path=str(saida), omit_background=True, clip={
            "x": 0, "y": 0, "width": lado, "height": lado,
        })
        nav.close()


def png_para_ico(png_path: pathlib.Path, ico_path: pathlib.Path) -> None:
    """Empacota um PNG dentro de um arquivo .ico válido (1 imagem)."""
    png = png_path.read_bytes()
    # Lê largura/altura do header IHDR do PNG (bytes 16-23).
    w = struct.unpack(">I", png[16:20])[0]
    h = struct.unpack(">I", png[20:24])[0]
    # Header ICONDIR: reserved(2)=0, type(2)=1, count(2)=1
    header = struct.pack("<HHH", 0, 1, 1)
    # ICONDIRENTRY: width(1) height(1) colors(1) reserved(1) planes(2) bitcount(2) size(4) offset(4)
    # Para w/h ≥ 256, especificação manda usar 0.
    entry = struct.pack("<BBBBHHII",
                        0 if w >= 256 else w,
                        0 if h >= 256 else h,
                        0, 0, 1, 32, len(png), 22)  # 22 = 6 (header) + 16 (entry)
    ico_path.write_bytes(header + entry + png)


def main():
    svg_text = SVG.read_text(encoding="utf-8")
    print(f"SVG fonte: {SVG.relative_to(RAIZ)}")
    for nome, lado in TAMANHOS.items():
        saida = RAIZ / nome
        renderizar_png(svg_text, lado, saida)
        print(f"  gerou {nome} ({lado}×{lado})")
    # favicon.ico = empacota o PNG 32x32 (tamanho-padrão histórico).
    png_para_ico(RAIZ / "favicon-32x32.png", RAIZ / "favicon.ico")
    print(f"  gerou favicon.ico (envolvendo o PNG 32×32)")
    print("✅ favicons gerados na raiz.")


if __name__ == "__main__":
    main()
