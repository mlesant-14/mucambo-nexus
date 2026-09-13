"""
MUCAMBO Nexus - Domain Marketplace Syndication Engine
Formats and exports domain catalog for instant listing on global secondary marketplaces (Sedo, Afternic, Dan.com).
"""

import csv
import io
from typing import List, Dict, Any
from core.database import Database


class DomainSyndicator:
    def __init__(self, db: Database):
        self.db = db

    def get_syndication_catalog(self) -> List[Dict[str, Any]]:
        """Extracts all active high-value domain opportunities."""
        catalog = self.db.get_active_catalog(limit=100)
        return [item for item in catalog if item["asset_type"] == "EXPIRED_DOMAIN"]

    def export_afternic_csv(self) -> str:
        """
        Generates standard Afternic / GoDaddy Fast Transfer bulk upload CSV.
        Format: Domain Name, Buy Now Price, Floor Price, Minimum Offer
        """
        domains = self.get_syndication_catalog()
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["Domain Name", "Buy Now Price (USD)", "Floor Price (USD)", "Minimum Offer (USD)"])

        for d in domains:
            buy_now = round(d["target_price_usd"], 2)
            floor = round(d["source_cost_usd"] * 1.5, 2)
            min_offer = round(d["source_cost_usd"] * 1.2, 2)
            writer.writerow([d["identifier"], buy_now, floor, min_offer])

        return output.getvalue()

    def export_sedo_csv(self) -> str:
        """
        Generates standard Sedo Bulk Upload CSV.
        Format: Domain, Currency, Fixed Price, Min Bid, Category
        """
        domains = self.get_syndication_catalog()
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["Domain", "Currency", "Fixed Price", "Minimum Bid", "Category"])

        for d in domains:
            price = round(d["target_price_usd"], 2)
            min_bid = round(price * 0.6, 2)
            writer.writerow([d["identifier"], "USD", price, min_bid, "Technology & Internet"])

        return output.getvalue()

    def get_syndication_status(self) -> Dict[str, Any]:
        domains = self.get_syndication_catalog()
        return {
            "total_domains_ready": len(domains),
            "marketplaces": [
                {"name": "Afternic / GoDaddy Network", "status": "READY_FOR_UPLOAD", "channels": "100+ Registrars"},
                {"name": "Sedo.com Global Marketplace", "status": "READY_FOR_UPLOAD", "channels": "Worldwide Escrow"},
                {"name": "Dan.com (GoDaddy Brands)", "status": "READY_FOR_UPLOAD", "channels": "Fast Checkout"},
            ]
        }
