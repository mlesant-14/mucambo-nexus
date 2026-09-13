"""
MUCAMBO Nexus - Autonomous Intangible Asset Arbitrage Engine
Configuration & Global Parameters
"""

import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

DB_PATH = BASE_DIR / "mucambo_arbitrage.db"

# System Operation Modes
# Set SIMULATION_MODE=false in .env to switch to real production execution
SIMULATION_MODE = os.getenv("SIMULATION_MODE", "true").lower() in ["true", "1", "yes"]
AUTO_EXECUTE_HIGH_CONFIDENCE = True  # Automatically execute when spread exceeds threshold
MIN_PROFIT_MARGIN_PERCENT = float(os.getenv("MIN_PROFIT_MARGIN_PERCENT", "30.0"))
MIN_NET_PROFIT_USD = float(os.getenv("MIN_NET_PROFIT_USD", "15.0"))

# Currency Exchange Rates (Dynamic reference to USD)
CURRENCY_RATES = {
    "USD": 1.0,
    "BRL": 5.65,
    "EUR": 0.92,
    "GBP": 0.78,
    "JPY": 152.0,
}

# Scan Intervals (in seconds)
SCAN_INTERVAL_SECONDS = 6
CYCLE_DELAY_SECONDS = 4

# Supported Asset Categories (All Intangible)
ASSET_TYPES = {
    "EXPIRED_DOMAIN": "Expired & High-Value Domain Names",
    "DIGITAL_SERVICE": "Automated B2B Digital Reports & AI Micro-Services",
    "PREDICTION_CONTRACT": "Global Prediction Market & Micro-Spreads",
    "API_ACCESS": "Wholesale API Token & Cloud Credit Arbitrage",
}

# Server Config
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", "8000"))
