"""
MUCAMBO Nexus - Domain Models
Data representations for Intangible Assets, Opportunities, Orders, and Financial Settlements.
"""

from enum import Enum
from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field
import uuid


class AssetType(str, Enum):
    EXPIRED_DOMAIN = "EXPIRED_DOMAIN"
    DIGITAL_SERVICE = "DIGITAL_SERVICE"
    PREDICTION_CONTRACT = "PREDICTION_CONTRACT"
    API_ACCESS = "API_ACCESS"


class OpportunityStatus(str, Enum):
    DETECTED = "DETECTED"
    LISTED = "LISTED"
    MATCHED = "MATCHED"
    SETTLED = "SETTLED"
    EXPIRED = "EXPIRED"


class OrderStatus(str, Enum):
    PENDING = "PENDING"
    PURCHASING_SOURCE = "PURCHASING_SOURCE"
    DELIVERING = "DELIVERING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class Opportunity(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4())[:8])
    asset_type: AssetType
    identifier: str  # e.g., "fintech-ai-cloud.io", "B2B-CyberSec-Audit", "US-Econ-Rate-Cut-0.25"
    title: str
    description: str
    source_platform: str  # e.g., "Namecheap Auction", "OpenAI/DeepSeek API", "Polymarket"
    target_platform: str  # e.g., "Global Domain Broker", "Direct Enterprise Client", "Decentralized Settlement"
    source_cost_usd: float
    target_price_usd: float
    net_profit_usd: float
    profit_margin_pct: float
    confidence_score: float  # 0.0 to 1.0
    status: OpportunityStatus = OpportunityStatus.DETECTED
    origin_country: str = "US"
    target_countries: list[str] = ["US", "BR", "EU", "GB"]
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)


class Order(BaseModel):
    id: str = Field(default_factory=lambda: f"ORD-{uuid.uuid4().hex[:8].upper()}")
    opportunity_id: str
    buyer_name: str
    buyer_country: str
    buyer_currency: str
    paid_amount_local: float
    paid_amount_usd: float
    status: OrderStatus = OrderStatus.PENDING
    created_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None


class Transaction(BaseModel):
    id: str = Field(default_factory=lambda: f"TX-{uuid.uuid4().hex[:10].upper()}")
    order_id: str
    opportunity_identifier: str
    asset_type: AssetType
    source_cost_usd: float
    sell_price_usd: float
    net_profit_usd: float
    profit_margin_pct: float
    buyer_country: str
    buyer_currency: str
    execution_time_ms: int
    delivery_proof_hash: str = ""  # SHA-256 cryptographic proof of delivery
    delivery_status: str = "CONFIRMED_DELIVERED"
    created_at: datetime = Field(default_factory=datetime.utcnow)
