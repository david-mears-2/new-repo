"""
Base scraper class for property search.
"""
from abc import ABC, abstractmethod
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
    def fetch_description(self, url: str) -> str:
        """
        Fetch the full description for a property listing.
        
        Args:
            url: URL of the property listing
            
        Returns:
            str: Full property description
        """
        pass
