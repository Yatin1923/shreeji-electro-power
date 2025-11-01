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

class PolycabSwitchgearExtractor:
    def __init__(self, switchgear_type_slug: str = "mcb", switchgear_display_name: str = "MCB"):
        """
        Initialize the comprehensive switchgear extractor with configurable switchgear type
        """
        self.base_url = "https://polycab.com"
        self.cms_base_url = "https://cms.polycab.com"
        self.switchgear_type_slug = switchgear_type_slug
        self.switchgear_display_name = switchgear_display_name
        
        # Create directories
        self.base_dir = f'polycab_{self.switchgear_type_slug.replace("-", "_")}_switchgear'
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
        
        # Amperage patterns for consolidation
        self.amperage_patterns = [
            r'(\d+)a\b', r'(\d+)\s*amp', r'(\d+)\s*amps',
            r'(\d+)\s*ampere', r'(\d+)\s*amperes', r'amperage:\s*(\d+)',
            r'(\d+)\s*a\b', r'current:\s*(\d+)', r'rated:\s*(\d+)a'
        ]
        
        # Common voltage patterns
        self.voltage_patterns = [
            r'(\d+)v\b', r'(\d+)\s*volt', r'(\d+)\s*volts',
            r'(\d+)\s*v\b', r'voltage:\s*(\d+)'
        ]
        
        # Switchgear type URLs mapping
        self.switchgear_urls = {
            "mcb": "https://polycab.com/switchgear/mcb/c",
            "rccb": "https://polycab.com/switchgear/rccb/c",
            "rcbo": "https://polycab.com/switchgear/rcbo/c",
            "isolator": "https://polycab.com/switchgear/isolator/c",
            "accl": "https://polycab.com/switchgear/accl/c",
            "mcb-changeover-switch": "https://polycab.com/switchgear/mcb-changeover-switch/c",
            "distribution-board": "https://polycab.com/switchgear/distribution-board/c"
        }
    
    def discover_switchgear_urls(self) -> List[str]:
        """Discover switchgear product URLs from all pages of category"""
        switchgear_urls = set()
        
        try:
            category_url = self.switchgear_urls.get(self.switchgear_type_slug, f"{self.base_url}/switchgear/{self.switchgear_type_slug}/c")
            print(f"🔍 Fetching switchgear products from: {category_url}")
            
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
                
                page_switchgear_urls = set()
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
                            if href and self._is_switchgear_product_url(href):
                                if not href.startswith('http'):
                                    href = urljoin(self.base_url, href)
                                current_page_urls.add(href)
                        
                        if current_page_urls:
                            page_switchgear_urls = current_page_urls
                            print(f"✅ Page {page}: Found {len(current_page_urls)} products using {page_url}")
                            break
                            
                    except Exception as e:
                        print(f"⚠️  Failed to fetch {page_url}: {e}")
                        continue
                
                if not page_switchgear_urls and response:
                    page_switchgear_urls = self._try_ajax_pagination(category_url, page)
                
                if not page_switchgear_urls:
                    print(f"🏁 No more products found on page {page}. Stopping pagination.")
                    break
                
                new_urls = page_switchgear_urls - switchgear_urls
                if not new_urls and page > 1:
                    print(f"🏁 No new products on page {page}. Reached end of pagination.")
                    break
                
                switchgear_urls.update(page_switchgear_urls)
                print(f"📊 Page {page}: Added {len(new_urls)} new URLs (Total: {len(switchgear_urls)})")
                
                page += 1
                # time.sleep(2)
            
            print(f"✅ Found {len(switchgear_urls)} total switchgear product URLs across {page-1} pages")
            
        except Exception as e:
            print(f"❌ Error discovering URLs: {e}")
        
        return list(switchgear_urls)

    def _try_ajax_pagination(self, base_url: str, page: int) -> set:
        """Try to fetch products using AJAX pagination"""
        try:
            ajax_patterns = [
                f"{self.base_url}/api/products/switchgear/{self.switchgear_type_slug}?page={page}",
                f"{self.base_url}/Products/GetSwitchgearGridPartial?page={page}&productTypeSlug={self.switchgear_type_slug}",
                f"{self.base_url}/Products/GetProductsGridPartial?page={page}&category={self.switchgear_type_slug}",
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
                                if href and self._is_switchgear_product_url(href):
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

    def _is_switchgear_product_url(self, url: str) -> bool:
        """Check if URL is a switchgear product page"""
        url_lower = url.lower()
        return (
            '/p-' in url and 
            ('/c-' in url or any(term in url_lower for term in ['mcb', 'rccb', 'rcbo', 'isolator', 'accl', 'distribution', 'changeover', 'switchgear'])) and
            not any(x in url_lower for x in ['javascript:', 'mailto:', '#', '?'])
        )

    def consolidate_variants(self, all_switchgear_data: List[Dict]) -> List[Dict]:
        """
        Consolidate switchgear variants based on similar specs but different amperages
        
        Consolidation Strategy:
        1. Group by base product name (removing amperage references)
        2. Group by core specifications (excluding amperage)
        3. Merge if specifications match but amperages differ
        4. Create comma-separated lists for different amperage configurations
        """
        print("\n🔄 Consolidating switchgear variants...")
        
        # Group switchgear products by base name
        switchgear_groups = defaultdict(list)
        
        for switchgear_data in all_switchgear_data:
            base_name = self._get_base_switchgear_name(switchgear_data['Name'])
            switchgear_groups[base_name].append(switchgear_data)
        
        consolidated_switchgear = []
        
        for base_name, variants in switchgear_groups.items():
            if len(variants) == 1:
                consolidated_switchgear.append(variants[0])
            else:
                # Group by core specifications (excluding amperage)
                spec_groups = self._group_by_core_specifications(variants)
                
                for spec_signature, spec_variants in spec_groups.items():
                    if len(spec_variants) == 1:
                        consolidated_switchgear.append(spec_variants[0])
                    else:
                        # Check if variants should be consolidated
                        if self._should_consolidate_switchgear_variants(spec_variants):
                            consolidated_product = self._merge_switchgear_variants(base_name, spec_variants)
                            consolidated_switchgear.append(consolidated_product)
                            
                            # Show what was consolidated
                            amperages = set()
                            voltages = set()
                            poles = set()
                            for v in spec_variants:
                                if v.get('Amperage'):
                                    amperages.add(v['Amperage'])
                                if v.get('Voltage'):
                                    voltages.add(v['Voltage'])
                                if v.get('Poles'):
                                    poles.add(v['Poles'])
                            
                            print(f"  🔗 Consolidated {len(spec_variants)} variants of: {base_name}")
                            if amperages:
                                print(f"    ⚡ Amperages: {', '.join(sorted(amperages))}")
                            if voltages:
                                print(f"    🔌 Voltages: {', '.join(sorted(voltages))}")
                            if poles:
                                print(f"    🔧 Poles: {', '.join(sorted(poles))}")
                        else:
                            # Don't consolidate - keep as separate entries
                            consolidated_switchgear.extend(spec_variants)
        
        print(f"✅ Consolidated {len(all_switchgear_data)} products into {len(consolidated_switchgear)} unique items")
        return consolidated_switchgear

    def _get_base_switchgear_name(self, switchgear_name: str) -> str:
        """Extract base switchgear name by removing amperage and voltage references"""
        base_name = switchgear_name.lower()
        
        # Remove amperage patterns
        for pattern in self.amperage_patterns:
            base_name = re.sub(pattern, '', base_name, flags=re.IGNORECASE)
        
        # Remove voltage patterns
        for pattern in self.voltage_patterns:
            base_name = re.sub(pattern, '', base_name, flags=re.IGNORECASE)
        
        # Remove pole patterns
        pole_patterns = [r'\b(\d+)\s*pole?\b', r'\b(\d+)p\b', r'\bsp\b', r'\bdp\b', r'\btp\b', r'\b4p\b']
        for pattern in pole_patterns:
            base_name = re.sub(pattern, '', base_name, flags=re.IGNORECASE)
        
        # Clean up spacing and normalize
        base_name = ' '.join(base_name.split())
        base_name = base_name.strip().title()
        
        return base_name

    def _group_by_core_specifications(self, variants: List[Dict]) -> Dict[str, List[Dict]]:
        """Group variants by core specifications (excluding amperage)"""
        spec_groups = defaultdict(list)
        
        for variant in variants:
            spec_signature = self._get_core_specification_signature(variant)
            spec_groups[spec_signature].append(variant)
        
        return spec_groups

    def _get_core_specification_signature(self, switchgear_data: Dict) -> str:
        """Generate signature based on core specifications (excluding amperage)"""
        # Core specs that must match for consolidation (excluding amperage)
        core_specs = [
            # 'Type',  # MCB, RCCB, etc.
            # 'Voltage',  # But we'll be flexible with this
            'Poles',  
            'Gen (Dg) Current Rating (A)'
            # 'Breaking_Capacity',
            # 'Trip_Curve',
            # 'IP_Rating',
            # 'Operating_Temperature',
            # 'Body_Material',
            # 'Warranty',
            # 'Standards',
            # 'Application',
            # 'Mounting_Type'
        ]
        
        spec_values = []
        for spec in core_specs:
            value = switchgear_data.get(spec, 'N/A')
            if isinstance(value, str):
                value = value.strip().lower()
            spec_values.append(f"{spec}:{value}")
        
        return "|".join(spec_values)

    def _should_consolidate_switchgear_variants(self, variants: List[Dict]) -> bool:
        """Check if switchgear variants should be consolidated"""
        if len(variants) < 2:
            return False
        
        # Get all amperages, sensitivities, and other variant attributes
        all_amperages = set()
        all_sensitivities = set()
        all_modules = set()
        all_colours = set()
        
        for variant in variants:
            # Amperages
            amperage = variant.get('Amperage', '')
            if amperage and amperage not in ['N/A', '']:
                all_amperages.add(amperage.lower())
            
            # Sensitivities (for RCCB)
            sensitivity = variant.get('Sensitivity', '')
            if sensitivity and sensitivity not in ['N/A', '']:
                all_sensitivities.add(sensitivity.lower())
            
            # Modules
            module = variant.get('Module', '')
            if module and module not in ['N/A', '']:
                all_modules.add(module.lower())
                
            # Color
            colour = variant.get('Color', '')
            if colour and colour not in ['N/A', '']:
                all_colours.add(colour.lower())
        
        # Consolidate if we have multiple amperages OR multiple sensitivities OR multiple modules
        has_multiple_amperages = len(all_amperages) > 1
        has_multiple_sensitivities = len(all_sensitivities) > 1
        has_multiple_modules = len(all_modules) > 1
        has_multiple_colours = len(all_colours) > 1
        
        should_consolidate = has_multiple_amperages or has_multiple_sensitivities or has_multiple_modules
        
        print(f"    ⚡ Amperages found: {len(all_amperages)} - {', '.join(sorted(all_amperages)) if all_amperages else 'None'}")
        print(f"    🎯 Sensitivities found: {len(all_sensitivities)} - {', '.join(sorted(all_sensitivities)) if all_sensitivities else 'None'}")
        print(f"    📦 Modules found: {len(all_modules)} - {', '.join(sorted(all_modules)) if all_modules else 'None'}")
        print(f"    🎨 Color found: {len(all_colours)} - {', '.join(sorted(all_colours)) if all_colours else 'None'}")
        print(f"    🤔 Should consolidate: {should_consolidate}")
        
        return should_consolidate

    def _merge_switchgear_variants(self, base_name: str, variants: List[Dict]) -> Dict:
        """Merge multiple switchgear variants into single entry"""
        merged = variants[0].copy()
        merged['Name'] = base_name
        
        # Collect all variants of configurable attributes
        amperages = []
        voltages = []
        poles = []
        currentRating = []
        breaking_capacities = []
        prices = []
        sensitivities = []
        image_paths = []
        
        for variant in variants:
            # Amperages
            if variant.get('Amperage') and variant['Amperage'] != 'N/A':
                amperages.append(variant['Amperage'])
            
            # Voltages
            if variant.get('Voltage') and variant['Voltage'] != 'N/A':
                voltages.append(variant['Voltage'])
            
            if variant.get('Sensitivity') and variant['Sensitivity'] != 'N/A':
                sensitivities.append(variant['Sensitivity'])
            
            # Poles
            if variant.get('Poles') and variant['Poles'] != 'N/A':
                poles.append(variant['Poles'])

            # Gen (Dg) Current Rating (A)
            if variant.get('Gen (Dg) Current Rating (A)') and variant['Gen (Dg) Current Rating (A)'] != 'N/A':
                currentRating.append(variant['Gen (Dg) Current Rating (A)'])
            
            # Breaking Capacity
            if variant.get('Breaking_Capacity') and variant['Breaking_Capacity'] != 'N/A':
                breaking_capacities.append(variant['Breaking_Capacity'])
            
            # Prices
            if variant.get('Price') and variant['Price'] != 'N/A':
                prices.append(variant['Price'])
            
            # Images
            if variant.get('Image_Path'):
                image_paths.append(variant['Image_Path'])
        
        # Remove duplicates and update merged data
        unique_amperages = list(dict.fromkeys(amperages))  # Preserve order, remove duplicates
        unique_voltages = list(dict.fromkeys(voltages))
        unique_poles = list(dict.fromkeys(poles))
        unique_currentRating = list(dict.fromkeys(currentRating))
        unique_sensitivities = list(dict.fromkeys(sensitivities))
        unique_breaking_capacities = list(dict.fromkeys(breaking_capacities))
        unique_image_paths = list(dict.fromkeys(image_paths))
        
        # Update merged data with consolidated information
        merged['Amperage'] = ', '.join(unique_amperages) if unique_amperages else 'N/A'
        merged['Voltage'] = ', '.join(unique_voltages) if unique_voltages else 'N/A'
        merged['Poles'] = ', '.join(unique_poles) if unique_poles else 'N/A'
        merged['Gen (Dg) Current Rating (A)'] = ', '.join(unique_currentRating) if unique_currentRating else 'N/A'
        merged['Sensitivity'] = ', '.join(unique_sensitivities) if unique_sensitivities else 'N/A'
        merged['Breaking_Capacity'] = ', '.join(unique_breaking_capacities) if unique_breaking_capacities else 'N/A'
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

    def extract_switchgear_details(self, switchgear_url: str) -> Dict[str, str]:
        """Extract detailed switchgear information from a product page"""
        print(f"\n🔌 Extracting: {switchgear_url}")
        
        switchgear_data = {
            'Name': '',
            'Type': 'Switchgear',
            'Product_Type': self.switchgear_display_name,
            'Brand': 'Polycab',
            'Model_Number': '',
            'Specifications': '',
            'Key_Features': '',
            'Amperage': '',
            'Voltage': '',
            'Poles': '',
            'Gen (Dg) Current Rating (A)':'',
            'Breaking_Capacity': '',
            'Trip_Curve': '',
            'Sensitivity': '',  # For RCCB/RCBO
            'Application': '',  # AC/DC
            'MCB_Type': '',     # 6kA MCB, DC MCB, etc.
            'IP_Rating': '',
            'Operating_Temperature': '',
            'Body_Material': '',
            'Contact_Material': '',
            'Standards': '',  # IS, IEC, etc.
            'Mounting_Type': '',  # DIN Rail, Surface, etc.
            'Warranty': '',
            'Module': '',     # For modular products (1, 2 Module)
            'Color': '',     # White, Magnesium Grey, etc.
            'Price': 'N/A',
            'Full_Description': '',
            'Short_Description': '',
            'Product_URL': switchgear_url,
            'Image_Path': '',
            'Image_Download_Status': 'Not Found'
        }
        
        try:
            response = self.session.get(switchgear_url, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract basic information
            switchgear_data['Name'] = self._extract_switchgear_name(soup)
            switchgear_data['Price'] = self._extract_price(soup)
            switchgear_data['Full_Description'] = self._extract_description(soup)
            switchgear_data['Key_Features'] = self._extract_key_features(soup)
            switchgear_data['Short_Description'] = self._extract_short_description(soup)
            
            # Extract specifications from table using HTML parsing
            specs = self._extract_specifications_table(soup)
            switchgear_data.update(specs)
            
            # Extract additional specifications
            switchgear_data['Amperage'] = self._extract_amperage_from_page(soup, switchgear_data['Name'])
            switchgear_data['Sensitivity'] = self._extract_sensitivity_from_page(soup)
            
            # Extract and download image
            print(f"🔍 Looking for images for: {switchgear_data['Name']}")
            image_url = self._extract_image_url(soup)
            if image_url:
                if(switchgear_data.get('Poles', '')=='N/A'):
                    image_path = "/Polycab/Switchgear/"+self.download_image(
                        switchgear_data['Name'] + "_" + switchgear_data.get('Color', ''),
                        image_url
                    )
                else:
                    image_path = "/Polycab/Switchgear/"+self.download_image(
                        switchgear_data['Name'] + "_" + switchgear_data.get('Poles', ''),
                        image_url
                )
                if image_path:
                    switchgear_data['Image_Path'] = image_path
                    switchgear_data['Image_Download_Status'] = 'Downloaded'
                else:
                    switchgear_data['Image_Download_Status'] = 'Failed'
            
            print(f"✅ Extracted: {switchgear_data['Name'][:50]}...")
            
        except Exception as e:
            print(f"❌ Error extracting from {switchgear_url}: {e}")
            switchgear_data['Name'] = f"Error: {str(e)}"
        
        return switchgear_data

    def _extract_switchgear_name(self, soup: BeautifulSoup) -> str:
        """Extract switchgear product name from soup"""
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
        
        return 'Unknown Switchgear Product'

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
        
        # Look for safety certifications
        cert_elem = soup.find('img', src=lambda x: x and any(cert in x.lower() for cert in ['is', 'iec', 'bis']) if x else False)
        if cert_elem:
            features.append("IS/IEC Certified")
        
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
        
        # Look for switchgear-specific features
        page_text = soup.get_text().upper()
        switchgear_features = [
            ('OVERLOAD PROTECTION', 'Overload Protection'),
            ('SHORT CIRCUIT PROTECTION', 'Short Circuit Protection'),
            ('EARTH FAULT PROTECTION', 'Earth Fault Protection'),
            ('HIGH BREAKING CAPACITY', 'High Breaking Capacity'),
            ('DIN RAIL MOUNTING', 'DIN Rail Mounting'),
            ('FLAME RETARDANT', 'Flame Retardant Housing'),
        ]
        
        for search_term, feature_name in switchgear_features:
            if search_term in page_text and feature_name not in features:
                features.append(feature_name)
        
        # Return features or fallback
        if features:
            return ' , '.join(features)
        else:
            return 'Circuit protection | High reliability | Safety certified'

    def _extract_specifications_table(self, soup: BeautifulSoup) -> Dict[str, str]:
        """Extract specifications from table using HTML parsing instead of regex"""
        specs = {
            'Amperage': 'N/A',
            'Voltage': 'N/A', 
            'Poles': 'N/A',
            'Breaking_Capacity': 'N/A',
            'Trip_Curve': 'N/A',
            'Sensitivity': 'N/A',  # Added for RCCB/RCBO
            'Application': 'N/A',
            'MCB_Type': 'N/A',
            'IP_Rating': 'N/A',
            'Operating_Temperature': 'N/A',
            'Body_Material': 'N/A',
            'Contact_Material': 'N/A',
            'Standards': 'N/A',
            'Mounting_Type': 'N/A',
            'Warranty': 'N/A',
            'Module': 'N/A',  # For modular products
            'Color': 'N/A'   # For aesthetic variants
        }
        
        # Find specifications table - Polycab uses a simple table structure
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
                    specs[key] = value
        # Also extract from product title/heading structure
        self._extract_specs_from_product_title(soup, specs)
        
        # Format specifications string
        spec_parts = []
        for key, value in specs.items():
            if value != 'N/A' and key != 'Specifications':
                clean_key = key.replace('_', ' ').title()
                spec_parts.append(f"{clean_key}: {value}")
        
        specs['Specifications'] = ' ; '.join(spec_parts) if spec_parts else 'Standard switchgear specifications'
        
        return specs
    
    def _extract_specs_from_product_title(self, soup: BeautifulSoup, specs: Dict[str, str]):
        """Extract specifications from product title structure"""
        
        # Find product name section - Polycab shows key specs in the title area
        title_section = soup.find('h2')  # Main product title
        if title_section:
            title_text = title_section.get_text().strip().lower()
            
            # Extract amperage from title
            if specs['Amperage'] == 'N/A':
                amperage_match = re.search(r'(\d+)\s*(?:ampere?|amp|a)\b', title_text)
                if amperage_match:
                    specs['Amperage'] = f"{amperage_match.group(1)}A"
        
        # Look for specification details under the title
        spec_details = soup.find_all(['p', 'span', 'div'], string=lambda text: text and any(
            term in text.lower() for term in ['ampere', 'pole', 'breaking capacity', 'sensitivity']
        ))
        
        for detail in spec_details:
            text = detail.get_text().strip().lower()
            
            # Extract amperage
            if specs['Amperage'] == 'N/A' and 'ampere' in text:
                amperage_match = re.search(r'(\d+)\s*ampere', text)
                if amperage_match:
                    specs['Amperage'] = f"{amperage_match.group(1)}A"
            
            # Extract poles
            if specs['Poles'] == 'N/A' and 'pole' in text:
                pole_match = re.search(r'(\w+)\s*pole', text)
                if pole_match:
                    specs['Poles'] = pole_match.group(1).upper()
            
            # Extract breaking capacity
            if specs['Breaking_Capacity'] == 'N/A' and ('ka' in text or 'breaking capacity' in text):
                ka_match = re.search(r'(\d+(?:\.\d+)?)\s*ka', text)
                if ka_match:
                    specs['Breaking_Capacity'] = f"{ka_match.group(1)}kA"
            
            # Extract sensitivity (critical for RCCB)
            if specs['Sensitivity'] == 'N/A' and ('ma' in text or 'sensitivity' in text):
                sensitivity_match = re.search(r'(\d+)\s*ma', text)
                if sensitivity_match:
                    specs['Sensitivity'] = f"{sensitivity_match.group(1)}mA"

    def _extract_amperage_from_page(self, soup: BeautifulSoup, switchgear_name: str) -> str:
        """Extract available amperage using HTML parsing instead of regex"""
        amperages = set()
        
        # First check specifications table
        table = soup.find('table')
        if table:
            rows = table.find_all('tr')
            for row in rows:
                cells = row.find_all(['td', 'th'])
                if len(cells) == 2:
                    key = cells[0].get_text().strip().lower()
                    value = cells[1].get_text().strip()
                    
                    if key == 'ampere' and value:
                        amperages.add(f"{value}A" if not value.endswith('A') else value)
        
        # Check product title/heading
        title_elem = soup.find('h2')
        if title_elem and not amperages:
            title_text = title_elem.get_text().strip()
            # Look for patterns like "32 Ampere" or "40A"
            amperage_patterns = [
                r'(\d+)\s*(?:Ampere|A)\b',
                r'(\d+)A\b'
            ]
            for pattern in amperage_patterns:
                matches = re.findall(pattern, title_text, re.IGNORECASE)
                for match in matches:
                    amperages.add(f"{match}A")
        
        # Check product description area
        desc_area = soup.find_all(['p', 'span', 'div'])
        if not amperages:
            for elem in desc_area:
                text = elem.get_text().strip()
                if 'ampere' in text.lower() or re.search(r'\d+A\b', text):
                    amperage_match = re.search(r'(\d+)\s*(?:Ampere|A)\b', text, re.IGNORECASE)
                    if amperage_match:
                        amperages.add(f"{amperage_match.group(1)}A")
        
        if amperages:
            return ', '.join(sorted(amperages))
        else:
            return 'Standard Amperage'

    def _extract_sensitivity_from_page(self, soup: BeautifulSoup) -> str:
        """Extract sensitivity information specifically for RCCB/RCBO products"""
        
        # First check specifications table for sensitivity
        table = soup.find('table')
        if table:
            rows = table.find_all('tr')
            for row in rows:
                cells = row.find_all(['td', 'th'])
                if len(cells) == 2:
                    key = cells[0].get_text().strip().lower()
                    value = cells[1].get_text().strip()
                    
                    if key == 'sensitivity' and value:
                        return value
        
        # Check product title for sensitivity (e.g., "300mA Sensitivity")
        title_elem = soup.find('h2')
        if title_elem:
            title_text = title_elem.get_text().strip()
            sensitivity_match = re.search(r'(\d+)mA\s*Sensitivity', title_text, re.IGNORECASE)
            if sensitivity_match:
                return f"{sensitivity_match.group(1)}mA"
        
        # Check product description
        desc_elements = soup.find_all(['p', 'span', 'div'])
        for elem in desc_elements:
            text = elem.get_text().strip()
            if 'sensitivity' in text.lower():
                sensitivity_match = re.search(r'(\d+)\s*mA', text, re.IGNORECASE)
                if sensitivity_match:
                    return f"{sensitivity_match.group(1)}mA"
        
        return 'N/A'

    def _extract_specs_from_text(self, soup: BeautifulSoup, specs: Dict[str, str]):
        """Extract specs from product text/description"""
        text = soup.get_text().lower()
        
        # Extract amperage
        if specs['Amperage'] == 'N/A':
            for pattern in self.amperage_patterns:
                match = re.search(pattern, text)
                if match:
                    specs['Amperage'] = f"{match.group(1)}A"
                    break
        
        # Extract voltage
        if specs['Voltage'] == 'N/A':
            for pattern in self.voltage_patterns:
                match = re.search(pattern, text)
                if match:
                    specs['Voltage'] = f"{match.group(1)}V"
                    break
        
        # Extract poles
        if specs['Poles'] == 'N/A':
            pole_match = re.search(r'\b(\d+)\s*(?:pole?|p)\b', text, re.IGNORECASE)
            if pole_match:
                specs['Poles'] = f"{pole_match.group(1)}P"
        
        # Extract breaking capacity
        if specs['Breaking_Capacity'] == 'N/A':
            ka_match = re.search(r'(\d+(?:\.\d+)?)\s*ka\b', text, re.IGNORECASE)
            if ka_match:
                specs['Breaking_Capacity'] = f"{ka_match.group(1)}kA"
  
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
                if any(term in src.lower() for term in ['_img_', 'product', 'switchgear', 'mcb', 'rccb', 'rcbo']):
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

    def download_image(self, switchgear_name: str, image_url: str) -> str:
        """Download switchgear image"""
        try:
            print(f"🔽 Downloading image for: {switchgear_name}")
            
            filename = self.clean_filename(switchgear_name, '_image')
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

    def save_to_excel(self, switchgear_data: List[Dict[str, str]], filename: str = None):
        """Save switchgear data to Excel"""
        if filename is None:
            filename = f'polycab_{self.switchgear_type_slug.replace("-", "_")}_switchgear_complete.xlsx'
        
        print(f"\n💾 Saving switchgear data to Excel: {filename}")
        
        try:
            df = pd.DataFrame(switchgear_data)
            
            # Reorder columns for better presentation - including new fields
            column_order = [
                'Name', 'Product_Type', 'Type', 'Brand', 'Model_Number',
                'Short_Description', 'Price', 'Amperage', 'Voltage', 'Poles',
                'Breaking_Capacity', 'Trip_Curve', 'Sensitivity', 'Application', 
                'MCB_Type', 'Module', 'Color', 'IP_Rating',
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
                df.to_excel(writer, sheet_name='Switchgear Data', index=False)
                
                # Format worksheet
                workbook = writer.book
                worksheet = writer.sheets['Switchgear Data']
                
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
            print(f"🔌 Total switchgear products: {len(switchgear_data)}")
            
            # Summary statistics
            downloaded_images = sum(1 for f in switchgear_data if f['Image_Download_Status'] == 'Downloaded')
            
            print(f"🖼️  Images downloaded: {downloaded_images}/{len(switchgear_data)}")
            
        except Exception as e:
            print(f"❌ Error saving Excel: {e}")

    def run(self):
        """Main execution method"""
        print(f"🚀 Polycab {self.switchgear_display_name} Extractor")
        print("=" * 60)
        print(f"📁 Working directory: {self.base_dir}")
        
        try:
            # 1. Discover switchgear URLs
            switchgear_urls = self.discover_switchgear_urls()
            print(f"\n🔍 Found {len(switchgear_urls)} switchgear URLs")
            
            if not switchgear_urls:
                print("❌ No switchgear URLs found!")
                return
            
            # Show first few URLs
            print("\n📋 Sample URLs:")
            for i, url in enumerate(switchgear_urls[:3], 1):
                print(f"  {i}. {url}")
            
            if len(switchgear_urls) > 3:
                print(f"  ... and {len(switchgear_urls) - 3} more")
            
            # 2. Extract switchgear data
            all_switchgear_data = []
            
            for i, url in enumerate(switchgear_urls, 1):
                print(f"\n{'='*50}")
                print(f"[{i}/{len(switchgear_urls)}] Processing Product {i}")
                print(f"{'='*50}")
                
                switchgear_data = self.extract_switchgear_details(url)
                all_switchgear_data.append(switchgear_data)
                
                # time.sleep(2)
            
            # 3. Consolidate variants
            if all_switchgear_data:
                consolidated_switchgear = self.consolidate_variants(all_switchgear_data)
                
                # Save final results
                excel_filename = os.path.join(self.base_dir, f'polycab_{self.switchgear_type_slug.replace("-", "_")}_switchgear_complete.xlsx')
                self.save_to_excel(all_switchgear_data, excel_filename)
                
                # Save JSON
                json_filename = os.path.join(self.base_dir, f'polycab_{self.switchgear_type_slug.replace("-", "_")}_switchgear_complete.json')
                with open(json_filename, 'w', encoding='utf-8') as f:
                    json.dump(all_switchgear_data, f, indent=2, ensure_ascii=False)
                
                print(f"\n🎉 Switchgear Extraction Complete!")
                print(f"✅ Successfully processed: {len(all_switchgear_data)} unique switchgear products")
                print(f"📊 Files saved in: {self.base_dir}")
                
            else:
                print("❌ No switchgear data extracted!")
                
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
            import traceback
            traceback.print_exc()


def main():
    """Main function with all available switchgear types"""
    
    # Complete list of available switchgear types
    available_switchgear_types = {
        # Main switchgear types
        '1': ('mcb', 'MCB (Miniature Circuit Breaker)'),
        '2': ('rccb', 'RCCB (Residual Current Circuit Breaker)'),
        '3': ('rcbo', 'RCBO (Residual Current Circuit Breaker with Overcurrent Protection)'),
        '4': ('isolator', 'Isolator'),
        '5': ('accl', 'ACCL (Auxiliary Contact and Control Lamp)'),
        '6': ('mcb-changeover-switch', 'MCB Changeover Switch'),
        '7': ('distribution-board', 'Distribution Board'),
        
        # Custom option
        '8': ('custom', 'Custom (Enter your own)')
    }
    
    print("🔌 Polycab Comprehensive Switchgear Extractor")
    print("=" * 50)
    print("📋 Available switchgear types:\n")
    
    # Display all switchgear categories
    for key in ['1', '2', '3', '4', '5', '6', '7']:
        slug, display_name = available_switchgear_types[key]
        print(f"  {key}. {display_name}")
    
    print(f"\n  8. Custom (Enter your own slug)")
    
    # Get user choice - supports multiple selections and ranges
    print("\n🔌 Selection Options:")
    print("  • Single: 1")
    print("  • Multiple: 1,2,5")
    print("  • Range: 1-4")
    print("  • Mixed: 1,3-5,6")
    print("  • All: 1-7")
    
    choice_input = input(f"\nSelect switchgear type(s) (1-8): ").strip()
    
    # Parse the input to get list of choices
    selected_choices = parse_choice_input(choice_input, available_switchgear_types.keys())
    
    if not selected_choices:
        print("Invalid choice. Using default MCB.")
        selected_choices = ['1']
    
    # Display selected switchgear types
    print(f"\n🎯 Selected Switchgear Types ({len(selected_choices)}):")
    selected_switchgear = []
    
    for choice in selected_choices:
        if choice in available_switchgear_types:
            switchgear_slug, display_name = available_switchgear_types[choice]
            if switchgear_slug == 'custom':
                switchgear_slug = input(f"Enter switchgear type slug for choice {choice}: ").strip()
                display_name = input(f"Enter display name for choice {choice}: ").strip()
            selected_switchgear.append((switchgear_slug, display_name))
            print(f"  ✅ {display_name} ({switchgear_slug})")
    
    print(f"\n📋 This will extract for {len(selected_switchgear)} switchgear type(s):")
    print("  ✅ Product details (name, specs, features, etc.)")
    print("  ⚡ Amperage & Pole consolidation (merge similar variants)")
    print("  🖼️  Product images")
    print("  💰 Price information") 
    print("  🔌 Technical specifications (Amperage, Voltage, Poles, Breaking Capacity, etc.)")
    print("  💾 Save everything to Excel with proper structure")
    print("  🔄 Multi-page crawling for complete data")
    
    # Show what consolidation strategy will be used
    print(f"\n🔧 Consolidation Strategy:")
    print("  📝 Group products by base name (removing amperage/pole)")
    print("  🔍 Match core specifications (Type, Voltage, Breaking Capacity, etc.)")
    print("  ⚡ Merge variants with same specs but different Amperage/Poles")
    print("  📊 Create comma-separated lists: Amperage, Poles, Voltages")
    print("  💡 Example: '16A MCB' + '32A MCB' → 'MCB (16A, 32A)'")
    
    # Confirmation
    confirm = input(f"\nProceed with comprehensive extraction for all {len(selected_switchgear)} switchgear types? (y/N): ").strip().lower()
    if confirm not in ['y', 'yes']:
        print("❌ Extraction cancelled.")
        return
    
    # Run the comprehensive extractor for each selected switchgear type
    total_switchgear = len(selected_switchgear)
    for i, (switchgear_slug, display_name) in enumerate(selected_switchgear, 1):
        print(f"\n{'='*60}")
        print(f"🔄 Processing {i}/{total_switchgear}: {display_name}")
        print(f"{'='*60}")
        
        try:
            extractor = PolycabSwitchgearExtractor(switchgear_slug, display_name)
            extractor.run()
            print(f"✅ Completed: {display_name}")
        except Exception as e:
            print(f"❌ Error processing {display_name}: {str(e)}")
            continue
    
    print(f"\n🎉 Batch extraction completed for {total_switchgear} switchgear types!")


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


def run_all_switchgear():
    """Quick function to run all switchgear types"""
    available_switchgear_types = {
        '1': ('mcb', 'MCB (Miniature Circuit Breaker)'),
        '2': ('rccb', 'RCCB (Residual Current Circuit Breaker)'),
        '3': ('rcbo', 'RCBO (Residual Current Circuit Breaker with Overcurrent Protection)'),
        '4': ('isolator', 'Isolator'),
        '5': ('accl', 'ACCL (Auxiliary Contact and Control Lamp)'),
        '6': ('mcb-changeover-switch', 'MCB Changeover Switch'),
        '7': ('distribution-board', 'Distribution Board'),
    }
    
    print("🔌 Polycab All Switchgear Types Batch Extractor")
    print("=" * 50)
    print("📋 Will process the following switchgear types:\n")
    
    for key, (slug, display_name) in available_switchgear_types.items():
        print(f"  {key}. {display_name}")
    
    confirm = input(f"\nProceed with extraction for all {len(available_switchgear_types)} switchgear types? (y/N): ").strip().lower()
    if confirm not in ['y', 'yes']:
        print("❌ Extraction cancelled.")
        return
    
    # Run extraction for each switchgear type
    total_switchgear = len(available_switchgear_types)
    for i, (key, (switchgear_slug, display_name)) in enumerate(available_switchgear_types.items(), 1):
        print(f"\n{'='*60}")
        print(f"🔄 Processing {i}/{total_switchgear}: {display_name}")
        print(f"{'='*60}")
        
        try:
            extractor = PolycabSwitchgearExtractor(switchgear_slug, display_name)
            extractor.run()
            print(f"✅ Completed: {display_name}")
        except Exception as e:
            print(f"❌ Error processing {display_name}: {str(e)}")
            continue
    
    print(f"\n🎉 Batch extraction completed for all {total_switchgear} switchgear types!")


if __name__ == "__main__":
    # Option 1: Use the interactive main function
    main()
    
    # Option 2: Or use the run all function
    # run_all_switchgear()
