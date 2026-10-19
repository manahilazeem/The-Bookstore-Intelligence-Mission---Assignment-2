"""
Assignment 2 - The Bookstore Intelligence Mission Manahil Azeem (23i5082)
Scrapes https://books.toscrape.com/ and answers the business questions.

Run:  python scraper.py
Needs: pip install requests beautifulsoup4 pandas matplotlib

Set PAGES = 3 (required), 5 (Bonus 1) or None (Boss Level: all pages).
"""

import re
import sys
import time
from urllib.parse import urljoin

import pandas as pd
import requests
from bs4 import BeautifulSoup
import matplotlib.pyplot as plt

BASE_URL = "https://books.toscrape.com/"
PAGE_URL = "https://books.toscrape.com/catalogue/page-{}.html"
PAGES = None          # None = all pages (Boss Level). Use 3 or 5 for the basic tasks.
BUDGET = 100.00       # CEO challenge budget in GBP
OUTPUT_CSV = "competitor_books.csv"

RATING_MAP = {"One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5}

# ---------------------------------------------------------------------------
# Mission 1 - Reconnaissance notes (what we found by inspecting a product card)
#   Book card   : <article class="product_pod">
#   Title       : <h3><a title="Full Title">  (the text is truncated, the title attribute is not)
#   Price       : <p class="price_color">£51.77</p>
#   Rating      : <p class="star-rating Three">  (rating word is the 2nd CSS class)
#   Availability: <p class="instock availability"> In stock </p>
#   Product link: <h3><a href="...">  (relative URL)
# ---------------------------------------------------------------------------


def get_soup(url):
    """Download a page and return a BeautifulSoup object (None if page missing)."""
    response = requests.get(url, timeout=15)
    if response.status_code == 404:
        return None
    response.raise_for_status()
    response.encoding = "utf-8"          # avoids 'Â£' garbage in prices
    return BeautifulSoup(response.text, "html.parser"), response.url


def parse_book(card, page_url):
    """Extract one book's data from an <article class='product_pod'> element."""
    link = card.h3.a
    title = link["title"]
    url = urljoin(page_url, link["href"])

    price_text = card.find("p", class_="price_color").get_text(strip=True)
    price = float(re.sub(r"[^\d.]", "", price_text))

    rating_word = [c for c in card.find("p", class_="star-rating")["class"]
                   if c != "star-rating"][0]
    rating = RATING_MAP[rating_word]

    availability = card.find("p", class_="availability").get_text(strip=True)

    return {
        "Title": title,
        "Price": price,
        "Rating": rating,
        "Availability": availability,
        "URL": url,                      # Bonus 2
    }


def scrape_books(max_pages=None):
    """Loop over catalogue pages and collect every book into a list of dicts."""
    records = []
    page = 1
    while max_pages is None or page <= max_pages:
        url = BASE_URL if page == 1 else PAGE_URL.format(page)
        result = get_soup(url)
        if result is None:               # ran out of pages
            break
        soup, final_url = result
        cards = soup.find_all("article", class_="product_pod")
        if not cards:
            break
        records.extend(parse_book(card, final_url) for card in cards)
        print(f"Scraped page {page}: {len(cards)} books (total {len(records)})")
        page += 1
        time.sleep(0.3)                  # be polite to the server
    return records


def best_basket(df, budget):
    """
    CEO challenge: 0/1 knapsack. Maximise total star rating with total price <= budget.
    Ties are broken in favour of the cheaper basket. Prices are handled in pence
    to avoid floating point errors.
    """
    cap = int(round(budget * 100))
    items = [(int(round(p * 100)), r, i)
             for i, (p, r) in enumerate(zip(df["Price"], df["Rating"]))
             if int(round(p * 100)) <= cap]

    # best[c] = (total_rating, -total_cost, chosen_indices) using exactly <= c pence
    best = [(0, 0, [])] * (cap + 1)
    for cost, rating, idx in items:
        for c in range(cap, cost - 1, -1):
            prev_rating, prev_negcost, prev_set = best[c - cost]
            cand = (prev_rating + rating, prev_negcost - cost, prev_set + [idx])
            if cand[:2] > best[c][:2]:
                best[c] = cand
    total_rating, _, chosen = best[cap]
    return df.iloc[chosen][["Title", "Price", "Rating"]].reset_index(drop=True), total_rating


def main():
    # ------------------ Missions 2 & 3: scrape and build DataFrame ------------------
    df = pd.DataFrame(scrape_books(PAGES))
    print("\nFirst rows:")
    print(df.head())
    print("\nColumns:", list(df.columns), "| Rows:", len(df))
    print(df.dtypes)

    df.to_csv(OUTPUT_CSV, index=False, encoding="utf-8")
    print(f"\nSaved {OUTPUT_CSV}")

    # ------------------ Mission 4: intelligence analysis ------------------
    print("\n===== INTELLIGENCE ANALYSIS =====")

    priciest = df.loc[df["Price"].idxmax()]
    print(f"1. Most expensive: {priciest['Title']} (£{priciest['Price']:.2f})")

    cheapest = df.loc[df["Price"].idxmin()]
    print(f"2. Cheapest: {cheapest['Title']} (£{cheapest['Price']:.2f})")

    print(f"3. Average price: £{df['Price'].mean():.2f}")

    five_star = df[df["Rating"] == 5]
    print(f"4. Number of 5-star books: {len(five_star)}")

    in_stock_pct = df["Availability"].str.contains("In stock", case=False).mean() * 100
    print(f"5. Percentage in stock: {in_stock_pct:.1f}%")

    print("6. Top 5 highest-rated books (ties broken by lower price):")
    top5 = df.sort_values(["Rating", "Price"], ascending=[False, True]).head(5)
    print(top5[["Title", "Price", "Rating"]].to_string(index=False))

    cheapest_5 = five_star.loc[five_star["Price"].idxmin()]
    print(f"7. Cheapest 5-star book: {cheapest_5['Title']} (£{cheapest_5['Price']:.2f})")

    # ------------------ Business decision evidence ------------------
    print("\n===== BUSINESS DECISION EVIDENCE =====")
    by_rating = df.groupby("Rating")["Price"].agg(["count", "mean"]).round(2)
    print(by_rating)
    print(f"5-star books average £{five_star['Price'].mean():.2f} "
          f"vs overall £{df['Price'].mean():.2f}")
    print(f"{in_stock_pct:.1f}% of titles are in stock.")

    # ------------------ Final challenge: CEO has £100 ------------------
    print(f"\n===== CEO CHALLENGE (budget £{BUDGET:.2f}) =====")
    basket, total_rating = best_basket(df, BUDGET)
    print(basket.to_string(index=False))
    print(f"Books chosen : {len(basket)}")
    print(f"Total cost   : £{basket['Price'].sum():.2f}")
    print(f"Total rating : {total_rating}")

    # ------------------ Bonus 3 & 4: rating counts + bar chart ------------------
    counts = df["Rating"].value_counts().sort_index()
    print("\nBooks per star rating:")
    print(counts)

    ax = counts.plot(kind="bar", color="steelblue", edgecolor="black")
    ax.set_title("Number of Books by Star Rating")
    ax.set_xlabel("Star rating")
    ax.set_ylabel("Number of books")
    plt.xticks(rotation=0)
    plt.tight_layout()
    plt.savefig("rating_counts.png", dpi=150)
    plt.show()


class Tee:
    """Send everything that is printed to the screen AND to a text file."""

    def __init__(self, *streams):
        self.streams = streams

    def write(self, text):
        for s in self.streams:
            s.write(text)
            s.flush()

    def flush(self):
        for s in self.streams:
            s.flush()


if __name__ == "__main__":
    with open("analysis_results.txt", "w", encoding="utf-8") as report:
        sys.stdout = Tee(sys.__stdout__, report)
        main()
        sys.stdout = sys.__stdout__
    print("Analysis also saved to analysis_results.txt")
