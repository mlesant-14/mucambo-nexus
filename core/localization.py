"""
MUCAMBO Nexus - Autonomous Localization & i18n Engine
Dynamically adapts language, currencies, formatting and asset descriptions based on user or client geography.
"""

from typing import Dict, Any, Optional
from config import CURRENCY_RATES

# Currency configuration per locale
LOCALE_CURRENCY_MAP = {
    "pt": {"code": "BRL", "symbol": "R$", "prefix": True},
    "pt-br": {"code": "BRL", "symbol": "R$", "prefix": True},
    "en": {"code": "USD", "symbol": "$", "prefix": True},
    "en-us": {"code": "USD", "symbol": "$", "prefix": True},
    "en-gb": {"code": "GBP", "symbol": "£", "prefix": True},
    "es": {"code": "EUR", "symbol": "€", "prefix": False},
    "es-es": {"code": "EUR", "symbol": "€", "prefix": False},
    "fr": {"code": "EUR", "symbol": "€", "prefix": False},
    "de": {"code": "EUR", "symbol": "€", "prefix": False},
    "ja": {"code": "JPY", "symbol": "¥", "prefix": True},
}

# UI & System Translations
TRANSLATIONS: Dict[str, Dict[str, str]] = {
    "pt": {
        "dashboard_title": "MUCAMBO NEXUS - Sistema Autônomo de Arbitragem 24/7",
        "system_status": "Status Operacional",
        "running_24_7": "ATIVO 24/7 (VARREDURA GLOBAL)",
        "paused": "PAUSADO",
        "total_profit": "Lucro Líquido Acumulado",
        "active_offers": "Ofertas Ativas no Mercado",
        "opportunities_scanned": "Oportunidades Analisadas",
        "win_rate": "Taxa de Sucesso",
        "live_opportunities": "Radar Global de Ativos Intangíveis",
        "market_catalog": "Vitrine Global Just-in-Time (Sem Estoque)",
        "recent_trades": "Livro de Transações & Liquidações",
        "terminal_logs": "Console de Auditoria do Robô",
        "buy_source": "Custo Fonte",
        "sell_price": "Preço Venda",
        "net_profit": "Spread Líquido",
        "margin": "Margem",
        "action_buy": "Comprar Agora (Dispara JIT)",
        "asset_domain": "Nome de Domínio de Alto Valor",
        "asset_service": "Micro-Serviço B2B / Relatório IA",
        "asset_prediction": "Micro-Spread Mercado Preditivo",
        "asset_api": "Arbitragem de Crédito Cloud / Token",
        "sim_mode_badge": "MODO SIMULAÇÃO ATIVO (SEGURO)",
        "live_mode_badge": "MODO LIVE ATIVO",
        "instant_delivery": "Liquidação Instantânea Garantida",
        "risk_free_desc": "Zero capital preso: a compra na fonte só ocorre com o comprador garantido.",
        "order_success": "Pedido liquidado com sucesso! Lucro gerado na carteira.",
        "currency_selector": "Moeda & Região",
        "filter_all": "Todos os Ativos",
    },
    "en": {
        "dashboard_title": "MUCAMBO NEXUS - Autonomous 24/7 Arbitrage Engine",
        "system_status": "Operational Status",
        "running_24_7": "ONLINE 24/7 (GLOBAL SCANNER)",
        "paused": "PAUSED",
        "total_profit": "Total Net Profit",
        "active_offers": "Active Market Listings",
        "opportunities_scanned": "Scanned Opportunities",
        "win_rate": "Success Win Rate",
        "live_opportunities": "Global Intangible Asset Radar",
        "market_catalog": "Just-in-Time Global Catalog (Zero Inventory)",
        "recent_trades": "Settlement & Transaction Ledger",
        "terminal_logs": "Autonomous Robot Audit Log",
        "buy_source": "Source Cost",
        "sell_price": "Listing Price",
        "net_profit": "Net Spread",
        "margin": "Margin",
        "action_buy": "Acquire Now (Triggers JIT)",
        "asset_domain": "High-Value Web Domain",
        "asset_service": "B2B AI Intelligence & Micro-Service",
        "asset_prediction": "Prediction Market Micro-Spread",
        "asset_api": "Cloud Credit & Token Wholesale",
        "sim_mode_badge": "SIMULATION MODE ACTIVE (SAFE)",
        "live_mode_badge": "LIVE PRODUCTION MODE",
        "instant_delivery": "Instant Digital Delivery Guaranteed",
        "risk_free_desc": "Zero stuck capital: source purchase is triggered strictly upon verified buyer order.",
        "order_success": "Order settled successfully! Net profit recorded.",
        "currency_selector": "Currency & Region",
        "filter_all": "All Assets",
    },
    "es": {
        "dashboard_title": "MUCAMBO NEXUS - Motor Autónomo de Arbitraje 24/7",
        "system_status": "Estado Operativo",
        "running_24_7": "ACTIVO 24/7 (ESCANEO GLOBAL)",
        "paused": "PAUSADO",
        "total_profit": "Beneficio Neto Acumulado",
        "active_offers": "Ofertas Activas en Mercado",
        "opportunities_scanned": "Oportunidades Analizadas",
        "win_rate": "Tasa de Éxito",
        "live_opportunities": "Radar Global de Activos Intangibles",
        "market_catalog": "Catálogo Global Just-in-Time (Sin Stock)",
        "recent_trades": "Libro de Transacciones y Liquidaciones",
        "terminal_logs": "Consola de Auditoría del Robot",
        "buy_source": "Coste Fuente",
        "sell_price": "Precio Venta",
        "net_profit": "Spread Neto",
        "margin": "Margen",
        "action_buy": "Comprar Ahora (Dispara JIT)",
        "asset_domain": "Dominio Web de Alto Valor",
        "asset_service": "Micro-Servicio B2B / Informe IA",
        "asset_prediction": "Micro-Spread Mercado Predictivo",
        "asset_api": "Arbitraje Crédito Cloud / Token",
        "sim_mode_badge": "MODO SIMULACIÓN ACTIVO (SEGURO)",
        "live_mode_badge": "MODO LIVE ACTIVO",
        "instant_delivery": "Entrega Digital Instantánea Garantizada",
        "risk_free_desc": "Cero capital inmovilizado: la compra en origen solo se ejecuta con comprador asegurado.",
        "order_success": "¡Orden liquidada con éxito! Ganancia acreditada.",
        "currency_selector": "Moneda y Región",
        "filter_all": "Todos los Activos",
    }
}


class LocalizationEngine:
    """Handles adaptive localization, dynamic translations, and currency conversions."""

    @staticmethod
    def detect_lang(lang_header: Optional[str] = None) -> str:
        """Determines best-matching language code from header or parameter."""
        if not lang_header:
            return "pt"
        norm = lang_header.lower()
        if "pt" in norm or "br" in norm:
            return "pt"
        if "es" in norm:
            return "es"
        if "en" in norm:
            return "en"
        return "en"

    @classmethod
    def get_currency_info(cls, lang: str) -> Dict[str, Any]:
        return LOCALE_CURRENCY_MAP.get(lang.lower(), LOCALE_CURRENCY_MAP["en"])

    @classmethod
    def convert_from_usd(cls, usd_amount: float, target_currency: str) -> float:
        rate = CURRENCY_RATES.get(target_currency.upper(), 1.0)
        return round(usd_amount * rate, 2)

    @classmethod
    def format_money(cls, usd_amount: float, lang: str = "pt") -> str:
        curr = cls.get_currency_info(lang)
        local_val = cls.convert_from_usd(usd_amount, curr["code"])
        
        # Local formatting
        if curr["code"] in ["BRL", "EUR"]:
            val_str = f"{local_val:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        else:
            val_str = f"{local_val:,.2f}"

        if curr["prefix"]:
            return f"{curr['symbol']} {val_str}"
        return f"{val_str} {curr['symbol']}"

    @classmethod
    def translate(cls, key: str, lang: str = "pt") -> str:
        lang_dict = TRANSLATIONS.get(lang, TRANSLATIONS["en"])
        return lang_dict.get(key, TRANSLATIONS["en"].get(key, key))

    @classmethod
    def adapt_asset_text(cls, title: str, description: str, lang: str = "pt") -> Dict[str, str]:
        """Translates or contextualizes asset descriptions for the target region."""
        if lang == "pt":
            return {"title": title, "description": description}
        
        # Automatic quick mappings for titles and concepts
        translated_title = title
        translated_desc = description
        
        if lang == "en":
            translated_title = (
                title.replace("Relatório de", "Market Report for")
                .replace("Auditoria de", "Audit for")
                .replace("Domínio Premium", "Premium Domain")
                .replace("Contrato Preditivo", "Prediction Contract")
            )
            translated_desc = (
                description.replace("Alta demanda comercial", "High commercial demand")
                .replace("Entrega imediata em formato JSON/PDF", "Instant delivery in JSON/PDF format")
                .replace("Autoridade SEO histórica com backlinks ativos", "Historical SEO authority with active backlinks")
                .replace("Discrepância de probabilidade detectada", "Probability discrepancy detected")
            )
        elif lang == "es":
            translated_title = (
                title.replace("Relatório de", "Informe de")
                .replace("Auditoria de", "Auditoría de")
                .replace("Domínio Premium", "Dominio Premium")
                .replace("Contrato Preditivo", "Contrato Predictivo")
            )
            translated_desc = (
                description.replace("Alta demanda comercial", "Alta demanda comercial")
                .replace("Entrega imediata em formato JSON/PDF", "Entrega inmediata en formato JSON/PDF")
                .replace("Autoridade SEO histórica com backlinks ativos", "Autoridad SEO histórica con backlinks activos")
                .replace("Discrepância de probabilidade detectada", "Discrepancia de probabilidad detectada")
            )

        return {"title": translated_title, "description": translated_desc}
