"""
MUCAMBO Nexus - Base Hunter Interface
Abstract interface for 24/7 global opportunity scanners.
"""

from abc import ABC, abstractmethod
from typing import List
from core.models import Opportunity


class BaseHunter(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        """Name of the hunter module."""
        pass

    @abstractmethod
    async def scan(self) -> List[Opportunity]:
        """Scans the global web/market and returns viable arbitrage opportunities."""
        pass
