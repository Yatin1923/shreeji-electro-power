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

class PolycabSwitchesAccessoriesExtractor:
    def __init__(self, category_type_slug: str = "levana", category_display_name: str = "Levana"):
        """
        Initialize the comprehensive switches and accessories extractor
        """
        self.base_url = "https://polycab.com"
        self.cms_base_url = "https://cms.polycab.com"
        self.category_type_slug = category_type_slug
        self.category_display_name = category_display_name
        
        # Create directories
        self.base_dir = f'polycab_{self.category_type_slug.replace("-", "_")}_switches_accessories'
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
        
        # Amperage patterns
        self.amperage_patterns = [
            r'(\d+)a\b', r'(\d+)\s*amp', r'(\d+)\s*amps',
            r'(\d+)\s*ampere', r'(\d+)\s*amperes', r'amperage:\s*(\d+)',
            r'(\d+)\s*a\b', r'current:\s*(\d+)', r'rated:\s*(\d+)a'
        ]
        
        # Available category URLs
        self.category_urls = {
            "levana": "https://polycab.com/switches-and-accessories/levana/c",
            "etira": "https://polycab.com/switches-and-accessories/etira/c",
            "plastic-modular-boxes": "https://polycab.com/switches-and-accessories/plastic-modular-boxes/c",
            "accessories": "https://polycab.com/switches-and-accessories/accessories/c"
        }
    
    def discover_product_urls(self) -> List[str]:
        """Discover all product URLs from the category"""
        product_urls = set()
        
        try:
            category_url = self.category_urls.get(self.category_type_slug, f"{self.base_url}/switches-and-accessories/{self.category_type_slug}/c")
            print(f"🔍 Fetching products from: {category_url}")
            
            # Get subcategories first
            subcategories = self._discover_subcategories(category_url)
            print(f"📋 Found {len(subcategories)} subcategories")
            
            for subcategory in subcategories:
                print(f"📂 Processing subcategory: {subcategory}")
                sub_urls = self._get_products_from_category(subcategory)
                product_urls.update(sub_urls)
                print(f"   Found {len(sub_urls)} products")
                
            
            # Also get direct products from main category
            direct_urls = self._get_products_from_category(category_url)
            product_urls.update(direct_urls)
            print(f"📦 Found {len(direct_urls)} direct products from main category")
            
            print(f"✅ Total product URLs discovered: {len(product_urls)}")
            
        except Exception as e:
            print(f"❌ Error discovering URLs: {e}")
        
        return list(product_urls)
    
    def _discover_subcategories(self, category_url: str) -> List[str]:
        """Discover subcategories from main category page"""
        subcategories = []
        
        try:
            response = self.session.get(category_url, timeout=30)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Look for subcategory links inside category-box divs
            subcategory_links = soup.select('div.category-box a[href]')
            
            for link in subcategory_links:
                href = link.get('href')
                if href and self._is_subcategory_url(href, category_url):
                    if not href.startswith('http'):
                        href = urljoin(self.base_url, href)
                    subcategories.append(href)
            
        except Exception as e:
            print(f"⚠️  Error discovering subcategories: {e}")
        
        return list(set(subcategories))

    
    def _is_subcategory_url(self, url: str, parent_url: str) -> bool:
        """Check if URL is a valid subcategory"""
        url_lower = url.lower()
        parent_path = urlparse(parent_url).path.lower()
        parent_path = parent_path.rstrip('c')
        # print(url_lower)
        return (
            url_lower.startswith(parent_path) and 
            url_lower.endswith('/c') and 
            url != parent_url and
            not any(x in url_lower for x in ['javascript:', 'mailto:', '#', '?'])
        )
    
    def _get_products_from_category(self, category_url: str) -> Set[str]:
        """Get all product URLs from a specific category"""
        product_urls = set()
        
        try:
            page = 1
            max_pages = 100  # Reasonable limit
            
            while page <= max_pages:
                page_url = f"{category_url}?page={page}" if page > 1 else category_url
                
                try:
                    response = self.session.get(page_url, timeout=30)
                    response.raise_for_status()
                    
                    soup = BeautifulSoup(response.text, 'html.parser')
                    # Look for product links inside prod-card divs
                    product_links = soup.select('div.prod-card a[href]')
                    
                    page_products = set()
                    for link in product_links:
                        href = link.get('href')
                        if href and self._is_product_url(href):
                            if not href.startswith('http'):
                                href = urljoin(self.base_url, href)
                            page_products.add(href)
                    
                    if not page_products:
                        print(f"🏁 No products found on page {page}, stopping pagination")
                        break
                    
                    new_urls = page_products - product_urls
                    if not new_urls and page > 1:
                        print(f"🏁 No new products on page {page}, reached end")
                        break
                    
                    product_urls.update(page_products)
                    print(f"   📄 Page {page}: {len(new_urls)} new products (Total: {len(product_urls)})")
                    
                    page += 1
                    
                except Exception as e:
                    print(f"⚠️  Error on page {page}: {e}")
                    break
        
        except Exception as e:
            print(f"❌ Error getting products from {category_url}: {e}")
        
        return product_urls

    def _is_product_url(self, url: str) -> bool:
        return True
        """Check if URL is a product page"""
        url_lower = url.lower()
        return (
            '/p-' in url and 
            '/c-' in url and
            'switches-and-accessories' in url_lower and
            not any(x in url_lower for x in ['javascript:', 'mailto:', '#'])
        )
    
    def extract_product_details(self, product_url: str) -> Dict[str, str]:
        """Extract detailed product information from a product page"""
        print(f"\n🔌 Extracting: {product_url}")
        
        product_data = {
            'Name': '',
            'Product_Type': self.category_display_name,
            'Type': 'Switch',
            'Brand': 'Polycab',
            'Model_Number': '',
            'Key_Features': '',
            'Short_Description': '',
            'Full_Description': '',
            'Specifications': '',
            
            # Switch/Accessory specific fields
            'Module': '',
            'Color': '',
            'Amperage': '',
            'Voltage': '',
            'IP_Rating': '',
            'Operating_Temperature': '',
            'Body_Material': '',
            'Contact_Material': '',
            'Standards': '',
            'Mounting_Type': '',
            'Warranty': '',
            'Switch_Type': '',  # 1-Way, 2-Way, DP, etc.
            'Socket_Type': '',  # 3-Pin, Twin, etc.
            'Regulator_Type': '',  # Fan Regulator, Dimmer, etc.
            
            # Common fields
            'Price': 'N/A',
            'Product_URL': product_url,
            'Image_Path': '',
            'Image_Download_Status': 'Not Found'
        }
        
        try:
            response = self.session.get(product_url, timeout=30)
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
            product_data.update(specs)
            
            # Determine product sub-type based on URL and content
            product_data['Switch_Type'] = self._determine_switch_type(soup, product_data['Name'])
            product_data['Socket_Type'] = self._determine_socket_type(soup, product_data['Name'])
            product_data['Regulator_Type'] = self._determine_regulator_type(soup, product_data['Name'])
            
            # Extract and download image
            print(f"🔍 Looking for images for: {product_data['Name']}")
            image_url = self._extract_image_url(soup)
            if image_url:
                if(product_data.get('Amperage','')!=''):
                    image_path = "/Polycab/Switches/" + self.download_image(
                        product_data['Name'] + "_" + product_data.get('Color', '')+"_" + product_data.get('Amperage', ''),
                        image_url)
                else:
                    image_path = "/Polycab/Switches/" + self.download_image(
                        product_data['Name'] + "_" + product_data.get('Color', ''),
                        image_url)
                if image_path:
                    product_data['Image_Path'] = image_path
                    product_data['Image_Download_Status'] = 'Downloaded'
                else:
                    product_data['Image_Download_Status'] = 'Failed'
            
            print(f"✅ Extracted: {product_data['Name'][:50]}...")
            
        except Exception as e:
            print(f"❌ Error extracting from {product_url}: {e}")
            product_data['Name'] = f"Error: {str(e)}"
        
        return product_data
    
    def _extract_product_name(self, soup: BeautifulSoup) -> str:
        """Extract product name from soup"""
        # Try h2 with product name first
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
        
        return 'Unknown Product'
    
    def _extract_short_description(self, soup: BeautifulSoup) -> str:
        """Extract short description"""
        # Look for subtitle elements
        subtitle_selectors = [
            'div.prod__subtitle',
            'p[class*="subtitle"]',
            'h3[class*="subtitle"]',
            '.product-subtitle'
        ]
        
        for selector in subtitle_selectors:
            elem = soup.select_one(selector)
            if elem:
                text = elem.get_text().strip()
                if text and len(text) > 5:
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
            'section.prod__desc p',
            '.product-description p',
            'div[class*="description"]',
            'p[class*="description"]'
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
        
        # Look for features in highlights section
        features_section = soup.find('div', class_='prod__highlights') or soup.find('section', string=re.compile(r'Highlights?', re.I))
        if features_section:
            # if features_section.name != 'section':
            #     features_section = features_section.find_parent('section')
            
            if features_section:
                highlight_list = features_section.find('ul')
                if highlight_list:
                    list_items = highlight_list.find_all('li')
                    for item in list_items:
                        text = item.get_text().strip()
                        if text:
                            features.append(text)
        
        # Look for switch/accessory-specific features
        # page_text = soup.get_text().upper()
        # switch_features = [
        #     ('ZERO SPARK', 'Zero Spark Technology'),
        #     ('SOFT TOUCH', 'Soft Touch Control'),
        #     ('HEAT RESISTANCE', 'Heat Resistant'),
        #     ('FIRE RESISTANCE', 'Fire Resistant'),
        #     ('FLAME RETARDANT', 'Flame Retardant Housing'),
        #     ('MODULAR', 'Modular Design'),
        #     ('EASY INSTALL', 'Easy Installation'),
        #     ('QUICK RESPONSE', 'Quick Response Time'),
        #     ('HI GRADE', 'High Grade Materials'),
        # ]
        
        # for search_term, feature_name in switch_features:
        #     if search_term in page_text and feature_name not in features:
        #         features.append(feature_name)
        print(f"🔍 Found {len(features)} key features")
        return ' , '.join(features) if features else 'High quality electrical switch/accessory'
    
    def _extract_specifications_table(self, soup: BeautifulSoup) -> Dict[str, str]:
        """Extract specifications from table"""
        specs = {
            'Module': 'N/A',
            'Color': 'N/A', 
            'Amperage': 'N/A',
            'Voltage': 'N/A',
            'IP_Rating': 'N/A',
            'Operating_Temperature': 'N/A',
            'Body_Material': 'N/A',
            'Contact_Material': 'N/A',
            'Standards': 'N/A',
            'Mounting_Type': 'N/A',
            'Warranty': 'N/A'
        }
        
        # Find specifications table
        table = soup.find('table')
        if table:
            rows = table.find_all('tr')
            for row in rows:
                cells = row.find_all(['td', 'th'])
                if len(cells) == 2:
                    key_elem = cells[0]
                    value_elem = cells[1] 
                    
                    key = key_elem.get_text().strip()
                    value = value_elem.get_text().strip()
                    
                    if not key or not value:
                        continue
                    
                    # Map table keys to our spec keys
                    key_mapping = {
                        'module': 'Module',
                        'colour': 'Color',
                        'color': 'Color',
                        'ampere': 'Amperage',
                        'amperage': 'Amperage',
                        'voltage': 'Voltage',
                        'ip rating': 'IP_Rating',
                        'temperature': 'Operating_Temperature',
                        'material': 'Body_Material',
                        'standards': 'Standards',
                        'mounting': 'Mounting_Type',
                        'warranty': 'Warranty'
                    }
                    
                    for table_key, spec_key in key_mapping.items():
                        if table_key in key.lower():
                            specs[spec_key] = value
                            break
                    
                    # Direct key matching
                    if key in specs:
                        specs[key] = value
        
        # Extract from product title/name structure
        self._extract_specs_from_product_info(soup, specs)
        
        # Format specifications string
        spec_parts = []
        for key, value in specs.items():
            if value != 'N/A' and key != 'Specifications':
                clean_key = key.replace('_', ' ').title()
                spec_parts.append(f"{clean_key}: {value}")
        
        specs['Specifications'] = ' ; '.join(spec_parts) if spec_parts else 'Standard switch/accessory specifications'
        
        return specs
    
    def _extract_specs_from_product_info(self, soup: BeautifulSoup, specs: Dict[str, str]):
        """Extract specifications from product information area"""
        
        # Look for product info area
        info_area = soup.find('div', class_='product-info') or soup.find('section', class_='prod__info')
        
        if info_area:
            text = info_area.get_text().lower()
            
            # Extract amperage
            if specs['Amperage'] == 'N/A':
                amperage_match = re.search(r'(\d+)\s*(?:ampere?|amp|a)\b', text)
                if amperage_match:
                    specs['Amperage'] = f"{amperage_match.group(1)}A"
            
            # Extract module info
            if specs['Module'] == 'N/A':
                module_match = re.search(r'(\d+)\s*module', text)
                if module_match:
                    specs['Module'] = f"{module_match.group(1)} Module"
        
        # Also check direct text elements on page
        page_elements = soup.find_all(['p', 'span', 'div'], string=lambda text: text and any(
            term in text.lower() for term in ['ampere', 'module', 'white', 'grey', 'black']
        ))
        
        for element in page_elements:
            text = element.get_text().strip().lower()
            
            # Extract color
            if specs['Color'] == 'N/A':
                color_patterns = ['white', 'black', 'grey', 'gray', 'magnesium grey', 'dark black']
                for color in color_patterns:
                    if color in text:
                        specs['Color'] = color.title()
                        break
    
    def _determine_switch_type(self, soup: BeautifulSoup, product_name: str) -> str:
        """Determine switch type from product info"""
        name_lower = product_name.lower()
        text_lower = soup.get_text().lower()
        
        switch_types = [
            ('1 way', '1-Way Switch'),
            ('2 way', '2-Way Switch'),
            ('dp switch', 'DP Switch'),
            ('bell push', 'Bell Push'),
            ('motor starter', 'Motor Starter'),
        ]
        
        for pattern, switch_type in switch_types:
            if pattern in name_lower or pattern in text_lower:
                return switch_type
        
        if 'switch' in name_lower:
            return 'Switch'
        
        return 'N/A'
    
    def _determine_socket_type(self, soup: BeautifulSoup, product_name: str) -> str:
        """Determine socket type from product info"""
        name_lower = product_name.lower()
        
        socket_types = [
            ('3 pin socket', '3-Pin Socket'),
            ('twin socket', 'Twin Socket'),
            ('universal socket', 'Universal Socket'),
            ('usb', 'USB Socket'),
        ]
        
        for pattern, socket_type in socket_types:
            if pattern in name_lower:
                return socket_type
        
        if 'socket' in name_lower:
            return 'Socket'
        
        return 'N/A'
    
    def _determine_regulator_type(self, soup: BeautifulSoup, product_name: str) -> str:
        """Determine regulator/dimmer type from product info"""
        name_lower = product_name.lower()
        
        regulator_types = [
            ('fan regulator', 'Fan Regulator'),
            ('dimmer', 'Dimmer'),
            ('5 step', '5-Step Regulator'),
            ('4 step', '4-Step Regulator'),
        ]
        
        for pattern, regulator_type in regulator_types:
            if pattern in name_lower:
                return regulator_type
        
        return 'N/A'
    
    def _extract_image_url(self, soup: BeautifulSoup) -> str:
        """Extract main product image URL"""
        img_elements = soup.find_all('img')
        
        for img in img_elements:
            src = img.get('src', '')
            alt = img.get('alt', '').lower()
            
            # Skip small icons and logos
            if any(skip in src.lower() for skip in ['icon', 'logo', 'menu', 'search', 'sticky']):
                continue
            
            # Look for product images from CMS
            if 'cms.polycab.com' in src and any(ext in src.lower() for ext in ['.png', '.jpg', '.jpeg', '.webp']):
                if any(term in src.lower() for term in ['_img_', 'product', 'switch', 'socket', 'slv']):
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
    
    def consolidate_variants(self, all_product_data: List[Dict]) -> List[Dict]:
        """
        Consolidate product variants based on similar specs but different modules/colors
        """
        print("\n🔄 Consolidating product variants...")
        
        # Group products by base name
        product_groups = defaultdict(list)
        
        for product_data in all_product_data:
            base_name = self._get_base_product_name(product_data['Name'])
            product_groups[base_name].append(product_data)
        
        consolidated_products = []
        
        for base_name, variants in product_groups.items():
            if len(variants) == 1:
                consolidated_products.append(variants[0])
            else:
                # Group by core specifications (excluding module/color)
                spec_groups = self._group_by_core_specifications(variants)
                
                for spec_signature, spec_variants in spec_groups.items():
                    if len(spec_variants) == 1:
                        consolidated_products.append(spec_variants[0])
                    else:
                        # Check if variants should be consolidated
                        if self._should_consolidate_variants(spec_variants):
                            consolidated_product = self._merge_variants(base_name, spec_variants)
                            consolidated_products.append(consolidated_product)
                            
                            # Show what was consolidated
                            modules = set()
                            colors = set()
                            for v in spec_variants:
                                if v.get('Module'):
                                    modules.add(v['Module'])
                                if v.get('Color'):
                                    colors.add(v['Color'])
                            
                            print(f"  🔗 Consolidated {len(spec_variants)} variants of: {base_name}")
                            if modules:
                                print(f"    📦 Modules: {', '.join(sorted(modules))}")
                            if colors:
                                print(f"    🎨 Colors: {', '.join(sorted(colors))}")
                        else:
                            # Don't consolidate - keep as separate entries
                            consolidated_products.extend(spec_variants)
        
        print(f"✅ Consolidated {len(all_product_data)} products into {len(consolidated_products)} unique items")
        return consolidated_products
    
    def _get_base_product_name(self, product_name: str) -> str:
        """Extract base product name by removing module and color references"""
        base_name = product_name
        
        # Remove module patterns
        module_patterns = [r'\b\d+\s*module\b', r'\b[12]\s*module\b']
        for pattern in module_patterns:
            base_name = re.sub(pattern, '', base_name, flags=re.IGNORECASE)
        
        # Remove color patterns
        color_patterns = [r'\bwhite\b', r'\bblack\b', r'\bgrey\b', r'\bmagnesium\s*grey\b', r'\bdark\s*black\b']
        for pattern in color_patterns:
            base_name = re.sub(pattern, '', base_name, flags=re.IGNORECASE)
        
        # Clean up spacing and normalize
        base_name = ' '.join(base_name.split())
        base_name = base_name.strip()
        
        return base_name
    
    def _group_by_core_specifications(self, variants: List[Dict]) -> Dict[str, List[Dict]]:
        """Group variants by core specifications (excluding module/color)"""
        spec_groups = defaultdict(list)
        
        for variant in variants:
            spec_signature = self._get_core_specification_signature(variant)
            spec_groups[spec_signature].append(variant)
        
        return spec_groups
    
    def _get_core_specification_signature(self, product_data: Dict) -> str:
        """Generate signature based on core specifications (excluding module/color)"""
        core_specs = [
            'Switch_Type',
            'Socket_Type', 
            'Regulator_Type',
            'Amperage'
        ]
        
        spec_values = []
        for spec in core_specs:
            value = product_data.get(spec, 'N/A')
            if isinstance(value, str):
                value = value.strip().lower()
            spec_values.append(f"{spec}:{value}")
        
        return "|".join(spec_values)
    
    def _should_consolidate_variants(self, variants: List[Dict]) -> bool:
        """Check if variants should be consolidated"""
        if len(variants) < 2:
            return False
        
        # Get all modules and colors
        all_modules = set()
        all_colors = set()
        
        for variant in variants:
            module = variant.get('Module', '')
            if module and module not in ['N/A', '']:
                all_modules.add(module.lower())
            
            color = variant.get('Color', '')
            if color and color not in ['N/A', '']:
                all_colors.add(color.lower())
        
        # Consolidate if we have multiple modules OR multiple colors
        has_multiple_modules = len(all_modules) > 1
        has_multiple_colors = len(all_colors) > 1
        
        should_consolidate = has_multiple_modules or has_multiple_colors
        
        print(f"    📦 Modules found: {len(all_modules)} - {', '.join(sorted(all_modules)) if all_modules else 'None'}")
        print(f"    🎨 Colors found: {len(all_colors)} - {', '.join(sorted(all_colors)) if all_colors else 'None'}")
        print(f"    🤔 Should consolidate: {should_consolidate}")
        
        return should_consolidate
    
    def _merge_variants(self, base_name: str, variants: List[Dict]) -> Dict:
        """Merge multiple variants into single entry"""
        merged = variants[0].copy()
        merged['Name'] = base_name
        
        # Collect all variants of configurable attributes
        modules = []
        colors = []
        amperages = []
        prices = []
        image_paths = []
        
        for variant in variants:
            # Modules
            if variant.get('Module') and variant['Module'] != 'N/A':
                modules.append(variant['Module'])
            
            # Colors
            if variant.get('Color') and variant['Color'] != 'N/A':
                colors.append(variant['Color'])
            
            # Amperages
            if variant.get('Amperage') and variant['Amperage'] != 'N/A':
                amperages.append(variant['Amperage'])
            
            # Prices
            if variant.get('Price') and variant['Price'] != 'N/A':
                prices.append(variant['Price'])
            
            # Images
            if variant.get('Image_Path'):
                image_paths.append(variant['Image_Path'])
        
        # Remove duplicates and update merged data
        unique_modules = list(dict.fromkeys(modules))
        unique_colors = list(dict.fromkeys(colors))
        unique_amperages = list(dict.fromkeys(amperages))
        unique_image_paths = list(dict.fromkeys(image_paths))
        
        # Update merged data with consolidated information
        merged['Module'] = ', '.join(unique_modules) if unique_modules else 'N/A'
        merged['Color'] = ', '.join(unique_colors) if unique_colors else 'N/A'
        merged['Amperage'] = ', '.join(unique_amperages) if unique_amperages else 'N/A'
        merged['Price'] = self._consolidate_prices(prices)
        merged['Image_Path'] = '; '.join(unique_image_paths) if unique_image_paths else ''
        
        # Update download status
        merged['Image_Download_Status'] = 'Multiple' if len(unique_image_paths) > 1 else (variants[0].get('Image_Download_Status', 'Not Found'))
        
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
            filename = f'polycab_{self.category_type_slug.replace("-", "_")}_switches_accessories_complete.xlsx'
        
        print(f"\n💾 Saving product data to Excel: {filename}")
        
        try:
            df = pd.DataFrame(product_data)
            
            # Reorder columns for better presentation
            column_order = [
                'Name', 'Product_Type', 'Type', 'Brand', 'Model_Number',
                'Short_Description', 'Price', 'Module', 'Color', 'Amperage', 'Voltage',
                'Switch_Type', 'Socket_Type', 'Regulator_Type', 'IP_Rating',
                'Operating_Temperature', 'Body_Material', 'Contact_Material',
                'Standards', 'Mounting_Type', 'Warranty',
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
                df.to_excel(writer, sheet_name='Switches & Accessories', index=False)
                
                # Format worksheet
                workbook = writer.book
                worksheet = writer.sheets['Switches & Accessories']
                
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
            print(f"🔌 Total products: {len(product_data)}")
            
            # Summary statistics
            downloaded_images = sum(1 for f in product_data if f['Image_Download_Status'] == 'Downloaded')
            
            print(f"🖼️  Images downloaded: {downloaded_images}/{len(product_data)}")
            
        except Exception as e:
            print(f"❌ Error saving Excel: {e}")

    def load_json_data(self, json_file_path: str) -> List[Dict]:
        """Load product data from JSON file"""
        try:
            with open(json_file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            print(f"✅ Loaded {len(data)} products from {json_file_path}")
            return data
        except Exception as e:
            print(f"❌ Error loading JSON file {json_file_path}: {e}")
            return []

    def consolidate_existing_data(self):
        """Consolidate existing JSON data files"""
        print(f"🔄 Consolidate Existing Data Mode")
        print("=" * 50)
        
        # Look for existing JSON files in current directory and subdirectories
        json_files = []
        for root, dirs, files in os.walk('.'):
            for file in files:
                if file.endswith('_complete.json') and 'polycab' in file.lower() and 'switches' in file.lower():
                    json_files.append(os.path.join(root, file))
        
        if not json_files:
            print("❌ No compatible JSON files found!")
            print("Looking for files matching pattern: polycab_*_switches_accessories_complete.json")
            return
        
        print(f"📁 Found {len(json_files)} JSON files:")
        for i, file_path in enumerate(json_files, 1):
            print(f"  {i}. {file_path}")
        
        # Ask user which files to consolidate
        print(f"\nSelect files to consolidate:")
        print("  - Enter numbers separated by commas (e.g., 1,2,3)")
        print("  - Enter 'all' to consolidate all files")
        print("  - Enter single number for one file")
        
        selection = input("Your selection: ").strip().lower()
        
        selected_files = []
        if selection == 'all':
            selected_files = json_files
        else:
            try:
                indices = [int(x.strip()) - 1 for x in selection.split(',')]
                selected_files = [json_files[i] for i in indices if 0 <= i < len(json_files)]
            except:
                print("❌ Invalid selection. Using first file.")
                selected_files = [json_files[0]] if json_files else []
        
        if not selected_files:
            print("❌ No valid files selected!")
            return
        
        print(f"\n🎯 Selected {len(selected_files)} files for consolidation:")
        for file_path in selected_files:
            print(f"  ✅ {file_path}")
        
        # Load all data
        all_product_data = []
        for file_path in selected_files:
            data = self.load_json_data(file_path)
            if data:
                all_product_data.extend(data)
        
        if not all_product_data:
            print("❌ No data loaded!")
            return
        
        print(f"\n📊 Total products loaded: {len(all_product_data)}")
        
        # Run consolidation
        print(f"\n🔄 Running consolidation...")
        consolidated_products = self.consolidate_variants(all_product_data)
        
        # Generate output filename
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        output_base = f'polycab_switches_accessories_consolidated_{timestamp}'
        
        # Save consolidated results
        excel_filename = f'{output_base}.xlsx'
        json_filename = f'{output_base}.json'
        
        self.save_to_excel(consolidated_products, excel_filename)
        
        with open(json_filename, 'w', encoding='utf-8') as f:
            json.dump(consolidated_products, f, indent=2, ensure_ascii=False)
        
        print(f"\n🎉 Consolidation Complete!")
        print(f"📊 Original products: {len(all_product_data)}")
        print(f"📊 Consolidated products: {len(consolidated_products)}")
        print(f"💾 Saved consolidated data to:")
        print(f"   📋 Excel: {excel_filename}")
        print(f"   📋 JSON: {json_filename}")

    def run(self):
        """Main execution method"""
        print(f"🚀 Polycab {self.category_display_name} Switches & Accessories Extractor")
        print("=" * 70)
        print(f"📁 Working directory: {self.base_dir}")
        
        try:
            # 1. Discover product URLs
            product_urls = self.discover_product_urls()
            print(f"\n🔍 Found {len(product_urls)} product URLs")
            
            if not product_urls:
                print("❌ No product URLs found!")
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
                
            
            # 3. Consolidate variants
            if all_product_data:
                consolidated_products = self.consolidate_variants(all_product_data)
                
                # Save final results - Complete data
                excel_filename = os.path.join(self.base_dir, f'polycab_{self.category_type_slug.replace("-", "_")}_switches_accessories_complete.xlsx')
                self.save_to_excel(all_product_data, excel_filename)
                
                # Save final results - Consolidated data
                excel_filename = os.path.join(self.base_dir, f'polycab_{self.category_type_slug.replace("-", "_")}_switches_accessories_consolidated.xlsx')
                self.save_to_excel(consolidated_products, excel_filename)
                
                # Save JSON - Complete data
                json_filename = os.path.join(self.base_dir, f'polycab_{self.category_type_slug.replace("-", "_")}_switches_accessories_complete.json')
                with open(json_filename, 'w', encoding='utf-8') as f:
                    json.dump(all_product_data, f, indent=2, ensure_ascii=False)

                # Save JSON - Consolidated data
                json_filename = os.path.join(self.base_dir, f'polycab_{self.category_type_slug.replace("-", "_")}_switches_accessories_consolidated.json')
                with open(json_filename, 'w', encoding='utf-8') as f:
                    json.dump(consolidated_products, f, indent=2, ensure_ascii=False)
                
                print(f"\n🎉 Switches & Accessories Extraction Complete!")
                print(f"✅ Successfully processed: {len(all_product_data)} unique products")
                print(f"🔗 Consolidated to: {len(consolidated_products)} consolidated products")
                print(f"📊 Files saved in: {self.base_dir}")
                
            else:
                print("❌ No product data extracted!")
                
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
            import traceback
            traceback.print_exc()


def main():
    """Main function with all available categories"""
    
    # Available category types
    available_categories = {
        '1': ('levana', 'Levana'),
        '2': ('etira', 'Etira'),
        '3': ('plastic-modular-boxes', 'Plastic Modular Boxes'),
        '4': ('accessories', 'Accessories'),
        '5': ('custom', 'Custom (Enter your own)'),
        '6': ('consolidate', 'Consolidate Existing Data')
    }
    
    print("🔌 Polycab Switches & Accessories Extractor")
    print("=" * 50)
    print("📋 Available options:\n")
    
    for key, (slug, display_name) in available_categories.items():
        print(f"  {key}. {display_name}")
    
    # Get user choice
    choice_input = input(f"\nSelect option (1-6): ").strip()
    
    if choice_input not in available_categories:
        print("Invalid choice. Using default Levana.")
        choice_input = '1'
    
    category_slug, display_name = available_categories[choice_input]
    
    # Handle consolidate option
    if category_slug == 'consolidate':
        # Create a temporary extractor instance for consolidation methods
        extractor = PolycabSwitchesAccessoriesExtractor('temp', 'Consolidation')
        extractor.consolidate_existing_data()
        return
    
    if category_slug == 'custom':
        category_slug = input(f"Enter category slug: ").strip()
        display_name = input(f"Enter display name: ").strip()
    
    print(f"\n🎯 Selected Category: {display_name} ({category_slug})")
    print(f"\n📋 This will extract:")
    print("  ✅ Product details (name, specs, features, etc.)")
    print("  🔗 Module & Color consolidation (merge similar variants)")
    print("  🖼️  Product images")
    print("  💰 Price information") 
    print("  🔌 Technical specifications (Module, Color, Amperage, etc.)")
    print("  💾 Save everything to Excel with proper structure")
    print("  🔄 Multi-page crawling for complete data")
    
    # Confirmation
    confirm = input(f"\nProceed with extraction for {display_name}? (y/N): ").strip().lower()
    if confirm not in ['y', 'yes']:
        print("❌ Extraction cancelled.")
        return
    
    # Run the extractor
    try:
        extractor = PolycabSwitchesAccessoriesExtractor(category_slug, display_name)
        extractor.run()
    except Exception as e:
        print(f"❌ Error running extractor: {str(e)}")


def run_all_categories():
    """Quick function to run all categories"""
    available_categories = {
        '1': ('levana', 'Levana'),
        '2': ('etira', 'Etira'),
        '3': ('plastic-modular-boxes', 'Plastic Modular Boxes'),
        '4': ('accessories', 'Accessories'),
    }
    
    print("🔌 Polycab All Categories Batch Extractor")
    print("=" * 50)
    print("📋 Will process the following categories:\n")
    
    for key, (slug, display_name) in available_categories.items():
        print(f"  {key}. {display_name}")
    
    confirm = input(f"\nProceed with extraction for all {len(available_categories)} categories? (y/N): ").strip().lower()
    if confirm not in ['y', 'yes']:
        print("❌ Extraction cancelled.")
        return
    
    # Run extraction for each category
    total_categories = len(available_categories)
    for i, (key, (category_slug, display_name)) in enumerate(available_categories.items(), 1):
        print(f"\n{'='*60}")
        print(f"🔄 Processing {i}/{total_categories}: {display_name}")
        print(f"{'='*60}")
        
        try:
            extractor = PolycabSwitchesAccessoriesExtractor(category_slug, display_name)
            extractor.run()
            print(f"✅ Completed: {display_name}")
        except Exception as e:
            print(f"❌ Error processing {display_name}: {str(e)}")
            continue
    
    print(f"\n🎉 Batch extraction completed for all {total_categories} categories!")


if __name__ == "__main__":
    # Option 1: Use the interactive main function
    main()
    
    # Option 2: Or use the run all function
    # run_all_categories()
