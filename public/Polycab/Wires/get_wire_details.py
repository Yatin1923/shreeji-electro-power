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
    def __init__(self, wire_type_slug: str = "polycabsuprema-house-wires", wire_display_name: str = "PolycabSuprema House Wires"):
        """
        Initialize the comprehensive wire extractor with configurable wire type
        """
        self.base_url = "https://polycab.com"
        self.cms_base_url = "https://cms.polycab.com"
        self.wire_type_slug = wire_type_slug
        self.wire_display_name = wire_display_name
        
        # Create directories
        self.base_dir = f'polycab_{self.wire_type_slug.replace("-", "_")}_wires'
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
        
        # Size patterns for consolidation
        self.size_patterns = [
            r'(\d+(?:\.\d+)?)\s*sq\.?\s*mm',
            r'(\d+(?:\.\d+)?)\s*sqmm',
            r'(\d+(?:\.\d+)?)\s*square\s*mm'
        ]
        
        # Length patterns
        self.length_patterns = [
            r'(\d+)\s*meters?',
            r'(\d+)\s*m\b',
            r'(\d+)\s*meter'
        ]
        
        # Wire type URLs mapping
        self.wire_urls = {
            # House Wires
            "polycabsuprema-house-wires": "https://polycab.com/wires/polycabsuprema-house-wires/c",
            "polycabmaximaplus-green-wire": "https://polycab.com/wires/polycabmaximaplus-green-wire/c",
            "polycabprimma-house-wires": "https://polycab.com/wires/polycabprimma-house-wires/c",
            "etira-house-wires": "https://polycab.com/wires/etira-house-wires/c",
            "polycaboptima-plus": "https://polycab.com/wires/polycaboptima-plus/c",
            
            # 180 Meter Wires
            "greenwire-180m": "https://polycab.com/wires/greenwire-180m/c",
            "polycab-lf-fr-180m": "https://polycab.com/wires/polycab-lf-fr-180m/c"
        }
    
    def discover_wire_urls(self) -> List[str]:
        """Discover wire product URLs from all pages of category"""
        wire_urls = set()
        
        try:
            category_url = self.wire_urls.get(self.wire_type_slug, f"{self.base_url}/wires/{self.wire_type_slug}/c")
            print(f"🔍 Fetching wire products from: {category_url}")
            
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
                    page_wire_urls = self._try_ajax_pagination(category_url, page)
                
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
                # time.sleep(2)
            
            print(f"✅ Found {len(wire_urls)} total wire product URLs across {page-1} pages")
            
        except Exception as e:
            print(f"❌ Error discovering URLs: {e}")
        
        return list(wire_urls)

    def _try_ajax_pagination(self, base_url: str, page: int) -> set:
        """Try to fetch products using AJAX pagination"""
        try:
            ajax_patterns = [
                f"{self.base_url}/api/products/wires/{self.wire_type_slug}?page={page}",
                f"{self.base_url}/Products/GetWireGridPartial?page={page}&productTypeSlug={self.wire_type_slug}",
                f"{self.base_url}/Products/GetProductsGridPartial?page={page}&category={self.wire_type_slug}",
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
            ('/c-' in url or any(term in url_lower for term in [
                'polycabsuprema', 'polycabmaxima', 'polycabprimma', 'etira', 
                'polycaboptima', 'greenwire', 'lf-fr', 'house-wire', 'wire'
            ])) and
            not any(x in url_lower for x in ['javascript:', 'mailto:', '#', '?'])
        )

    def consolidate_variants(self, all_wire_data: List[Dict]) -> List[Dict]:
        """
        Consolidate wire variants based on similar specs but different colors/lengths
        
        Consolidation Strategy:
        1. Group by base product name (removing color/length references)
        2. Group by core specifications (excluding color/length)
        3. Merge if specifications match but colors/lengths differ
        4. Create comma-separated lists for different color and length configurations
        """
        print("\n🔄 Consolidating wire variants...")
        
        # Group wire products by base name
        wire_groups = defaultdict(list)
        
        for wire_data in all_wire_data:
            base_name = self._get_base_wire_name(wire_data['Name'])
            wire_groups[base_name].append(wire_data)
        
        consolidated_wires = []
        
        for base_name, variants in wire_groups.items():
            if len(variants) == 1:
                consolidated_wires.append(variants[0])
            else:
                # Group by core specifications (excluding color/length)
                spec_groups = self._group_by_core_specifications(variants)
                
                for spec_signature, spec_variants in spec_groups.items():
                    if len(spec_variants) == 1:
                        consolidated_wires.append(spec_variants[0])
                    else:
                        # Check if variants should be consolidated
                        if self._should_consolidate_wire_variants(spec_variants):
                            consolidated_product = self._merge_wire_variants(base_name, spec_variants)
                            consolidated_wires.append(consolidated_product)
                            
                            # Show what was consolidated
                            colors = set()
                            lengths = set()
                            sizes = set()
                            for v in spec_variants:
                                if v.get('Color'):
                                    colors.add(v['Color'])
                                if v.get('Length'):
                                    lengths.add(v['Length'])
                                if v.get('Size_Sq_MM'):
                                    sizes.add(v['Size_Sq_MM'])
                            
                            print(f"  🔗 Consolidated {len(spec_variants)} variants of: {base_name}")
                            if colors:
                                print(f"    🎨 Color: {', '.join(sorted(colors))}")
                            if lengths:
                                print(f"    📏 Lengths: {', '.join(sorted(lengths))}")
                            if sizes:
                                print(f"    📐 Sizes: {', '.join(sorted(sizes))}")
                        else:
                            # Don't consolidate - keep as separate entries
                            consolidated_wires.extend(spec_variants)
        
        print(f"✅ Consolidated {len(all_wire_data)} products into {len(consolidated_wires)} unique items")
        return consolidated_wires

    def _get_base_wire_name(self, wire_name: str) -> str:
        """Extract base wire name by removing color and length references"""
        base_name = wire_name.lower()
        
        # Remove color patterns
        color_patterns = [
            r'\bred\b', r'\byellow\b', r'\bblue\b', r'\bblack\b', r'\bgreen\b',
            r'\bwhite\b', r'\bgrey\b', r'\bgray\b'
        ]
        for pattern in color_patterns:
            base_name = re.sub(pattern, '', base_name, flags=re.IGNORECASE)
        
        # Remove size patterns  
        for pattern in self.size_patterns:
            base_name = re.sub(pattern, '', base_name, flags=re.IGNORECASE)
        
        # Remove length patterns
        for pattern in self.length_patterns:
            base_name = re.sub(pattern, '', base_name, flags=re.IGNORECASE)
        
        # Clean up spacing and normalize
        base_name = ' '.join(base_name.split())
        base_name = base_name.strip().title()
        
        return base_name

    def _group_by_core_specifications(self, variants: List[Dict]) -> Dict[str, List[Dict]]:
        """Group variants by core specifications (excluding color/length)"""
        spec_groups = defaultdict(list)
        
        for variant in variants:
            spec_signature = self._get_core_specification_signature(variant)
            spec_groups[spec_signature].append(variant)
        
        return spec_groups

    def _get_core_specification_signature(self, wire_data: Dict) -> str:
        """Generate signature based on core specifications (excluding color/length)"""
        # Core specs that must match for consolidation (excluding color/length)
        core_specs = [
            'Product_Series',  # PolycabSuprema, PolycabMaxima+, etc.
            # 'Size_Sq_MM',     # But we'll be flexible with this for some consolidations
            'Insulation_Type',
            'Heat_Resistance',
            'Copper_Grade',
            'Technology',
            'Fire_Safety',
            'Certifications'
        ]
        
        spec_values = []
        for spec in core_specs:
            value = wire_data.get(spec, 'N/A')
            if isinstance(value, str):
                value = value.strip().lower()
            spec_values.append(f"{spec}:{value}")
        
        return "|".join(spec_values)

    def _should_consolidate_wire_variants(self, variants: List[Dict]) -> bool:
        """Check if wire variants should be consolidated"""
        if len(variants) < 2:
            return False
        
        # Get all colors, lengths, and sizes
        all_colors = set()
        all_lengths = set()
        all_sizes = set()
        
        for variant in variants:
            # Color
            color = variant.get('Color', '')
            if color and color not in ['N/A', '']:
                all_colors.add(color.lower())
            
            # Lengths
            length = variant.get('Length', '')
            if length and length not in ['N/A', '']:
                all_lengths.add(length.lower())
            
            # Sizes
            size = variant.get('Size_Sq_MM', '')
            if size and size not in ['N/A', '']:
                all_sizes.add(size.lower())
        
        # Consolidate if we have multiple colors OR multiple lengths (but same size)
        has_multiple_colors = len(all_colors) > 1
        has_multiple_lengths = len(all_lengths) > 1
        has_single_size = len(all_sizes) <= 1  # Same size or no size specified
        
        should_consolidate = (has_multiple_colors or has_single_size) 
        
        print(f"    🎨 Color found: {len(all_colors)} - {', '.join(sorted(all_colors)) if all_colors else 'None'}")
        print(f"    📏 Lengths found: {len(all_lengths)} - {', '.join(sorted(all_lengths)) if all_lengths else 'None'}")
        print(f"    📐 Sizes found: {len(all_sizes)} - {', '.join(sorted(all_sizes)) if all_sizes else 'None'}")
        print(f"    🤔 Should consolidate: {should_consolidate}")
        
        return should_consolidate

    def _merge_wire_variants(self, base_name: str, variants: List[Dict]) -> Dict:
        """Merge multiple wire variants into single entry"""
        merged = variants[0].copy()
        merged['Name'] = base_name
        
        # Collect all variants of configurable attributes
        colors = []
        lengths = []
        sizes = []
        prices = []
        image_paths = []
        
        for variant in variants:
            # Color
            if variant.get('Color') and variant['Color'] != 'N/A':
                colors.append(variant['Color'])
            
            # Lengths
            if variant.get('Length') and variant['Length'] != 'N/A':
                lengths.append(variant['Length'])
            
            # Sizes
            if variant.get('Size_Sq_MM') and variant['Size_Sq_MM'] != 'N/A':
                sizes.append(variant['Size_Sq_MM'])
            
            # Prices
            if variant.get('Price') and variant['Price'] != 'N/A':
                prices.append(variant['Price'])
            
            # Images
            if variant.get('Image_Path'):
                image_paths.append(variant['Image_Path'])
        
        # Remove duplicates and update merged data
        unique_colors = list(dict.fromkeys(colors))  # Preserve order, remove duplicates
        unique_lengths = list(dict.fromkeys(lengths))
        unique_sizes = list(dict.fromkeys(sizes))
        unique_image_paths = list(dict.fromkeys(image_paths))
        
        # Update merged data with consolidated information
        merged['Color'] = ', '.join(unique_colors) if unique_colors else 'N/A'
        merged['Length'] = ', '.join(unique_lengths) if unique_lengths else 'N/A'
        merged['Size_Sq_MM'] = ', '.join(unique_sizes) if unique_sizes else 'N/A'
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

    def extract_wire_details(self, wire_url: str) -> Dict[str, str]:
        """Extract detailed wire information from a product page"""
        print(f"\n🔌 Extracting: {wire_url}")
        
        wire_data = {
            'Name': '',
            'Type': 'Wire',
            'Product_Type': self.wire_display_name.split()[0],  # PolycabSuprema, PolycabMaxima+, etc.
            'Product_Series': self.wire_display_name,
            'Brand': 'Polycab',
            'Model_Number': '',
            'Specifications': '',
            'Key_Features': '',
            'Size_Sq_MM': '',
            'Length': '',
            'Color': '',
            'Insulation_Type': '',
            'Heat_Resistance': '',
            'Copper_Grade': '',
            'Technology': '',
            'Fire_Safety': '',
            'Moisture_Resistance': '',
            'Abrasion_Resistance': '',
            'Eco_Certifications': '',
            'Standards': '',
            'Current_Carrying_Capacity': '',
            'Product_Life': '',
            'Voltage_Rating': '',
            'Conductor_Type': '',
            'Certifications': '',
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
            
            # Extract specifications from table using HTML parsing
            specs = self._extract_specifications_table(soup)
            wire_data.update(specs)
            
            # Extract additional specifications from name/title
            wire_data['Size_Sq_MM'] = self._extract_size_from_page(soup, wire_data['Name'])
            wire_data['Color'] = self._extract_color_from_page(soup, wire_data['Name'])
            wire_data['Length'] = self._extract_length_from_page(soup, wire_data['Name'])
            
            # Extract and download image
            print(f"🔍 Looking for images for: {wire_data['Name']}")
            image_url = self._extract_image_url(soup)
            if image_url:
                image_path = "/Polycab/Wires/" + self.download_image(
                    f"{wire_data['Name']}", 
                    image_url
                )
                if image_path:
                    wire_data['Image_Path'] = image_path
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
            r'Rs\.\s*([\d,]+)',
            r'₹\s*([\d,]+)',
            r'Price[:\s]*Rs\.\s*([\d,]+)',
            r'Price[:\s]*₹\s*([\d,]+)',
            r'MRP[:\s]*Rs\.\s*([\d,]+)',
            r'MRP[:\s]*₹\s*([\d,]+)',
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
        
        # Look for highlights section - Polycab uses specific structure
        highlights_section = soup.find('section', string=lambda text: text and 'highlights' in text.lower()) or soup.find('div', class_='prod__highlights')
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
                    features.append(text)
        
        # If no highlights found, try to extract from general features
        if not features:
            feature_keywords = [
                'Electron beam technology', 'Heat resistance', 'Current carrying capacity',
                'Fire safety', 'Moisture resistance', 'Abrasion resistant',
                'Lead free', 'RoHS', 'REACH', 'Product life'
            ]
            
            page_text = soup.get_text()
            for keyword in feature_keywords:
                if keyword.lower() in page_text.lower():
                    features.append(keyword)
        
        # Return features or fallback
        if features:
            return ' , '.join(features)
        else:
            return 'High quality electrical wire | Safety certified | Durable construction'

    def _extract_specifications_table(self, soup: BeautifulSoup) -> Dict[str, str]:
        """Extract specifications from table using HTML parsing"""
        specs = {
            'Size_Sq_MM': 'N/A',
            'Color': 'N/A',
            'Length': 'N/A',
            'Insulation_Type': 'N/A',
            'Heat_Resistance': 'N/A',
            'Copper_Grade': 'N/A',
            'Technology': 'N/A',
            'Fire_Safety': 'N/A',
            'Moisture_Resistance': 'N/A',
            'Abrasion_Resistance': 'N/A',
            'Eco_Certifications': 'N/A',
            'Standards': 'N/A',
            'Current_Carrying_Capacity': 'N/A',
            'Product_Life': 'N/A',
            'Voltage_Rating': 'N/A',
            'Conductor_Type': 'N/A'
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
                    
                    # Map table keys to our spec keys
                    key_lower = key.lower()
                    if 'size' in key_lower and ('sqmm' in key_lower or 'sq' in key_lower):
                        specs['Size_Sq_MM'] = value
                    elif 'colour' in key_lower or 'color' in key_lower:
                        specs['Color'] = value
                    elif 'length' in key_lower and ('meter' in key_lower or 'm' in key_lower):
                        specs['Length'] = value
                    elif 'insulation' in key_lower:
                        specs['Insulation_Type'] = value
                    elif 'heat' in key_lower and 'resistance' in key_lower:
                        specs['Heat_Resistance'] = value
                    elif 'copper' in key_lower:
                        specs['Copper_Grade'] = value
                    elif 'certification' in key_lower:
                        specs['Eco_Certifications'] = value
                    else:
                        # Store with original key
                        specs[key.replace(' ', '_').replace('(', '').replace(')', '')] = value
        
        # Also extract from product title/heading structure
        self._extract_specs_from_product_title(soup, specs)
        
        # Format specifications string
        spec_parts = []
        for key, value in specs.items():
            if value != 'N/A' and key != 'Specifications':
                clean_key = key.replace('_', ' ').title()
                spec_parts.append(f"{clean_key}: {value}")
        
        specs['Specifications'] = ' ; '.join(spec_parts) if spec_parts else 'Standard wire specifications'
        
        return specs
    
    def _extract_specs_from_product_title(self, soup: BeautifulSoup, specs: Dict[str, str]):
        """Extract specifications from product title structure"""
        
        # Find product name section - Polycab shows key specs in the title area
        title_section = soup.find('h2')  # Main product title
        if title_section:
            title_text = title_section.get_text().strip()
            
            # Extract size from title
            if specs['Size_Sq_MM'] == 'N/A':
                size_match = re.search(r'(\d+(?:\.\d+)?)\s*sq\.?\s*mm', title_text, re.IGNORECASE)
                if size_match:
                    specs['Size_Sq_MM'] = f"{size_match.group(1)} Sq. MM"
            
            # Extract color from title
            if specs['Color'] == 'N/A':
                color_patterns = [r'\b(red|yellow|blue|black|green|white|grey|gray)\b']
                for pattern in color_patterns:
                    color_match = re.search(pattern, title_text, re.IGNORECASE)
                    if color_match:
                        specs['Color'] = color_match.group(1).title()
                        break
            
            # Extract length from title
            if specs['Length'] == 'N/A':
                length_match = re.search(r'(\d+)\s*meters?', title_text, re.IGNORECASE)
                if length_match:
                    specs['Length'] = f"{length_match.group(1)} Meters"

    def _extract_size_from_page(self, soup: BeautifulSoup, wire_name: str) -> str:
        """Extract wire size using HTML parsing"""
        # First check specifications table
        table = soup.find('table')
        if table:
            rows = table.find_all('tr')
            for row in rows:
                cells = row.find_all(['td', 'th'])
                if len(cells) == 2:
                    key = cells[0].get_text().strip().lower()
                    value = cells[1].get_text().strip()
                    
                    if ('size' in key and ('sqmm' in key or 'sq' in key)) and value:
                        return value
        
        # Check product title/heading
        title_elem = soup.find('h2')
        if title_elem:
            title_text = title_elem.get_text().strip()
            for pattern in self.size_patterns:
                match = re.search(pattern, title_text, re.IGNORECASE)
                if match:
                    return f"{match.group(1)} Sq. MM"
        
        return 'N/A'

    def _extract_color_from_page(self, soup: BeautifulSoup, wire_name: str) -> str:
        """Extract wire color"""
        # First check specifications table
        table = soup.find('table')
        if table:
            rows = table.find_all('tr')
            for row in rows:
                cells = row.find_all(['td', 'th'])
                if len(cells) == 2:
                    key = cells[0].get_text().strip().lower()
                    value = cells[1].get_text().strip()
                    
                    if ('colour' in key or 'color' in key) and value:
                        return value
        
        # Check product title/heading
        title_elem = soup.find('h2')
        if title_elem:
            title_text = title_elem.get_text().strip().lower()
            color_patterns = [r'\b(red|yellow|blue|black|green|white|grey|gray)\b']
            for pattern in color_patterns:
                match = re.search(pattern, title_text, re.IGNORECASE)
                if match:
                    return match.group(1).title()
        
        return 'N/A'

    def _extract_length_from_page(self, soup: BeautifulSoup, wire_name: str) -> str:
        """Extract wire length"""
        # First check specifications table
        table = soup.find('table')
        if table:
            rows = table.find_all('tr')
            for row in rows:
                cells = row.find_all(['td', 'th'])
                if len(cells) == 2:
                    key = cells[0].get_text().strip().lower()
                    value = cells[1].get_text().strip()
                    
                    if ('length' in key and ('meter' in key or 'm' in key)) and value:
                        return value
        
        # Check product title/heading
        title_elem = soup.find('h2')
        if title_elem:
            title_text = title_elem.get_text().strip()
            for pattern in self.length_patterns:
                match = re.search(pattern, title_text, re.IGNORECASE)
                if match:
                    return f"{match.group(1)} Meters"
        
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
                if any(term in src.lower() for term in ['_img_', 'product', 'wire', 'ldis', 'housewire']):
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
            return filepath
            
        except Exception as e:
            print(f"❌ Failed to download image: {e}")
            return ""

    def save_to_excel(self, wire_data: List[Dict[str, str]], filename: str = None):
        """Save wire data to Excel"""
        if filename is None:
            filename = f'polycab_{self.wire_type_slug.replace("-", "_")}_wires_complete.xlsx'
        
        print(f"\n💾 Saving wire data to Excel: {filename}")
        
        try:
            df = pd.DataFrame(wire_data)
            
            # Reorder columns for better presentation
            column_order = [
                'Name', 'Product_Type', 'Product_Series', 'Type', 'Brand', 'Model_Number',
                'Short_Description', 'Price', 'Size_Sq_MM', 'Length', 'Color',
                'Insulation_Type', 'Heat_Resistance', 'Copper_Grade', 'Technology',
                'Fire_Safety', 'Moisture_Resistance', 'Abrasion_Resistance',
                'Current_Carrying_Capacity', 'Product_Life', 'Voltage_Rating',
                'Conductor_Type', 'Eco_Certifications', 'Standards', 'Certifications',
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
            
            print(f"🖼️  Images downloaded: {downloaded_images}/{len(wire_data)}")
            
        except Exception as e:
            print(f"❌ Error saving Excel: {e}")

    def run(self):
        """Main execution method"""
        print(f"🚀 Polycab {self.wire_display_name} Extractor")
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
                print(f"[{i}/{len(wire_urls)}] Processing Product {i}")
                print(f"{'='*50}")
                
                wire_data = self.extract_wire_details(url)
                all_wire_data.append(wire_data)
                
                # time.sleep(2)
            
            # 3. Consolidate variants
            if all_wire_data:
                consolidated_wires = self.consolidate_variants(all_wire_data)
                
                # Save final results
                excel_filename = os.path.join(self.base_dir, f'polycab_{self.wire_type_slug.replace("-", "_")}_wires_complete.xlsx')
                self.save_to_excel(consolidated_wires, excel_filename)
                
                # Save JSON
                json_filename = os.path.join(self.base_dir, f'polycab_{self.wire_type_slug.replace("-", "_")}_wires_complete.json')
                with open(json_filename, 'w', encoding='utf-8') as f:
                    json.dump(consolidated_wires, f, indent=2, ensure_ascii=False)
                
                print(f"\n🎉 Wire Extraction Complete!")
                print(f"✅ Successfully processed: {len(consolidated_wires)} unique wire products")
                print(f"📊 Files saved in: {self.base_dir}")
                
            else:
                print("❌ No wire data extracted!")
                
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
            import traceback
            traceback.print_exc()


def main():
    """Main function with all available wire types"""
    
    # Complete list of available wire types
    available_wire_types = {
        # House Wires
        '1': ('polycabsuprema-house-wires', 'PolycabSuprema House Wires'),
        '2': ('polycabmaximaplus-green-wire', 'PolycabMaxima+ Green Wire'),  
        '3': ('polycabprimma-house-wires', 'PolycabPrimma House Wires'),
        '4': ('etira-house-wires', 'Etira House Wires'),
        '5': ('polycaboptima-plus', 'PolycabOptima+ Wires'),
        
        # 180 Meter Wires
        '6': ('greenwire-180m', 'Greenwire 180M'),
        '7': ('polycab-lf-fr-180m', 'Polycab LF FR 180M'),
        
        # Custom option
        '8': ('custom', 'Custom (Enter your own)')
    }
    
    print("🔌 Polycab Comprehensive Wire Extractor")
    print("=" * 50)
    print("📋 Available wire types:\n")
    
    # Display all wire categories
    print("🏠 House Wires:")
    for key in ['1', '2', '3', '4', '5']:
        slug, display_name = available_wire_types[key]
        print(f"  {key}. {display_name}")
    
    print("\n📏 180 Meter Wires:")
    for key in ['6', '7']:
        slug, display_name = available_wire_types[key]
        print(f"  {key}. {display_name}")
    
    print(f"\n  8. Custom (Enter your own slug)")
    
    # Get user choice - supports multiple selections and ranges
    print("\n🔌 Selection Options:")
    print("  • Single: 1")
    print("  • Multiple: 1,2,5")
    print("  • Range: 1-4")
    print("  • Mixed: 1,3-5,6")
    print("  • All: 1-7")
    
    choice_input = input(f"\nSelect wire type(s) (1-8): ").strip()
    
    # Parse the input to get list of choices
    selected_choices = parse_choice_input(choice_input, available_wire_types.keys())
    
    if not selected_choices:
        print("Invalid choice. Using default PolycabSuprema.")
        selected_choices = ['1']
    
    # Display selected wire types
    print(f"\n🎯 Selected Wire Types ({len(selected_choices)}):")
    selected_wires = []
    
    for choice in selected_choices:
        if choice in available_wire_types:
            wire_slug, display_name = available_wire_types[choice]
            if wire_slug == 'custom':
                wire_slug = input(f"Enter wire type slug for choice {choice}: ").strip()
                display_name = input(f"Enter display name for choice {choice}: ").strip()
            selected_wires.append((wire_slug, display_name))
            print(f"  ✅ {display_name} ({wire_slug})")
    
    print(f"\n📋 This will extract for {len(selected_wires)} wire type(s):")
    print("  ✅ Product details (name, specs, features, etc.)")
    print("  🎨 Color & Length consolidation (merge similar variants)")
    print("  🖼️  Product images")
    print("  💰 Price information") 
    print("  🔌 Technical specifications (Size, Length, Color, Insulation, etc.)")
    print("  💾 Save everything to Excel with proper structure")
    print("  🔄 Multi-page crawling for complete data")
    
    # Show what consolidation strategy will be used
    print(f"\n🔧 Consolidation Strategy:")
    print("  📝 Group products by base name (removing color/length)")
    print("  🔍 Match core specifications (Size, Insulation, Technology, etc.)")
    print("  🎨 Merge variants with same specs but different Color/Lengths")
    print("  📊 Create comma-separated lists: Color, Lengths")
    print("  💡 Example: 'Red Wire 90M' + 'Blue Wire 90M' → 'Wire 90M (Red, Blue)'")
    
    # Confirmation
    confirm = input(f"\nProceed with comprehensive extraction for all {len(selected_wires)} wire types? (y/N): ").strip().lower()
    if confirm not in ['y', 'yes']:
        print("❌ Extraction cancelled.")
        return
    
    # Run the comprehensive extractor for each selected wire type
    total_wires = len(selected_wires)
    for i, (wire_slug, display_name) in enumerate(selected_wires, 1):
        print(f"\n{'='*60}")
        print(f"🔄 Processing {i}/{total_wires}: {display_name}")
        print(f"{'='*60}")
        
        try:
            extractor = PolycabWireExtractor(wire_slug, display_name)
            extractor.run()
            print(f"✅ Completed: {display_name}")
        except Exception as e:
            print(f"❌ Error processing {display_name}: {str(e)}")
            continue
    
    print(f"\n🎉 Batch extraction completed for {total_wires} wire types!")


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


def run_all_wires():
    """Quick function to run all wire types"""
    available_wire_types = {
        '1': ('polycabsuprema-house-wires', 'PolycabSuprema House Wires'),
        '2': ('polycabmaximaplus-green-wire', 'PolycabMaxima+ Green Wire'),  
        '3': ('polycabprimma-house-wires', 'PolycabPrimma House Wires'),
        '4': ('etira-house-wires', 'Etira House Wires'),
        '5': ('polycaboptima-plus', 'PolycabOptima+ Wires'),
        '6': ('greenwire-180m', 'Greenwire 180M'),
        '7': ('polycab-lf-fr-180m', 'Polycab LF FR 180M'),
    }
    
    print("🔌 Polycab All Wire Types Batch Extractor")
    print("=" * 50)
    print("📋 Will process the following wire types:\n")
    
    for key, (slug, display_name) in available_wire_types.items():
        print(f"  {key}. {display_name}")
    
    confirm = input(f"\nProceed with extraction for all {len(available_wire_types)} wire types? (y/N): ").strip().lower()
    if confirm not in ['y', 'yes']:
        print("❌ Extraction cancelled.")
        return
    
    # Run extraction for each wire type
    total_wires = len(available_wire_types)
    for i, (key, (wire_slug, display_name)) in enumerate(available_wire_types.items(), 1):
        print(f"\n{'='*60}")
        print(f"🔄 Processing {i}/{total_wires}: {display_name}")
        print(f"{'='*60}")
        
        try:
            extractor = PolycabWireExtractor(wire_slug, display_name)
            extractor.run()
            print(f"✅ Completed: {display_name}")
        except Exception as e:
            print(f"❌ Error processing {display_name}: {str(e)}")
            continue
    
    print(f"\n🎉 Batch extraction completed for all {total_wires} wire types!")


if __name__ == "__main__":
    # Option 1: Use the interactive main function
    main()
    
    # Option 2: Or use the run all function
    # run_all_wires()
