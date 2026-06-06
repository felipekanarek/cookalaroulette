#!/usr/bin/env python3
"""gerar_og.py — gera assets/og-image.png (1200×630) para o preview social.

Build-time apenas (não faz parte do site/runtime). Renderiza um HTML on-brand
(COOK À LA ROULETTE laranja sobre off-white, fonte Anton) via Playwright e tira um screenshot.

Uso:  python3 scripts/gerar_og.py
"""
from __future__ import annotations

import pathlib

from playwright.sync_api import sync_playwright

HTML = """<!doctype html><html lang="pt-BR"><head><meta charset="utf-8">
<link href="https://fonts.googleapis.com/css2?family=Anton&display=swap" rel="stylesheet">
<style>
  html, body { margin: 0; width: 1200px; height: 630px; }
  .wrap {
    width: 1200px; height: 630px; box-sizing: border-box; padding: 80px;
    background: #faf7f2; color: #e85d29;
    display: flex; flex-direction: column; justify-content: center; align-items: center;
    font-family: "Anton", Georgia, serif; text-transform: uppercase;
    line-height: 0.92; letter-spacing: 0.02em;
  }
  .l { font-size: 156px; }
</style></head><body>
  <div class="wrap"><div class="l">COOK</div><div class="l">À LA</div><div class="l">ROULETTE</div></div>
</body></html>"""

SAIDA = pathlib.Path(__file__).resolve().parent.parent / "assets" / "og-image.png"


def main():
    with sync_playwright() as pw:
        nav = pw.chromium.launch(headless=True)
        pg = nav.new_page(viewport={"width": 1200, "height": 630})
        pg.set_content(HTML, wait_until="networkidle")
        pg.wait_for_timeout(800)  # garante a fonte carregada antes do screenshot
        pg.screenshot(path=str(SAIDA))
        nav.close()
    print("gerado:", SAIDA)


if __name__ == "__main__":
    main()
