# Property Search System

An automated system to search for multi-unit properties in London and send email notifications.

## Overview

This system searches for properties in London with 2 separate dwellings/units, where each unit has at least 3 bedrooms. It uses the Rightmove property portal and sends daily email summaries of matching properties.

## Features

- 🔍 Searches Rightmove for properties with 6+ bedrooms under £2.5M in London
- 🏠 Detects multi-unit properties using keyword analysis of full descriptions
- 📧 Sends HTML email summaries via SendGrid
- ⏰ Runs automatically via GitHub Actions daily cron job
- 💻 Can also be run locally on your laptop

## Requirements

- Python 3.11+
- SendGrid API key
- Email address for notifications

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/david-mears-2/new-repo.git
cd new-repo
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment Variables

Create a `.env` file in the project root:

```env
SENDGRID_API_KEY=your_sendgrid_api_key_here
NOTIFICATION_EMAIL=your.email@example.com
MAX_PRICE=2500000
```

#### Getting a SendGrid API Key

1. Sign up for a free SendGrid account at https://sendgrid.com/
2. Navigate to Settings → API Keys
3. Create a new API key with "Mail Send" permissions
4. Copy the API key to your `.env` file

## Usage

### Running Locally

```bash
python main.py
```

The script will:
1. Search Rightmove for properties matching the criteria
2. Fetch full descriptions for each property
3. Filter for multi-unit properties based on keywords
4. Send an email summary to your configured email address

### Running via GitHub Actions

The system runs automatically every day at 9:00 AM UTC via GitHub Actions.

#### Setting Up GitHub Actions

1. Go to your repository on GitHub
2. Navigate to Settings → Secrets and variables → Actions
3. Add the following repository secrets:
   - `SENDGRID_API_KEY`: Your SendGrid API key
   - `NOTIFICATION_EMAIL`: Your email address
   - `MAX_PRICE` (optional): Maximum price, defaults to 2500000

#### Manual Trigger

You can also manually trigger the workflow:
1. Go to the Actions tab in your GitHub repository
2. Select "Property Search Daily"
3. Click "Run workflow"

## Configuration

Environment variables can be set in `.env` file (for local) or GitHub Secrets (for Actions):

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `SENDGRID_API_KEY` | Yes | - | SendGrid API key for sending emails |
| `NOTIFICATION_EMAIL` | Yes | - | Email address to receive notifications |
| `MAX_PRICE` | No | 2500000 | Maximum property price in pounds |
| `MIN_BEDROOMS` | No | 6 | Minimum total bedrooms (2 units × 3 beds) |
| `REQUEST_DELAY` | No | 2.0 | Seconds to wait between requests |

## Search Criteria

The system searches for:
- **Location**: All of London
- **Property Type**: Properties with 2 separate dwellings/units
- **Bedrooms**: Minimum 6 total (assuming 2 units × 3 bedrooms each)
- **Price**: Maximum £2,500,000
- **Status**: For sale only

### Multi-Unit Detection Keywords

The system looks for these patterns in property descriptions:
- "two flats" / "2 flats"
- "comprises two" / "arranged as two"
- "two self-contained"
- "split into two" / "converted into two"
- "ground floor flat" AND "first floor flat"
- "freehold block"
- "two separate"
- "dual accommodation"

## Project Structure

```
property-search/
├── main.py                    # Entry point
├── config.py                  # Configuration management
├── scrapers/
│   ├── __init__.py
│   ├── base.py                # Base scraper class
│   └── rightmove.py           # Rightmove scraper implementation
├── filters/
│   ├── __init__.py
│   └── multi_unit.py          # Multi-unit property detection
├── notifications/
│   ├── __init__.py
│   └── email_sender.py        # SendGrid email integration
├── requirements.txt           # Python dependencies
├── .github/
│   └── workflows/
│       └── property_search.yml  # GitHub Actions workflow
└── docs/
    └── DEVELOPMENT_NOTES_FOR_FUTURE_AGENTS_WORKING_ON_THIS_PROJECT.md
```

## Development

See [DEVELOPMENT_NOTES_FOR_FUTURE_AGENTS_WORKING_ON_THIS_PROJECT.md](docs/DEVELOPMENT_NOTES_FOR_FUTURE_AGENTS_WORKING_ON_THIS_PROJECT.md) for detailed development notes, known limitations, and future enhancement plans.

## Troubleshooting

### No email received

- Check spam/junk folder
- Verify `NOTIFICATION_EMAIL` is correct
- Check SendGrid dashboard for delivery status
- Ensure SendGrid API key has "Mail Send" permission

### Search returns no results

- The keyword detection may need refinement
- Try running manually to see log output
- Check that properties matching criteria exist on Rightmove

### Rate limiting / blocked by Rightmove

- Increase `REQUEST_DELAY` in configuration
- Add longer delays between runs
- This tool is for personal use only

## Important Notes

⚠️ **Legal Disclaimer**: This tool is for personal use only. Rightmove's terms of service discourage automated scraping. Use responsibly and respectfully.

🔄 **Iterative Development**: This is the first iteration. Keyword detection will be refined based on real-world results in future updates.

## License

This project uses the MIT-licensed `rightmove-webscraper` library.

## Support

For issues or questions, please open an issue on the GitHub repository.
