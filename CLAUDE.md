# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a web scraper for Zonaprop (Argentine real estate website). It extracts property listings (apartments for rent/sale) and saves them to CSV files for analysis. The scraper uses cloudscraper to bypass anti-bot protections and BeautifulSoup for HTML parsing.

## Commands

### Install Dependencies
```bash
pip install -r requirements.txt
```

### Run Scraper
```bash
python zonaprop-scraping.py <url>
```
Default URL if none provided: https://www.zonaprop.com.ar/departamentos-alquiler.html

Output: CSV file saved to `data/` directory with timestamp.

### Run Tests
```bash
# Run all tests
pytest

# Run specific test file
pytest test/test_scraper.py

# Run with verbose output
pytest -v
```

## Architecture

### Core Components

**Browser** (`src/browser.py`): Wrapper around cloudscraper to handle HTTP requests and bypass Cloudflare/bot detection.

**Scraper** (`src/scraper.py`): Main scraping logic.
- `scrap_website()`: Entry point that orchestrates pagination through all results
- `scrap_page(page_number)`: Scrapes a single page, extracts all property postings
- `parse_estate(estate_post)`: Parses individual property card HTML into structured dict
- `get_estates_quantity()`: Determines total number of properties from first page H1 tag
- URL pattern: Base URL + "-pagina-N.html" for page N (page 1 has no suffix, just ".html")

**Utils** (`src/utils.py`): Helper functions for URL parsing, filename generation, and CSV saving.

### Data Extraction

The scraper looks for `div` elements with `data-qa` attributes and maps them to property fields:
- `POSTING_CARD_PRICE` → price_value, price_type (USD/ARS/$)
- `expensas` → expenses_value, expenses_type
- `POSTING_CARD_LOCATION` → location
- `POSTING_CARD_DESCRIPTION` → description
- `POSTING_CARD_FEATURES` → parsed into: square_meters_area, rooms, bedrooms, bathrooms, parking

Feature parsing uses regex to extract number + unit pairs (e.g., "50 m²", "2 amb"). Multiple instances of same feature type get suffixed with index (e.g., bathrooms_0, bathrooms_1).

### Test Structure

Tests use pytest with mocking via pytest_mock. Mock HTML pages stored in `test/mock/` directory. Tests mock the Browser class and validate parsing logic without hitting real websites.

### Data Flow

1. User provides Zonaprop URL
2. Browser fetches first page to determine total property count
3. Scraper iterates through pages (3-second delay between requests)
4. Each page parsed with BeautifulSoup (lxml parser)
5. Property cards extracted and parsed into dicts
6. All properties collected into list
7. List converted to pandas DataFrame
8. DataFrame saved to CSV in `data/` directory with timestamped filename

## Analysis

Exploratory data analysis notebook available at `analysis/exploratory-analysis.ipynb` demonstrating how to analyze scraped data.
