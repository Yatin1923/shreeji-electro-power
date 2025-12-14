from urllib.parse import urljoin
import requests
from bs4 import BeautifulSoup

CATEGORY_SLUGS = [
    "medium-voltage",
    "lv-iec-panels",
    "power-distribution-products-lv-switchgear",
    "motor-management-control",
    "industrial-automation-control",
    "energy-management-products",
    "mcb-rccb-distribution-boards",
    "pump-starters-and-controllers",
    "industrial-signalling-products"
]
def fetch_all_products():
    all_products = []

    for slug in CATEGORY_SLUGS:
        print(f"\n🔍 Fetching products for category: {slug}")
        products = fetch_all_products_for_category(slug)
        all_products.extend(products)
        print(f"✅ Found {len(products)} products for {slug}")

    return all_products

def fetch_subcategory_urls(subcategory_url,productName):
    response = requests.get(subcategory_url, timeout=20)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    urls = []
    seen_links = set()

    # Find all anchor tags pointing to medium-voltage product pages
    for a in soup.find_all("a", href=True):
        href = a["href"].strip()
        name = a.get_text(strip=True)

        if (
            href.startswith(f"/products/{productName}/")
            and name
            and href not in seen_links
        ):
            seen_links.add(href)

            urls.append("https://www.lk-ea.com"+href)
            print(f"Found subcategory: https://www.lk-ea.com{href}")

    return urls
def fetch_all_products_for_category(category_slug):
    """
    category_slug examples:
    - 'medium-voltage'
    - 'lv-iec-panels'
    """

    BASE_URL = "https://www.lk-ea.com"
    category_url = f"{BASE_URL}/products/{category_slug}"

    print(f"Fetching subcategories for: {category_slug}")

    all_products = []

    subcategory_urls = fetch_subcategory_urls(category_url, category_slug)

    for subcategory_url in subcategory_urls:
        try:
            products = fetch_products_from_subcategory(subcategory_url)
            all_products.extend(products)
        except Exception as e:
            print(f"❌ Failed for {subcategory_url}: {e}")

    return all_products

def fetch_all_medium_voltage_products():
    all_products = []
    name = "medium-voltage"
    BASE_URL = "https://www.lk-ea.com"
    category_url = f"{BASE_URL}/products/medium-voltage"
    subcategory_urls = fetch_subcategory_urls(category_url,name)
    for subcategory_url in subcategory_urls:
        try:
            category_products = fetch_products_from_subcategory(subcategory_url)
            all_products.extend(category_products)
        except Exception as e:
            print(f"❌ Failed for {subcategory_url}: {e}")

    return all_products



def fetch_all_lv_iec_panels(category_url):
    all_products = []
    name = "lv-iec-panels"
    name = category_url.split("/")[-1]
    print(f"Fetching subcategories for: {name}")
    BASE_URL = "https://www.lk-ea.com"
    category_url = f"{BASE_URL}/products/lv-iec-panels"
    subcategory_urls = fetch_subcategory_urls(category_url,name)
    for subcategory_url in subcategory_urls:
        try:
            category_products = fetch_products_from_subcategory(subcategory_url)
            all_products.extend(category_products)
        except Exception as e:
            print(f"❌ Failed for {subcategory_url}: {e}")

    return all_products

def fetch_products_from_subcategory(subcategory_url):
    response = requests.get(subcategory_url, timeout=20)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    productsUrls = []
    seen = set()

    # Product cards are anchor-based
    for a in soup.select("a[href]"):
        href = a.get("href").strip()
        name = a.get_text(strip=True)

        # Filter only real product links
        if (
            href.startswith(subcategory_url.replace("https://www.lk-ea.com", ""))
            and name
            and href not in seen
            and href != subcategory_url.replace("https://www.lk-ea.com", "")
        ):
            seen.add(href)

            productsUrls.append({
                # "name": name,
                "url": urljoin("https://www.lk-ea.com", href),
                "subcategory_url": subcategory_url
            })

    return productsUrls
import json
from datetime import datetime


def export_to_json(data, filename_prefix="lk_products"):
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    filename = f"{filename_prefix}_{timestamp}.json"

    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"✅ Data exported to {filename}")

if __name__ == "__main__":
    all_products = fetch_all_products()

    total = sum(len(v) for v in all_products)
    print(f"\n📦 Total products found: {total}")

    export_to_json(all_products)
