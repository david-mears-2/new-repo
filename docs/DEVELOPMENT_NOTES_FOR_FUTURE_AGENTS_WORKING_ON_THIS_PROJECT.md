# Development Notes for Future Agents Working on This Project

## Project Goal

Find properties in London with **2 separate units/dwellings**, where each unit has at least **3 bedrooms**, priced under **£2.5 million**.

This is for investors looking to purchase freehold buildings containing two self-contained flats, not HMOs or properties with annexes/granny flats that typically have insufficient bedroom counts.

## Current State (Iteration 1)

### What's Implemented

✅ **Core Infrastructure**
- Project structure with modular architecture (scrapers, filters, notifications)
- Configuration management via environment variables
- Base scraper class for future extensibility

✅ **Rightmove Integration**
- Uses `rightmove-webscraper` library to fetch initial search results
- Fetches full property descriptions from individual listings
- Multiple extraction methods for description text:
  - PAGE_MODEL JSON parsing
  - data-test attribute extraction
  - Common CSS class fallbacks
- Rate limiting with configurable delays (default 2 seconds)

✅ **Multi-Unit Detection**
- Keyword-based filtering using regex patterns
- Primary indicators: "two flats", "comprises two", "two self-contained", etc.
- Combined indicators: presence of both "ground floor flat" AND "first floor flat"
- Exclusion patterns: standalone "annexe" or "granny flat" mentions

✅ **Email Notifications**
- SendGrid integration for HTML emails
- Formatted property listings with details (address, price, bedrooms, link)
- Display of matched keyword patterns for transparency
- Error notification emails if system fails

✅ **GitHub Actions Automation**
- Daily cron job (9:00 AM UTC)
- Manual workflow dispatch option
- Secrets management for API keys

✅ **Documentation**
- Comprehensive README with setup instructions
- Configuration guide
- Troubleshooting section

## Known Uncertainties and Limitations

### 1. Keyword Detection Effectiveness

⚠️ **This is the biggest unknown**. The keyword patterns are based on common property listing language, but we won't know their effectiveness until we analyze real search results.

**Potential Issues:**
- **False Positives**: Properties that match keywords but aren't actually 2 separate units
- **False Negatives**: Valid multi-unit properties described with different terminology
- **Bedroom Count Per Unit**: The system can't yet determine if EACH unit has 3+ bedrooms (only total bedrooms)

**Example False Positive Scenarios:**
- "Ground floor flat and first floor flat" might describe a house being sold with tenant in place
- "Comprises two reception rooms" might trigger "comprises two" pattern
- "Split into two levels" describes layout, not separate dwellings

**Example False Negative Scenarios:**
- "Duplex with two independent flats" (missing "duplex" keyword)
- "Upper and lower maisonettes" (different terminology)
- "Two apartments" (we search for "flats" but not "apartments")

### 2. Rightmove Search Limitations

- **Maximum 42 pages** per search (1008 listings total) - this is a `rightmove-webscraper` library limitation
- We search for 6+ bedrooms (2 × 3), but this doesn't guarantee distribution (could be 5+1 or even 6+0)
- No API access - relying on web scraping which may break if Rightmove changes their HTML structure

### 3. Description Extraction Challenges

- Rightmove may change their HTML structure at any time
- Some listings may have minimal descriptions
- PAGE_MODEL JSON structure varies and may not always contain descriptions
- Risk of rate limiting if we fetch too many pages too quickly

### 4. Bedroom Count Per Unit

**Critical Gap**: We can see total bedrooms but not the breakdown per unit. A property with 6 bedrooms could be:
- ✅ 3-bed flat + 3-bed flat (what we want)
- ❌ 4-bed flat + 2-bed flat (not what we want)
- ❌ 5-bed flat + 1-bed annex (not what we want)

The only way to determine this is from the description text, which may or may not be explicit.

## Planned Future Work

### PR 2: Analyze and Refine Keyword Detection

**Goal**: Run the current implementation, collect results, and analyze effectiveness.

**Tasks:**
1. Run script manually several times over a week
2. Manually review all results to identify:
   - False positives: Matched keywords but not actually 2 units
   - Patterns in false positives (to add exclusion rules)
   - Better keyword phrases we missed
3. Refine keyword lists based on findings
4. Add logging of ALL keyword matches for analysis
5. Consider adding confidence scores to matches

**Questions to Answer:**
- What percentage of results are valid multi-unit properties?
- What phrases consistently indicate false positives?
- Are there common ways estate agents describe 2-unit properties that we missed?

### PR 3: Enhanced Filtering and Fallback Logic

**Potential Features:**
1. **Bedroom Distribution Detection**
   - Look for explicit mentions: "3 bed first floor" + "3 bed ground floor"
   - Pattern: "X bed [location]" mentioned twice
   
2. **Fallback to Rental Listings**
   - If no sale properties found, search rental market
   - Different URL construction for rentals
   
3. **Conversion Potential Detection**
   - Properties suitable for conversion to 2 units
   - Keywords: "potential to convert", "planning permission granted"
   
4. **Price Per Unit Calculation**
   - Estimate value per flat (total price ÷ 2)
   - Filter based on price per unit thresholds

### PR 4: Additional Property Portals

**Add Zoopla Scraper:**
- Implement `scrapers/zoopla.py` following base scraper interface
- May require different scraping approach (Zoopla structure differs)
- Cross-reference listings across platforms

**Other Portals to Consider:**
- OnTheMarket
- Primelocation

### PR 5: Advanced Features

**Potential Enhancements:**
1. **Database Storage**
   - Store all seen properties to avoid duplicate notifications
   - Track price changes over time
   - Historical analysis of matching properties
   
2. **Map Integration**
   - Generate map with property locations
   - Identify property clusters
   
3. **Enhanced Notifications**
   - Slack integration option
   - Push notifications
   - Weekly summary emails
   
4. **Machine Learning**
   - Train classifier on manually labeled data
   - Improve detection accuracy beyond keyword matching
   - Extract structured data from unstructured descriptions

## Technical Notes

### Rightmove-Webscraper Library

**Important Details:**
- **Library**: `rightmove-webscraper` v1.1.0 on PyPI
- **License**: MIT (community-maintained)
- **Returns**: Pandas DataFrame with: price, type, address, url, agent_url, postcode, number_bedrooms, search_date
- **Limitation**: Only gets summary data from search results page, NOT full descriptions
- **Max Results**: 42 pages × 24 listings per page = 1008 properties maximum per search

**Why We Need Additional Fetching:**
The library only scrapes the search results page, which doesn't include full property descriptions. To detect multi-unit properties, we must:
1. Use library to get initial results (URLs, basic info)
2. Fetch each individual listing page
3. Extract full description from listing page
4. Apply keyword detection to description

### Rightmove HTML Structure

**PAGE_MODEL JSON:**
```javascript
window.PAGE_MODEL = {
    propertyData: {
        text: {
            description: "Full property description here..."
        }
        // ... other fields
    }
};
```

**Alternative Extraction:**
```html
<div data-test="property-description">
    Full property description here...
</div>
```

### Rate Limiting Strategy

**Current Implementation:**
- Default 2-second delay between requests
- Configurable via `REQUEST_DELAY` environment variable
- Applied before each individual listing fetch

**Recommendations:**
- Monitor for HTTP 429 (Too Many Requests) responses
- If blocked, increase delay to 3-5 seconds
- Consider exponential backoff on errors
- Respect robots.txt (though this is for personal use)

### Search URL Construction

**For Sale - London - 6+ Beds - Under £2.5M:**
```
https://www.rightmove.co.uk/property-for-sale/find.html?
  searchType=SALE&
  locationIdentifier=REGION%5E87490&
  minBedrooms=6&
  maxPrice=2500000&
  includeSSTC=false
```

**Key Parameters:**
- `locationIdentifier=REGION%5E87490`: London region code
- `minBedrooms=6`: 2 units × 3 beds minimum
- `maxPrice=2500000`: £2.5 million maximum
- `includeSSTC=false`: Exclude "Sold Subject to Contract" properties

**For Rental (Future):**
Change `searchType=SALE` to `searchType=RENT` and adjust price to weekly rent.

## Testing Approach

### Phase 1: Initial Validation (This PR)

✅ Code compiles without errors
✅ All dependencies install correctly
✅ Configuration validation works
✅ Email sending works (test with dummy data)

### Phase 2: Real-World Testing (PR 2)

1. **Dry Run**: Run locally with email to yourself
2. **Manual Review**: Review all results for accuracy
3. **Data Collection**: Save results for analysis
4. **Iteration**: Adjust keywords based on findings

### Phase 3: Production Validation (PR 3+)

1. **False Positive Rate**: Track % of invalid results
2. **False Negative Rate**: Manual spot-checking of Rightmove for missed properties
3. **A/B Testing**: Try different keyword combinations
4. **User Feedback**: Does it find valuable properties?

## Error Handling Strategy

**Current Implementation:**
- Network errors: Log and continue with next property
- Scraping failures: Send error notification email
- Configuration errors: Fail fast with clear error message
- Individual listing failures: Skip and continue

**Future Improvements:**
- Retry logic with exponential backoff
- Circuit breaker pattern for repeated failures
- Detailed error categorization in notifications
- Graceful degradation (e.g., use cached data if available)

## Code Maintenance Notes

### Adding New Keywords

To add new detection patterns, edit `filters/multi_unit.py`:

```python
PRIMARY_KEYWORDS = [
    r'\btwo flats\b',
    r'\byour new pattern\b',  # Add here
]
```

Use `\b` for word boundaries to avoid partial matches.

### Adding New Scrapers

Follow the interface in `scrapers/base.py`:

```python
class NewScraper(BaseScraper):
    def search(self, **kwargs) -> pd.DataFrame:
        # Implement search
        pass
    
    def fetch_description(self, url: str) -> str:
        # Implement description fetching
        pass
```

### Modifying Email Templates

Edit `notifications/email_sender.py`:
- `_format_properties_email()`: Main results email
- `_format_no_results_email()`: No results email

## Performance Considerations

**Current Bottleneck**: Fetching individual listing descriptions
- With 100 properties and 2-second delay: ~3.5 minutes
- With 1000 properties: ~35 minutes

**Optimization Ideas (Future):**
1. **Parallel Fetching**: Use `asyncio` or `concurrent.futures`
2. **Caching**: Store fetched descriptions to avoid re-fetching
3. **Smarter Filtering**: Apply cheap filters before expensive description fetching
4. **Incremental Processing**: Process in batches with intermediate notifications

## Security Considerations

✅ **API Keys**: Stored as GitHub Secrets, never in code
✅ **Environment Variables**: Loaded from `.env` (gitignored)
✅ **Minimal Permissions**: SendGrid key only needs Mail Send permission

⚠️ **Potential Issues:**
- No input sanitization (not user-facing)
- No rate limiting on GitHub Actions (could exhaust API quotas)

## Monitoring and Observability

**Current State:**
- Console logging with timestamps
- Email notifications on completion
- Error emails on failure
- GitHub Actions artifacts on failure

**Future Improvements:**
- Structured logging (JSON format)
- Metrics: properties found, match rate, execution time
- Alerting on repeated failures
- Dashboard for trends over time

## Questions for Future Development

1. **Should we store historical data?** Would enable price tracking, duplicate detection
2. **How to handle properties that appear in multiple searches?** Dedupe? Track first seen date?
3. **Should we notify on price changes for tracked properties?**
4. **What's the right frequency?** Daily might be too often if market is slow
5. **Should we support multiple search profiles?** Different locations, price ranges, etc.

## Final Notes for Future Agents

**Remember:**
- This is iteration 1 - the foundation
- Real-world testing will drive all future improvements
- Keyword detection WILL need refinement
- User feedback is crucial
- Be respectful with scraping - this is for personal use only

**Before Making Changes:**
1. Read this entire document
2. Review recent email results to understand current performance
3. Check for any new issues reported
4. Test locally before committing

**When Iterating:**
1. Keep changes focused and incremental
2. Update this document with new learnings
3. Add comments explaining non-obvious decisions
4. Consider backward compatibility
5. Test with real data, not just synthetic examples

Good luck! 🏠🔍
