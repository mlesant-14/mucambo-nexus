"""
MUCAMBO Nexus - Automated Verification Suite
Tests domain valuation, risk filters, i18n adaptation, and JIT fulfillment.
"""

import sys
import os
import asyncio
from pathlib import Path

# Add project root to sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from core.database import Database
from core.models import Opportunity, AssetType, OpportunityStatus
from core.localization import LocalizationEngine
from execution.arbitrage_engine import ArbitrageEngine
from execution.fulfillment import FulfillmentEngine
from hunters.domain_hunter import DomainHunter
from hunters.digital_service_hunter import DigitalServiceHunter


async def run_tests():
    print("[*] Running MUCAMBO Nexus Verification Suite...")
    test_db_path = BASE_DIR / "test_verification.db"
    if test_db_path.exists():
        test_db_path.unlink()

    db = Database(db_path=test_db_path)
    arbitrage_engine = ArbitrageEngine(db)
    fulfillment_engine = FulfillmentEngine(db)

    # 1. Test Localization & Currencies
    print("[1/4] Testing i18n and Currency Adaptation...")
    usd_price = 100.0
    brl_price = LocalizationEngine.convert_from_usd(usd_price, "BRL")
    assert brl_price > 500.0, f"Expected BRL price > 500, got {brl_price}"
    
    brl_formatted = LocalizationEngine.format_money(usd_price, "pt")
    assert "R$" in brl_formatted, f"Expected R$ in formatted string, got {brl_formatted}"
    
    eur_formatted = LocalizationEngine.format_money(usd_price, "es")
    assert "€" in eur_formatted, f"Expected € in formatted string, got {eur_formatted}"
    print("    -> i18n & Currency Adaptation: PASSED")

    # 2. Test Hunters
    print("[2/4] Testing Autonomous Hunters...")
    domain_hunter = DomainHunter()
    opportunities = await domain_hunter.scan()
    assert len(opportunities) > 0, "Domain hunter produced no opportunities"
    sample_opp = opportunities[0]
    assert sample_opp.asset_type == AssetType.EXPIRED_DOMAIN
    assert sample_opp.net_profit_usd > 0
    print(f"    -> Scanned sample: {sample_opp.identifier} (Net: ${sample_opp.net_profit_usd:.2f})")

    service_hunter = DigitalServiceHunter()
    service_opps = await service_hunter.scan()
    assert len(service_opps) > 0, "Service hunter produced no opportunities"
    print("    -> Autonomous Hunters: PASSED")

    # 3. Test Risk Filter & Arbitrage Engine
    print("[3/4] Testing Arbitrage Risk Filter...")
    admitted = arbitrage_engine.process_incoming_opportunities(opportunities)
    assert admitted > 0, "No opportunities passed arbitrage filter"
    catalog = db.get_active_catalog()
    assert len(catalog) >= admitted, "Catalog does not match admitted count"
    print(f"    -> Successfully admitted {admitted} opportunities into catalog.")
    print("    -> Arbitrage Risk Engine: PASSED")

    # 4. Test Just-in-Time Order Fulfillment
    print("[4/4] Testing Zero-Inventory JIT Fulfillment...")
    target_item = catalog[0]
    trade_result = await fulfillment_engine.execute_trade(
        opportunity_id=target_item["id"],
        buyer_name="Alpha Global Fund",
        buyer_country="BR",
        buyer_currency="BRL"
    )
    assert trade_result["success"] is True, "Trade execution failed"
    assert trade_result["net_profit_usd"] > 0, "Profit must be positive"
    
    summary = db.get_financial_summary()
    assert summary["total_trades"] == 1
    assert summary["total_profit_usd"] > 0
    print(f"    -> Trade executed: Order {trade_result['order_id']} | Profit: +${trade_result['net_profit_usd']:.2f}")
    print(f"    -> Latency: {trade_result['execution_ms']}ms")
    print("    -> JIT Fulfillment Engine: PASSED")

    # Clean up test database
    try:
        if test_db_path.exists():
            test_db_path.unlink()
    except Exception:
        pass

    print("\n=======================================================")
    print(" >>> ALL VERIFICATION TESTS PASSED SUCCESSFULLY! <<<")
    print("=======================================================\n")


if __name__ == "__main__":
    asyncio.run(run_tests())
