"""
MUCAMBO Nexus - Autonomous 24/7 Scheduler
Manages non-blocking concurrent scanning, opportunity ingestion, and autonomous trade execution.
"""

import asyncio
import random
from typing import List, Callable, Optional
from core.database import Database
from core.localization import LocalizationEngine
from hunters.base_hunter import BaseHunter
from hunters.domain_hunter import DomainHunter
from hunters.digital_service_hunter import DigitalServiceHunter
from hunters.prediction_hunter import PredictionHunter
from execution.arbitrage_engine import ArbitrageEngine
from execution.fulfillment import FulfillmentEngine
from config import SCAN_INTERVAL_SECONDS, CYCLE_DELAY_SECONDS


class AutonomousScheduler:
    def __init__(self, db: Database, ws_broadcaster: Optional[Callable] = None):
        self.db = db
        self.ws_broadcaster = ws_broadcaster
        self.arbitrage_engine = ArbitrageEngine(db)
        self.fulfillment_engine = FulfillmentEngine(db)
        self.hunters: List[BaseHunter] = [
            DomainHunter(),
            DigitalServiceHunter(),
            PredictionHunter()
        ]
        self.is_running = False
        self._task: Optional[asyncio.Task] = None

        # Sample realistic global buyers for 24/7 market interaction
        self.GLOBAL_BUYERS = [
            {"name": "Nova Capital Partners", "country": "US", "currency": "USD"},
            {"name": "InovaTech Soluções Digitais", "country": "BR", "currency": "BRL"},
            {"name": "Nordic AI Ventures", "country": "SE", "currency": "EUR"},
            {"name": "London Alpha Syndicate", "country": "GB", "currency": "GBP"},
            {"name": "Tokyo Cyber Logistics", "country": "JP", "currency": "JPY"},
            {"name": "Vanguard Digital Assets", "country": "US", "currency": "USD"},
            {"name": "Iberia Media Group", "country": "ES", "currency": "EUR"},
            {"name": "São Paulo Growth Tech", "country": "BR", "currency": "BRL"},
        ]

    def start(self):
        if not self.is_running:
            self.is_running = True
            self._task = asyncio.create_task(self._main_loop())
            self.db.log_event("INFO", "Scheduler", "Autonomous 24/7 Scheduler started successfully.")

    def stop(self):
        self.is_running = False
        if self._task:
            self._task.cancel()
            self._task = None
        self.db.log_event("WARNING", "Scheduler", "Autonomous Scheduler paused.")

    async def _broadcast(self, event_type: str, data: dict):
        if self.ws_broadcaster:
            try:
                await self.ws_broadcaster({"type": event_type, "data": data})
            except Exception:
                pass

    async def _main_loop(self):
        cycle = 0
        while self.is_running:
            cycle += 1
            try:
                # 1. Select a hunter and scan for new opportunities
                hunter = random.choice(self.hunters)
                self.db.log_event("DEBUG", "Hunter", f"Scanning global markets with {hunter.name} (Cycle #{cycle})...")
                
                opportunities = await hunter.scan()
                if opportunities:
                    admitted = self.arbitrage_engine.process_incoming_opportunities(opportunities)
                    if admitted > 0:
                        await self._broadcast("new_opportunities", {
                            "count": admitted,
                            "summary": self.db.get_financial_summary()
                        })

                # No modo real, o sistema NÃO simula compradores fictícios.
                # Ele apenas vasculha o mundo, alimenta a vitrine e aguarda compras reais de clientes via Stripe/Webhooks.
                pass

                # 2. Sleep until next scan cycle
                await asyncio.sleep(random.uniform(SCAN_INTERVAL_SECONDS - 1, SCAN_INTERVAL_SECONDS + 2))

            except asyncio.CancelledError:
                break
            except Exception as e:
                self.db.log_event("ERROR", "Scheduler", f"Loop exception: {str(e)}")
                await asyncio.sleep(CYCLE_DELAY_SECONDS)
