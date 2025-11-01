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

class PolycabWireExtractor:
    def __init__(self):
        """
        Initialize the comprehensive wire extractor
        """
        self.base_url = "https://polycab.com"
        self.cms_base_url = "https://cms.polycab.com"
        self.wire_category_url = "https://polycab.com/wires/c"
        
        # Create directories
        self.base_dir = 'polycab_wires'
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
        
        # Color keywords for consolidation
        self.color_keywords = [
            'red', 'black', 'white', 'blue', 'green', 'yellow', 'brown', 
            'grey', 'gray', 'orange', 'pink', 'purple', 'violet', 'amber',
            'silver', 'gold', 'copper', 'aluminum', 'multicolor', 'multi'
        ]
    
    def discover_wire_urls(self) -> List[str]:
        """Discover wire product URLs from all pages of category"""
        wire_urls = set()
        
        try:
            print(f"🔍 Fetching wire products from: {self.wire_category_url}")
            
            page = 1
            max_pages = 20
            
            while page <= max_pages:
                print(f"📄 Fetching page {page}...")
                
                page_urls = [
                    f"{self.wire_category_url}?page={page}",
                    f"{self.wire_category_url}?p={page}",
                    f"{self.wire_category_url}/?page={page}",
                    f"{self.wire_category_url}/?p={page}",
                    self.wire_category_url if page == 1 else None
                ]
                
                page_wire_urls = set()
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
                            if href and self._is_wire_product_url(href):
                                if not href.startswith('http'):
                                    href = urljoin(self.base_url, href)
                                current_page_urls.add(href)
                        
                        if current_page_urls:
                            page_wire_urls = current_page_urls
                            print(f"✅ Page {page}: Found {len(current_page_urls)} products using {page_url}")
                            break
                            
                    except Exception as e:
                        print(f"⚠️  Failed to fetch {page_url}: {e}")
                        continue
                
                if not page_wire_urls and response:
                    page_wire_urls = self._try_ajax_pagination(page)
                
                if not page_wire_urls:
                    print(f"🏁 No more products found on page {page}. Stopping pagination.")
                    break
                
                new_urls = page_wire_urls - wire_urls
                if not new_urls and page > 1:
                    print(f"🏁 No new products on page {page}. Reached end of pagination.")
                    break
                
                wire_urls.update(page_wire_urls)
                print(f"📊 Page {page}: Added {len(new_urls)} new URLs (Total: {len(wire_urls)})")
                
                page += 1
                time.sleep(2)
            
            print(f"✅ Found {len(wire_urls)} total wire product URLs across {page-1} pages")
            
        except Exception as e:
            print(f"❌ Error discovering URLs: {e}")
        
        return list(wire_urls)

    def _try_ajax_pagination(self, page: int) -> set:
        """Try to fetch products using AJAX pagination"""
        try:
            ajax_patterns = [
                f"{self.base_url}/api/products/wires?page={page}",
                f"{self.base_url}/Products/GetWireGridPartial?page={page}",
                f"{self.base_url}/Products/GetProductsGridPartial?page={page}&category=wires",
                f"{self.wire_category_url}/load-more?page={page}",
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
                                if href and self._is_wire_product_url(href):
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

    def _is_wire_product_url(self, url: str) -> bool:
        """Check if URL is a wire product page"""
        url_lower = url.lower()
        return (
            '/p-' in url and 
            ('wire' in url_lower or 'cable' in url_lower or '/c-' in url_lower) and
            not any(x in url_lower for x in ['javascript:', 'mailto:', '#', '?'])
        )

    def consolidate_wire_variants(self, all_wire_data: List[Dict]) -> List[Dict]:
        """
        Consolidate wire variants based on identical specs except color
        
        Consolidation Strategy:
        1. Group by all specifications EXCEPT color
        2. If specs match but colors differ, merge into single entry
        3. Create comma-separated color list
        4. Keep separate if any other spec differs
        """
        print("\n🔄 Consolidating wire variants by color...")
        
        # Group wires by core specifications (excluding color)
        wire_groups = defaultdict(list)
        
        for wire_data in all_wire_data:
            spec_signature = self._get_core_wire_specification_signature(wire_data)
            wire_groups[spec_signature].append(wire_data)
        
        consolidated_wires = []
        
        for spec_signature, variants in wire_groups.items():
            if len(variants) == 1:
                consolidated_wires.append(variants[0])
            else:
                # Check if variants differ only in color
                if self._should_consolidate_wire_variants(variants):
                    consolidated_product = self._merge_wire_color_variants(variants)
                    consolidated_wires.append(consolidated_product)
                    
                    # Show what was consolidated
                    colors = set()
                    for v in variants:
                        if v.get('Color'):
                            colors.update([c.strip() for c in v['Color'].split(',')])
                    
                    print(f"  🔗 Consolidated {len(variants)} color variants of: {consolidated_product['Name']}")
                    if colors:
                        print(f"    🎨 Colors: {', '.join(sorted(colors))}")
                else:
                    # Don't consolidate - keep as separate entries
                    consolidated_wires.extend(variants)
        
        print(f"✅ Consolidated {len(all_wire_data)} products into {len(consolidated_wires)} unique items")
        return consolidated_wires

    def _get_core_wire_specification_signature(self, wire_data: Dict) -> str:
        """Generate signature based on core specifications (excluding color)"""
        # Core specs that must match for consolidation (excluding color)
        core_specs = [
            'Type',
            'Wire_Type',
            'Cross_Sectional_Area',
            'Core_Configuration',
            'Voltage_Rating',
            'Insulation_Type', 
            'Standards',
            'Length',
            'Packing',
            'Conductor_Material',
            'Jacket_Material',
            'Fire_Retardant',
            'Halogen_Free',
            'Brand_Series'
        ]
        
        spec_values = []
        for spec in core_specs:
            value = wire_data.get(spec, 'N/A')
            if isinstance(value, str):
                value = value.strip().lower()
            spec_values.append(f"{spec}:{value}")
        
        return "|".join(spec_values)

    def _should_consolidate_wire_variants(self, variants: List[Dict]) -> bool:
        """Check if wire variants should be consolidated (only color differs)"""
        if len(variants) < 2:
            return False
        
        # Get all colors
        all_colors = set()
        
        for variant in variants:
            color = variant.get('Color', '')
            if color and color not in ['N/A', '']:
                color_list = [c.strip().lower() for c in color.split(',')]
                all_colors.update(color_list)
        
        # Check if we have multiple colors
        has_multiple_colors = len(all_colors) > 1
        
        print(f"    🎨 Colors found: {len(all_colors)} - {', '.join(sorted(all_colors)) if all_colors else 'None'}")
        print(f"    🤔 Should consolidate: {has_multiple_colors}")
        
        return has_multiple_colors

    def _merge_wire_color_variants(self, variants: List[Dict]) -> Dict:
        """Merge multiple wire color variants into single entry"""
        merged = variants[0].copy()
        
        # Collect all colors
        colors = []
        image_paths = []
        prices = []
        
        for variant in variants:
            # Colors
            variant_color = variant.get('Color', '')
            if variant_color and variant_color not in ['N/A', '']:
                colors.extend([c.strip() for c in variant_color.split(',') if c.strip()])
            
            # Prices
            if variant.get('Price') and variant['Price'] != 'N/A':
                prices.append(variant['Price'])
            
            # Images
            if variant.get('Image_Path'):
                image_paths.append(variant['Image_Path'])
        
        # Remove duplicates and update merged data
        unique_colors = list(dict.fromkeys(colors))  # Preserve order, remove duplicates
        
        # Update merged data with consolidated information
        merged['Color'] = ', '.join(unique_colors) if unique_colors else 'Multiple Colors Available'
        merged['Price'] = self._consolidate_wire_prices(prices)
        merged['Image_Path'] = '; '.join(image_paths) if image_paths else ''
        
        # Update download status
        merged['Image_Download_Status'] = 'Multiple' if len(image_paths) > 1 else (variants[0].get('Image_Download_Status', 'Not Found'))
        
        return merged

    def _consolidate_wire_prices(self, prices: List[str]) -> str:
        """Consolidate multiple prices for wire variants"""
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

    def extract_wire_details(self, wire_url: str) -> Dict[str, str]:
        """Extract detailed wire information from a product page"""
        print(f"\n🔌 Extracting: {wire_url}")
        
        wire_data = {
            'Name': '',
            'Type': 'Wire',
            'Wire_Type': '',  # House Wire, Armoured Cable, etc.
            'Brand': 'Polycab',
            'Brand_Series': '',  # SUPREMA, MAXIMA+, etc.
            'Model_Number': '',
            'Cross_Sectional_Area': '',  # 1.5mm², 2.5mm², etc.
            'Core_Configuration': '',  # Single Core, Multi Core, etc.
            'Voltage_Rating': '',  # 1100V, 650/1100V, etc.
            'Insulation_Type': '',  # PVC, XLPE, etc.
            'Conductor_Material': '',  # Copper, Aluminum
            'Jacket_Material': '',
            'Standards': '',  # IS 694, IS 1554, etc.
            'Length': '',  # 90M, 180M, etc.
            'Packing': '',
            'Color': '',
            'Fire_Retardant': '',
            'Halogen_Free': '',
            'Temperature_Rating': '',
            'Current_Rating': '',
            'Specifications': '',
            'Key_Features': '',
            'Price': 'N/A',
            'Full_Description': '',
            'Short_Description': '',
            'Product_URL': wire_url,
            'Image_Path': '',
            'Image_Download_Status': 'Not Found'
        }
        
        try:
            response = self.session.get(wire_url, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract basic information
            wire_data['Name'] = self._extract_wire_name(soup)
            wire_data['Price'] = self._extract_price(soup)
            wire_data['Full_Description'] = self._extract_description(soup)
            wire_data['Key_Features'] = self._extract_key_features(soup)
            wire_data['Short_Description'] = self._extract_short_description(soup)
            
            # Extract specifications from table and text
            specs = self._extract_wire_specifications(soup)
            wire_data.update(specs)
            
            # Extract color from page
            wire_data['Color'] = self._extract_color_from_page(soup, wire_data['Name'])
            
            # Extract brand series
            wire_data['Brand_Series'] = self._extract_brand_series(wire_data['Name'])
            
            # Extract and download image
            print(f"🔍 Looking for images for: {wire_data['Name']}")
            image_url = self._extract_image_url(soup)
            if image_url:
                image_path = self.download_image(wire_data['Name'] + "_" + wire_data.get('Color', ''), image_url)
                if image_path:
                    wire_data['Image_Path'] = "/Polycab/Wires/" + image_path
                    wire_data['Image_Download_Status'] = 'Downloaded'
                else:
                    wire_data['Image_Download_Status'] = 'Failed'
            
            print(f"✅ Extracted: {wire_data['Name'][:50]}...")
            
        except Exception as e:
            print(f"❌ Error extracting from {wire_url}: {e}")
            wire_data['Name'] = f"Error: {str(e)}"
        
        return wire_data

    def _extract_wire_name(self, soup: BeautifulSoup) -> str:
        """Extract wire product name from soup"""
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
        
        return 'Unknown Wire Product'

    def _extract_short_description(self, soup: BeautifulSoup) -> str:
        """Extract short description from prod__subtitle"""
        subtitle_elem = soup.find('div', class_='prod__subtitle')
        if subtitle_elem:
            short_desc = subtitle_elem.get_text().strip()
            if short_desc:
                return short_desc
        
        # Fallback to other subtitle-like elements
        subtitle_selectors = [
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
            r'Rs\.\s*([\d,]+)',
            r'₹\s*([\d,]+)',
            r'Price[:\s]*Rs\.\s*([\d,]+)',
            r'Price[:\s]*₹\s*([\d,]+)',
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
        
        # Look in prod__desc section
        prod_desc_section = soup.find('section', class_='prod__desc')
        if prod_desc_section:
            paragraphs = prod_desc_section.find_all('p')
            for p in paragraphs:
                text = p.get_text().strip()
                if text and len(text) > 20:
                    return text
        
        return ''

    def _extract_key_features(self, soup: BeautifulSoup) -> str:
        """Extract key features/highlights for wires"""
        features = []
        
        # Look for features in the specific Polycab structure
        features_section = soup.find('div', class_='prod__highlights')
        if features_section:
            highlight_list = features_section.find('ul')
            if highlight_list:
                list_items = highlight_list.find_all('li')
                for item in list_items:
                    text = item.get_text().strip()
                    if text:
                        features.append(text)
        
        # Look for common wire features in text
        page_text = soup.get_text().upper()
        
        wire_features = [
            ('FIRE RETARDANT', 'Fire Retardant'),
            ('HALOGEN FREE', 'Halogen Free'),
            ('LOW SMOKE', 'Low Smoke'),
            ('HIGH CONDUCTIVITY', 'High Conductivity'),
            ('COPPER CONDUCTOR', 'Copper Conductor'),
            ('PVC INSULATED', 'PVC Insulated'),
            ('XLPE', 'XLPE Insulated'),
            ('FLAME RETARDANT', 'Flame Retardant'),
            ('IS 694', 'IS 694 Standard'),
            ('IS 1554', 'IS 1554 Standard'),
            ('BIS APPROVED', 'BIS Approved'),
            ('RoHS COMPLIANT', 'RoHS Compliant')
        ]
        
        for search_term, feature_text in wire_features:
            if search_term in page_text and feature_text not in features:
                features.append(feature_text)
        
        # Return features or fallback
        if features:
            return ' , '.join(features)
        else:
            return 'High quality copper conductor | PVC insulated | IS standard compliant'

    def _extract_wire_specifications(self, soup: BeautifulSoup) -> Dict[str, str]:
        """Extract specifications from table and text"""
        specs = {
            'Wire_Type': 'N/A',
            'Cross_Sectional_Area': 'N/A',
            'Core_Configuration': 'N/A',
            'Voltage_Rating': 'N/A',
            'Insulation_Type': 'N/A',
            'Conductor_Material': 'N/A',
            'Jacket_Material': 'N/A',
            'Standards': 'N/A',
            'Length': 'N/A',
            'Packing': 'N/A',
            'Fire_Retardant': 'N/A',
            'Halogen_Free': 'N/A',
            'Temperature_Rating': 'N/A',
            'Current_Rating': 'N/A'
        }
        
        # Find specifications table
        table = soup.find('table')
        if table:
            rows = table.find_all('tr')
            for row in rows:
                cells = row.find_all(['td', 'th'])
                if len(cells) == 2:
                    key = cells[0].get_text().strip().lower()
                    value = cells[1].get_text().strip()
                    
                    if any(x in key for x in ['cross section', 'area', 'size']):
                        specs['Cross_Sectional_Area'] = value
                    elif any(x in key for x in ['core', 'conductor']):
                        specs['Core_Configuration'] = value
                    elif any(x in key for x in ['voltage', 'volt']):
                        specs['Voltage_Rating'] = value
                    elif 'insulation' in key:
                        specs['Insulation_Type'] = value
                    elif 'material' in key and 'conductor' in key:
                        specs['Conductor_Material'] = value
                    elif 'jacket' in key or 'sheath' in key:
                        specs['Jacket_Material'] = value
                    elif any(x in key for x in ['standard', 'is ', 'bs ', 'iec']):
                        specs['Standards'] = value
                    elif any(x in key for x in ['length', 'meter', 'm ']):
                        specs['Length'] = value
                    elif 'packing' in key:
                        specs['Packing'] = value
                    elif 'fire retardant' in key or 'flame retardant' in key:
                        specs['Fire_Retardant'] = value
                    elif 'halogen' in key:
                        specs['Halogen_Free'] = value
                    elif 'temperature' in key:
                        specs['Temperature_Rating'] = value
                    elif 'current' in key and 'rating' in key:
                        specs['Current_Rating'] = value
        
        # Extract from product text/description
        self._extract_wire_specs_from_text(soup, specs)
        
        # Determine wire type from name/description
        specs['Wire_Type'] = self._determine_wire_type(soup)
        
        # Format specifications string
        spec_parts = []
        for key, value in specs.items():
            if value != 'N/A':
                clean_key = key.replace('_', ' ').title()
                spec_parts.append(f"{clean_key}: {value}")
        
        specs['Specifications'] = ' ; '.join(spec_parts) if spec_parts else 'Standard wire specifications'
        
        return specs

    def _extract_wire_specs_from_text(self, soup: BeautifulSoup, specs: Dict[str, str]):
        """Extract specs from product text/description"""
        text = soup.get_text().lower()
        
        # Extract cross-sectional area
        if specs['Cross_Sectional_Area'] == 'N/A':
            area_patterns = [
                r'(\d+(?:\.\d+)?)\s*sq\s*mm',
                r'(\d+(?:\.\d+)?)\s*mm²',
                r'(\d+(?:\.\d+)?)\s*sqmm'
            ]
            for pattern in area_patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    specs['Cross_Sectional_Area'] = f"{match.group(1)} Sq. MM"
                    break
        
        # Extract voltage rating
        if specs['Voltage_Rating'] == 'N/A':
            voltage_patterns = [
                r'(\d+/\d+)\s*v\b',
                r'(\d+)\s*volts?\b',
                r'(\d+)\s*v\b'
            ]
            for pattern in voltage_patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    specs['Voltage_Rating'] = f"{match.group(1)}V"
                    break
        
        # Extract length
        if specs['Length'] == 'N/A':
            length_patterns = [
                r'(\d+)\s*meters?\b',
                r'(\d+)\s*m\b',
                r'(\d+)\s*mtr\b'
            ]
            for pattern in length_patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    specs['Length'] = f"{match.group(1)}M"
                    break
        
        # Extract conductor material
        if specs['Conductor_Material'] == 'N/A':
            if 'copper' in text:
                specs['Conductor_Material'] = 'Copper'
            elif 'aluminum' in text or 'aluminium' in text:
                specs['Conductor_Material'] = 'Aluminum'
        
        # Extract insulation type
        if specs['Insulation_Type'] == 'N/A':
            if 'pvc' in text:
                specs['Insulation_Type'] = 'PVC'
            elif 'xlpe' in text:
                specs['Insulation_Type'] = 'XLPE'
        
        # Extract standards
        if specs['Standards'] == 'N/A':
            standard_patterns = [
                r'is\s*(\d+)',
                r'bs\s*(\d+)',
                r'iec\s*(\d+)'
            ]
            for pattern in standard_patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    prefix = match.group(0).split()[0].upper()
                    specs['Standards'] = f"{prefix} {match.group(1)}"
                    break

    def _determine_wire_type(self, soup: BeautifulSoup) -> str:
        """Determine wire type from page content"""
        text = soup.get_text().lower()
        
        wire_types = [
            ('house wire', 'House Wire'),
            ('armoured cable', 'Armoured Cable'),
            ('armored cable', 'Armoured Cable'), 
            ('power cable', 'Power Cable'),
            ('building wire', 'Building Wire'),
            ('flexible cable', 'Flexible Cable'),
            ('control cable', 'Control Cable'),
            ('instrumentation cable', 'Instrumentation Cable'),
            ('coaxial cable', 'Coaxial Cable'),
            ('telephone cable', 'Telephone Cable'),
            ('data cable', 'Data Cable'),
            ('submersible cable', 'Submersible Cable'),
            ('solar cable', 'Solar Cable')
        ]
        
        for search_term, wire_type in wire_types:
            if search_term in text:
                return wire_type
        
        return 'House Wire'  # Default

    def _extract_brand_series(self, wire_name: str) -> str:
        """Extract brand series from wire name"""
        wire_name_upper = wire_name.upper()
        
        series_names = [
            'SUPREMA', 'MAXIMA+', 'MAXIMA PLUS', 'PRIMMA', 'OPTIMA+', 'OPTIMA PLUS',
            'ETIRA', 'GREENWIRE', 'GREEN WIRE', 'LF FR'
        ]
        
        for series in series_names:
            if series in wire_name_upper:
                return series
        
        return 'Standard'

    def _extract_color_from_page(self, soup: BeautifulSoup, wire_name: str) -> str:
        """Extract wire color from page"""
        # Look for the specific colorName span element
        color_elem = soup.find('span', id='colorName')
        if color_elem:
            color_text = color_elem.get_text().strip()
            if color_text:
                return color_text.title()
        
        # Look for color in product description
        desc_elem = soup.find('p', class_='prod__desc no-pipe')
        if desc_elem:
            desc_text = desc_elem.get_text().strip()
            color_match = re.match(r'^([^(]+)', desc_text)
            if color_match:
                color_text = color_match.group(1).strip()
                if color_text and any(color in color_text.lower() for color in self.color_keywords):
                    return color_text.title()
        
        # Extract from wire name
        wire_name_lower = wire_name.lower()
        for color in self.color_keywords:
            if color in wire_name_lower:
                return color.title()
        
        # Look in page text for color mentions
        text = soup.get_text().lower()
        for color in self.color_keywords:
            if f' {color} ' in text or f'{color} wire' in text:
                return color.title()
        
        return 'Red'  # Default for house wires

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
                if any(term in src.lower() for term in ['_img_', 'product', 'wire', 'cable']):
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

    def download_image(self, wire_name: str, image_url: str) -> str:
        """Download wire image"""
        try:
            print(f"🔽 Downloading image for: {wire_name}")
            
            filename = self.clean_filename(wire_name, '_image')
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
            return filename
            
        except Exception as e:
            print(f"❌ Failed to download image: {e}")
            return ""

    def save_to_excel(self, wire_data: List[Dict[str, str]], filename: str = None):
        """Save wire data to Excel"""
        if filename is None:
            filename = 'polycab_wires_complete.xlsx'
        
        print(f"\n💾 Saving wire data to Excel: {filename}")
        
        try:
            df = pd.DataFrame(wire_data)
            
            # Reorder columns for better presentation
            column_order = [
                'Name', 'Type', 'Wire_Type', 'Brand', 'Brand_Series', 'Model_Number',
                'Short_Description', 'Price', 'Color', 'Cross_Sectional_Area', 
                'Core_Configuration', 'Voltage_Rating', 'Length', 'Packing',
                'Insulation_Type', 'Conductor_Material', 'Jacket_Material',
                'Standards', 'Fire_Retardant', 'Halogen_Free', 'Temperature_Rating', 'Current_Rating',
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
                df.to_excel(writer, sheet_name='Wire Data', index=False)
                
                # Format worksheet
                workbook = writer.book
                worksheet = writer.sheets['Wire Data']
                
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
            print(f"🔌 Total wire products: {len(wire_data)}")
            
            # Summary statistics
            downloaded_images = sum(1 for f in wire_data if f['Image_Download_Status'] == 'Downloaded')
            colors_consolidated = sum(1 for f in wire_data if ',' in f.get('Color', ''))
            
            print(f"🖼️  Images downloaded: {downloaded_images}/{len(wire_data)}")
            print(f"🎨 Color variants consolidated: {colors_consolidated}")
            
        except Exception as e:
            print(f"❌ Error saving Excel: {e}")

    def run(self):
        """Main execution method"""
        print(f"🚀 Polycab Wire Extractor with Color Consolidation")
        print("=" * 60)
        print(f"📁 Working directory: {self.base_dir}")
        
        try:
            # 1. Discover wire URLs
            wire_urls = self.discover_wire_urls()
            print(f"\n🔍 Found {len(wire_urls)} wire URLs")
            
            if not wire_urls:
                print("❌ No wire URLs found!")
                return
            
            # Show first few URLs
            print("\n📋 Sample URLs:")
            for i, url in enumerate(wire_urls[:3], 1):
                print(f"  {i}. {url}")
            
            if len(wire_urls) > 3:
                print(f"  ... and {len(wire_urls) - 3} more")
            
            # 2. Extract wire data
            all_wire_data = []
            
            for i, url in enumerate(wire_urls, 1):
                print(f"\n{'='*50}")
                print(f"[{i}/{len(wire_urls)}] Processing Wire Product {i}")
                print(f"{'='*50}")
                
                wire_data = self.extract_wire_details(url)
                all_wire_data.append(wire_data)
                
                time.sleep(2)
            
            # 3. Consolidate color variants
            if all_wire_data:
                consolidated_wires = self.consolidate_wire_variants(all_wire_data)
                
                # Save original data (before consolidation)
                excel_filename_original = os.path.join(self.base_dir, 'polycab_wires_raw.xlsx')
                self.save_to_excel(all_wire_data, excel_filename_original)
                
                # Save consolidated data
                excel_filename_consolidated = os.path.join(self.base_dir, 'polycab_wires_consolidated.xlsx')
                self.save_to_excel(consolidated_wires, excel_filename_consolidated)
                
                # Save JSON
                json_filename = os.path.join(self.base_dir, 'polycab_wires_complete.json')
                with open(json_filename, 'w', encoding='utf-8') as f:
                    json.dump(consolidated_wires, f, indent=2, ensure_ascii=False)
                
                print(f"\n🎉 Wire Extraction Complete!")
                print(f"✅ Successfully processed: {len(all_wire_data)} individual wire variants")
                print(f"🔄 Consolidated into: {len(consolidated_wires)} unique wire products") 
                print(f"📊 Files saved in: {self.base_dir}")
                print(f"📄 Files created:")
                print(f"  • {excel_filename_original} - Raw data (all variants)")
                print(f"  • {excel_filename_consolidated} - Consolidated data (colors merged)")
                print(f"  • {json_filename} - JSON format (consolidated)")
                
            else:
                print("❌ No wire data extracted!")
                
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
            import traceback
            traceback.print_exc()


def main():
    """Main function to run the wire extractor"""
    
    print("🔌 Polycab Wire Extractor with Color Consolidation")
    print("=" * 60)
    print("📋 This extractor will:")
    print("  ✅ Extract all wire products from Polycab")
    print("  🔍 Get detailed specifications (Area, Voltage, Length, etc.)")
    print("  🎨 Consolidate variants that differ only in COLOR")
    print("  💾 Save raw data + consolidated data to Excel")
    print("  🖼️  Download product images")
    
    print(f"\n🔧 Consolidation Strategy:")
    print("  📝 Group wires by ALL specs EXCEPT color")
    print("  🎨 If only color differs → Merge into single entry")
    print("  📊 Create comma-separated color list")
    print("  💡 Example: 'Red 2.5mm² Wire' + 'Black 2.5mm² Wire' → '2.5mm² Wire (Red, Black)'")
    
    print(f"\n📋 Wire specifications extracted:")
    print("  • Wire Type (House Wire, Armoured Cable, etc.)")
    print("  • Cross-Sectional Area (1.5mm², 2.5mm², 4mm², etc.)")
    print("  • Core Configuration (Single Core, Multi Core)")
    print("  • Voltage Rating (1100V, 650/1100V, etc.)")
    print("  • Insulation Type (PVC, XLPE, etc.)")
    print("  • Length & Packing (90M, 180M, etc.)")
    print("  • Standards (IS 694, IS 1554, etc.)")
    print("  • Colors (consolidated for similar wires)")
    
    # Confirmation
    confirm = input(f"\nProceed with comprehensive wire extraction? (y/N): ").strip().lower()
    if confirm not in ['y', 'yes']:
        print("❌ Extraction cancelled.")
        return
    
    # Run the wire extractor
    try:
        extractor = PolycabWireExtractor()
        extractor.run()
        print(f"\n🎉 Wire extraction completed successfully!")
    except Exception as e:
        print(f"❌ Error during extraction: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
