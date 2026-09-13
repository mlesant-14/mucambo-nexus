"""
MUCAMBO Nexus - B2B Lead Prospector & Autonomous Outreach Engine
Generates targeted corporate leads and personalized outreach emails with direct Stripe checkout links.
"""

import random
from typing import List, Dict, Any
from core.database import Database
from core.localization import LocalizationEngine


class LeadProspector:
    def __init__(self, db: Database):
        self.db = db

        # Target B2B company segments that purchase intelligence reports
        self.PROSPECT_PROFILES = [
            {"company": "Veloce Capital Tech", "role": "Chief Operating Officer", "email": "director@velocecap.io", "country": "US", "lang": "en"},
            {"company": "NexGen Retail Brasil", "role": "Diretor de E-Commerce", "email": "contato@nexgenretail.com.br", "country": "BR", "lang": "pt"},
            {"company": "Apex Cloud Solutions", "role": "Head of Security & Tech", "email": "sec@apexcloud.co", "country": "GB", "lang": "en"},
            {"company": "Inovare Logística Digital", "role": "Head de Inteligência", "email": "operacoes@inovarelog.com.br", "country": "BR", "lang": "pt"},
            {"company": "Hyperion Growth Ventures", "role": "Managing Partner", "email": "partners@hyperionvc.com", "country": "US", "lang": "en"},
        ]

    def generate_outreach_campaign(self, base_url: str = "http://localhost:8000") -> List[Dict[str, Any]]:
        """Generates ready-to-send personalized B2B outreach proposals."""
        catalog = self.db.get_active_catalog(limit=30)
        service_items = [item for item in catalog if item["asset_type"] == "DIGITAL_SERVICE"]

        if not service_items:
            # Fallback sample service if catalog is refreshing
            service_items = [{
                "id": "SVC-AUDIT-01",
                "title": "Auditoria de Segurança e Vulnerabilidades Web",
                "target_price_usd": 79.0,
                "description": "Varredura automatizada com relatório executivo de conformidade e mitigação."
            }]

        campaign = []
        for prospect in self.PROSPECT_PROFILES:
            service = random.choice(service_items)
            lang = prospect["lang"]
            price_usd = service["target_price_usd"]
            formatted_price = LocalizationEngine.format_money(price_usd, lang)

            # Direct checkout link
            checkout_link = f"{base_url}/api/checkout?opp_id={service['id']}"

            if lang == "pt":
                subject = f"Oportunidade e Diagnóstico Estratégico para {prospect['company']}"
                body = (
                    f"Olá, prezado(a) {prospect['role']} da {prospect['company']},\n\n"
                    f"Identificamos uma oportunidade de aprimoramento no seu segmento por meio de nosso sistema de monitoramento contínuo.\n\n"
                    f"Preparamos o '{service['title']}', que detalha métricas competitivas e pontos de ação imediatos para a sua equipe.\n\n"
                    f"O relatório completo com entrega instantânea e certificado de conformidade pode ser liberado no link seguro abaixo:\n"
                    f"👉 Adquirir Relatório ({formatted_price}): {checkout_link}\n\n"
                    f"A entrega é 100% digital e enviada em segundos após a confirmação.\n\n"
                    f"Atenciosamente,\n"
                    f"MUCAMBO Nexus - Inteligência e Ativos Digitais"
                )
            else:
                subject = f"Executive Intelligence & Security Brief for {prospect['company']}"
                body = (
                    f"Dear {prospect['role']} at {prospect['company']},\n\n"
                    f"Our autonomous market radar has flagged critical performance opportunities for companies in your sector.\n\n"
                    f"We have prepared the '{service['title']}', covering competitive benchmark data and verified mitigation steps.\n\n"
                    f"You can instantly unlock the complete verified deliverable via our secure enterprise portal:\n"
                    f"👉 Instant Delivery ({formatted_price}): {checkout_link}\n\n"
                    f"Delivered automatically to your inbox upon settlement.\n\n"
                    f"Best regards,\n"
                    f"MUCAMBO Nexus Global Intelligence"
                )

            campaign.append({
                "company": prospect["company"],
                "role": prospect["role"],
                "email": prospect["email"],
                "country": prospect["country"],
                "subject": subject,
                "body": body,
                "price": formatted_price,
                "checkout_link": checkout_link
            })

        return campaign
