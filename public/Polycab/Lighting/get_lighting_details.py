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

class PolycabLightingExtractor:
    def __init__(self, lighting_type_slug: str = "led-bulb", lighting_display_name: str = "LED Bulb"):
        """
        Initialize the comprehensive lighting extractor with configurable lighting type
        """
        self.base_url = "https://polycab.com"
        self.cms_base_url = "https://cms.polycab.com"
        self.lighting_type_slug = lighting_type_slug
        self.lighting_display_name = lighting_display_name
        
        # Create directories
        self.base_dir = f'polycab_{self.lighting_type_slug.replace("-", "_")}_lighting'
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
        
        # Color and wattage consolidation patterns
        self.color_keywords = [
            'white', 'warm white', 'cool white', 'daylight', 'natural white',
            'yellow', 'blue', 'red', 'green', 'rgb', 'multi', 'multicolor',
            'amber', 'pink', 'purple', 'orange', 'golden', 'silver', 'chrome',
            'black', 'brown', 'grey', 'gray', 'bronze'
        ]
        
        # Common wattage patterns for consolidation
        self.wattage_patterns = [
            r'(\d+)w\b', r'(\d+)\s*watt', r'(\d+)\s*watts',
            r'(\d+)\s*w\b', r'wattage:\s*(\d+)'
        ]
        
        # Product type URLs mapping
        self.lighting_urls = {
            "led-bulb": "https://polycab.com/lighting/led-bulb/c",
            "downlight": "https://polycab.com/lighting/downlight/c",
            "panel-light": "https://polycab.com/lighting/panel-light/c",
            "led-batten": "https://polycab.com/lighting/led-batten/c",
            "outdoor-lights": "https://polycab.com/lighting/outdoor-lights/c",
            "rope-and-strip-lights": "https://polycab.com/lighting/rope-and-strip-lights/c"
        }
    
    def discover_lighting_urls(self) -> List[str]:
        """Discover lighting product URLs from all pages of category"""
        lighting_urls = set()
        
        try:
            category_url = self.lighting_urls.get(self.lighting_type_slug, f"{self.base_url}/lighting/{self.lighting_type_slug}/c")
            print(f"🔍 Fetching lighting products from: {category_url}")
            
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
                
                page_lighting_urls = set()
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
                            if href and self._is_lighting_product_url(href):
                                if not href.startswith('http'):
                                    href = urljoin(self.base_url, href)
                                current_page_urls.add(href)
                        
                        if current_page_urls:
                            page_lighting_urls = current_page_urls
                            print(f"✅ Page {page}: Found {len(current_page_urls)} products using {page_url}")
                            break
                            
                    except Exception as e:
                        print(f"⚠️  Failed to fetch {page_url}: {e}")
                        continue
                
                if not page_lighting_urls and response:
                    page_lighting_urls = self._try_ajax_pagination(category_url, page)
                
                if not page_lighting_urls:
                    print(f"🏁 No more products found on page {page}. Stopping pagination.")
                    break
                
                new_urls = page_lighting_urls - lighting_urls
                if not new_urls and page > 1:
                    print(f"🏁 No new products on page {page}. Reached end of pagination.")
                    break
                
                lighting_urls.update(page_lighting_urls)
                print(f"📊 Page {page}: Added {len(new_urls)} new URLs (Total: {len(lighting_urls)})")
                
                page += 1
                time.sleep(2)
            
            print(f"✅ Found {len(lighting_urls)} total lighting product URLs across {page-1} pages")
            
        except Exception as e:
            print(f"❌ Error discovering URLs: {e}")
        
        return list(lighting_urls)

    def _try_ajax_pagination(self, base_url: str, page: int) -> set:
        """Try to fetch products using AJAX pagination"""
        try:
            ajax_patterns = [
                f"{self.base_url}/api/products/lighting/{self.lighting_type_slug}?page={page}",
                f"{self.base_url}/Products/GetLightingGridPartial?page={page}&productTypeSlug={self.lighting_type_slug}",
                f"{self.base_url}/Products/GetProductsGridPartial?page={page}&category={self.lighting_type_slug}",
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
                                if href and self._is_lighting_product_url(href):
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

    def _is_lighting_product_url(self, url: str) -> bool:
        """Check if URL is a lighting product page"""
        url_lower = url.lower()
        return (
            '/p-' in url and 
            ('/c-' in url or 'light' in url_lower or 'bulb' in url_lower or 'led' in url_lower) and
            not any(x in url_lower for x in ['javascript:', 'mailto:', '#', '?'])
        )

    def consolidate_variants(self, all_lighting_data: List[Dict]) -> List[Dict]:
        """
        Consolidate lighting variants based on similar specs but different colors/wattages
        
        Consolidation Strategy:
        1. Group by base product name (removing color and wattage references)
        2. Group by core specifications (excluding color and wattage)
        3. Merge if specifications match but colors/wattages differ
        4. Create comma-separated lists for different configurations
        """
        print("\n🔄 Consolidating lighting variants...")
        
        # Group lighting products by base name
        lighting_groups = defaultdict(list)
        
        for lighting_data in all_lighting_data:
            base_name = self._get_base_lighting_name(lighting_data['Name'])
            lighting_groups[base_name].append(lighting_data)
        
        consolidated_lighting = []
        
        for base_name, variants in lighting_groups.items():
            if len(variants) == 1:
                consolidated_lighting.append(variants[0])
            else:
                # Group by core specifications (excluding color/wattage)
                spec_groups = self._group_by_core_specifications(variants)
                
                for spec_signature, spec_variants in spec_groups.items():
                    if len(spec_variants) == 1:
                        consolidated_lighting.append(spec_variants[0])
                    else:
                        # Check if variants should be consolidated
                        if self._should_consolidate_lighting_variants(spec_variants):
                            consolidated_product = self._merge_lighting_variants(base_name, spec_variants)
                            consolidated_lighting.append(consolidated_product)
                            
                            # Show what was consolidated
                            colors = set()
                            wattages = set()
                            for v in spec_variants:
                                if v.get('Colors'):
                                    colors.update([c.strip() for c in v['Colors'].split(',')])
                                if v.get('Wattage'):
                                    wattages.add(v['Wattage'])
                            
                            print(f"  🔗 Consolidated {len(spec_variants)} variants of: {base_name}")
                            if colors:
                                print(f"    🎨 Colors: {', '.join(sorted(colors))}")
                            if wattages:
                                print(f"    ⚡ Wattages: {', '.join(sorted(wattages))}")
                        else:
                            # Don't consolidate - keep as separate entries
                            consolidated_lighting.extend(spec_variants)
        
        print(f"✅ Consolidated {len(all_lighting_data)} products into {len(consolidated_lighting)} unique items")
        return consolidated_lighting

    def _get_base_lighting_name(self, lighting_name: str) -> str:
        """Extract base lighting name by removing color and wattage references"""
        base_name = lighting_name.lower()
        
        # Remove wattage patterns
        for pattern in self.wattage_patterns:
            base_name = re.sub(pattern, '', base_name, flags=re.IGNORECASE)
        
        # Remove color words
        for color in self.color_keywords:
            pattern = rf'\b{color}\b'
            base_name = re.sub(pattern, '', base_name, flags=re.IGNORECASE)
        
        # Remove common lighting terms that are just descriptive
        common_terms = ['led', 'light', 'bulb', 'lamp', 'tube', 'strip', 'panel']
        # Keep these terms as they're part of product identity, just clean extra spaces
        
        # Clean up spacing and normalize
        base_name = ' '.join(base_name.split())
        base_name = base_name.strip().title()
        
        return base_name

    def _group_by_core_specifications(self, variants: List[Dict]) -> Dict[str, List[Dict]]:
        """Group variants by core specifications (excluding color and wattage)"""
        spec_groups = defaultdict(list)
        
        for variant in variants:
            spec_signature = self._get_core_specification_signature(variant)
            spec_groups[spec_signature].append(variant)
        
        return spec_groups

    def _get_core_specification_signature(self, lighting_data: Dict) -> str:
        """Generate signature based on core specifications (excluding color/wattage)"""
        # Core specs that must match for consolidation (excluding color and wattage)
        core_specs = [
            'Type',  # LED Bulb, Panel Light, etc.
            'Base_Type',  # B22, E27, etc.
            'Beam_Angle',
            'IP_Rating',
            'Operating_Temperature',
            'Body_Material',
            'Lens_Material',
            'Warranty',
            'Dimmable',
            'Shape',  # But we'll be flexible with this
            'Usage'  # Indoor/Outdoor
        ]
        
        spec_values = []
        for spec in core_specs:
            value = lighting_data.get(spec, 'N/A')
            if isinstance(value, str):
                value = value.strip().lower()
            spec_values.append(f"{spec}:{value}")
        
        return "|".join(spec_values)

    def _should_consolidate_lighting_variants(self, variants: List[Dict]) -> bool:
        """Check if lighting variants should be consolidated"""
        if len(variants) < 2:
            return False
        
        # Get all colors and wattages
        all_colors = set()
        all_wattages = set()
        
        for variant in variants:
            # Colors
            colors = variant.get('Colors', '')
            if colors and colors not in ['N/A', '']:
                color_list = [c.strip().lower() for c in colors.split(',')]
                all_colors.update(color_list)
            
            # Wattages
            wattage = variant.get('Wattage', '')
            if wattage and wattage not in ['N/A', '']:
                all_wattages.add(wattage.lower())
        
        # Consolidate if we have multiple colors OR multiple wattages
        has_multiple_colors = len(all_colors) > 1
        has_multiple_wattages = len(all_wattages) > 1
        
        should_consolidate = has_multiple_colors or has_multiple_wattages
        
        print(f"    🎨 Colors found: {len(all_colors)} - {', '.join(sorted(all_colors)) if all_colors else 'None'}")
        print(f"    ⚡ Wattages found: {len(all_wattages)} - {', '.join(sorted(all_wattages)) if all_wattages else 'None'}")
        print(f"    🤔 Should consolidate: {should_consolidate}")
        
        return should_consolidate

    def _merge_lighting_variants(self, base_name: str, variants: List[Dict]) -> Dict:
        """Merge multiple lighting variants into single entry"""
        merged = variants[0].copy()
        merged['Name'] = base_name
        
        # Collect all variants of configurable attributes
        colors = []
        wattages = []
        lumens = []
        color_temperatures = []
        prices = []
        image_paths = []
        
        for variant in variants:
            # Colors
            variant_colors = variant.get('Colors', '')
            if variant_colors and variant_colors not in ['N/A', '']:
                colors.extend([c.strip() for c in variant_colors.split(',') if c.strip()])
            
            # Wattages
            if variant.get('Wattage') and variant['Wattage'] != 'N/A':
                wattages.append(variant['Wattage'])
            
            # Lumens
            if variant.get('Lumens') and variant['Lumens'] != 'N/A':
                lumens.append(variant['Lumens'])
            
            # Color Temperature
            if variant.get('Color_Temperature') and variant['Color_Temperature'] != 'N/A':
                color_temperatures.append(variant['Color_Temperature'])
            
            # Prices
            if variant.get('Price') and variant['Price'] != 'N/A':
                prices.append(variant['Price'])
            
            # Images
            if variant.get('Image_Path'):
                image_paths.append(variant['Image_Path'])
        
        # Remove duplicates and update merged data
        unique_colors = list(dict.fromkeys(colors))  # Preserve order, remove duplicates
        unique_wattages = list(dict.fromkeys(wattages))
        unique_lumens = list(dict.fromkeys(lumens))
        unique_color_temps = list(dict.fromkeys(color_temperatures))
        
        # Update merged data with consolidated information
        merged['Colors'] = ', '.join(unique_colors) if unique_colors else 'Multiple Colors Available'
        merged['Wattage'] = ', '.join(unique_wattages) if unique_wattages else 'N/A'
        merged['Lumens'] = ', '.join(unique_lumens) if unique_lumens else 'N/A'
        merged['Color_Temperature'] = ', '.join(unique_color_temps) if unique_color_temps else 'N/A'
        merged['Price'] = self._consolidate_prices(prices)
        merged['Image_Path'] = '; '.join(image_paths) if image_paths else ''
        
        # Update download status
        merged['Image_Download_Status'] = 'Multiple' if len(image_paths) > 1 else (variants[0].get('Image_Download_Status', 'Not Found'))
        
        return merged

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

    def extract_lighting_details(self, lighting_url: str) -> Dict[str, str]:
        """Extract detailed lighting information from a product page"""
        print(f"\n💡 Extracting: {lighting_url}")
        
        lighting_data = {
            'Name': '',
            'Type': 'Lighting',
            'Product_Type': self.lighting_display_name,
            'Brand': 'Polycab',
            'Model_Number': '',
            'Specifications': '',
            'Key_Features': '',
            'Colors': '',
            'Wattage': '',
            'Lumens': '',
            'Color_Temperature': '',
            'Base_Type': '',
            'Beam_Angle': '',
            'IP_Rating': '',
            'Operating_Temperature': '',
            'Body_Material': '',
            'Lens_Material': '',
            'Warranty': '',
            'Dimmable': '',
            'Shape': '',
            'Usage': '',  # Indoor/Outdoor
            'Price': 'N/A',
            'Full_Description': '',
            'Short_Description': '',
            'Product_URL': lighting_url,
            'Image_Path': '',
            'Image_Download_Status': 'Not Found'
        }
        
        try:
            response = self.session.get(lighting_url, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract basic information
            lighting_data['Name'] = self._extract_lighting_name(soup)
            lighting_data['Price'] = self._extract_price(soup)
            lighting_data['Full_Description'] = self._extract_description(soup)
            lighting_data['Key_Features'] = self._extract_key_features(soup)
            lighting_data['Short_Description'] = self._extract_short_description(soup)
            
            # Extract specifications from table
            specs = self._extract_specifications_table(soup)
            lighting_data.update(specs)
            
            # Extract colors from page
            lighting_data['Colors'] = self._extract_colors_from_page(soup, lighting_data['Name'])
            
            # Extract and download image
            print(f"🔍 Looking for images for: {lighting_data['Name']}")
            image_url = self._extract_image_url(soup)
            if image_url:
                image_path = "/Polycab/Lighting/"+self.download_image(lighting_data['Name'] + "_" + lighting_data.get('Colors', ''), image_url)
                if image_path:
                    lighting_data['Image_Path'] = image_path
                    lighting_data['Image_Download_Status'] = 'Downloaded'
                else:
                    lighting_data['Image_Download_Status'] = 'Failed'
            
            print(f"✅ Extracted: {lighting_data['Name'][:50]}...")
            
        except Exception as e:
            print(f"❌ Error extracting from {lighting_url}: {e}")
            lighting_data['Name'] = f"Error: {str(e)}"
        
        return lighting_data

    def _extract_lighting_name(self, soup: BeautifulSoup) -> str:
        """Extract lighting product name from soup"""
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
        
        return 'Unknown Lighting Product'

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
        """Extract key features/highlights"""
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
        
        # Look for energy rating/star information
        star_elem = soup.find('img', src=lambda x: x and 'star' in x.lower() if x else False)
        if star_elem:
            src = star_elem.get('src', '')
            star_match = re.search(r'(\d+)_star', src)
            if star_match:
                star_text = f"{star_match.group(1)} Star Rated"
                if star_text not in features:
                    features.append(star_text)
        
        # Look for warranty information
        warranty_elem = soup.find('img', src=lambda x: x and 'warranty' in x.lower() if x else False)
        if warranty_elem:
            src = warranty_elem.get('src', '')
            warranty_match = re.search(r'(\d+)_year_warranty', src)
            if warranty_match:
                warranty_text = f"{warranty_match.group(1)} Year Warranty"
                if warranty_text not in features:
                    features.append(warranty_text)
            else:
                features.append("Product Warranty")
        
        # Look for LED/energy efficiency mentions
        page_text = soup.get_text().upper()
        if 'LED' in page_text:
            led_text = "LED Technology"
            if led_text not in features:
                features.append(led_text)
        
        if 'ENERGY EFFICIENT' in page_text:
            if "Energy Efficient" not in features:
                features.append("Energy Efficient")
        
        # Return features or fallback
        if features:
            return ' , '.join(features)
        else:
            return 'LED technology | Energy efficient | Long lasting'

    def _extract_specifications_table(self, soup: BeautifulSoup) -> Dict[str, str]:
        """Extract specifications from table"""
        specs = {
            'Wattage': 'N/A',
            'Lumens': 'N/A',
            'Color_Temperature': 'N/A',
            'Base_Type': 'N/A',
            'Beam_Angle': 'N/A',
            'IP_Rating': 'N/A',
            'Operating_Temperature': 'N/A',
            'Body_Material': 'N/A',
            'Lens_Material': 'N/A',
            'Warranty': 'N/A',
            'Dimmable': 'N/A',
            'Shape': 'N/A',
            'Usage': 'N/A'
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
                    
                    if 'wattage' in key or 'power' in key:
                        specs['Wattage'] = value
                    elif 'lumen' in key:
                        specs['Lumens'] = value
                    elif 'color temperature' in key or 'cct' in key:
                        specs['Color_Temperature'] = value
                    elif 'base' in key or 'cap' in key:
                        specs['Base_Type'] = value
                    elif 'beam angle' in key:
                        specs['Beam_Angle'] = value
                    elif 'ip rating' in key or 'ip' in key:
                        specs['IP_Rating'] = value
                    elif 'operating temperature' in key or 'temp' in key:
                        specs['Operating_Temperature'] = value
                    elif 'body material' in key:
                        specs['Body_Material'] = value
                    elif 'lens' in key and 'material' in key:
                        specs['Lens_Material'] = value
                    elif 'warranty' in key:
                        specs['Warranty'] = value
                    elif 'dimmable' in key or 'dimming' in key:
                        specs['Dimmable'] = value
                    elif 'shape' in key:
                        specs['Shape'] = value
                    elif 'usage' in key or 'application' in key:
                        specs['Usage'] = value
        
        # Also try to extract from product text
        self._extract_specs_from_text(soup, specs)
        
        # Format specifications string
        spec_parts = []
        for key, value in specs.items():
            if value != 'N/A':
                clean_key = key.replace('_', ' ').title()
                spec_parts.append(f"{clean_key}: {value}")
        
        specs['Specifications'] = ' ; '.join(spec_parts) if spec_parts else 'Standard LED specifications'
        
        return specs

    def _extract_specs_from_text(self, soup: BeautifulSoup, specs: Dict[str, str]):
        """Extract specs from product text/description"""
        text = soup.get_text().lower()
        
        # Extract wattage
        if specs['Wattage'] == 'N/A':
            for pattern in self.wattage_patterns:
                match = re.search(pattern, text)
                if match:
                    specs['Wattage'] = f"{match.group(1)}W"
                    break
        
        # Extract base type
        if specs['Base_Type'] == 'N/A':
            base_match = re.search(r'\b(b22|e27|e14|gu10|mr16)\b', text, re.IGNORECASE)
            if base_match:
                specs['Base_Type'] = base_match.group(1).upper()
        
        # Extract lumens
        if specs['Lumens'] == 'N/A':
            lumen_match = re.search(r'(\d+)\s*(?:lm|lumens?)\b', text, re.IGNORECASE)
            if lumen_match:
                specs['Lumens'] = f"{lumen_match.group(1)} Lumens"
        
        # Extract color temperature
        if specs['Color_Temperature'] == 'N/A':
            color_temp_match = re.search(r'(\d+)k?\s*(?:kelvin|k)\b', text, re.IGNORECASE)
            if color_temp_match:
                specs['Color_Temperature'] = f"{color_temp_match.group(1)}K"

    def _extract_colors_from_page(self, soup: BeautifulSoup, lighting_name: str) -> str:
        """Extract available colors from page"""
        colors = set()
        
        # Look for the specific colorName span element
        color_elem = soup.find('span', id='colorName')
        if color_elem:
            color_text = color_elem.get_text().strip()
            if color_text:
                colors.add(color_text.title())
        
        # Look for color in product description
        if not colors:
            desc_elem = soup.find('p', class_='prod__desc no-pipe')
            if desc_elem:
                desc_text = desc_elem.get_text().strip()
                color_match = re.match(r'^([^(]+)', desc_text)
                if color_match:
                    color_text = color_match.group(1).strip()
                    if color_text:
                        colors.add(color_text.title())
        
        # Extract from lighting name
        if not colors:
            lighting_name_lower = lighting_name.lower()
            for color in self.color_keywords:
                if color in lighting_name_lower:
                    colors.add(color.title())
        
        if colors:
            return ', '.join(sorted(colors))
        else:
            return 'White'  # Default for LED lighting

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
                if any(term in src.lower() for term in ['_img_', 'product', 'light', 'bulb', 'led']):
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

    def download_image(self, lighting_name: str, image_url: str) -> str:
        """Download lighting image"""
        try:
            print(f"🔽 Downloading image for: {lighting_name}")
            
            filename = self.clean_filename(lighting_name, '_image')
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

    def save_to_excel(self, lighting_data: List[Dict[str, str]], filename: str = None):
        """Save lighting data to Excel"""
        if filename is None:
            filename = f'polycab_{self.lighting_type_slug.replace("-", "_")}_lighting_complete.xlsx'
        
        print(f"\n💾 Saving lighting data to Excel: {filename}")
        
        try:
            df = pd.DataFrame(lighting_data)
            
            # Reorder columns for better presentation
            column_order = [
                'Name', 'Product_Type', 'Type', 'Brand', 'Model_Number',
                'Short_Description', 'Price', 'Colors', 'Wattage', 'Lumens', 'Color_Temperature',
                'Base_Type', 'Beam_Angle', 'IP_Rating', 'Operating_Temperature',
                'Body_Material', 'Lens_Material', 'Warranty', 'Dimmable', 'Shape', 'Usage',
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
                df.to_excel(writer, sheet_name='Lighting Data', index=False)
                
                # Format worksheet
                workbook = writer.book
                worksheet = writer.sheets['Lighting Data']
                
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
            print(f"💡 Total lighting products: {len(lighting_data)}")
            
            # Summary statistics
            downloaded_images = sum(1 for f in lighting_data if f['Image_Download_Status'] == 'Downloaded')
            
            print(f"🖼️  Images downloaded: {downloaded_images}/{len(lighting_data)}")
            
        except Exception as e:
            print(f"❌ Error saving Excel: {e}")

    def run(self):
        """Main execution method"""
        print(f"🚀 Polycab {self.lighting_display_name} Extractor")
        print("=" * 60)
        print(f"📁 Working directory: {self.base_dir}")
        
        try:
            # 1. Discover lighting URLs
            lighting_urls = self.discover_lighting_urls()
            print(f"\n🔍 Found {len(lighting_urls)} lighting URLs")
            
            if not lighting_urls:
                print("❌ No lighting URLs found!")
                return
            
            # Show first few URLs
            print("\n📋 Sample URLs:")
            for i, url in enumerate(lighting_urls[:3], 1):
                print(f"  {i}. {url}")
            
            if len(lighting_urls) > 3:
                print(f"  ... and {len(lighting_urls) - 3} more")
            
            # 2. Extract lighting data
            all_lighting_data = []
            
            for i, url in enumerate(lighting_urls, 1):
                print(f"\n{'='*50}")
                print(f"[{i}/{len(lighting_urls)}] Processing Product {i}")
                print(f"{'='*50}")
                
                lighting_data = self.extract_lighting_details(url)
                all_lighting_data.append(lighting_data)
                
                time.sleep(2)
            
            # 3. Consolidate variants
            if all_lighting_data:
                consolidated_lighting = self.consolidate_variants(all_lighting_data)
                
                # Save final results
                excel_filename = os.path.join(self.base_dir, f'polycab_{self.lighting_type_slug.replace("-", "_")}_lighting_complete.xlsx')
                self.save_to_excel(all_lighting_data, excel_filename)
                
                # Save JSON
                json_filename = os.path.join(self.base_dir, f'polycab_{self.lighting_type_slug.replace("-", "_")}_lighting_complete.json')
                with open(json_filename, 'w', encoding='utf-8') as f:
                    json.dump(all_lighting_data, f, indent=2, ensure_ascii=False)
                
                print(f"\n🎉 Lighting Extraction Complete!")
                print(f"✅ Successfully processed: {len(all_lighting_data)} unique lighting products")
                print(f"📊 Files saved in: {self.base_dir}")
                
            else:
                print("❌ No lighting data extracted!")
                
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
            import traceback
            traceback.print_exc()


def main():
    """Main function with all available lighting types"""
    
    # Complete list of available lighting types
    available_lighting_types = {
        # Main lighting types
        '1': ('led-bulb', 'LED Bulb'),
        '2': ('downlight', 'Downlight'),
        '3': ('panel-light', 'Panel Light'),
        '4': ('led-batten', 'LED Batten'),
        '5': ('outdoor-lights', 'Outdoor Lights'),
        '6': ('rope-and-strip-lights', 'Rope and Strip Lights'),
        
        # Custom option
        '7': ('custom', 'Custom (Enter your own)')
    }
    
    print("💡 Polycab Comprehensive Lighting Extractor")
    print("=" * 50)
    print("📋 Available lighting types:\n")
    
    # Display all lighting categories
    for key in ['1', '2', '3', '4', '5', '6']:
        slug, display_name = available_lighting_types[key]
        print(f"  {key}. {display_name}")
    
    print(f"\n  7. Custom (Enter your own slug)")
    
    # Get user choice - supports multiple selections and ranges
    print("\n💡 Selection Options:")
    print("  • Single: 1")
    print("  • Multiple: 1,2,5")
    print("  • Range: 1-4")
    print("  • Mixed: 1,3-5,6")
    print("  • All: 1-6")
    
    choice_input = input(f"\nSelect lighting type(s) (1-7): ").strip()
    
    # Parse the input to get list of choices
    selected_choices = parse_choice_input(choice_input, available_lighting_types.keys())
    
    if not selected_choices:
        print("Invalid choice. Using default LED Bulb.")
        selected_choices = ['1']
    
    # Display selected lighting types
    print(f"\n🎯 Selected Lighting Types ({len(selected_choices)}):")
    selected_lighting = []
    
    for choice in selected_choices:
        if choice in available_lighting_types:
            lighting_slug, display_name = available_lighting_types[choice]
            if lighting_slug == 'custom':
                lighting_slug = input(f"Enter lighting type slug for choice {choice}: ").strip()
                display_name = input(f"Enter display name for choice {choice}: ").strip()
            selected_lighting.append((lighting_slug, display_name))
            print(f"  ✅ {display_name} ({lighting_slug})")
    
    print(f"\n📋 This will extract for {len(selected_lighting)} lighting type(s):")
    print("  ✅ Product details (name, specs, features, etc.)")
    print("  🎨 Color & Wattage consolidation (merge similar variants)")
    print("  🖼️  Product images")
    print("  💰 Price information") 
    print("  ⚡ Technical specifications (Wattage, Lumens, Color Temperature, etc.)")
    print("  💾 Save everything to Excel with proper structure")
    print("  🔄 Multi-page crawling for complete data")
    
    # Show what consolidation strategy will be used
    print(f"\n🔧 Consolidation Strategy:")
    print("  📝 Group products by base name (removing color/wattage)")
    print("  🔍 Match core specifications (Type, Base, Material, etc.)")
    print("  🎨 Merge variants with same specs but different Colors/Wattages")
    print("  📊 Create comma-separated lists: Colors, Wattages, Lumens, Color Temperatures")
    print("  💡 Example: '9W LED Bulb' + '12W LED Bulb' → 'LED Bulb (9W, 12W)'")
    
    # Confirmation
    confirm = input(f"\nProceed with comprehensive extraction for all {len(selected_lighting)} lighting types? (y/N): ").strip().lower()
    if confirm not in ['y', 'yes']:
        print("❌ Extraction cancelled.")
        return
    
    # Run the comprehensive extractor for each selected lighting type
    total_lighting = len(selected_lighting)
    for i, (lighting_slug, display_name) in enumerate(selected_lighting, 1):
        print(f"\n{'='*60}")
        print(f"🔄 Processing {i}/{total_lighting}: {display_name}")
        print(f"{'='*60}")
        
        try:
            extractor = PolycabLightingExtractor(lighting_slug, display_name)
            extractor.run()
            print(f"✅ Completed: {display_name}")
        except Exception as e:
            print(f"❌ Error processing {display_name}: {str(e)}")
            continue
    
    print(f"\n🎉 Batch extraction completed for {total_lighting} lighting types!")


def parse_choice_input(choice_input, valid_keys):
    """Parse user input for multiple selections and ranges"""
    choices = []
    
    try:
        # Split by comma for multiple selections
        parts = [part.strip() for part in choice_input.split(',')]
        
        for part in parts:
            if '-' in part:
                # Handle range (e.g., "1-4")
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


def run_all_lighting():
    """Quick function to run all lighting types"""
    available_lighting_types = {
        '1': ('led-bulb', 'LED Bulb'),
        '2': ('downlight', 'Downlight'),
        '3': ('panel-light', 'Panel Light'),
        '4': ('led-batten', 'LED Batten'),
        '5': ('outdoor-lights', 'Outdoor Lights'),
        '6': ('rope-and-strip-lights', 'Rope and Strip Lights'),
    }
    
    print("💡 Polycab All Lighting Types Batch Extractor")
    print("=" * 50)
    print("📋 Will process the following lighting types:\n")
    
    for key, (slug, display_name) in available_lighting_types.items():
        print(f"  {key}. {display_name}")
    
    confirm = input(f"\nProceed with extraction for all {len(available_lighting_types)} lighting types? (y/N): ").strip().lower()
    if confirm not in ['y', 'yes']:
        print("❌ Extraction cancelled.")
        return
    
    # Run extraction for each lighting type
    total_lighting = len(available_lighting_types)
    for i, (key, (lighting_slug, display_name)) in enumerate(available_lighting_types.items(), 1):
        print(f"\n{'='*60}")
        print(f"🔄 Processing {i}/{total_lighting}: {display_name}")
        print(f"{'='*60}")
        
        try:
            extractor = PolycabLightingExtractor(lighting_slug, display_name)
            extractor.run()
            print(f"✅ Completed: {display_name}")
        except Exception as e:
            print(f"❌ Error processing {display_name}: {str(e)}")
            continue
    
    print(f"\n🎉 Batch extraction completed for all {total_lighting} lighting types!")


if __name__ == "__main__":
    # Option 1: Use the interactive main function
    main()
    
    # Option 2: Or use the run all function
    # run_all_lighting()
