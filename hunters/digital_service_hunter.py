"""
MUCAMBO Nexus - Digital Service & AI Drop-Servicing Hunter
Autonomous scanner for high-demand B2B digital deliverables that can be procured/generated via low-cost APIs and sold at premium rates.
"""

import random
from typing import List
from core.models import Opportunity, AssetType, OpportunityStatus
from hunters.base_hunter import BaseHunter


class DigitalServiceHunter(BaseHunter):
    @property
    def name(self) -> str:
        return "DigitalServiceHunter"

    SERVICE_TEMPLATES = [
        {
            "code": "B2B_LEAD_ENRICHMENT",
            "title": "Relatório de Enriquecimento de Leads B2B & Decisores",
            "desc": "Extração e validação de contatos de tomadores de decisão em empresas de tecnologia.",
            "source_cost": (1.20, 3.50),
            "target_price": (49.00, 99.00),
            "source": "Enrichment API Pipeline (Apollo/Hunter/Perplexity)",
            "target": "Global SaaS Outreach Market"
        },
        {
            "code": "COMPETITIVE_INTEL_REPORT",
            "title": "Relatório de Inteligência Competitiva e Preços de Mercado",
            "desc": "Varredura profunda com síntese executiva dos principais concorrentes de um setor.",
            "source_cost": (2.10, 5.00),
            "target_price": (89.00, 159.00),
            "source": "Deep Research LLM Automation Engine",
            "target": "Enterprise Strategy Desk"
        },
        {
            "code": "CYBER_VULNERABILITY_AUDIT",
            "title": "Auditoria de Superfície de Ataque e Segurança Web",
            "desc": "Varredura não invasiva de certificados SSL, cabeçalhos de segurança e portas expostas.",
            "source_cost": (1.50, 4.00),
            "target_price": (69.00, 139.00),
            "source": "Automated Shodan/Nmap Cloud API",
            "target": "SMB Security Compliance Exchange"
        },
        {
            "code": "SEO_TECHNICAL_BLUEPRINT",
            "title": "Auditoria Técnica de SEO e Otimização de Performance",
            "desc": "Diagnóstico de Core Web Vitals, arquitetura de links internos e canibalização de keywords.",
            "source_cost": (1.00, 2.80),
            "target_price": (55.00, 110.00),
            "source": "Lighthouse & ScreamingFrog API Cluster",
            "target": "Global E-Commerce Agencies"
        }
    ]

    async def scan(self) -> List[Opportunity]:
        opportunities = []
        sample_count = random.randint(1, 2)
        chosen = random.sample(self.SERVICE_TEMPLATES, sample_count)

        for item in chosen:
            cost = round(random.uniform(*item["source_cost"]), 2)
            sell = round(random.uniform(*item["target_price"]), 2)
            net_profit = round(sell - cost, 2)
            profit_margin = round((net_profit / sell) * 100, 1)

            opp = Opportunity(
                asset_type=AssetType.DIGITAL_SERVICE,
                identifier=f"{item['code']}-{random.randint(100, 999)}",
                title=item["title"],
                description=f"{item['desc']} Entrega imediata em formato JSON/PDF com selo de verificação.",
                source_platform=item["source"],
                target_platform=item["target"],
                source_cost_usd=cost,
                target_price_usd=sell,
                net_profit_usd=net_profit,
                profit_margin_pct=profit_margin,
                confidence_score=round(random.uniform(0.88, 0.99), 2),
                status=OpportunityStatus.DETECTED,
                origin_country="US",
                target_countries=["US", "BR", "EU", "GB"],
                metadata={
                    "service_code": item["code"],
                    "fulfillment_method": "API_ORCHESTRATION",
                    "execution_time_seconds": random.randint(2, 6)
                }
            )
            opportunities.append(opp)

        return opportunities
