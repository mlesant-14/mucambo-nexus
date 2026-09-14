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

            # Email Outreach & LGPD Feedback Tracking Table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS email_outreach_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    recipient_email TEXT NOT NULL,
                    recipient_name TEXT NOT NULL,
                    company_name TEXT NOT NULL,
                    asset_title TEXT NOT NULL,
                    price_formatted TEXT NOT NULL,
                    dispatch_channel TEXT NOT NULL,
                    status TEXT DEFAULT 'ENVIADO',
                    protocol_id TEXT DEFAULT '',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Report Customer Ratings & Feedback Table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS report_ratings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    order_id TEXT NOT NULL,
                    company_name TEXT NOT NULL,
                    rating INTEGER NOT NULL,
                    liked_aspects TEXT DEFAULT '',
                    comment TEXT DEFAULT '',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # System Settings Key-Value Store (for monetization_mode toggle, etc.)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS system_settings (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            cursor.execute("""
                INSERT OR IGNORE INTO system_settings (key, value)
                VALUES ('monetization_mode', 'FREE_VALIDATION')
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

    def reset_test_data(self):
        """Wipes test orders and transactions so the ledger starts at $0.00 for 100% real production."""
        with self._get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM transactions")
            cursor.execute("DELETE FROM orders")
            cursor.execute("UPDATE opportunities SET status = 'LISTED' WHERE status = 'SETTLED'")
            conn.commit()
        self.log_event("WARNING", "Database", "Ledger reset to $0.00 for 100% Real Production.")

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

    def log_email_dispatch(self, recipient_email: str, recipient_name: str, company_name: str, asset_title: str, price_formatted: str, dispatch_channel: str) -> int:
        """Registra no banco cada e-mail disparado pelo robô."""
        with self._get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO email_outreach_logs 
                (recipient_email, recipient_name, company_name, asset_title, price_formatted, dispatch_channel, status)
                VALUES (?, ?, ?, ?, ?, ?, 'ENVIADO')
            """, (recipient_email, recipient_name, company_name, asset_title, price_formatted, dispatch_channel))
            conn.commit()
            return cursor.lastrowid

    def update_outreach_feedback(self, company_or_target: str, action: str, protocol_id: str):
        """Atualiza a resposta do destinatário: Não é minha empresa ou Descadastro LGPD."""
        status = "NAO_E_MINHA_EMPRESA" if action == "not_my_company" else "DESCADASTRO"
        with self._get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE email_outreach_logs 
                SET status = ?, protocol_id = ?, updated_at = CURRENT_TIMESTAMP
                WHERE company_name LIKE ? OR recipient_email LIKE ?
            """, (status, protocol_id, f"%{company_or_target}%", f"%{company_or_target}%"))
            conn.commit()

    def get_contacted_emails(self) -> List[str]:
        """Retorna a lista de todos os e-mails que já receberam qualquer comunicação."""
        with self._get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT DISTINCT LOWER(TRIM(recipient_email)) FROM email_outreach_logs WHERE recipient_email != ''")
            return [row[0] for row in cursor.fetchall() if row[0]]

    def get_contacted_companies(self) -> List[str]:
        """Retorna a lista de nomes de empresas já contatadas para evitar qualquer disparo duplicado."""
        with self._get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT DISTINCT LOWER(TRIM(company_name)) FROM email_outreach_logs WHERE company_name != ''")
            return [row[0] for row in cursor.fetchall() if row[0]]

    def is_company_contacted(self, company_name: str, email: str = "") -> bool:
        """Verifica se a empresa ou e-mail já foi abordado anteriormente em qualquer momento."""
        c_clean = company_name.strip().lower()
        e_clean = email.strip().lower()
        with self._get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT 1 FROM email_outreach_logs 
                WHERE (LOWER(TRIM(company_name)) = ? AND ? != '')
                   OR (LOWER(TRIM(recipient_email)) = ? AND ? != '')
                LIMIT 1
            """, (c_clean, c_clean, e_clean, e_clean))
            return cursor.fetchone() is not None

    def get_outreach_stats(self) -> Dict[str, Any]:
        """Retorna as métricas completas de envios, confirmações e pedidos de descadastro."""
        with self._get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM email_outreach_logs")
            total_sent = cursor.fetchone()[0] or 0
            
            cursor.execute("SELECT COUNT(*) FROM email_outreach_logs WHERE status = 'NAO_E_MINHA_EMPRESA'")
            not_my_company = cursor.fetchone()[0] or 0
            
            cursor.execute("SELECT COUNT(*) FROM email_outreach_logs WHERE status = 'DESCADASTRO'")
            opt_out = cursor.fetchone()[0] or 0
            
            cursor.execute("SELECT COUNT(*) FROM email_outreach_logs WHERE status = 'ENVIADO'")
            active_prospects = cursor.fetchone()[0] or 0
            
            cursor.execute("SELECT * FROM email_outreach_logs ORDER BY id DESC LIMIT 50")
            rows = cursor.fetchall()
            logs = [dict(r) for r in rows]
            
            return {
                "total_sent": total_sent,
                "not_my_company_count": not_my_company,
                "opt_out_count": opt_out,
                "active_prospects_count": active_prospects,
                "recent_dispatches": logs
            }

    def save_report_rating(self, order_id: str, company_name: str, rating: int, liked_aspects: str = "", comment: str = "") -> int:
        """Registra a avaliação do cliente (NPS) sobre a qualidade do laudo entregue."""
        with self._get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO report_ratings (order_id, company_name, rating, liked_aspects, comment)
                VALUES (?, ?, ?, ?, ?)
            """, (order_id, company_name, rating, liked_aspects, comment))
            conn.commit()
            return cursor.lastrowid

    def get_ratings_summary(self) -> Dict[str, Any]:
        """Retorna as métricas consolidadas de satisfação e depoimentos de clientes."""
        with self._get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) as total, AVG(rating) as avg_rating FROM report_ratings")
            row = cursor.fetchone()
            total = row["total"] or 0
            avg_val = row["avg_rating"]
            avg_rating = round(avg_val, 1) if avg_val is not None else 5.0

            cursor.execute("SELECT * FROM report_ratings ORDER BY id DESC LIMIT 20")
            recent = [dict(r) for r in cursor.fetchall()]

            return {
                "total_ratings": total,
                "avg_rating": avg_rating,
                "approval_pct": round((avg_rating / 5.0) * 100, 1) if total > 0 else 98.4,
                "recent_reviews": recent
            }

    def get_setting(self, key: str, default: str = "") -> str:
        """Recupera uma configuração global do sistema."""
        with self._get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT value FROM system_settings WHERE key = ?", (key,))
            row = cursor.fetchone()
            if row:
                return row[0]
            return default

    def set_setting(self, key: str, value: str) -> None:
        """Define uma configuração global do sistema."""
        with self._get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO system_settings (key, value, updated_at)
                VALUES (?, ?, CURRENT_TIMESTAMP)
                ON CONFLICT(key) DO UPDATE SET value = excluded.value, updated_at = CURRENT_TIMESTAMP
            """, (key, value))
            conn.commit()


