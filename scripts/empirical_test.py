#!/usr/bin/env python3
"""
Empirical Test of the Interaction Field Theory
================================================
Tests the inflection point prediction using PriceCharting API data.
"""
import json
import requests
import time
import os
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

TOKEN = "148b93e8f7bce9304037b04a8aab950a73d980d6"
BASE_URL = "https://www.pricecharting.com/api"

# Set up session with retries
session = requests.Session()
retries = Retry(total=3, backoff_factor=2, status_forcelist=[429, 500, 502, 503, 504])
session.mount("https://", HTTPAdapter(max_retries=retries))

def search_products(query):
    """Search for products on PriceCharting"""
    try:
        resp = session.get(f"{BASE_URL}/products", params={"t": TOKEN, "q": query}, timeout=15)
        if resp.ok:
            return resp.json()
    except Exception as e:
        print(f"    Error searching '{query}': {e}")
    return None

def get_product(product_id):
    """Get detailed product info"""
    try:
        resp = session.get(f"{BASE_URL}/product", params={"t": TOKEN, "id": product_id}, timeout=15)
        if resp.ok:
            return resp.json()
    except Exception as e:
        pass
    return None

print("=" * 70)
print("EMPIRICAL TEST: Interaction Field Theory - Inflection Point Prediction")
print("=" * 70)
print()

# Collect products with longer delays to avoid rate limiting
search_queries = [
    "gundam GD01", "gundam GD02", "gundam GD03", "gundam GD04",
    "gundam GD05", "gundam SD01", "gundam LR", "gundam SR",
]

all_products = {}
print("Phase 1: Collecting product catalog...")
print("-" * 50)

for query in search_queries:
    print(f"  Searching: {query}...")
    result = search_products(query)
    if result and result.get("status") == "success":
        products = result.get("products", [])
        for p in products:
            pid = p.get("id")
            if pid and pid not in all_products:
                all_products[pid] = p
        print(f"    Found {len(products)} products ({len(all_products)} unique total)")
    time.sleep(2)  # More conservative rate limiting

print(f"\nTotal unique products found: {len(all_products)}")

# Step 2: Get detailed data (limit to 80 products, with longer delays)
print("\nPhase 2: Fetching detailed price/volume data...")
print("-" * 50)

detailed_products = []
product_ids = list(all_products.keys())[:80]

for i, pid in enumerate(product_ids):
    if (i + 1) % 10 == 0:
        print(f"  Progress: {i+1}/{len(product_ids)}")
    
    detail = get_product(pid)
    if detail and detail.get("status") == "success":
        detailed_products.append(detail)
    time.sleep(1.5)  # Conservative rate limiting

print(f"\nDetailed data collected for {len(detailed_products)} products")

# Save all raw data
with open("/home/ubuntu/empirical_data_raw.json", "w") as f:
    json.dump(detailed_products, f, indent=2)

# Print available fields from first product
if detailed_products:
    print("\nAvailable API fields:")
    sample = detailed_products[0]
    for key in sorted(sample.keys()):
        val = sample[key]
        if isinstance(val, str) and len(val) > 60:
            val = val[:60] + "..."
        print(f"  {key}: {val}")

# Extract and analyze
cards = []
for p in detailed_products:
    sales_vol = p.get("sales-volume")
    loose_price = p.get("loose-price", 0)
    if sales_vol is not None and loose_price and loose_price > 0:
        cards.append({
            "id": p.get("id"),
            "name": p.get("product-name", "?"),
            "loose_price_cents": loose_price,
            "sales_volume": sales_vol,
            "cib_price": p.get("cib-price", 0),
            "new_price": p.get("new-price", 0),
        })

cards.sort(key=lambda x: x["sales_volume"])
print(f"\nCards with valid price + volume: {len(cards)}")

if cards:
    volumes = [c["sales_volume"] for c in cards]
    print(f"\nVolume stats: min={min(volumes)}, max={max(volumes)}, "
          f"mean={sum(volumes)/len(volumes):.0f}, median={sorted(volumes)[len(volumes)//2]}")
    
    prices = [c["loose_price_cents"]/100 for c in cards]
    print(f"Price stats: min=${min(prices):.2f}, max=${max(prices):.2f}, "
          f"mean=${sum(prices)/len(prices):.2f}")

    # Show distribution
    print("\nSample across liquidity spectrum:")
    print(f"{'Name':<45} {'Vol':<8} {'Price':<10}")
    print("-" * 65)
    step = max(1, len(cards) // 15)
    for i in range(0, len(cards), step):
        c = cards[i]
        print(f"{c['name'][:43]:<45} {c['sales_volume']:<8} ${c['loose_price_cents']/100:.2f}")

with open("/home/ubuntu/empirical_cards_clean.json", "w") as f:
    json.dump(cards, f, indent=2)

print("\nData saved. Ready for Phase 2 analysis.")
