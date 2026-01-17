"""
Email notification sender using SendGrid.
"""
import logging
from typing import List, Dict, Any
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Email, To, Content
from config import Config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EmailSender:
    """Send email notifications using SendGrid."""
    
    def __init__(self):
        if not Config.SENDGRID_API_KEY:
            raise ValueError("SENDGRID_API_KEY is required")
        
        self.client = SendGridAPIClient(Config.SENDGRID_API_KEY)
        self.from_email = Email("noreply@propertysearch.com")
        self.to_email = To(Config.NOTIFICATION_EMAIL)
    
    def send_property_results(self, properties: List[Dict[str, Any]]) -> bool:
        """
        Send email with property search results.
        
        Args:
            properties: List of property dictionaries
            
        Returns:
            bool: True if email sent successfully
        """
        try:
            if not properties:
                logger.info("No properties to send")
                subject = "Property Search Results - No Properties Found"
                html_content = self._format_no_results_email()
            else:
                subject = f"Property Search Results - {len(properties)} Properties Found"
                html_content = self._format_properties_email(properties)
            
            message = Mail(
                from_email=self.from_email,
                to_emails=self.to_email,
                subject=subject,
                html_content=html_content
            )
            
            response = self.client.send(message)
            
            if response.status_code in [200, 202]:
                logger.info(f"Email sent successfully to {Config.NOTIFICATION_EMAIL}")
                return True
            else:
                logger.error(f"Failed to send email. Status code: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Error sending email: {e}")
            return False
    
    def send_error_notification(self, error_message: str) -> bool:
        """
        Send error notification email.
        
        Args:
            error_message: Error message to send
            
        Returns:
            bool: True if email sent successfully
        """
        try:
            subject = "Property Search Error"
            html_content = f"""
            <html>
                <body>
                    <h2>Property Search Error</h2>
                    <p>An error occurred during the property search:</p>
                    <pre style="background-color: #f5f5f5; padding: 10px; border-radius: 5px;">
{error_message}
                    </pre>
                </body>
            </html>
            """
            
            message = Mail(
                from_email=self.from_email,
                to_emails=self.to_email,
                subject=subject,
                html_content=html_content
            )
            
            response = self.client.send(message)
            
            if response.status_code in [200, 202]:
                logger.info(f"Error notification sent successfully")
                return True
            else:
                logger.error(f"Failed to send error notification. Status code: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Error sending error notification: {e}")
            return False
    
    def _format_no_results_email(self) -> str:
        """Format email for no results."""
        return """
        <html>
            <body>
                <h2>Property Search Results</h2>
                <p>No properties matching your criteria were found in this search.</p>
                <p><strong>Search Criteria:</strong></p>
                <ul>
                    <li>Location: London</li>
                    <li>Minimum Bedrooms: 6 (2 units × 3 bedrooms)</li>
                    <li>Maximum Price: £2,500,000</li>
                    <li>Property Type: Multi-unit (2 separate dwellings)</li>
                </ul>
            </body>
        </html>
        """
    
    def _format_properties_email(self, properties: List[Dict[str, Any]]) -> str:
        """
        Format email with property listings.
        
        Args:
            properties: List of property dictionaries
            
        Returns:
            str: HTML formatted email content
        """
        html_parts = [
            """
            <html>
                <head>
                    <style>
                        body { font-family: Arial, sans-serif; }
                        .property { 
                            border: 1px solid #ddd; 
                            margin: 20px 0; 
                            padding: 15px; 
                            border-radius: 5px;
                            background-color: #f9f9f9;
                        }
                        .property h3 { 
                            margin-top: 0; 
                            color: #2c3e50;
                        }
                        .property-detail { 
                            margin: 5px 0; 
                        }
                        .price { 
                            font-size: 1.2em; 
                            font-weight: bold; 
                            color: #27ae60;
                        }
                        .link { 
                            display: inline-block; 
                            margin-top: 10px;
                            padding: 8px 15px;
                            background-color: #3498db;
                            color: white;
                            text-decoration: none;
                            border-radius: 3px;
                        }
                        .matched-patterns {
                            background-color: #fff3cd;
                            padding: 10px;
                            margin-top: 10px;
                            border-radius: 3px;
                            border-left: 4px solid #ffc107;
                        }
                    </style>
                </head>
                <body>
                    <h2>Property Search Results</h2>
                    <p>Found <strong>""" + str(len(properties)) + """</strong> properties matching your criteria:</p>
            """
        ]
        
        for i, prop in enumerate(properties, 1):
            address = prop.get('address', 'Unknown Address')
            price = prop.get('price', 'Price not available')
            bedrooms = prop.get('number_bedrooms', 'N/A')
            url = prop.get('url', '#')
            matched_patterns = prop.get('matched_patterns', [])
            
            property_html = f"""
                <div class="property">
                    <h3>Property {i}: {address}</h3>
                    <div class="property-detail price">{price}</div>
                    <div class="property-detail"><strong>Total Bedrooms:</strong> {bedrooms}</div>
                    <div class="property-detail"><strong>Location:</strong> {address}</div>
                    <a href="{url}" class="link" target="_blank">View Listing</a>
            """
            
            if matched_patterns:
                patterns_text = '<br>'.join([f"• {pattern}" for pattern in matched_patterns])
                property_html += f"""
                    <div class="matched-patterns">
                        <strong>Matched Keywords:</strong><br>
                        {patterns_text}
                    </div>
                """
            
            property_html += """
                </div>
            """
            
            html_parts.append(property_html)
        
        html_parts.append("""
                </body>
            </html>
        """)
        
        return ''.join(html_parts)
