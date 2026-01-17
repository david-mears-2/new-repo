"""
Rightmove scraper using rightmove-webscraper library.
"""
import time
import json
import re
import logging
from typing import Optional
import requests
from bs4 import BeautifulSoup
from rightmove_webscraper import RightmoveData
import pandas as pd
from .base import BaseScraper
from config import Config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RightmoveScraper(BaseScraper):
    """Scraper for Rightmove property listings."""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
    
    def build_search_url(self, max_price: int = None, min_bedrooms: int = None, location: str = None) -> str:
        """
        Build Rightmove search URL.
        
        Args:
            max_price: Maximum price
            min_bedrooms: Minimum number of bedrooms
            location: Location identifier
            
        Returns:
            str: Search URL
        """
        max_price = max_price or Config.MAX_PRICE
        min_bedrooms = min_bedrooms or Config.MIN_BEDROOMS
        location = location or Config.LOCATION
        
        url = (
            f"https://www.rightmove.co.uk/property-for-sale/find.html?"
            f"searchType=SALE&"
            f"locationIdentifier={location}&"
            f"minBedrooms={min_bedrooms}&"
            f"maxPrice={max_price}&"
            f"includeSSTC=false"
        )
        
        logger.info(f"Built search URL: {url}")
        return url
    
    def search(self, **kwargs) -> pd.DataFrame:
        """
        Search for properties using rightmove-webscraper.
        
        Returns:
            pd.DataFrame: DataFrame with property information
        """
        try:
            search_url = self.build_search_url(**kwargs)
            logger.info(f"Searching Rightmove with URL: {search_url}")
            
            # Use rightmove-webscraper to get search results
            rightmove_data = RightmoveData(search_url)
            df = rightmove_data.get_results
            
            logger.info(f"Found {len(df)} properties in search results")
            return df
            
        except Exception as e:
            logger.error(f"Error searching Rightmove: {e}")
            raise
    
    def fetch_description(self, url: str) -> Optional[str]:
        """
        Fetch the full description from a Rightmove property listing.
        
        Args:
            url: URL of the property listing
            
        Returns:
            str: Full property description, or None if fetch fails
        """
        try:
            # Add delay to avoid rate limiting
            time.sleep(Config.REQUEST_DELAY)
            
            logger.info(f"Fetching description from: {url}")
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Method 1: Try to extract from PAGE_MODEL JSON
            description = self._extract_from_page_model(response.text)
            
            # Method 2: Try to extract from data-test attribute
            if not description:
                description = self._extract_from_data_test(soup)
            
            # Method 3: Try to extract from common description classes
            if not description:
                description = self._extract_from_common_classes(soup)
            
            if description:
                logger.info(f"Successfully fetched description ({len(description)} chars)")
                return description
            else:
                logger.warning(f"Could not extract description from {url}")
                return None
                
        except Exception as e:
            logger.error(f"Error fetching description from {url}: {e}")
            return None
    
    def _extract_from_page_model(self, html_text: str) -> Optional[str]:
        """Extract description from PAGE_MODEL JSON in script tag."""
        try:
            # Find PAGE_MODEL JSON in script tag
            match = re.search(r'window\.PAGE_MODEL\s*=\s*({.*?});?\s*</script>', html_text, re.DOTALL)
            if match:
                page_model = json.loads(match.group(1))
                
                # Navigate through the JSON structure to find description
                # Common paths: propertyData.text.description or similar
                if 'propertyData' in page_model:
                    prop_data = page_model['propertyData']
                    if 'text' in prop_data and 'description' in prop_data['text']:
                        return prop_data['text']['description']
                
        except (json.JSONDecodeError, KeyError) as e:
            logger.debug(f"Could not extract from PAGE_MODEL: {e}")
        
        return None
    
    def _extract_from_data_test(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract description from data-test attribute."""
        try:
            desc_element = soup.find(attrs={'data-test': 'property-description'})
            if desc_element:
                return desc_element.get_text(strip=True)
        except Exception as e:
            logger.debug(f"Could not extract from data-test: {e}")
        
        return None
    
    def _extract_from_common_classes(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract description from common class names."""
        try:
            # Try common class names for descriptions
            class_names = [
                'property-description',
                '_2RnXSVJcWbWvdA5aWBSqI8',  # Rightmove sometimes uses obfuscated class names
                'propertyDescription'
            ]
            
            for class_name in class_names:
                element = soup.find(class_=class_name)
                if element:
                    return element.get_text(strip=True)
                    
        except Exception as e:
            logger.debug(f"Could not extract from common classes: {e}")
        
        return None
