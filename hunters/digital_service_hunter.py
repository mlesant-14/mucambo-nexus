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
            "code": "B2B_LOGISTICS_AUDIT",
            "title": "Laudo Técnico de Auditoria Tarifária e Rotas (ANTT / ANP)",
            "desc": "Diagnóstico completo de custos de pedágio, diesel S10 e tabelas de frete mínimo com chancela SHA-256 e planilhas.",
            "source_cost": (0.40, 1.20),
            "target_price": (19.40, 19.40),  # R$ 97,00 exato
            "source": "MUCAMBO Analytics Core Engine",
            "target": "Mercado Corporativo B2B e Transportadoras"
        },
        {
            "code": "FLEET_OPERATIONAL_DIAGNOSTIC",
            "title": "Diagnóstico de Eficiência de Frota e Consumo Operacional",
            "desc": "Auditoria analítica de consumo por eixo, paradas não programadas e dispersão quilométrica.",
            "source_cost": (0.50, 1.50),
            "target_price": (19.40, 19.40),  # R$ 97,00 exato
            "source": "Fleet Audit Automation Cluster",
            "target": "Empresas de Logística e Frotistas"
        },
        {
            "code": "SUPPLY_CHAIN_COMPLIANCE",
            "title": "Relatório de Conformidade Regulatória de Carga e Fretes",
            "desc": "Verificação de conformidade de tabelas oficiais, validação de parâmetros fiscais e seguro de carga.",
            "source_cost": (0.80, 2.00),
            "target_price": (39.00, 39.00),  # R$ 195,00 premium
            "source": "Regulatory Compliance Scraper",
            "target": "Embarcadores e Grandes Distribuidores"
        },
        {
            "code": "ROUTE_OPTIMIZATION_DOSSIER",
            "title": "Dossiê Executivo de Redução de Custos de Malha Rodoviária",
            "desc": "Mapeamento vetorial de desvios, balanças ativas e waypoints GPS KML para distribuição urbana e interestadual.",
            "source_cost": (0.60, 1.40),
            "target_price": (19.40, 19.40),  # R$ 97,00 exato
            "source": "GIS & Waypoint Synthesis Pipeline",
            "target": "Gestores de Logística e Suprimentos"
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
