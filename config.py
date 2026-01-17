"""
Configuration module for property search system.
Loads settings from environment variables.
"""
import os
from dotenv import load_dotenv

# Load environment variables from .env file if it exists
load_dotenv()


class Config:
    """Configuration class for property search system."""
    
    # SendGrid configuration
    SENDGRID_API_KEY = os.getenv('SENDGRID_API_KEY')
    NOTIFICATION_EMAIL = os.getenv('NOTIFICATION_EMAIL')
    
    # Search configuration
    MAX_PRICE = int(os.getenv('MAX_PRICE', '2500000'))
    MIN_BEDROOMS = int(os.getenv('MIN_BEDROOMS', '6'))  # 2 units × 3 bedrooms minimum
    LOCATION = os.getenv('LOCATION', 'REGION^87490')  # London
    
    # Scraping configuration
    REQUEST_DELAY = float(os.getenv('REQUEST_DELAY', '2.0'))  # Seconds between requests
    
    @classmethod
    def validate(cls):
        """Validate that required configuration is present."""
        errors = []
        
        if not cls.SENDGRID_API_KEY:
            errors.append("SENDGRID_API_KEY environment variable is required")
        
        if not cls.NOTIFICATION_EMAIL:
            errors.append("NOTIFICATION_EMAIL environment variable is required")
        
        if errors:
            raise ValueError(f"Configuration errors: {', '.join(errors)}")
        
        return True
