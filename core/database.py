"""
MUCAMBO Nexus - Database Layer
SQLite persistent storage for opportunities, orders, settlements, and live robot logs.
"""

import sqlite3
import json
from datetime import datetime
from typing import List, Dict, Any, Optional
from config import DB_PATH
from core.models import Opportunity, Order, Transaction, OpportunityStatus, OrderStatus, AssetType


class Database:
    def __init__(self, db_path=DB_PATH):
        self.db_path = str(db_path)
        self._init_db()

    def _get_conn(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self):
        with self._get_conn() as conn:
            cursor = conn.cursor()
            
            # Opportunities Table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS opportunities (
                    id TEXT PRIMARY KEY,
                    asset_type TEXT NOT NULL,
                    identifier TEXT NOT NULL,
                    title TEXT NOT NULL,
                    description TEXT NOT NULL,
                    source_platform TEXT NOT NULL,
                    target_platform TEXT NOT NULL,
                    source_cost_usd REAL NOT NULL,
                    target_price_usd REAL NOT NULL,
                    net_profit_usd REAL NOT NULL,
                    profit_margin_pct REAL NOT NULL,
                    confidence_score REAL NOT NULL,
                    status TEXT NOT NULL,
                    origin_country TEXT NOT NULL,
                    metadata_json TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Orders Table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS orders (
                    id TEXT PRIMARY KEY,
                    opportunity_id TEXT NOT NULL,
                    buyer_name TEXT NOT NULL,
                    buyer_country TEXT NOT NULL,
                    buyer_currency TEXT NOT NULL,
                    paid_amount_local REAL NOT NULL,
                    paid_amount_usd REAL NOT NULL,
                    status TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    completed_at TIMESTAMP
                )
            """)

            # Transactions (Financial Ledger) Table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS transactions (
                    id TEXT PRIMARY KEY,
                    order_id TEXT NOT NULL,
                    opportunity_identifier TEXT NOT NULL,
                    asset_type TEXT NOT NULL,
                    source_cost_usd REAL NOT NULL,
                    sell_price_usd REAL NOT NULL,
                    net_profit_usd REAL NOT NULL,
                    profit_margin_pct REAL NOT NULL,
                    buyer_country TEXT NOT NULL,
                    buyer_currency TEXT NOT NULL,
                    execution_time_ms INTEGER NOT NULL,
                    delivery_proof_hash TEXT DEFAULT '',
                    delivery_status TEXT DEFAULT 'CONFIRMED_DELIVERED',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Audit / System Logs Table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS system_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    level TEXT NOT NULL,
                    source TEXT NOT NULL,
                    message TEXT NOT NULL,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.commit()

    def save_opportunity(self, opp: Opportunity) -> bool:
        with self._get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO opportunities (
                    id, asset_type, identifier, title, description,
                    source_platform, target_platform, source_cost_usd,
                    target_price_usd, net_profit_usd, profit_margin_pct,
                    confidence_score, status, origin_country, metadata_json, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                opp.id, opp.asset_type.value, opp.identifier, opp.title, opp.description,
                opp.source_platform, opp.target_platform, opp.source_cost_usd,
                opp.target_price_usd, opp.net_profit_usd, opp.profit_margin_pct,
                opp.confidence_score, opp.status.value, opp.origin_country,
                json.dumps(opp.metadata), opp.created_at.isoformat()
            ))
            conn.commit()
            return True

    def get_active_catalog(self, limit: int = 50) -> List[Dict[str, Any]]:
        with self._get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM opportunities 
                WHERE status IN ('DETECTED', 'LISTED')
                ORDER BY created_at DESC LIMIT ?
            """, (limit,))
            rows = cursor.fetchall()
            return [dict(row) for row in rows]

    def get_opportunity(self, opp_id: str) -> Optional[Dict[str, Any]]:
        with self._get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM opportunities WHERE id = ?", (opp_id,))
            row = cursor.fetchone()
            return dict(row) if row else None

    def update_opportunity_status(self, opp_id: str, status: OpportunityStatus):
        with self._get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE opportunities SET status = ? WHERE id = ?", (status.value, opp_id))
            conn.commit()

    def save_order(self, order: Order):
        with self._get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO orders (
                    id, opportunity_id, buyer_name, buyer_country, buyer_currency,
                    paid_amount_local, paid_amount_usd, status, created_at, completed_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                order.id, order.opportunity_id, order.buyer_name, order.buyer_country,
                order.buyer_currency, order.paid_amount_local, order.paid_amount_usd,
                order.status.value, order.created_at.isoformat(),
                order.completed_at.isoformat() if order.completed_at else None
            ))
            conn.commit()

    def save_transaction(self, tx: Transaction):
        with self._get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO transactions (
                    id, order_id, opportunity_identifier, asset_type,
                    source_cost_usd, sell_price_usd, net_profit_usd,
                    profit_margin_pct, buyer_country, buyer_currency,
                    execution_time_ms, delivery_proof_hash, delivery_status, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                tx.id, tx.order_id, tx.opportunity_identifier, tx.asset_type.value,
                tx.source_cost_usd, tx.sell_price_usd, tx.net_profit_usd,
                tx.profit_margin_pct, tx.buyer_country, tx.buyer_currency,
                tx.execution_time_ms, tx.delivery_proof_hash, tx.delivery_status, tx.created_at.isoformat()
            ))
            conn.commit()

    def get_transaction(self, tx_id: str) -> Optional[Dict[str, Any]]:
        with self._get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM transactions WHERE id = ?", (tx_id,))
            row = cursor.fetchone()
            return dict(row) if row else None

    def log_event(self, level: str, source: str, message: str):
        with self._get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO system_logs (level, source, message, timestamp)
                VALUES (?, ?, ?, ?)
            """, (level, source, message, datetime.utcnow().isoformat()))
            conn.commit()

    def get_recent_logs(self, limit: int = 30) -> List[Dict[str, Any]]:
        with self._get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM system_logs ORDER BY id DESC LIMIT ?", (limit,))
            return [dict(row) for row in cursor.fetchall()]

    def get_recent_transactions(self, limit: int = 30) -> List[Dict[str, Any]]:
        with self._get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM transactions ORDER BY created_at DESC LIMIT ?", (limit,))
            return [dict(row) for row in cursor.fetchall()]

    def get_financial_summary(self) -> Dict[str, Any]:
        with self._get_conn() as conn:
            cursor = conn.cursor()
            
            # Total Profit and Trades
            cursor.execute("""
                SELECT 
                    COUNT(*) as total_trades,
                    COALESCE(SUM(net_profit_usd), 0.0) as total_profit_usd,
                    COALESCE(SUM(sell_price_usd), 0.0) as total_volume_usd,
                    COALESCE(AVG(profit_margin_pct), 0.0) as avg_margin_pct
                FROM transactions
            """)
            summary = dict(cursor.fetchone())

            # Total Opportunities Scanned
            cursor.execute("SELECT COUNT(*) as total_scanned FROM opportunities")
            summary["total_scanned"] = cursor.fetchone()["total_scanned"]

            # Active Catalog count
            cursor.execute("SELECT COUNT(*) as active_catalog FROM opportunities WHERE status = 'LISTED'")
            summary["active_catalog"] = cursor.fetchone()["active_catalog"]

            return summary
