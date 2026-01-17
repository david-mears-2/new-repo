"""
Property Search System - Main Entry Point

This script searches for multi-unit properties in London meeting specific criteria
and sends email summaries of the results.
"""
import logging
import sys
import traceback
from scrapers.rightmove import RightmoveScraper
from filters.multi_unit import MultiUnitFilter
from notifications.email_sender import EmailSender
from config import Config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    """Main entry point for property search."""
    try:
        # Validate configuration
        logger.info("Starting property search system...")
        Config.validate()
        logger.info("Configuration validated successfully")
        
        # Initialize components
        scraper = RightmoveScraper()
        multi_unit_filter = MultiUnitFilter()
        email_sender = EmailSender()
        
        # Search for properties
        logger.info("Searching for properties on Rightmove...")
        search_results = scraper.search()
        
        if search_results.empty:
            logger.info("No properties found in search results")
            email_sender.send_property_results([])
            return 0
        
        logger.info(f"Found {len(search_results)} properties in initial search")
        
        # Fetch descriptions and filter for multi-unit properties
        properties_with_descriptions = []
        
        for idx, row in search_results.iterrows():
            url = row.get('url', '')
            
            if not url:
                logger.warning(f"Skipping property at index {idx} - no URL")
                continue
            
            # Fetch full description
            description = scraper.fetch_description(url)
            
            if description:
                property_data = {
                    'address': row.get('address', 'Unknown'),
                    'price': row.get('price', 'N/A'),
                    'number_bedrooms': row.get('number_bedrooms', 'N/A'),
                    'url': url,
                    'description': description,
                    'postcode': row.get('postcode', ''),
                    'type': row.get('type', ''),
                }
                properties_with_descriptions.append(property_data)
            else:
                logger.warning(f"Could not fetch description for {url}")
        
        logger.info(f"Successfully fetched descriptions for {len(properties_with_descriptions)} properties")
        
        # Filter for multi-unit properties
        multi_unit_properties = multi_unit_filter.filter_properties(properties_with_descriptions)
        
        logger.info(f"Found {len(multi_unit_properties)} multi-unit properties")
        
        # Send email notification
        success = email_sender.send_property_results(multi_unit_properties)
        
        if success:
            logger.info("Email notification sent successfully")
            return 0
        else:
            logger.error("Failed to send email notification")
            return 1
            
    except Exception as e:
        error_message = f"Error in property search: {str(e)}\n{traceback.format_exc()}"
        logger.error(error_message)
        
        # Try to send error notification
        try:
            email_sender = EmailSender()
            email_sender.send_error_notification(error_message)
        except Exception as email_error:
            logger.error(f"Failed to send error notification: {email_error}")
        
        return 1


if __name__ == "__main__":
    sys.exit(main())
