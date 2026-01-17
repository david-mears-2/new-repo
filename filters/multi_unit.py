"""
Multi-unit property detection using keyword matching.
"""
import re
import logging
from typing import Tuple, List, Dict, Any

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MultiUnitFilter:
    """Filter to detect properties with multiple units."""
    
    # Primary indicators of 2+ units
    PRIMARY_KEYWORDS = [
        r'\btwo flats\b',
        r'\b2 flats\b',
        r'\bcomprises two\b',
        r'\barranged as two\b',
        r'\btwo self-contained\b',
        r'\bsplit into two\b',
        r'\bconverted into two\b',
        r'\bfreehold block\b',
        r'\btwo separate\b',
        r'\bdual accommodation\b',
    ]
    
    # Combined indicators (both must be present)
    COMBINED_INDICATORS = [
        (r'\bground floor flat\b', r'\bfirst floor flat\b'),
    ]
    
    # Patterns to avoid (usually insufficient bedrooms)
    EXCLUDE_KEYWORDS = [
        r'\bannexe\b(?!\s+flat)',  # "annexe" alone (not "annexe flat")
        r'\bgranny flat\b(?!\s+and)',  # "granny flat" alone
    ]
    
    def __init__(self):
        # Compile regex patterns for efficiency
        self.primary_patterns = [re.compile(pattern, re.IGNORECASE) for pattern in self.PRIMARY_KEYWORDS]
        self.combined_patterns = [
            (re.compile(p1, re.IGNORECASE), re.compile(p2, re.IGNORECASE))
            for p1, p2 in self.COMBINED_INDICATORS
        ]
        self.exclude_patterns = [re.compile(pattern, re.IGNORECASE) for pattern in self.EXCLUDE_KEYWORDS]
    
    def is_multi_unit(self, description: str) -> Tuple[bool, List[str]]:
        """
        Check if a property description indicates multiple units.
        
        Args:
            description: Property description text
            
        Returns:
            Tuple[bool, List[str]]: (is_multi_unit, matched_patterns)
        """
        if not description:
            return False, []
        
        matched_patterns = []
        
        # Check for exclusion patterns first
        for pattern in self.exclude_patterns:
            if pattern.search(description):
                match_text = pattern.pattern
                logger.debug(f"Excluded due to pattern: {match_text}")
                # Don't immediately return, but note this for consideration
        
        # Check primary keywords
        for pattern in self.primary_patterns:
            if pattern.search(description):
                match_text = pattern.pattern
                matched_patterns.append(match_text)
                logger.debug(f"Matched primary pattern: {match_text}")
        
        # Check combined indicators
        for pattern1, pattern2 in self.combined_patterns:
            if pattern1.search(description) and pattern2.search(description):
                match_text = f"{pattern1.pattern} AND {pattern2.pattern}"
                matched_patterns.append(match_text)
                logger.debug(f"Matched combined pattern: {match_text}")
        
        is_multi_unit = len(matched_patterns) > 0
        
        if is_multi_unit:
            logger.info(f"Property identified as multi-unit. Matched patterns: {matched_patterns}")
        
        return is_multi_unit, matched_patterns
    
    def filter_properties(self, properties: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Filter a list of properties to only include multi-unit properties.
        
        Args:
            properties: List of property dictionaries with 'description' key
            
        Returns:
            List[Dict[str, Any]]: Filtered list of multi-unit properties
        """
        multi_unit_properties = []
        
        for prop in properties:
            description = prop.get('description', '')
            is_multi, patterns = self.is_multi_unit(description)
            
            if is_multi:
                prop['matched_patterns'] = patterns
                multi_unit_properties.append(prop)
        
        logger.info(f"Filtered {len(multi_unit_properties)} multi-unit properties from {len(properties)} total")
        return multi_unit_properties
