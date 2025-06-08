# Decathlon Singapore Product Scraper

This project extracts structured product data from [Decathlon Singapore](https://www.decathlon.sg/c/all-sports.html), handling dynamic content and pagination for at least 100 products.

## Features

✅ Automated scraping with Playwright  
✅ Extracts:
- Product Name
- Price
- Promotional Status
- Brand
- Discount
- Product URL  
✅ Outputs:
- `decathlon_products.json`
- `decathlon_products.csv`  
✅ Handles:
- Dynamic loading via "View More" button
- JavaScript-rendered content
- Anti-scraping rate limiting with short delays  
✅ Robust selectors to ensure data completeness

## Installation & Setup

```bash
pip install -r requirements.txt
playwright install chromium
