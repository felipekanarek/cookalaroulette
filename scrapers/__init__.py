"""Pacote de adaptadores de scraping do Cook à la Roulette (Fase 2).

Cada módulo `scrapers/<site>.py` implementa o contrato de adaptador
(ver specs/002-scraper-receitas/contracts/adapter-contract.md):

    CHEF: str
    SITE: str
    TECNICAS: list[str]
    def coletar(limite: int) -> list[dict]   # registros {chef, site, titulo, url}

O orquestrador (../orquestrador.py) consome esses adaptadores.
"""
