from bs4 import BeautifulSoup
import requests
import re
from urllib.parse import urljoin, urlparse
import time
import json
import os
from typing import Set, List, Dict
import pandas as pd
from collections import defaultdict

class PolycabSolarExtractor:
    def __init__(self, product_type: str = "solar-panel", product_display_name: str = "Polycab Solar Panel"):
        """
        Initialize the comprehensive solar product extractor
        
        Args:
            product_type: 'solar-panel' or 'solar-inverter'
            product_display_name: Display name for the product type
        """
        self.base_url = "https://polycab.com"
        self.cms_base_url = "https://cms.polycab.com"
        self.product_type = product_type
        self.product_display_name = product_display_name
        
        # Create directories
        self.base_dir = f'polycab_{product_type.replace("-", "_")}_products'
        self.images_dir = os.path.join(self.base_dir, 'images')
        
        for directory in [self.base_dir, self.images_dir]:
            if not os.path.exists(directory):
                os.makedirs(directory)
        
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Cache-Control': 'max-age=0',
        })
        
        # Pattern for specifications extraction
        self.power_patterns = [
            r'(\d+(?:\.\d+)?)\s*[kK]?[wW]',
            r'(\d+(?:\.\d+)?)\s*watts?',
            r'(\d+(?:\.\d+)?)\s*kilo\s*watts?'
        ]
        
        self.voltage_patterns = [
            r'(\d+(?:\.\d+)?)\s*[vV]',
            r'(\d+(?:\.\d+)?)\s*volts?'
        ]
        
        # Solar product URLs mapping
        self.product_urls = {
            "solar-panel": "https://polycab.com/solar/solar-panel/c",
            "solar-inverter": "https://polycab.com/solar/solar-inverter/c"
        }

    def discover_product_urls(self) -> List[str]:
        """Discover solar product URLs from all pages of category"""
        product_urls = set()
        
        try:
            category_url = self.product_urls.get(self.product_type, f"{self.base_url}/solar/{self.product_type}/c")
            print(f"🔍 Fetching {self.product_type} products from: {category_url}")
            
            page = 1
            max_pages = 20
            
            while page <= max_pages:
                print(f"📄 Fetching page {page}...")
                
                page_urls = [
                    f"{category_url}?page={page}",
                    f"{category_url}?p={page}",
                    f"{category_url}/?page={page}",
                    f"{category_url}/?p={page}",
                    category_url if page == 1 else None
                ]
                
                page_product_urls = set()
                response = None
                
                for page_url in page_urls:
                    if page_url is None:
                        continue
                        
                    try:
                        response = self.session.get(page_url, timeout=30)
                        response.raise_for_status()
                        
                        soup = BeautifulSoup(response.text, 'html.parser')
                        product_links = soup.find_all('a', href=True)
                        
                        current_page_urls = set()
                        for link in product_links:
                            href = link.get('href')
                            if href and self._is_solar_product_url(href):
                                if not href.startswith('http'):
                                    href = urljoin(self.base_url, href)
                                current_page_urls.add(href)
                        
                        if current_page_urls:
                            page_product_urls = current_page_urls
                            print(f"✅ Page {page}: Found {len(current_page_urls)} products using {page_url}")
                            break
                            
                    except Exception as e:
                        print(f"⚠️  Failed to fetch {page_url}: {e}")
                        continue
                
                if not page_product_urls and response:
                    page_product_urls = self._try_ajax_pagination(category_url, page)
                
                if not page_product_urls:
                    print(f"🏁 No more products found on page {page}. Stopping pagination.")
                    break
                
                new_urls = page_product_urls - product_urls
                if not new_urls and page > 1:
                    print(f"🏁 No new products on page {page}. Reached end of pagination.")
                    break
                
                product_urls.update(page_product_urls)
                print(f"📊 Page {page}: Added {len(new_urls)} new URLs (Total: {len(product_urls)})")
                
                page += 1
                # time.sleep(2)
            
            print(f"✅ Found {len(product_urls)} total solar product URLs across {page-1} pages")
            
        except Exception as e:
            print(f"❌ Error discovering URLs: {e}")
        
        return list(product_urls)

    def _try_ajax_pagination(self, base_url: str, page: int) -> set:
        """Try to fetch products using AJAX pagination"""
        try:
            ajax_patterns = [
                f"{self.base_url}/api/products/solar/{self.product_type}?page={page}",
                f"{self.base_url}/Products/GetSolarGridPartial?page={page}&productTypeSlug={self.product_type}",
                f"{self.base_url}/Products/GetProductsGridPartial?page={page}&category={self.product_type}",
                f"{base_url}/load-more?page={page}",
            ]
            
            for ajax_url in ajax_patterns:
                try:
                    response = self.session.get(ajax_url, timeout=15)
                    if response.status_code == 200 and len(response.text) > 100:
                        try:
                            data = response.json()
                            html_content = data.get('html', '') or data.get('content', '') or str(data)
                        except:
                            html_content = response.text
                        
                        if html_content:
                            soup = BeautifulSoup(html_content, 'html.parser')
                            product_links = soup.find_all('a', href=True)
                            
                            urls = set()
                            for link in product_links:
                                href = link.get('href')
                                if href and self._is_solar_product_url(href):
                                    if not href.startswith('http'):
                                        href = urljoin(self.base_url, href)
                                    urls.add(href)
                            
                            if urls:
                                print(f"✅ AJAX success: Found {len(urls)} products")
                                return urls
                                
                except Exception as e:
                    continue
                    
        except Exception as e:
            print(f"⚠️  AJAX pagination failed: {e}")
        
        return set()

    def _is_solar_product_url(self, url: str) -> bool:
        """Check if URL is a solar product page"""
        url_lower = url.lower()
        return (
            '/p-' in url and
            ('/c-' in url or any(term in url_lower for term in [
                'solar', 'inverter', 'panel', 'topcon', 'bi-facial', 'pv-module'
            ])) and
            not any(x in url_lower for x in ['javascript:', 'mailto:', '#', '?'])
        )

    def _group_by_core_specifications(self, variants: List[Dict]) -> Dict[str, List[Dict]]:
        """Group variants by core specifications"""
        spec_groups = defaultdict(list)
        
        for variant in variants:
            if not isinstance(variant, dict):
                continue
                
            try:
                spec_signature = self._get_core_specification_signature(variant)
                # Ensure spec_signature is a string (hashable)
                if not isinstance(spec_signature, str):
                    spec_signature = str(spec_signature)
                spec_groups[spec_signature].append(variant)
            except Exception as e:
                print(f"⚠️  Error getting spec signature: {e}")
                # Use a fallback signature
                fallback_signature = f"variant_{len(spec_groups)}"
                spec_groups[fallback_signature].append(variant)
        
        return spec_groups

    def _get_core_specification_signature(self, product_data: Dict) -> str:
        """Generate signature based on core specifications"""
        try:
            # Ensure product_data is a dictionary
            if not isinstance(product_data, dict):
                return f"non_dict_{hash(str(product_data))}"
            
            # Core specs that must match for consolidation
            if self.product_type == "solar-panel":
                core_specs = [
                    'Technology_Type',
                    'Cell_Type', 
                    'Module_Efficiency',
                    'Temperature_Coefficient'
                ]
            else:  # solar-inverter
                core_specs = [
                    'Inverter_Type',
                    'Max_Efficiency',
                    'Input_Voltage_Range', 
                    'Grid_Connection_Type'
                ]
            
            spec_values = []
            for spec in core_specs:
                value = product_data.get(spec, 'N/A')
                
                # Handle different data types safely
                if value is None:
                    value = 'N/A'
                elif isinstance(value, dict):
                    # If value is a dict, convert to string representation
                    value = f"dict_{len(value)}_keys"
                elif isinstance(value, list):
                    # If value is a list, join as string
                    value = '_'.join(str(v) for v in value)
                elif not isinstance(value, str):
                    # Convert other types to string
                    value = str(value)
                
                # Clean and normalize the value
                value = value.strip().lower().replace('|', '_').replace(':', '_')
                spec_values.append(f"{spec}:{value}")
            
            signature = "|".join(spec_values)
            return signature
            
        except Exception as e:
            print(f"⚠️  Error in _get_core_specification_signature: {e}")
            print(f"Product data type: {type(product_data)}")
            if isinstance(product_data, dict):
                print(f"Product data keys: {list(product_data.keys())}")
            # Fallback signature
            return f"error_signature_{hash(str(product_data))}"

    def _get_base_product_key(self, product_data: Dict) -> str:
        """Generate base product key for grouping"""
        try:
            # Ensure product_data is a dictionary
            if not isinstance(product_data, dict):
                return f"non_dict_product_{hash(str(product_data))}"
            
            name = product_data.get('Name', '')
            product_type = product_data.get('Product_Type', '')
            
            # Handle different data types safely
            if isinstance(name, dict):
                name = f"dict_name_{len(name)}"
            elif not isinstance(name, str):
                name = str(name) if name is not None else ''
                
            if isinstance(product_type, dict):
                product_type = f"dict_type_{len(product_type)}"
            elif not isinstance(product_type, str):
                product_type = str(product_type) if product_type is not None else ''
            
            name = name.lower()
            product_type = product_type.lower()
            
            # Remove model numbers and specific variations
            base_name = re.sub(r'[A-Z]{2,}\d+[A-Z]*-[A-Z]*\d*', '', name, flags=re.IGNORECASE)
            base_name = re.sub(r'\d+[kw]+', '', base_name, flags=re.IGNORECASE)
            base_name = ' '.join(base_name.split())
            
            result = f"{product_type}_{base_name}".strip()
            # Ensure the result is a valid string
            return result if result else f"unnamed_product_{hash(str(product_data))}"
            
        except Exception as e:
            print(f"⚠️  Error in _get_base_product_key: {e}")
            print(f"Product data type: {type(product_data)}")
            # Fallback to a simple key
            return f"error_product_{hash(str(product_data))}"

    # Also, let's add some debugging to the main consolidate method:
    def consolidate_variants(self, all_product_data: List[Dict]) -> List[Dict]:
        """
        Consolidate solar product variants based on similar specs
        """
        print(f"\n🔄 Consolidating {self.product_type} variants...")
        
        # Debug: Check the input data
        print(f"📊 Input data types: {[type(item) for item in all_product_data[:3]]}")
        
        # Group products by base name and power rating
        product_groups = defaultdict(list)
        
        for i, product_data in enumerate(all_product_data):
            print(f"🔍 Processing item {i+1}/{len(all_product_data)}")
            
            # Add comprehensive type checking
            if not isinstance(product_data, dict):
                print(f"⚠️  Skipping non-dict item at index {i}: {type(product_data)}")
                print(f"    Content: {str(product_data)[:100]}...")
                continue
            
            # Check if the dict contains other dicts as values
            problematic_keys = []
            for key, value in product_data.items():
                if isinstance(value, (dict, list)) and not isinstance(value, str):
                    problematic_keys.append((key, type(value)))
            
            if problematic_keys:
                print(f"⚠️  Found problematic data types in item {i}:")
                for key, value_type in problematic_keys:
                    print(f"    {key}: {value_type}")
            
            try:
                base_key = self._get_base_product_key(product_data)
                print(f"    ✅ Base key: {base_key}")
                product_groups[base_key].append(product_data)
            except Exception as e:
                print(f"⚠️  Error processing product data at index {i}: {e}")
                print(f"Product data keys: {list(product_data.keys()) if isinstance(product_data, dict) else 'Not a dict'}")
                # Try to add with a simple fallback key
                fallback_key = f"error_product_{i}"
                product_groups[fallback_key].append(product_data)
                continue
        
        consolidated_products = []
        
        for base_key, variants in product_groups.items():
            print(f"\n🔧 Processing group: {base_key} ({len(variants)} variants)")
            
            if len(variants) == 1:
                consolidated_products.append(variants[0])
            else:
                # Group by core specifications
                try:
                    spec_groups = self._group_by_core_specifications(variants)
                    print(f"    📋 Created {len(spec_groups)} spec groups")
                    
                    for spec_signature, spec_variants in spec_groups.items():
                        if len(spec_variants) == 1:
                            consolidated_products.append(spec_variants[0])
                        else:
                            # Check if variants should be consolidated
                            if self._should_consolidate_variants(spec_variants):
                                consolidated_product = self._merge_product_variants(base_key, spec_variants)
                                consolidated_products.append(consolidated_product)
                                
                                # Show what was consolidated
                                power_ratings = set()
                                models = set()
                                for v in spec_variants:
                                    if isinstance(v, dict):
                                        power = v.get('Power_Rating', '')
                                        if isinstance(power, str) and power not in ['N/A', '']:
                                            power_ratings.add(power)
                                        model = v.get('Model_Number', '')
                                        if isinstance(model, str) and model not in ['N/A', '']:
                                            models.add(model)
                                
                                print(f"  🔗 Consolidated {len(spec_variants)} variants of: {base_key}")
                                if power_ratings:
                                    print(f"    ⚡ Power: {', '.join(sorted(power_ratings))}")
                                if models:
                                    print(f"    🏷️  Models: {', '.join(sorted(models))}")
                            else:
                                # Don't consolidate - keep as separate entries
                                consolidated_products.extend(spec_variants)
                except Exception as e:
                    print(f"⚠️  Error in spec grouping for {base_key}: {e}")
                    import traceback
                    traceback.print_exc()
                    # Fallback: add variants as-is
                    consolidated_products.extend(variants)
        
        print(f"✅ Consolidated {len(all_product_data)} products into {len(consolidated_products)} unique items")
        return consolidated_products

    
    
    def _merge_product_variants(self, base_key: str, variants: List[Dict]) -> Dict:
        """Merge multiple product variants into single entry"""
        try:
            merged = variants[0].copy()
            merged['Name'] = base_key.replace('_', ' ').title()
            
            # Collect all variants of configurable attributes
            power_ratings = []
            model_numbers = []
            prices = []
            image_paths = []
            
            for variant in variants:
                if not isinstance(variant, dict):
                    continue
                    
                # Power ratings - ensure string type
                power = variant.get('Power_Rating', '')
                if isinstance(power, str) and power and power != 'N/A':
                    power_ratings.append(power)
                
                # Model numbers - ensure string type
                model = variant.get('Model_Number', '')
                if isinstance(model, str) and model and model != 'N/A':
                    model_numbers.append(model)
                
                # Prices - ensure string type
                price = variant.get('Price', '')
                if isinstance(price, str) and price and price != 'N/A':
                    prices.append(price)
                
                # Images - ensure string type
                image_path = variant.get('Image_Path', '')
                if isinstance(image_path, str) and image_path:
                    image_paths.append(image_path)
            
            # Remove duplicates and update merged data
            unique_powers = list(dict.fromkeys(power_ratings))  # Preserve order, remove duplicates
            unique_models = list(dict.fromkeys(model_numbers))
            unique_image_paths = list(dict.fromkeys(image_paths))
            
            # Update merged data with consolidated information
            merged['Power_Rating'] = ', '.join(unique_powers) if unique_powers else 'N/A'
            merged['Model_Number'] = ', '.join(unique_models) if unique_models else 'N/A'
            merged['Price'] = self._consolidate_prices(prices)
            merged['Image_Path'] = '; '.join(unique_image_paths) if unique_image_paths else ''
            
            # Update download status
            merged['Image_Download_Status'] = 'Multiple' if len(unique_image_paths) > 1 else (variants[0].get('Image_Download_Status', 'Not Found'))
            
            return merged
            
        except Exception as e:
            print(f"⚠️  Error in _merge_product_variants: {e}")
            # Return first variant as fallback
            return variants[0] if variants else {}
    def _consolidate_prices(self, prices: List[str]) -> str:
        """Consolidate multiple prices"""
        if not prices:
            return 'N/A'
        
        unique_prices = list(set(prices))
        if len(unique_prices) == 1:
            return unique_prices[0]
        else:
            # Return range if multiple prices
            try:
                numeric_prices = []
                for price in unique_prices:
                    # Extract numeric value from price string
                    match = re.search(r'[\d,]+', price.replace('₹', '').replace('Rs.', '').replace(',', ''))
                    if match:
                        numeric_prices.append(int(match.group().replace(',', '')))
                
                if numeric_prices:
                    min_price = min(numeric_prices)
                    max_price = max(numeric_prices)
                    return f"₹{min_price:,} - ₹{max_price:,}"
            except:
                pass
            
            return ' , '.join(unique_prices)

    def extract_product_details(self, product_url: str) -> Dict[str, str]:
        """Extract detailed solar product information from a product page"""
        print(f"\n☀️ Extracting: {product_url}")
        
        # Initialize product data based on product type
        if self.product_type == "solar-panel":
            print(f"\n☀️ Extracting Solor Panel")
            product_data = self._init_solar_panel_data(product_url)
        else:
            product_data = self._init_solar_inverter_data(product_url)
        
        try:
            
            print(f"\n☀️ Getting data")
            response = self.session.get(product_url, timeout=30)
            print(f"\n☀️ Data fetched")
            
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract basic information
            product_data['Name'] = self._extract_product_name(soup)
            product_data['Price'] = self._extract_price(soup)
            product_data['Full_Description'] = self._extract_description(soup)
            product_data['Key_Features'] = self._extract_key_features(soup)
            product_data['Short_Description'] = self._extract_short_description(soup)
            # Extract specifications from table
            specs = self._extract_specifications_table(soup)
            print(f"\n☀️ Basic info extracted:",{specs})
            product_data.update(specs)
            
            # Extract power rating and model from name/title
            product_data['Power_Rating'] = self._extract_power_from_page(soup, product_data['Name'])
            product_data['Model_Number'] = self._extract_model_from_page(soup, product_data['Name'])
            
            # Extract and download image
            print(f"🔍 Looking for images for: {product_data['Name']}")
            image_url = self._extract_image_url(soup)
            if image_url:
                image_path = self.download_image(
                    f"{product_data['Name']}", 
                    image_url
                )
                if image_path:
                    product_data['Image_Path'] = f"/Polycab/Solar/{image_path}"
                    product_data['Image_Download_Status'] = 'Downloaded'
                else:
                    product_data['Image_Download_Status'] = 'Failed'
            
            print(f"✅ Extracted: {product_data['Name'][:50]}...")
            
        except Exception as e:
            print(f"❌ Error extracting from {product_url}: {e}")
            product_data['Name'] = f"Error: {str(e)}"
        
        return product_data

    def _init_solar_panel_data(self, product_url: str) -> Dict[str, str]:
        """Initialize solar panel data structure"""
        return {
            'Name': '',
            'Type': 'Solar Panel',
            'Product_Type': 'Solar Panel',
            'Product_Series': self.product_display_name,
            'Brand': 'Polycab',
            'Model_Number': '',
            'Specifications': '',
            'Key_Features': '',
            'Power_Rating': '',
            'Module_Efficiency': '',
            'Technology_Type': '',
            'Cell_Type': '',
            'Voltage_Rating': '',
            'Current_Rating': '',
            'Temperature_Coefficient': '',
            'Frame_Material': '',
            'Glass_Type': '',
            'Junction_Box': '',
            'Connector_Type': '',
            'Dimensions': '',
            'Weight': '',
            'Operating_Temperature': '',
            'Max_System_Voltage': '',
            'Max_Series_Fuse': '',
            'Certifications': '',
            'Warranty': '',
            'Application': '',
            'Price': 'N/A',
            'Full_Description': '',
            'Short_Description': '',
            'Product_URL': product_url,
            'Image_Path': '',
            'Image_Download_Status': 'Not Found'
        }

    def _init_solar_inverter_data(self, product_url: str) -> Dict[str, str]:
        """Initialize solar inverter data structure"""
        return {
            'Name': '',
            'Type': 'Solar Inverter',
            'Product_Type': 'Solar Inverter',
            'Product_Series': self.product_display_name,
            'Brand': 'Polycab',
            'Model_Number': '',
            'Specifications': '',
            'Key_Features': '',
            'Power_Rating': '',
            'Inverter_Type': '',
            'Max_Efficiency': '',
            'European_Efficiency': '',
            'Input_Voltage_Range': '',
            'MPPT_Voltage_Range': '',
            'Max_Input_Current': '',
            'Output_Voltage': '',
            'Output_Frequency': '',
            'Grid_Connection_Type': '',
            'Power_Factor': '',
            'THD': '',
            'Protection_Features': '',
            'Communication_Interface': '',
            'Display_Type': '',
            'Cooling_Method': '',
            'Operating_Temperature': '',
            'Humidity_Range': '',
            'IP_Rating': '',
            'Dimensions': '',
            'Weight': '',
            'Topology': '',
            'Certifications': '',
            'Warranty': '',
            'Application': '',
            'Price': 'N/A',
            'Full_Description': '',
            'Short_Description': '',
            'Product_URL': product_url,
            'Image_Path': '',
            'Image_Download_Status': 'Not Found'
        }

    def _extract_product_name(self, soup: BeautifulSoup) -> str:
        """Extract product name from soup"""
        # Try h2 with product name
        name_elem = soup.find('h2')
        if name_elem:
            name = name_elem.get_text().strip()
            if name and len(name) > 3:
                return name
        
        # Try title tag
        title_elem = soup.find('title')
        if title_elem:
            title = title_elem.get_text().strip()
            # Clean title
            title = title.replace('Buy Polycab', '').replace('Buy', '').replace('Polycab', '').strip()
            if '|' in title:
                title = title.split('|')[0].strip()
            return title
        
        return f'Unknown {self.product_type.title()}'

    def _extract_short_description(self, soup: BeautifulSoup) -> str:
        """Extract short description from prod__subtitle or similar"""
        subtitle_selectors = [
            'div.prod__subtitle',
            'p.prod__subtitle', 
            'div[class*="subtitle"]',
            'p[class*="subtitle"]',
            'h3[class*="subtitle"]',
            'div[class*="tagline"]'
        ]
        
        for selector in subtitle_selectors:
            elem = soup.select_one(selector)
            if elem:
                text = elem.get_text().strip()
                if text and len(text) > 10:
                    return text
        
        return ''

    def _extract_price(self, soup: BeautifulSoup) -> str:
        """Extract price from soup"""
        price_text = soup.get_text()
        
        price_patterns = [
            r'Rs.\s*([\d,]+)',
            r'₹\s*([\d,]+)',
            r'Price[:\s]Rs.\s*([\d,]+)',
            r'Price[:\s]₹\s*([\d,]+)',
            r'MRP[:\s]Rs.\s*([\d,]+)',
            r'MRP[:\s]₹\s*([\d,]+)',
        ]
        
        for pattern in price_patterns:
            match = re.search(pattern, price_text, re.IGNORECASE)
            if match:
                return f"₹{match.group(1)}"
        
        return 'N/A'

    def _extract_description(self, soup: BeautifulSoup) -> str:
        """Extract product description"""
        desc_selectors = [
            'section.prod__desc p.section__desc',
            'p.section__desc',
            'section.prod__desc p',
            'div.product-description',
            'p[class*="description"]',
            'div[class*="desc"]'
        ]
        
        for selector in desc_selectors:
            elem = soup.select_one(selector)
            if elem:
                description = elem.get_text().strip()
                if description and len(description) > 20:
                    return description
        
        return ''

    def _extract_key_features(self, soup: BeautifulSoup) -> str:
        """Extract key features/highlights"""
        features = []
        print(f"🔍 Extracting key features/highlights...")
        # Look for highlights section
        highlights_section = soup.find('section', string=lambda text: text and 'highlights' in text.lower()) or soup.find('div', class_='prod__highlights')
        print(f"🔍 highlights_section: {highlights_section}")
        if not highlights_section:
            # Try to find highlights by looking for ul after h5 containing "highlights"
            highlight_headers = soup.find_all(['h5', 'h4', 'h3'], string=lambda text: text and 'highlights' in text.lower())
            for header in highlight_headers:
                next_elem = header.find_next_sibling('ul')
                if next_elem:
                    highlights_section = next_elem
                    break
        
        if highlights_section:
            list_items = highlights_section.find_all('li')
            for item in list_items:
                text = item.get_text().strip()
                if text:
                    print(f"  ➕ Found highlight: {text}")
                    features.append(text)
        
        # If no highlights found, try to extract from general features
        if not features:
            if self.product_type == "solar-panel":
                feature_keywords = [
                    'High efficiency', 'Anti-PID', 'Bifacial technology',
                    'Temperature coefficient', 'Corrosion resistant', 'Hail resistant',
                    'Low light performance', 'Long warranty'
                ]
            else:  # solar-inverter
                feature_keywords = [
                    'High efficiency', 'MPPT tracking', 'Grid tie',
                    'LCD display', 'WiFi monitoring', 'Surge protection',
                    'Anti-islanding', 'Temperature protection'
                ]
            
            page_text = soup.get_text()
            for keyword in feature_keywords:
                if keyword.lower() in page_text.lower():
                    features.append(keyword)
        
        # Return features or fallback
        if features:
            return ' ; '.join(features)
        else:
            return ''

    def _extract_power_from_page(self, soup: BeautifulSoup, product_name: str) -> str:
        """Extract power rating from page"""
        # Check product title/heading
        title_elem = soup.find('h2')
        if title_elem:
            title_text = title_elem.get_text().strip()
            for pattern in self.power_patterns:
                match = re.search(pattern, title_text, re.IGNORECASE)
                if match:
                    value = match.group(1)
                    if 'k' in match.group().lower():
                        return f"{value} kW"
                    else:
                        return f"{value} W"
        
        return 'N/A'
    
    def _extract_specifications_table(self, soup: BeautifulSoup) -> Dict[str, str]:
        """Extract specifications from table"""
        specs = {}
        
        # Find specifications table
        table = soup.find('table')
        if table:
            rows = table.find_all('tr')
            for row in rows:
                cells = row.find_all(['td', 'th'])
                if len(cells) == 2:
                    key_elem = cells[0]
                    value_elem = cells[1]
                    
                    # Extract text content
                    key = key_elem.get_text().strip()
                    value = value_elem.get_text().strip()
                    
                    if not key or not value:
                        continue
                    
                    # Map table keys to our spec keys
                    key_lower = key.lower()
                    if self.product_type == "solar-panel":
                        self._map_panel_specifications(key, key_lower, value, specs)
                    else:  # solar-inverter
                        self._map_inverter_specifications(key, key_lower, value, specs)
        
        # Format specifications string
        spec_parts = []
        for key, value in specs.items():
            if value != 'N/A' and key != 'Specifications':
                clean_key = key.replace('_', ' ').title()
                spec_parts.append(f"{clean_key}: {value}")
        
        specs['Specifications'] = ' ; '.join(spec_parts) if spec_parts else f'Standard {self.product_type.replace("-", " ")} specifications'
        
        return specs

    def _map_panel_specifications(self, original_key: str, key_lower: str, value: str, specs: Dict):
        """Map solar panel specifications"""
        if 'power' in key_lower or 'watt' in key_lower:
            specs['Power_Rating'] = value
        elif 'efficiency' in key_lower:
            specs['Module_Efficiency'] = value
        elif 'technology' in key_lower or 'type' in key_lower:
            specs['Technology_Type'] = value
        elif 'cell' in key_lower:
            specs['Cell_Type'] = value
        elif 'voltage' in key_lower and 'max' in key_lower:
            specs['Max_System_Voltage'] = value
        elif 'voltage' in key_lower:
            specs['Voltage_Rating'] = value
        elif 'current' in key_lower:
            specs['Current_Rating'] = value
        elif 'temperature' in key_lower and 'coefficient' in key_lower:
            specs['Temperature_Coefficient'] = value
        elif 'dimension' in key_lower:
            specs['Dimensions'] = value
        elif 'weight' in key_lower:
            specs['Weight'] = value
        elif 'frame' in key_lower:
            specs['Frame_Material'] = value
        elif 'glass' in key_lower:
            specs['Glass_Type'] = value
        elif 'certification' in key_lower:
            specs['Certifications'] = value
        elif 'warranty' in key_lower:
            specs['Warranty'] = value
        else:
            # Store with original key
            clean_key = original_key.replace(' ', '_').replace('(', '').replace(')', '').replace('/', '_')
            specs[clean_key] = value

    def _map_inverter_specifications(self, original_key: str, key_lower: str, value: str, specs: Dict):
        """Map solar inverter specifications"""
        if 'power' in key_lower and ('max' in key_lower or 'rated' in key_lower):
            specs['Power_Rating'] = value
        elif 'efficiency' in key_lower and 'max' in key_lower:
            specs['Max_Efficiency'] = value
        elif 'efficiency' in key_lower and ('eu' in key_lower or 'european' in key_lower):
            specs['European_Efficiency'] = value
        elif 'input' in key_lower and 'voltage' in key_lower:
            specs['Input_Voltage_Range'] = value
        elif 'mppt' in key_lower and 'voltage' in key_lower:
            specs['MPPT_Voltage_Range'] = value
        elif 'output' in key_lower and 'voltage' in key_lower:
            specs['Output_Voltage'] = value
        elif 'frequency' in key_lower:
            specs['Output_Frequency'] = value
        elif 'thd' in key_lower:
            specs['THD'] = value
        elif 'topology' in key_lower:
            specs['Topology'] = value
        elif 'protection' in key_lower:
            specs['Protection_Features'] = value
        elif 'communication' in key_lower:
            specs['Communication_Interface'] = value
        elif 'display' in key_lower:
            specs['Display_Type'] = value
        elif 'cooling' in key_lower:
            specs['Cooling_Method'] = value
        elif 'ip' in key_lower and 'rating' in key_lower:
            specs['IP_Rating'] = value
        elif 'dimension' in key_lower:
            specs['Dimensions'] = value
        elif 'weight' in key_lower:
            specs['Weight'] = value
        elif 'certification' in key_lower:
            specs['Certifications'] = value
        elif 'warranty' in key_lower:
            specs['Warranty'] = value
        else:
            # Store with original key
            clean_key = original_key.replace(' ', '_').replace('(', '').replace(')', '').replace('/', '_')
            specs[clean_key] = value

    def _extract_model_from_page(self, soup: BeautifulSoup, product_name: str) -> str:
        """Extract model number from page"""
        # Check product title for model patterns
        title_elem = soup.find('h2')
        if title_elem:
            title_text = title_elem.get_text().strip()
            # Look for model patterns like PILGS1815-HAD, PSIT-40K-SM6, etc.
            model_patterns = [
                r'([A-Z]{2,}\d+[A-Z]*-[A-Z]*\d*)',
                r'([A-Z]+-\d+[A-Z]*-[A-Z]+\d*)',
                r'(P[A-Z]{2,}-\d+[A-Z]*)'
            ]
            
            for pattern in model_patterns:
                match = re.search(pattern, title_text)
                if match:
                    return match.group(1)
        
        return 'N/A'

    def _extract_image_url(self, soup: BeautifulSoup) -> str:
        """Extract main product image URL"""
        img_elements = soup.find_all('img')
        
        for img in img_elements:
            src = img.get('src', '')
            alt = img.get('alt', '').lower()
            
            # Skip small icons
            if any(skip in src.lower() for skip in ['icon', 'logo', 'menu', 'search', 'sticky']):
                continue
            
            # Look for product images from CMS
            if 'cms.polycab.com' in src and any(ext in src.lower() for ext in ['.png', '.jpg', '.jpeg', '.webp']):
                if any(term in src.lower() for term in ['_img_', 'product', 'solar', 'panel', 'inverter']):
                    print(f"🖼️  Found product image: {src}")
                    return src
        
        # Fallback: return first CMS image
        for img in img_elements:
            src = img.get('src', '')
            if 'cms.polycab.com' in src and any(ext in src.lower() for ext in ['.png', '.jpg', '.jpeg', '.webp']):
                print(f"🖼️  Found fallback image: {src}")
                return src
        
        print("⚠️  No image URL found")
        return ""

    def clean_filename(self, text: str, extension: str = "") -> str:
        """Create clean filename"""
        clean_text = re.sub(r'[^\w\s-]', '', text)
        clean_text = re.sub(r'\s+', '_', clean_text.strip())
        return f"{clean_text[:100]}{extension}"

    def download_image(self, product_name: str, image_url: str) -> str:
        """Download product image"""
        try:
            print(f"🔽 Downloading image for: {product_name}")
            
            filename = self.clean_filename(product_name, '_image')
            parsed_url = urlparse(image_url)
            file_ext = os.path.splitext(parsed_url.path)[1] or '.webp'
            filename += file_ext
            filepath = os.path.join(self.images_dir, filename)
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Accept': 'image/webp,image/apng,image/*,*/*;q=0.8',
                'Referer': 'https://polycab.com/',
            }
            
            response = self.session.get(image_url, stream=True, timeout=30, headers=headers)
            response.raise_for_status()
            
            with open(filepath, 'wb') as file:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        file.write(chunk)
            
            file_size = os.path.getsize(filepath)
            if file_size < 500:
                os.remove(filepath)
                print(f"❌ Removed {filename} - too small")
                return ""
            
            print(f"✅ Downloaded image: {filename} ({file_size/1024:.1f} KB)")
            return filepath
            
        except Exception as e:
            print(f"❌ Failed to download image: {e}")
            return ""

    def save_to_excel(self, product_data: List[Dict[str, str]], filename: str = None):
        """Save product data to Excel"""
        if filename is None:
            filename = f'polycab_{self.product_type.replace("-", "_")}_complete.xlsx'
        
        print(f"\n💾 Saving {self.product_type} data to Excel: {filename}")
        
        try:
            df = pd.DataFrame(product_data)
            
            # Reorder columns for better presentation
            if self.product_type == "solar-panel":
                column_order = [
                    'Name', 'Product_Type', 'Product_Series', 'Type', 'Brand', 'Model_Number',
                    'Short_Description', 'Price', 'Power_Rating', 'Module_Efficiency',
                    'Technology_Type', 'Cell_Type', 'Voltage_Rating', 'Current_Rating',
                    'Temperature_Coefficient', 'Frame_Material', 'Glass_Type',
                    'Junction_Box', 'Connector_Type', 'Dimensions', 'Weight',
                    'Operating_Temperature', 'Max_System_Voltage', 'Max_Series_Fuse',
                    'Certifications', 'Warranty', 'Application', 'Specifications',
                    'Key_Features', 'Full_Description', 'Product_URL', 'Image_Path',
                    'Image_Download_Status'
                ]
            else:  # solar-inverter
                column_order = [
                    'Name', 'Product_Type', 'Product_Series', 'Type', 'Brand', 'Model_Number',
                    'Short_Description', 'Price', 'Power_Rating', 'Inverter_Type',
                    'Max_Efficiency', 'European_Efficiency', 'Input_Voltage_Range',
                    'MPPT_Voltage_Range', 'Max_Input_Current', 'Output_Voltage',
                    'Output_Frequency', 'Grid_Connection_Type', 'Power_Factor',
                    'THD', 'Protection_Features', 'Communication_Interface',
                    'Display_Type', 'Cooling_Method', 'Operating_Temperature',
                    'Humidity_Range', 'IP_Rating', 'Dimensions', 'Weight',
                    'Topology', 'Certifications', 'Warranty', 'Application',
                    'Specifications', 'Key_Features', 'Full_Description',
                    'Product_URL', 'Image_Path', 'Image_Download_Status'
                ]
            
            # Ensure all columns exist
            for col in column_order:
                if col not in df.columns:
                    df[col] = 'N/A'
            
            # Reorder DataFrame columns
            df = df[column_order]
            
            with pd.ExcelWriter(filename, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name=f'{self.product_type.title()} Data', index=False)
                
                # Format worksheet
                workbook = writer.book
                worksheet = writer.sheets[f'{self.product_type.title()} Data']
                
                # Adjust column widths
                for column in worksheet.columns:
                    max_length = 0
                    column_cells = [cell for cell in column]
                    for cell in column_cells:
                        try:
                            if len(str(cell.value)) > max_length:
                                max_length = len(str(cell.value))
                        except:
                            pass
                    adjusted_width = min(max_length + 2, 50)
                    worksheet.column_dimensions[column_cells[0].column_letter].width = adjusted_width
            
            print(f"✅ Excel file saved: {filename}")
            print(f"☀️ Total {self.product_type} products: {len(product_data)}")
            
            # Summary statistics
            downloaded_images = sum(1 for f in product_data if f['Image_Download_Status'] == 'Downloaded')
            
            print(f"🖼️  Images downloaded: {downloaded_images}/{len(product_data)}")
            
        except Exception as e:
            print(f"❌ Error saving Excel: {e}")

    def run(self):
        """Main execution method"""
        print(f"🚀 Polycab {self.product_display_name} Extractor")
        print("=" * 60)
        print(f"📁 Working directory: {self.base_dir}")
        
        try:
            # 1. Discover product URLs
            product_urls = self.discover_product_urls()
            print(f"\n🔍 Found {len(product_urls)} {self.product_type} URLs")
            
            if not product_urls:
                print(f"❌ No {self.product_type} URLs found!")
                return
            
            # Show first few URLs
            print("\n📋 Sample URLs:")
            for i, url in enumerate(product_urls[:3], 1):
                print(f"  {i}. {url}")
            
            if len(product_urls) > 3:
                print(f"  ... and {len(product_urls) - 3} more")
            
            # 2. Extract product data
            all_product_data = []
            
            for i, url in enumerate(product_urls, 1):
                print(f"\n{'='*50}")
                print(f"[{i}/{len(product_urls)}] Processing Product {i}")
                print(f"{'='*50}")
                
                product_data = self.extract_product_details(url)
                all_product_data.append(product_data)
                
                # time.sleep(2)
            
            # 3. Consolidate variants
            if all_product_data:
                consolidated_products = self.consolidate_variants(all_product_data)
                
                # Save final results
                excel_filename = os.path.join(self.base_dir, f'polycab_{self.product_type.replace("-", "_")}_complete.xlsx')
                self.save_to_excel(consolidated_products, excel_filename)
                
                # Save JSON
                json_filename = os.path.join(self.base_dir, f'polycab_{self.product_type.replace("-", "_")}_complete.json')
                with open(json_filename, 'w', encoding='utf-8') as f:
                    json.dump(consolidated_products, f, indent=2, ensure_ascii=False)
                
                print(f"\n🎉 {self.product_type.title()} Extraction Complete!")
                print(f"✅ Successfully processed: {len(consolidated_products)} unique {self.product_type} products")
                print(f"📊 Files saved in: {self.base_dir}")
                
            else:
                print(f"❌ No {self.product_type} data extracted!")
                
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
            import traceback
            traceback.print_exc()


def main():
    """Main function with solar product options"""
    
    # Available solar product types
    available_products = {
        '1': ('solar-panel', 'Polycab Solar Panel'),
        '2': ('solar-inverter', 'Polycab Solar Inverter'),
        '3': ('custom', 'Custom (Enter your own)')
    }
    
    print("☀️ Polycab Solar Product Extractor")
    print("=" * 50)
    print("📋 Available solar product types:\n")
    
    # Display all product categories
    for key, (slug, display_name) in available_products.items():
        print(f"  {key}. {display_name}")
    
    # Get user choice - supports multiple selections and ranges
    print("\n☀️ Selection Options:")
    print("  • Single: 1")
    print("  • Multiple: 1,2") 
    print("  • All: 1-2")
    
    choice_input = input(f"\nSelect solar product type(s) (1-3): ").strip()
    
    # Parse the input to get list of choices
    selected_choices = parse_choice_input(choice_input, available_products.keys())
    
    if not selected_choices:
        print("Invalid choice. Using default Solar Panel.")
        selected_choices = ['1']
    
    # Display selected product types
    print(f"\n🎯 Selected Solar Product Types ({len(selected_choices)}):")
    selected_products = []
    
    for choice in selected_choices:
        if choice in available_products:
            product_slug, display_name = available_products[choice]
            if product_slug == 'custom':
                product_slug = input(f"Enter product type slug for choice {choice}: ").strip()
                display_name = input(f"Enter display name for choice {choice}: ").strip()
            selected_products.append((product_slug, display_name))
            print(f"  ✅ {display_name} ({product_slug})")
    
    print(f"\n📋 This will extract for {len(selected_products)} solar product type(s):")
    print("  ✅ Product details (name, specs, features, etc.)")
    print("  ⚡ Power & Model consolidation (merge similar variants)")
    print("  🖼️  Product images")
    print("  💰 Price information")
    print("  🔌 Technical specifications (Power, Efficiency, Voltage, etc.)")
    print("  💾 Save everything to Excel with proper structure")
    print("  🔄 Multi-page crawling for complete data")
    
    # Show what consolidation strategy will be used
    print(f"\n🔧 Consolidation Strategy:")
    print("  📝 Group products by base name and technology type")
    print("  🔍 Match core specifications (Technology, Efficiency, etc.)")
    print("  ⚡ Merge variants with same specs but different Power/Models")
    print("  📊 Create comma-separated lists: Power Ratings, Models")
    print("  💡 Example: '540W Panel' + '545W Panel' → 'Solar Panel (540W, 545W)'")
    
    # Confirmation
    confirm = input(f"\nProceed with comprehensive extraction for all {len(selected_products)} solar product types? (y/N): ").strip().lower()
    if confirm not in ['y', 'yes']:
        print("❌ Extraction cancelled.")
        return
    
    # Run the comprehensive extractor for each selected product type
    total_products = len(selected_products)
    for i, (product_slug, display_name) in enumerate(selected_products, 1):
        print(f"\n{'='*60}")
        print(f"🔄 Processing {i}/{total_products}: {display_name}")
        print(f"{'='*60}")
        
        try:
            extractor = PolycabSolarExtractor(product_slug, display_name)
            extractor.run()
            print(f"✅ Completed: {display_name}")
        except Exception as e:
            print(f"❌ Error processing {display_name}: {str(e)}")
            continue
    
    print(f"\n🎉 Batch extraction completed for {total_products} solar product types!")


def parse_choice_input(choice_input, valid_keys):
    """Parse user input for multiple selections and ranges"""
    choices = []
    
    try:
        # Split by comma for multiple selections
        parts = [part.strip() for part in choice_input.split(',')]
        
        for part in parts:
            if '-' in part:
                # Handle range (e.g., "1-2")
                start, end = part.split('-')
                start, end = int(start.strip()), int(end.strip())
                choices.extend([str(i) for i in range(start, end + 1)])
            else:
                # Single choice
                choices.append(part)
        
        # Filter to only valid keys and remove duplicates
        choices = list(set([choice for choice in choices if choice in valid_keys]))
        choices.sort(key=lambda x: int(x))  # Sort numerically
    except ValueError:
        return []
    
    return choices


def run_all_solar_products():
    """Quick function to run all solar product types"""
    available_products = {
        '1': ('solar-panel', 'Polycab Solar Panel'),
        '2': ('solar-inverter', 'Polycab Solar Inverter'),
    }
    
    print("☀️ Polycab All Solar Products Batch Extractor")
    print("=" * 50)
    print("📋 Will process the following solar product types:\n")
    
    for key, (slug, display_name) in available_products.items():
        print(f"  {key}. {display_name}")
    
    confirm = input(f"\nProceed with extraction for all {len(available_products)} solar product types? (y/N): ").strip().lower()
    if confirm not in ['y', 'yes']:
        print("❌ Extraction cancelled.")
        return
    
    # Run extraction for each product type
    total_products = len(available_products)
    for i, (key, (product_slug, display_name)) in enumerate(available_products.items(), 1):
        print(f"\n{'='*60}")
        print(f"🔄 Processing {i}/{total_products}: {display_name}")
        print(f"{'='*60}")
        
        try:
            extractor = PolycabSolarExtractor(product_slug, display_name)
            extractor.run()
            print(f"✅ Completed: {display_name}")
        except Exception as e:
            print(f"❌ Error processing {display_name}: {str(e)}")
            continue
    
    print(f"\n🎉 Batch extraction completed for all {total_products} solar product types!")


if __name__ == "__main__":
    # Option 1: Use the interactive main function
    main()
    
    # Option 2: Or use the run all function
    # run_all_solar_products()
