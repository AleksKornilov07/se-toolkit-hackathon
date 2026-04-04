import httpx
from bs4 import BeautifulSoup
from decimal import Decimal
from typing import Optional


async def fetch_price(url: str, store: str) -> Optional[Decimal]:
    """Fetch price from store URL"""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers, timeout=30)
            response.raise_for_status()

            if store == "amazon":
                return parse_amazon_price(response.text)
            elif store == "bestbuy":
                return parse_bestbuy_price(response.text)
            else:
                return parse_generic_price(response.text)
    except Exception as e:
        print(f"Error fetching price: {e}")
        return None


def parse_amazon_price(html: str) -> Optional[Decimal]:
    soup = BeautifulSoup(html, "html.parser")
    price_elem = soup.find("span", class_="a-price-whole")
    if price_elem:
        text = price_elem.get_text().strip().replace("$", "").replace(",", "")
        return Decimal(text)
    return None


def parse_bestbuy_price(html: str) -> Optional[Decimal]:
    soup = BeautifulSoup(html, "html.parser")
    price_elem = soup.find("span", class_="priceView-hero-price")
    if price_elem:
        text = price_elem.get_text().strip().replace("$", "").replace(",", "")
        return Decimal(text.split()[0])
    return None


def parse_generic_price(html: str) -> Optional[Decimal]:
    """Generic price finder using common patterns"""
    soup = BeautifulSoup(html, "html.parser")

    price_patterns = [
        {"class": "price"},
        {"class": "product-price"},
        {"itemprop": "price"},
        {"data-price": True},
    ]

    for pattern in price_patterns:
        elem = soup.find(**pattern)
        if elem:
            text = elem.get_text().strip()
            import re

            match = re.search(r"[\d,]+\.?\d*", text)
            if match:
                return Decimal(match.group().replace(",", ""))

    return None
