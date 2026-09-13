"""
MUCAMBO Nexus - Arbitrage Decision & Risk Engine
Filters, validates, and admits high-probability opportunities into the live market catalog.
"""

from typing import List, Tuple
from core.models import Opportunity, OpportunityStatus
from core.database import Database
from config import MIN_PROFIT_MARGIN_PERCENT, MIN_NET_PROFIT_USD


class ArbitrageEngine:
    def __init__(self, db: Database):
        self.db = db

    def evaluate_opportunity(self, opp: Opportunity) -> Tuple[bool, str]:
        """Validates opportunity against risk criteria."""
        # 1. Profit Margin threshold
        if opp.profit_margin_pct < MIN_PROFIT_MARGIN_PERCENT:
            return False, f"Margin {opp.profit_margin_pct}% below required {MIN_PROFIT_MARGIN_PERCENT}%"

        # 2. Net Dollar Profit threshold
        if opp.net_profit_usd < MIN_NET_PROFIT_USD:
            return False, f"Net profit ${opp.net_profit_usd} below required minimum ${MIN_NET_PROFIT_USD}"

        # 3. Model Confidence Score
        if opp.confidence_score < 0.75:
            return False, f"Confidence score {opp.confidence_score} below minimum 0.75"

        return True, "Passed all risk and profitability guardrails"

    def process_incoming_opportunities(self, opportunities: List[Opportunity]) -> int:
        admitted = 0
        for opp in opportunities:
            passed, reason = self.evaluate_opportunity(opp)
            if passed:
                opp.status = OpportunityStatus.LISTED
                self.db.save_opportunity(opp)
                self.db.log_event(
                    level="INFO",
                    source="ArbitrageEngine",
                    message=f"LISTED: {opp.title} ({opp.identifier}) | Cost: ${opp.source_cost_usd} -> Sell: ${opp.target_price_usd} | Net: +${opp.net_profit_usd} ({opp.profit_margin_pct}%)"
                )
                admitted += 1
            else:
                self.db.log_event(
                    level="DEBUG",
                    source="ArbitrageEngine",
                    message=f"REJECTED: {opp.identifier} | Reason: {reason}"
                )
        return admitted
