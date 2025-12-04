# Basic Scraping Tutorial

Learn how to build your first web scraper with the Dynamic Web Scraper.

## Objective

Create a scraper that extracts product information from an e-commerce site.

## Prerequisites

- Completed [Getting Started Guide](../guides/getting-started.md)
- Basic Python knowledge

## Step 1: Setup

```python
from scraper.Scraper import Scraper

# Target URL
url = "https://example.com/products"

# Basic configuration
config = {
    "use_proxy": False,
    "max_retries": 3,
    "retry_delay": 2
}
```

## Step 2: Initialize Scraper

```python
# Create scraper instance
scraper = Scraper(url=url, config=config)
```

## Step 3: Fetch Data3

```python
# Run the scraper
result = scraper.fetch_data(
    enable_smart_detection=True,
    enable_enrichment=True
)
```

## Step 4: Access Results

```python
# Get raw data
raw_data = result['raw_data']

# Get enriched data
enriched_data = result.get('enriched_data', [])

# Print first item
if raw_data:
    print(raw_data[0])
```

## Step 5: Save Data

```python
# Save as CSV
scraper.save_data(
    data=raw_data,
    file_name="products.csv",
    format="csv"
)

# Save as JSON
scraper.save_data(
    data=enriched_data,
    file_name="products_enriched.json",
    format="json"
)
```

## Complete Example

```python
from scraper.Scraper import Scraper

def scrape_products(url):
    """Scrape products from a URL."""

    # Configure scraper
    config = {
        "use_proxy": False,
        "max_retries": 3
    }

    # Initialize
    scraper = Scraper(url=url, config=config)

    # Scrape
    result = scraper.fetch_data(
        enable_smart_detection=True,
        enable_enrichment=True
    )

    # Save results
    if result['raw_data']:
        scraper.save_data(
            data=result['raw_data'],
            file_name="products.csv",
            format="csv"
        )
        print(f"Scraped {len(result['raw_data'])} products")

    return result

# Run scraper
if __name__ == "__main__":
    url = "https://example.com/products"
    scrape_products(url)
```

## Next Steps

- [E-commerce Scraping Tutorial](ecommerce-scraping.md) for advanced techniques
- [Configuration Guide](../guides/configuration.md) to customize behavior
- [Anti-Bot Evasion Guide](../guides/anti-bot-evasion.md) for protected sites

## Common Issues

### No Data Extracted
- Check if the site requires JavaScript (use Selenium mode)
- Verify CSS selectors are correct
- Enable debug logging for more details

### Rate Limiting
- Add delays between requests
- Use proxies
- Respect robots.txt

### Blocked Requests
- See [Anti-Bot Evasion Guide](../guides/anti-bot-evasion.md)
