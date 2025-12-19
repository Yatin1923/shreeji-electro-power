import requests
from bs4 import BeautifulSoup
import time
import os
import csv
import json
from urllib.parse import urljoin, urlparse

BASE_URL = "https://www.neptuneindia.com"
OUTPUT_JSON = "neptune_products_extended_with_subcats.json"
OUTPUT_CSV = "neptune_products_extended_with_subcats.csv"
DOWNLOAD_DIR = "downloads"

# Make download directories
os.makedirs(DOWNLOAD_DIR, exist_ok=True)
os.makedirs(os.path.join(DOWNLOAD_DIR, "images"), exist_ok=True)
os.makedirs(os.path.join(DOWNLOAD_DIR, "brochures"), exist_ok=True)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; scrapperBot/1.0; +https://yourdomain.com)"
}

def get_soup(url):
    resp = requests.get(url, headers=HEADERS, timeout=30)
    resp.raise_for_status()
    return BeautifulSoup(resp.text, "html.parser")

def download_file(file_url, folder):
    try:
        parsed = urlparse(file_url)
        fname = os.path.basename(parsed.path)
        fpath = os.path.join(DOWNLOAD_DIR, folder, fname)
        if not os.path.exists(fpath):
            with requests.get(file_url, headers=HEADERS, stream=True, timeout=30) as r:
                r.raise_for_status()
                with open(fpath, 'wb') as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        f.write(chunk)
        return fpath
    except Exception as e:
        print(f"   Download failed {file_url}: {e}")
        return None

def extract_product_data(product_url, full_category_path):
    print(f"     Scraping product → {product_url}")
    soup = get_soup(product_url)
    # Define base pdata with all your fields (as before)
    pdata = {
        "Name": None,
        "Product_Type": full_category_path,
        "Type": None,
        "Brand": "Neptune India",
        "Key_Features": None,
        "Benefits": None,
        "Short_Description": None,
        "Full_Description": None,
        "Image_Path": None,
        "Color": None,
        "Model_Number": None,
        "Specifications": None,
        "Sweep_Size": None,
        "RPM": None,
        "Power_Consumption": None,
        "Air_Delivery": None,
        "BEE_Rating": None,
        "Number_of_Blades": None,
        "Blade_Material": None,
        "Body_Material": None,
        "Motor_Winding": None,
        "Warranty": None,
        "Price": None,
        "Standards": None,
        "Certifications": None,
        "Product_URL": product_url,
        "Brochure_Path": None,
        "Image_Download_Status": None,
        "Brochure_Download_Status": None,
        "Wattage": None,
        "Amperage": None,
        "Voltage": None,
        "Poles": None,
        "Breaking_Capacity": None,
        "Trip_Curve": None,
        "Sensitivity": None,
        "Application": None,
        "MCB_Type": None,
        "IP_Rating": None,
        "Operating_Temperature": None,
        "Contact_Material": None,
        "Mounting_Type": None,
        "Module": None,
        "GenCurrentRating": None,
        "Product_Series": None,
        "Size_Sq_MM": None,
        "Length": None,
        "Insulation_Type": None,
        "Heat_Resistance": None,
        "Copper_Grade": None,
        "Technology": None,
        "Fire_Safety": None,
        "Moisture_Resistance": None,
        "Abrasion_Resistance": None,
        "Eco_Certifications": None,
        "Current_Carrying_Capacity": None,
        "Product_Life": None,
        "Voltage_Rating": None,
        "Conductor_Type": None
    }

    # Name
    h1 = soup.find("h1", class_="product_title")
    if h1:
        pdata["Name"] = h1.get_text(strip=True)

    # Short description
    short_desc = soup.find("div", class_="woocommerce-product-details__short-description")
    if short_desc:
        pdata["Short_Description"] = short_desc.get_text("\n", strip=True)

    # Full description
    desc_tab = soup.find("div", id="tab-description")
    if desc_tab:
        pdata["Specifications"] = desc_tab.get_text("\n", strip=True)

    # Key Features (list)
    feat_ul = soup.find("ul", class_="features-list")
    if feat_ul:
        pdata["Key_Features"] = "\n".join(li.get_text(strip=True) for li in feat_ul.find_all("li"))

    # Image
    img = soup.find("img", class_="wp-post-image")
    if img and img.has_attr("src"):
        img_url = img["src"]
        pdata["Image_Path"] = img_url
        local_img = download_file(img_url, "images")
        pdata["Image_Download_Status"] = "Downloaded" if local_img else "Failed"

    # Price
    price_tag = soup.find("p", class_="price")
    if price_tag:
        pdata["Price"] = price_tag.get_text(strip=True)

    # Brochure link
    a_broch = soup.find("a", class_="btn-danger")
    if a_broch:
        brochure_url = urljoin(BASE_URL, a_broch["href"])
        pdata["Brochure_Path"] = brochure_url
        local_broch = download_file(brochure_url, "brochures")
        pdata["Brochure_Download_Status"] = "Downloaded" if local_broch else "Failed"
    return pdata

def scrape_category_recursive(category_url, category_name):
    """
    Scrape a category and its sub-categories recursively.
    category_name: the full path name (e.g. "Power Quality > Harmonic Filters")
    """
    print(f"Scraping category path: {category_name} → {category_url}")
    soup = get_soup(category_url)
    # First, check for sub-categories blocks on this page
    subcat_links = []
    # e.g., look for “a” elements inside a category grid or list
    for a in soup.select("li.product-category a"):  
        href = a.get("href")
        name = a.get_text(strip=True)
        print(href)
        print(name)
        if href and name:
            subcat_links.append((href, name))
    if subcat_links:
        # If sub-categories found: recurse each one
        for href, name in subcat_links:
            full_name = f"{category_name} > {name}"
            scrape_category_recursive(href, full_name)
    else:
        # No further sub-categories: this is a leaf category with products
        # Now handle pagination of product list
        page_url = category_url
        page_idx = 1
        while page_url:
            print(f"  Page {page_idx} in {category_name} → {page_url}")
            soup2 = get_soup(page_url)
            # product links
            links = [a.get("href") for a in soup2.select("a.woocommerce-loop-product__link") if a.get("href")]
            print(f"    → Found {len(links)} products")
            for url in links:
                try:
                    pdata = extract_product_data(url, category_name)
                    all_products.append(pdata)
                except Exception as e:
                    print(f"      ERROR scraping product {url}: {e}")
                time.sleep(1)
            # next page
            next_page = soup2.select_one("a.next.page-numbers")
            if next_page and next_page.get("href"):
                page_url = next_page.get("href")
                page_idx += 1
                time.sleep(2)
            else:
                page_url = None

def discover_categories():
    """Find top-level categories from the main products page."""
    print("Discovering top-level categories …")
    soup = get_soup(urljoin(BASE_URL, "/product/"))
    category_links = []
    for a in soup.select("li.product-category a"):
        href = a.get("href")
        name = a.get_text(strip=True)
        print(name)
        if href:
            category_links.append((href, name))
    print(f"Discovered {len(category_links)} top-level categories.")
    return category_links

def main():
    global all_products
    all_products = []
    top_cats = discover_categories()
    for href, name in top_cats:
        scrape_category_recursive(href, name)

    # Save JSON
    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(all_products, f, ensure_ascii=False, indent=2)

    # Save CSV
    fieldnames = list({k for p in all_products for k in p.keys()})
    with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for p in all_products:
            writer.writerow(p)

    print(f"Done. Total products scraped: {len(all_products)}")
    print(f"Saved JSON → {OUTPUT_JSON}")
    print(f"Saved CSV  → {OUTPUT_CSV}")

if __name__ == "__main__":
    main()
