# Bookstore Intelligence Mission: Web Scraper

A Python web scraper built for **Assignment 2 (Business Data and Text Mining)**. It collects book data from the practice site [books.toscrape.com](https://books.toscrape.com/), turns it into a clean Pandas DataFrame, saves it as a CSV, and uses the data to answer business questions.

> The webpage is not the dataset. Your scraper turns it into one.

## Features

- Scrapes **title, price, rating, availability and product URL** for every book
- Loops over catalogue pages with one reusable function (no copy-pasted code)
- Converts word ratings (One to Five) into numbers 1 to 5
- Cleans prices (removes the `£` symbol, converts to float)
- Saves the dataset as `competitor_books.csv`
- Answers the seven business-intelligence questions automatically
- Solves the CEO £100 challenge with a knapsack algorithm (maximises total stars within budget)
- Counts books per star rating and draws a bar chart

## Requirements

- Python 3.8+
- `requests`, `beautifulsoup4`, `pandas`, `matplotlib`

```bash
pip install requests beautifulsoup4 pandas matplotlib
```

## Usage

```bash
python scraper.py
```

Number of pages to scrape is controlled by the `PAGES` variable at the top of `scraper.py`:

| Value | Result |
|-------|--------|
| `3`   | Required mission (first 3 pages) |
| `5`   | Bonus 1 |
| `None`| Boss level (all catalogue pages) |

## Output

| File | Description |
|------|-------------|
| `competitor_books.csv` | Scraped dataset |
| `rating_counts.png` | Bar chart of books per star rating |

### Dataset structure

| Column | Description | Example |
|--------|-------------|---------|
| Title | Full book title | A Light in the Attic |
| Price | Price in GBP (float) | 51.77 |
| Rating | Star rating, 1 to 5 | 3 |
| Availability | Stock status | In stock |
| URL | Product page link | https://books.toscrape.com/catalogue/... |

## How it works

1. **Reconnaissance.** Each book is an `<article class="product_pod">`. The title is read from the link's `title` attribute (the visible text is truncated), the price from `p.price_color`, the rating from the second CSS class of `p.star-rating`, and availability from `p.availability`.
2. **Fetch.** `requests` downloads each page, and the encoding is set to UTF-8 so prices don't show `Â£`.
3. **Parse.** `BeautifulSoup` extracts the fields of every book card with `parse_book()`.
4. **Loop.** `scrape_books()` walks through `page-1`, `page-2`, ... and stops when there are no more pages.
5. **Analyse.** The DataFrame is used to answer the business questions and the CEO challenge.

## Analysis answered by the script

1. Most expensive book
2. Cheapest book
3. Average price
4. Number of 5-star books
5. Percentage of books in stock
6. Top 5 highest-rated books
7. Cheapest 5-star book

Plus the CEO £100 challenge: the selected titles, individual prices, total cost and total rating score.

## Project structure

```
.
├── scraper.py
├── competitor_books.csv
├── rating_counts.png
└── README.md
```

## Notes

- This scraper only targets the sandbox site made for scraping practice.
- A short delay between requests keeps the scraper polite to the server.
- Results such as the CEO selection come from the scraped data, so they change with the number of pages scraped.

## Author

**Hadi Saleemi** (22i-1043), FAST NUCES
