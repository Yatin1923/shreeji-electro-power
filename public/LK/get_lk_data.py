import requests
from bs4 import BeautifulSoup
import json
import pandas as pd
import re
import os
import time
from urllib.parse import urljoin, urlparse
import logging
from typing import Dict, List, Optional
import urllib.request
from pathlib import Path

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
from playwright.sync_api import sync_playwright
from urllib.parse import urljoin
import re


class LKEAProductScraper:
    def __init__(self, base_url="https://www.lk-ea.com", output_dir="lk_ea_products"):
        self.base_url = base_url
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # Create subdirectories
        (self.output_dir / "images").mkdir(exist_ok=True)
        (self.output_dir / "brochures").mkdir(exist_ok=True)
        (self.output_dir / "data").mkdir(exist_ok=True)
        
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
        self.products = []
        self.visited_urls = set()
        self.category_descriptions = {}
        
    def get_page_content(self, url: str) -> Optional[BeautifulSoup]:
        """Fetch and parse page content"""
        try:
            # if url in self.visited_urls:
            #     logger.info(f"Already visited: {url}")
            #     return None
                
            logger.info(f"Fetching: {url}")
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            self.visited_urls.add(url)
            
            return BeautifulSoup(response.content, 'html.parser')
        except Exception as e:
            logger.error(f"Error fetching {url}: {e}")
            return None
    def extract_document_pdf_playwright(self, url: str):
        from playwright.sync_api import sync_playwright
        from pathlib import Path

        documentPath = None  # ✅ initialize safely

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False)
            context = browser.new_context(accept_downloads=True)
            page = context.new_page()

            try:
                page.goto(url, timeout=30000)

                # If Documents tab doesn't exist → return None
                documents_btn = page.locator('button:has-text("Documents")')
                if documents_btn.count() == 0:
                    return None

                documents_btn.click()
                page.wait_for_timeout(2000)

                anchors = page.locator('a[download$=".pdf"]')
                count = anchors.count()

                if count == 0:
                    return None  # ✅ no documents found → safe exit

                for i in range(count):
                    a_tag = anchors.nth(i)

                    pdf_name = a_tag.get_attribute("download") or f"catalogue_{i+1}.pdf"
                    pdf_name = pdf_name.replace(" ", "_")

                    download_btn = a_tag.locator(
                        'xpath=following-sibling::button//button'
                    ).nth(2)

                    with page.expect_download() as download_info:
                        download_btn.click()

                    download = download_info.value
                    download_path = self.output_dir / "brochures" / pdf_name
                    download_path.parent.mkdir(parents=True, exist_ok=True)

                    download.save_as(download_path)
                    documentPath = str(download_path)

                    ok_btn = page.locator('button:has-text("OK")')
                    if ok_btn.count() > 0:
                        ok_btn.click()
                        page.wait_for_timeout(500)

            except Exception as e:
                # ❗ log only — NEVER crash pipeline
                logger.warning(f"⚠️ Document fetch skipped for {url}: {e}")

            finally:
                browser.close()

        return documentPath  # always defined

    def extract_product_categories(self) -> List[str]:
        """Extract all product category URLs"""
        logger.info("Extracting product categories...")
        
        # Get dynamic categories from the main page
        main_soup = self.get_page_content(self.base_url)
        categories = []
        
        if main_soup:
            # Find all product category links
            product_links = main_soup.find_all('a', href=re.compile(r'/products/'))
            for link in product_links:
                href = link.get('href')
                if href and href.startswith('/products/') and href.count('/') >= 2:
                    full_url = urljoin(self.base_url, href)
                    if full_url not in categories:
                        categories.append(full_url)
        
        # Also include known categories
        known_categories = [
            "/products/medium-voltage",
            "/products/lv-iec-panels", 
            "/products/power-distribution-products",
            "/products/motor-management-control",
            "/products/industrial-automation-control",
            "/products/energy-management-products",
            "/products/mcb-rccb-distribution-boards",
            "/products/switches-accessories",
            "/products/pump-starters-and-controllers",
            "/products/panel-accessories"
        ]
        
        for category in known_categories:
            full_url = urljoin(self.base_url, category)
            if full_url not in categories:
                categories.append(full_url)
            
        logger.info(f"Found {len(categories)} categories")
        return categories
    
    def extract_category_description(self, category_url: str) -> str:
        """Extract full description from category page"""
        if category_url in self.category_descriptions:
            return self.category_descriptions[category_url]
        
        logger.info(f"Extracting category description from: {category_url}")
        soup = self.get_page_content(category_url)
        
        if not soup:
            return ""
        
        full_description = ""

        # 🔥 Find the description section using the correct class
        desc_container = soup.find("div", class_="content-description")
        
        if desc_container:
            # Get ALL <p> text inside the container
            paragraphs = desc_container.find_all("p")
            
            combined_text = []
            for p in paragraphs:
                text = p.get_text(" ", strip=True)
                if text and text != " ":   # ignore empty &nbsp; 
                    combined_text.append(text)

            full_description = " ".join(combined_text).strip()

        # Fallback if nothing found
        if not full_description:
            full_description = ""
        
        # Cache and return
        self.category_descriptions[category_url] = full_description
        logger.info(f"Extracted category description: {full_description[:100]}...")
        
        return full_description
    
    def extract_category_image(self, category_url: str, product_name: str) -> str:
        """
        Extract product image from category page based on product card.
        """
        soup = self.get_page_content(category_url)
        if not soup:
            return ""

        # Normalize name for matching
        normalized = product_name.strip().lower()
        print(f"Looking for image of product: {normalized}")
        # Find the product card by <h2> title
        product_cards = soup.find_all('a', href=True)

        for card in product_cards:
            title = card.find('h2')
            if not title:
                continue

            title_text = title.get_text(strip=True).lower()

            if title_text.lower().__contains__(normalized):
                # Found the correct product card
                img = card.find('img')
                if img:
                    src = img.get('src')
                    if src:
                        return urljoin(self.base_url, src)

        return ""

    def extract_short_description(self, soup: BeautifulSoup) -> str:
        """Extract full description from category page"""
        if not soup:
            return ""
        
        short_description = ""

        # 🔥 Find the description section using the correct class
        desc_container = soup.find("div", class_="content-description")
        
        if desc_container:
            # Get ALL <p> text inside the container
            paragraphs = desc_container.find_all("p")
            
            combined_text = []
            for p in paragraphs:
                text = p.get_text(" ", strip=True)
                if text and text != " ":   # ignore empty &nbsp; 
                    combined_text.append(text)

            short_description = " ".join(combined_text).strip()

        # Fallback if nothing found
        if not short_description:
            short_description = ""
        return short_description

    def extract_subcategories_and_products(self, category_url: str) -> tuple[List[str], List[str]]:
        """Extract subcategories and product URLs from a category page"""
        logger.info(f"Processing category: {category_url}")
        
        soup = self.get_page_content(category_url)
        if not soup:
            return [], []
            
        subcategory_urls = []
        direct_product_urls = []
        
        # Find all links on the page
        links = soup.find_all('a', href=True)
        
        for link in links:
            href = link.get('href')
            if href:
                # Convert relative URLs to absolute
                if href.startswith('/'):
                    full_url = urljoin(self.base_url, href)
                else:
                    full_url = href
                
                # Filter for valid URLs
                if (full_url.startswith(self.base_url) and 
                    '/products/' in full_url and
                    not any(skip in full_url for skip in ['/forms/', '/contact', 'smartshop', '#', 'javascript:'])):
                    
                    # Determine if it's a subcategory or direct product
                    url_parts = urlparse(full_url).path.strip('/').split('/')
                    
                    # Count depth: products/category/subcategory/product
                    if len(url_parts) == 2:  # products/category
                        continue  # This is the current category
                    elif len(url_parts) == 3:  # products/category/subcategory
                        if full_url not in subcategory_urls:
                            subcategory_urls.append(full_url)
                    elif len(url_parts) >= 4:  # products/category/subcategory/product
                        if full_url not in direct_product_urls:
                            direct_product_urls.append(full_url)
        
        logger.info(f"Found {len(subcategory_urls)} subcategories and {len(direct_product_urls)} direct products")
        return subcategory_urls, direct_product_urls
    
    def download_file(self, url: str, local_path: Path) -> bool:
        """Download a file from URL to local path"""
        try:
            if local_path.exists():
                logger.info(f"File already exists: {local_path}")
                return True
            
            # Handle different types of URLs
            if url.startswith('blob:') or not url.startswith('http'):
                logger.warning(f"Cannot download blob URL: {url}")
                return False
                
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            with open(local_path, 'wb') as f:
                f.write(response.content)
            
            logger.info(f"Downloaded: {local_path}")
            return True
        except Exception as e:
            logger.error(f"Error downloading brochure: {e}")
            return False
    
    def extract_product_details(self, product_url: str, category_url: str = None) -> Optional[Dict]:
        """Extract detailed product information"""
        logger.info(f"Extracting product details from: {product_url}")
        
        soup = self.get_page_content(product_url)
        if not soup:
            return None
        
        product = {
            'Product_URL': product_url,
            'Brand': 'Lauritz Knudsen',
            'Type': 'Electrical Equipment',
            'Image_Download_Status': 'Not Downloaded',
            'Brochure_Download_Status': 'Not Downloaded',
            'Downloaded_Documents': []
        }
        
        # Extract product name - try multiple methods
        product_name = ""
        nav = soup.find('nav', attrs={"aria-label": "Breadcrumb"})
        product_name = None
        if nav:
            # find all spans under the primary breadcrumb UL
            spans = nav.find('ul').find_all('span')

            # get the last non-empty span text
            for span in reversed(spans):
                text = span.get_text(strip=True)
                if text and text.lower() not in ["home", "products", "all products"]:
                    product_name = text
                    break
        product['Name'] = product_name
        
        # Extract product type from URL path
        url_path = urlparse(product_url).path
        path_parts = url_path.strip('/').split('/')
        if len(path_parts) >= 3:
            product['Product_Type'] = path_parts[-2].replace('-', ' ').title()
        
        # Get full description from category page
        if category_url:
            product['Full_Description'] = self.extract_category_description(category_url)
        
        # Extract short description from product page
        short_description = ""
        short_description = self.extract_short_description(soup)
        
        product['Short_Description'] = short_description
        
        features = []

        # 1️⃣ Find the "Features" title
        feature_title = soup.find(lambda tag: tag.name == "p" and tag.get_text(strip=True).lower() == "features")

        if feature_title:
            # 2️⃣ The block immediately after contains all features
            feature_block = feature_title.find_next_sibling("p")

            if feature_block:
                # 3️⃣ Extract nested <p> tags containing each feature
                for fp in feature_block.find_all("p"):
                    text = fp.get_text(" ", strip=True)
                    if text and ":" in text:   # Feature pattern: "Label: detail"
                        features.append(text)

        # Optional: limit features
        if features:
            product["Key_Features"] = "; ".join(features[:10])

        benefits = []

        # 1️⃣ Find the "Features" title
        benefit_title = soup.find(lambda tag: tag.name == "p" and tag.get_text(strip=True).lower() == "benefits")
        if benefit_title:
            # 2️⃣ The block immediately after contains all benefits
            benefit_block = benefit_title.find_next_sibling("p")
            if benefit_block:
                # 3️⃣ Extract nested <p> tags containing each benefit
                for fp in benefit_block.find_all("li"):
                    text = fp.get_text(" ", strip=True)
                    if text:   # benefit pattern: "Label: detail"
                        benefits.append(text)
        # Optional: limit benefits
        if benefits:
            product["Benefits"] = "; ".join(benefits[:10])


        
        category_image_url = self.extract_category_image(category_url, product_name)

        if category_image_url:
            safe_filename = re.sub(r'[<>:"/\\|?*]', '_', product_name)
            img_filename = f"{safe_filename}.jpg"
            img_path = self.output_dir / "images" / img_filename

            if self.download_file(category_image_url, img_path):
                product['Image_Path'] = "/LK/lk_ea_products/"+str(img_path.relative_to(self.output_dir))
                product['Image_Download_Status'] = 'Downloaded'
        else:
            product['Image_Path'] = ""
            product['Image_Download_Status'] = "Not Found on Category Page"

        # Enhanced document extraction
        # doc_path = self.extract_document_pdf_playwright(product_url)
        doc_path = None
        product['Brochure_Download_Status'] = 'Not Downloaded'
        if doc_path:
            product['Brochure_Path'] = "/LK/lk_ea_products/"+doc_path
            product['Brochure_Download_Status'] = 'Downloaded'
        return product
    
    def _extract_technical_specs(self, soup: BeautifulSoup, product: Dict):
        """Extract technical specifications based on product type"""
        
        # Get all text content for pattern matching
        page_text = soup.get_text()
        
        # Common specifications patterns
        spec_patterns = {
            'Voltage': r'(\d+(?:\.\d+)?)\s*[kK]?[vV](?!\w)',
            'Amperage': r'(\d+(?:\.\d+)?)\s*[aA](?!\w)',
            'Wattage': r'(\d+(?:\.\d+)?)\s*[wW](?!\w)',
            'Frequency': r'(\d+)\s*[hH][zZ]',
            'IP_Rating': r'IP(\d+)',
            'Breaking_Capacity': r'(\d+(?:\.\d+)?)\s*[kK]?A\s*(?:breaking|short.?circuit)',
            'Poles': r'(\d+)\s*[pP]ole'
        }
        
        for spec_name, pattern in spec_patterns.items():
            matches = re.findall(pattern, page_text, re.IGNORECASE)
            if matches:
                # Take the first meaningful match
                product[spec_name] = matches[0]
        
        # Product-specific specifications
        product_type = product.get('Product_Type', '').lower()
        
        if 'mcb' in product_type or 'circuit breaker' in product_type:
            # MCB specific specs
            trip_curve_match = re.search(r'([bBcCdD])\s*(?:curve|type)', page_text, re.IGNORECASE)
            if trip_curve_match:
                product['Trip_Curve'] = trip_curve_match.group(1).upper()
                
            # Current rating
            current_match = re.search(r'(\d+)\s*A\s*(?:current|rating)', page_text, re.IGNORECASE)
            if current_match:
                product['GenCurrentRating'] = current_match.group(1) + "A"
                
        elif 'switchgear' in product_type:
            # Switchgear specific specs
            voltage_match = re.search(r'(?:up to|rated)\s*(\d+)\s*kV', page_text, re.IGNORECASE)
            if voltage_match:
                product['Voltage'] = voltage_match.group(1) + "kV"
                
            short_circuit_match = re.search(r'(\d+)\s*kA.*?short.?circuit', page_text, re.IGNORECASE)
            if short_circuit_match:
                product['Breaking_Capacity'] = short_circuit_match.group(1) + "kA"
        
        elif 'switch' in product_type:
            # Switch specific specs
            operating_temp_match = re.search(r'(-?\d+).*?(?:to|-).*?(\d+).*?°C', page_text)
            if operating_temp_match:
                product['Operating_Temperature'] = f"{operating_temp_match.group(1)} to {operating_temp_match.group(2)}°C"
    
    def scrape_all_products(self):
        """Main method to scrape all products"""
        logger.info("Starting comprehensive product scraping...")
        
        # Get all category URLs
        category_urls = self.extract_product_categories()
        
        all_product_urls = []
        
        # Extract product URLs from each category and subcategory
        for category_url in category_urls:
            try:
                subcategories, direct_products = self.extract_subcategories_and_products(category_url)
                
                # Add direct products from this category
                for product_url in direct_products:
                    all_product_urls.append((product_url, category_url))
                
                # Process subcategories
                for subcat_url in subcategories:
                    _, sub_products = self.extract_subcategories_and_products(subcat_url)
                    for product_url in sub_products:
                        all_product_urls.append((product_url, subcat_url))
                    time.sleep(1)  # Be respectful between subcategory requests
                    
                time.sleep(1)  # Be respectful between category requests
                
            except Exception as e:
                logger.error(f"Error processing category {category_url}: {e}")
                continue
        
        # Remove duplicates while preserving category association
        unique_products = {}
        for product_url, category_url in all_product_urls:
            if product_url not in unique_products:
                unique_products[product_url] = category_url
        
        logger.info(f"Found {len(unique_products)} unique product URLs")
        
        # Extract details for each product
        for i, (product_url, category_url) in enumerate(unique_products.items()):
            try:
                logger.info(f"Processing product {i+1}/{len(unique_products)}: {product_url}")
                product_details = self.extract_product_details(product_url, category_url)
                
                if product_details:
                    self.products.append(product_details)
                    logger.info(f"Successfully extracted: {product_details.get('Name', 'Unknown')} with {len(product_details.get('Downloaded_Documents', []))} documents")
                else:
                    logger.warning(f"No details extracted for: {product_url}")
                
                # Be respectful - add delay between requests
                time.sleep(2)
                
            except Exception as e:
                logger.error(f"Error processing {product_url}: {e}")
                continue
        
        logger.info(f"Successfully scraped {len(self.products)} products")
        
    def save_data(self):
        """Save scraped data to JSON and Excel files"""
        if not self.products:
            logger.warning("No products to save")
            return
        
        # Save to JSON
        json_path = self.output_dir / "data" / "lk_ea_products.json"
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(self.products, f, indent=2, ensure_ascii=False)
        
        # Save to Excel
        excel_path = self.output_dir / "data" / "lk_ea_products.xlsx"
        df = pd.DataFrame(self.products)
        df.to_excel(excel_path, index=False, engine='openpyxl')
        
        logger.info(f"Data saved to {json_path} and {excel_path}")
        
        # Calculate document statistics
        total_docs = sum(len(p.get('Downloaded_Documents', [])) for p in self.products)
        products_with_docs = sum(1 for p in self.products if p.get('Downloaded_Documents'))
        
        # Print detailed summary
        print(f"\n=== SCRAPING SUMMARY ===")
        print(f"Total products scraped: {len(self.products)}")
        print(f"Images downloaded: {sum(1 for p in self.products if p.get('Image_Download_Status') == 'Downloaded')}")
        print(f"Main brochures downloaded: {sum(1 for p in self.products if p.get('Brochure_Download_Status') == 'Downloaded')}")
        print(f"Total documents downloaded: {total_docs}")
        print(f"Products with documents: {products_with_docs}")
        print(f"Products with full description: {sum(1 for p in self.products if p.get('Full_Description'))}")
        print(f"Products with short description: {sum(1 for p in self.products if p.get('Short_Description'))}")
        print(f"Products with features: {sum(1 for p in self.products if p.get('Key_Features'))}")
        
        # Show document breakdown
        doc_types = {}
        for product in self.products:
            for doc in product.get('Downloaded_Documents', []):
                doc_type = doc.get('type', 'unknown')
                doc_types[doc_type] = doc_types.get(doc_type, 0) + 1
        
        if doc_types:
            print(f"\n=== DOCUMENT BREAKDOWN ===")
            for doc_type, count in sorted(doc_types.items()):
                print(f"{doc_type.title()}: {count} documents")
        
        # Show sample data
        if self.products:
            print(f"\n=== SAMPLE PRODUCT ===")
            sample = self.products[0]
            for key, value in sample.items():
                if value and len(str(value)) > 0:
                    if key == 'Downloaded_Documents' and isinstance(value, list):
                        print(f"{key}: {len(value)} documents")
                        for i, doc in enumerate(value[:3]):  # Show first 3 docs
                            print(f"  {i+1}. {doc.get('title', 'Unknown')} ({doc.get('type', 'unknown')})")
                    else:
                        display_value = str(value)[:100] + "..." if len(str(value)) > 100 else str(value)
                        print(f"{key}: {display_value}")
        
        # Show breakdown by product type
        product_types = {}
        for product in self.products:
            ptype = product.get('Product_Type', 'Unknown')
            product_types[ptype] = product_types.get(ptype, 0) + 1
        
        print(f"\n=== PRODUCT BREAKDOWN ===")
        for ptype, count in sorted(product_types.items()):
            print(f"{ptype}: {count} products")

# def main():
#     """Main execution function"""
    
#     # Install required packages if not already installed
#     try:
#         import requests
#         import pandas as pd
#         from bs4 import BeautifulSoup
#     except ImportError:
#         print("Installing required packages...")
#         os.system("pip install requests pandas beautifulsoup4 openpyxl lxml")
    
#     # Create scraper instance
#     scraper = LKEAProductScraper()
    
#     # Option to run a quick test on a few products first
#     test_mode = input("Run in test mode (scrape only 5 products)? [y/N]: ").lower().strip() == 'y'
    
#     if test_mode:
#         # Test with a few specific URLs including the one from your screenshot
#         test_data = [
#             ("https://www.lk-ea.com/products/pump-starters-and-controllers/starter/mk-starter",
#              "https://www.lk-ea.com/products/pump-starters-and-controllers/starter"),
#             ("https://www.lk-ea.com/products/medium-voltage/air-insulated-switchgear-ais/vh1h", 
#              "https://www.lk-ea.com/products/medium-voltage/air-insulated-switchgear-ais"),
#             ("https://www.lk-ea.com/products/medium-voltage/air-insulated-switchgear-ais/vh3h", 
#              "https://www.lk-ea.com/products/medium-voltage/air-insulated-switchgear-ais"),
#             ("https://www.lk-ea.com/products/mcb-rccb-distribution-boards/miniature-circuit-breaker-mcb/exora",
#              "https://www.lk-ea.com/products/mcb-rccb-distribution-boards/miniature-circuit-breaker-mcb"),
#             ("https://www.lk-ea.com/products/mcb-rccb-distribution-boards/miniature-circuit-breaker-mcb/au",
#              "https://www.lk-ea.com/products/mcb-rccb-distribution-boards/miniature-circuit-breaker-mcb")
#         ]
        
#         logger.info("Running in test mode with 5 products...")
        
#         for product_url, category_url in test_data:
#             product_details = scraper.extract_product_details(product_url, category_url)
#             if product_details:
#                 scraper.products.append(product_details)
#             time.sleep(1)
#     else:
#         # Full scraping
#         scraper.scrape_all_products()
    
#     # Save the data
#     scraper.save_data()
def main():
    """Main execution function using pre-generated JSON"""

    import os
    import json
    import time
    import logging

    logger = logging.getLogger(__name__)

    # Create scraper instance
    scraper = LKEAProductScraper()

    product_url_json = "./lk_products_urls.json"
    processed_products_json = "./products_updated.json"

    if not os.path.exists(product_url_json):
        print(f"❌ File not found: {product_url_json}")
        return

    if not os.path.exists(processed_products_json):
        print(f"❌ File not found: {processed_products_json}")
        return

    # Load JSON files
    with open(product_url_json, "r", encoding="utf-8") as f:
        products = json.load(f)

    with open(processed_products_json, "r", encoding="utf-8") as f:
        processed_products = json.load(f)

    # Build URL sets
    processed_urls = {
        item["Product_URL"].strip()
        for item in processed_products
        if item.get("Product_URL")
    }

    missing_urls = [
        item for item in products
        if item.get("url") and item["url"].strip() not in processed_urls
    ]

    print(f"📦 Total discovered URLs   : {len(products)}")
    print(f"✅ Already processed URLs  : {len(processed_urls)}")
    print(f"🔁 Missing URLs to process : {len(missing_urls)}")

    # Optional test mode
    test_mode = input("Run in test mode (process only 5 products)? [y/N]: ").lower().strip() == "y"

    if test_mode:
        missing_urls = missing_urls[:5]
        logger.info("🧪 Running in test mode with 5 products")

    # Process ONLY missing URLs
    for idx, product in enumerate(missing_urls, start=1):
        product_url = product.get("url")
        category_url = product.get("subcategory_url")

        if not product_url or not category_url:
            logger.warning(f"⚠️ Skipping invalid entry: {product}")
            continue

        logger.info(f"[{idx}/{len(missing_urls)}] Processing {product_url}")

        try:
            product_details = scraper.extract_product_details(
                product_url,
                category_url
            )

            if product_details:
                processed_products.append(product_details)

        except Exception as e:
            logger.error(f"❌ Failed for {product_url}: {e}")

        time.sleep(1)

    # Save merged results
    with open(processed_products_json, "w", encoding="utf-8") as f:
        json.dump(processed_products, f, indent=2, ensure_ascii=False)

    print("✅ Resume processing completed successfully")

if __name__ == "__main__":
    main()
