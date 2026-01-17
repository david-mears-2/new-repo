"""
Base scraper class for property search.
"""
from abc import ABC, abstractmethod
from typing import Optional
import pandas as pd


class BaseScraper(ABC):
    """Abstract base class for property scrapers."""
    
    @abstractmethod
    def search(self, **kwargs) -> pd.DataFrame:
        """
        Search for properties matching the given criteria.
        
        Returns:
            pd.DataFrame: DataFrame with property information
        """
        pass
    
    @abstractmethod
    def fetch_description(self, url: str) -> Optional[str]:
        """
        Fetch the full description for a property listing.
        
        Args:
            url: URL of the property listing
            
        Returns:
            Optional[str]: Full property description, or None if fetch fails
        """
        pass
