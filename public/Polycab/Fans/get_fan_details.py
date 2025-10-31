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

class PolycabFansExtractor:
    def __init__(self, fan_type_slug: str = "ceiling-fan", fan_display_name: str = "Ceiling Fan"):
        """
        Initialize the comprehensive fan extractor with configurable fan type
        """
        self.base_url = "https://polycab.com"
        self.cms_base_url = "https://cms.polycab.com"
        self.fan_type_slug = fan_type_slug
        self.fan_display_name = fan_display_name
        
        # Create directories
        self.base_dir = f'polycab_{self.fan_type_slug.replace("-", "_")}_fans'
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
        
        # Color consolidation patterns
        self.color_keywords = [
            'white', 'brown', 'black', 'ivory', 'antique', 'copper', 'bronze', 
            'silver', 'gold', 'blue', 'red', 'green', 'grey', 'gray', 'pearl',
            'matte', 'glossy', 'metallic', 'wooden', 'teak', 'mahogany', 'bianco',
            'rosewood', 'walnut', 'espresso', 'midnight', 'smoke', 'champagne',
            'titanium', 'onyx', 'opal', 'cream', 'classic', 'natural', 'luxe'
        ]
        
        # Product type URLs mapping
        self.fan_urls = {
            "ceiling-fan": "https://polycab.com/fans/ceiling-fan/c",
            "table-fan": "https://polycab.com/fans/table-fan/c",
            "wall-fan": "https://polycab.com/fans/wall-fan/c",
            "pedestal-fan": "https://polycab.com/fans/pedestal-fan/c",
            "exhaust-fan": "https://polycab.com/fans/exhaust-fan/c",
            "air-circulator": "https://polycab.com/fans/air-circulator/c",
            "farrata-fan": "https://polycab.com/fans/farrata-fan/c"
        }
    
    def discover_fan_urls(self) -> List[str]:
        """Discover fan product URLs from all pages of category"""
        fan_urls = set()
        
        try:
            category_url = self.fan_urls.get(self.fan_type_slug, f"{self.base_url}/fans/{self.fan_type_slug}/c")
            print(f"🔍 Fetching fans from: {category_url}")
            
            # Try different pagination approaches
            page = 1
            max_pages = 20  # Safety limit
            
            while page <= max_pages:
                print(f"📄 Fetching page {page}...")
                
                # Try different pagination URL patterns
                page_urls = [
                    f"{category_url}?page={page}",
                    f"{category_url}?p={page}",
                    f"{category_url}/?page={page}",
                    f"{category_url}/?p={page}",
                    category_url if page == 1 else None  # First page without parameters
                ]
                
                page_fan_urls = set()
                response = None
                
                for page_url in page_urls:
                    if page_url is None:
                        continue
                        
                    try:
                        response = self.session.get(page_url, timeout=30)
                        response.raise_for_status()
                        
                        soup = BeautifulSoup(response.text, 'html.parser')
                        
                        # Find all product links in the page
                        product_links = soup.find_all('a', href=True)
                        
                        current_page_urls = set()
                        for link in product_links:
                            href = link.get('href')
                            if href and self._is_fan_product_url(href):
                                if not href.startswith('http'):
                                    href = urljoin(self.base_url, href)
                                current_page_urls.add(href)
                        
                        if current_page_urls:
                            page_fan_urls = current_page_urls
                            print(f"✅ Page {page}: Found {len(current_page_urls)} products using {page_url}")
                            break
                            
                    except Exception as e:
                        print(f"⚠️  Failed to fetch {page_url}: {e}")
                        continue
                
                # If no URLs found on this page, try alternative approaches
                if not page_fan_urls and response:
                    page_fan_urls = self._try_ajax_pagination(category_url, page)
                
                # If still no URLs found, we've reached the end
                if not page_fan_urls:
                    print(f"🏁 No more products found on page {page}. Stopping pagination.")
                    break
                
                # Add new URLs (avoid duplicates)
                new_urls = page_fan_urls - fan_urls
                if not new_urls and page > 1:
                    print(f"🏁 No new products on page {page}. Reached end of pagination.")
                    break
                
                fan_urls.update(page_fan_urls)
                print(f"📊 Page {page}: Added {len(new_urls)} new URLs (Total: {len(fan_urls)})")
                
                page += 1
                time.sleep(2)  # Be respectful between page requests
            
            print(f"✅ Found {len(fan_urls)} total fan product URLs across {page-1} pages")
            
        except Exception as e:
            print(f"❌ Error discovering URLs: {e}")
        
        return list(fan_urls)

    def _try_ajax_pagination(self, base_url: str, page: int) -> set:
        """Try to fetch products using AJAX pagination"""
        ajax_urls = []
        
        try:
            # Common AJAX pagination patterns for e-commerce sites
            ajax_patterns = [
                f"{self.base_url}/api/products/fans/{self.fan_type_slug}?page={page}",
                f"{self.base_url}/Products/GetFansGridPartial?page={page}&productTypeSlug={self.fan_type_slug}",
                f"{self.base_url}/Products/GetProductsGridPartial?page={page}&category={self.fan_type_slug}",
                f"{base_url}/load-more?page={page}",
            ]
            
            for ajax_url in ajax_patterns:
                try:
                    response = self.session.get(ajax_url, timeout=15)
                    if response.status_code == 200 and len(response.text) > 100:
                        print(f"📡 Trying AJAX: {ajax_url}")
                        
                        # Try to parse as JSON first
                        try:
                            data = response.json()
                            # Look for HTML content in JSON response
                            html_content = data.get('html', '') or data.get('content', '') or str(data)
                        except:
                            # If not JSON, treat as HTML
                            html_content = response.text
                        
                        if html_content:
                            soup = BeautifulSoup(html_content, 'html.parser')
                            product_links = soup.find_all('a', href=True)
                            
                            urls = set()
                            for link in product_links:
                                href = link.get('href')
                                if href and self._is_fan_product_url(href):
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

    def _check_for_load_more_button(self, soup: BeautifulSoup) -> bool:
        """Check if there's a 'Load More' button indicating more pages"""
        load_more_selectors = [
            'button[class*="load-more"]',
            'a[class*="load-more"]',
            'button[class*="show-more"]',
            'a[class*="show-more"]',
            'button:contains("Load More")',
            'a:contains("Load More")',
            'button:contains("Show More")',
            'a:contains("Show More")'
        ]
        
        for selector in load_more_selectors:
            element = soup.select_one(selector)
            if element and not element.get('disabled'):
                return True
        
        return False

    def _extract_pagination_info(self, soup: BeautifulSoup) -> dict:
        """Extract pagination information from the page"""
        pagination_info = {
            'current_page': 1,
            'total_pages': 1,
            'has_next': False
        }
        
        # Look for pagination elements
        pagination_selectors = [
            '.pagination',
            '.page-numbers',
            '[class*="pagination"]',
            '[class*="paging"]'
        ]
        
        for selector in pagination_selectors:
            pagination = soup.select_one(selector)
            if pagination:
                # Look for page numbers
                page_links = pagination.find_all('a', href=True)
                page_numbers = []
                
                for link in page_links:
                    text = link.get_text().strip()
                    if text.isdigit():
                        page_numbers.append(int(text))
                
                if page_numbers:
                    pagination_info['total_pages'] = max(page_numbers)
                    
                # Look for "Next" button
                next_button = pagination.find('a', string=re.compile(r'next|>', re.IGNORECASE))
                if next_button and not next_button.get('disabled'):
                    pagination_info['has_next'] = True
                    
                break
        
        return pagination_info

    def _is_fan_product_url(self, url: str) -> bool:
        """Check if URL is a fan product page"""
        url_lower = url.lower()
        # Look for product patterns with category IDs and product IDs
        return (
            '/p-' in url and 
            ('/c-' in url or 'fan' in url_lower) and
            not any(x in url_lower for x in ['javascript:', 'mailto:', '#', '?'])
        )
    def consolidate_color_variants(self, all_fan_data: List[Dict]) -> List[Dict]:
        """Consolidate color variants into single products only if specs match"""
        print("\n🎨 Consolidating color variants...")
        
        # Group fans by base name (removing color references)
        fan_groups = defaultdict(list)
        
        for fan_data in all_fan_data:
            base_name = self._get_base_fan_name(fan_data['Name'])
            fan_groups[base_name].append(fan_data)
        
        consolidated_fans = []
        
        for base_name, variants in fan_groups.items():
            if len(variants) == 1:
                # Single variant, keep as is
                consolidated_fans.append(variants[0])
            else:
                # Multiple variants - group by specifications before consolidating
                spec_groups = self._group_by_specifications(variants)
                
                for spec_signature, spec_variants in spec_groups.items():
                    if len(spec_variants) == 1:
                        # Single variant with this spec, keep as is
                        consolidated_fans.append(spec_variants[0])
                    else:
                        # Multiple variants with same specs - check if they have different colors
                        if self._should_consolidate_variants(spec_variants):
                            consolidated_fan = self._merge_fan_variants(base_name, spec_variants)
                            consolidated_fans.append(consolidated_fan)
                            print(f"  🔗 Consolidated {len(spec_variants)} color variants of: {base_name} ({spec_signature})")
                        else:
                            # Don't consolidate - keep as separate entries
                            consolidated_fans.extend(spec_variants)
                            print(f"  ❌ Not consolidating {len(spec_variants)} variants of: {base_name} - same colors or different key specs")
        
        print(f"✅ Consolidated {len(all_fan_data)} fans into {len(consolidated_fans)} products")
        return consolidated_fans

    def _group_by_specifications(self, variants: List[Dict]) -> Dict[str, List[Dict]]:
        """Group variants by their specification signature"""
        spec_groups = defaultdict(list)
        
        for variant in variants:
            spec_signature = self._get_specification_signature(variant)
            spec_groups[spec_signature].append(variant)
        
        return spec_groups

    def _get_specification_signature(self, fan_data: Dict) -> str:
        """Generate a signature based on key specifications"""
        # Key specs that must match for consolidation
        key_specs = [
            'Sweep_Size',
            'Number_of_Blades', 
            'RPM',
            'Power_Consumption',
            'Air_Delivery',
            'BEE_Rating',
            'Body_Material',
            'Blade_Material',
            'Motor_Winding',
            'Warranty'
        ]
        
        spec_values = []
        for spec in key_specs:
            value = fan_data.get(spec, 'N/A')
            # Normalize the value
            if isinstance(value, str):
                value = value.strip().lower()
            spec_values.append(f"{spec}:{value}")
        
        return "|".join(spec_values)

    def _should_consolidate_variants(self, variants: List[Dict]) -> bool:
        """Check if variants should be consolidated (different colors, same specs)"""
        if len(variants) < 2:
            return False
        
        # Get all colors from variants
        all_colors = set()
        for variant in variants:
            colors = variant.get('Colors', '')
            if colors and colors != 'Available in Multiple Colors':
                # Split multiple colors and add to set
                color_list = [c.strip().lower() for c in colors.split(',')]
                all_colors.update(color_list)
        
        # Only consolidate if we have multiple different colors
        # If all variants have the same color or no color info, don't consolidate
        unique_colors = len(all_colors)
        should_consolidate = unique_colors > 1
        
        print(f"    🎨 Found {unique_colors} unique colors: {', '.join(sorted(all_colors)) if all_colors else 'None'}")
        print(f"    🤔 Should consolidate: {should_consolidate}")
        
        return should_consolidate

    def _merge_fan_variants(self, base_name: str, variants: List[Dict]) -> Dict:
        """Merge multiple color variants into single fan entry"""
        merged = variants[0].copy()  # Start with first variant
        merged['Name'] = base_name
        
        # Collect all colors
        colors = []
        prices = []
        image_paths = []
        
        for variant in variants:
            # Extract colors from Colors field
            variant_colors = variant.get('Colors', '')
            if variant_colors and variant_colors != 'Available in Multiple Colors':
                # Split multiple colors if comma-separated
                color_list = [c.strip() for c in variant_colors.split(',')]
                colors.extend(color_list)
            
            # Collect prices
            if variant.get('Price') and variant['Price'] != 'N/A':
                prices.append(variant['Price'])
            
            # Collect image paths
            if variant.get('Image_Path'):
                image_paths.append(variant['Image_Path'])
        
        # Remove duplicates and empty colors
        unique_colors = []
        for color in colors:
            if color and color.strip() and color not in unique_colors:
                unique_colors.append(color)
        
        # Update merged data
        print(f"  🖌️  Merging colors: {', '.join(unique_colors) if unique_colors else 'N/A'}")
        merged['Colors'] = ', '.join(unique_colors) if unique_colors else 'Multiple Colors Available'
        merged['Price'] = self._consolidate_prices(prices)
        merged['Image_Path'] = '; '.join(image_paths) if image_paths else ''
        
        # Update download status
        merged['Image_Download_Status'] = 'Multiple' if len(image_paths) > 1 else (variants[0].get('Image_Download_Status', 'Not Found'))
        
        return merged

    def _get_base_fan_name(self, fan_name: str) -> str:
        """Extract base fan name by removing color references"""
        base_name = fan_name.lower()
        
        # Remove color words
        for color in self.color_keywords:
            pattern = rf'\b{color}\b'
            base_name = re.sub(pattern, '', base_name, flags=re.IGNORECASE)
        
        # Remove extra whitespace and normalize
        base_name = ' '.join(base_name.split())
        
        # Remove common suffixes
        base_name = re.sub(r'\s+(fan|ceiling|exhaust)$', '', base_name, flags=re.IGNORECASE)
        
        return base_name.strip().title()
    
    def _extract_color_from_name(self, fan_name: str) -> str:
        """Extract color from fan name"""
        fan_name_lower = fan_name.lower()
        for color in self.color_keywords:
            if color in fan_name_lower:
                return color.title()
        return None
    
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
    
    def extract_fan_details(self, fan_url: str) -> Dict[str, str]:
        """Extract detailed fan information from a product page"""
        print(f"\n🪭 Extracting: {fan_url}")
        
        fan_data = {
            'Name': '',
            'Product_Type': 'Fans',
            'Type': self.fan_display_name,
            'Brand': 'Polycab',
            'Model_Number': '',
            'Specifications': '',
            'Key_Features': '',
            'Colors': '',
            'Sweep_Size': '',
            'RPM': '',
            'Power_Consumption': '',
            'Air_Delivery': '',
            'BEE_Rating': '',
            'Number_of_Blades': '',
            'Blade_Material': '',
            'Body_Material': '',
            'Motor_Winding': '',
            'Warranty': '',
            'Price': 'N/A',
            'Full_Description': '',
            'Product_URL': fan_url,
            'Image_Path': '',
            'Image_Download_Status': 'Not Found'
        }
        
        try:
            response = self.session.get(fan_url, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract fan name
            fan_name = self._extract_fan_name(soup)
            fan_data['Name'] = fan_name
            
            # Extract price
            fan_data['Price'] = self._extract_price(soup)
            
            # Extract description
            fan_data['Full_Description'] = self._extract_description(soup)
            
            # Extract Key_Features
            fan_data['Key_Features'] = self._extract_Key_Features(soup)
            # Extract short description
            fan_data['Short_Description'] = self._extract_short_description(soup)

            # Extract specifications from table
            specs = self._extract_specifications_table(soup)
            fan_data.update(specs)
            
            # Extract colors from name and page
            fan_data['Colors'] = self._extract_colors_from_page(soup, fan_name)
            
            # Extract and download image
            print(f"🔍 Looking for images for: {fan_name}")
            image_url = self._extract_image_url(soup)
            if image_url:
                image_path = self.download_image(fan_name+"_"+fan_data['Colors'], image_url)
                if image_path:
                    fan_data['Image_Path'] = image_path
                    fan_data['Image_Download_Status'] = 'Downloaded'
                else:
                    fan_data['Image_Download_Status'] = 'Failed'
            
            print(f"✅ Extracted: {fan_name[:50]}...")
            
        except Exception as e:
            print(f"❌ Error extracting from {fan_url}: {e}")
            fan_data['Name'] = f"Error: {str(e)}"
        
        return fan_data
    
    def _extract_fan_name(self, soup: BeautifulSoup) -> str:
        """Extract fan name from soup"""
        # Try h2 with fan name
        fan_name_elem = soup.find('h2')
        if fan_name_elem:
            name = fan_name_elem.get_text().strip()
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
        """Extract short description from prod__subtitle"""
        # Look for the specific prod__subtitle element
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
        # Look for price text patterns
        price_text = soup.get_text()
        
        # Try to find Rs. or ₹ followed by numbers
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
        # Look for description in the specific Polycab structure
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
                if description and len(description) > 20:  # Ensure it's meaningful content
                    return description
        
        # Look for any paragraph in prod__desc section
        prod_desc_section = soup.find('section', class_='prod__desc')
        if prod_desc_section:
            paragraphs = prod_desc_section.find_all('p')
            for p in paragraphs:
                text = p.get_text().strip()
                if text and len(text) > 20:
                    return text
        
        # Try to find description paragraph near product info
        paragraphs = soup.find_all('p')
        for p in paragraphs:
            text = p.get_text().strip()
            if len(text) > 50 and any(word in text.lower() for word in ['fan', 'blade', 'air', 'circulation', 'design', 'premium', 'luxury']):
                return text
        
        return ''

    def _extract_Key_Features(self, soup: BeautifulSoup) -> str:
        """Extract Key_Features/features"""
        Key_Features = []
        
        # Look for Key_Features in the specific Polycab structure
        Key_Features_section = soup.find('div', class_='prod__Key_Features')
        if Key_Features_section:
            # Extract Key_Features from the unordered list
            highlight_list = Key_Features_section.find('ul')
            if highlight_list:
                list_items = highlight_list.find_all('li')
                for item in list_items:
                    text = item.get_text().strip()
                    if text:
                        Key_Features.append(text)
        
        # Look for warranty information from warranty icon
        warranty_elem = soup.find('img', src=lambda x: x and 'warranty' in x.lower() if x else False)
        if warranty_elem:
            src = warranty_elem.get('src', '')
            # Extract warranty years from filename (e.g., "3_year_warranty.png" -> "3 Year Warranty")
            warranty_match = re.search(r'(\d+)_year_warranty', src)
            if warranty_match:
                warranty_text = f"{warranty_match.group(1)} Year Warranty"
                if warranty_text not in Key_Features:
                    Key_Features.append(warranty_text)
            else:
                Key_Features.append("Product Warranty")
        
        # Look for power saving/star rating from power saving icon
        power_elem = soup.find('img', src=lambda x: x and 'power_saving' in x.lower() if x else False)
        if power_elem:
            src = power_elem.get('src', '')
            # Extract star rating from filename (e.g., "power_saving_1.png" -> "1 Star Rated")
            star_match = re.search(r'power_saving_(\d+)', src)
            if star_match:
                star_text = f"{star_match.group(1)} Star Rated"
                if star_text not in Key_Features:
                    Key_Features.append(star_text)
            else:
                Key_Features.append("Energy Efficient")
        
        # Look for BLDC in product name or description
        page_text = soup.get_text().upper()
        if 'BLDC' in page_text:
            bldc_text = "BLDC Motor"
            if bldc_text not in Key_Features:
                Key_Features.append(bldc_text)
        
        # Remove duplicates while preserving order
        unique_Key_Features = []
        for highlight in Key_Features:
            if highlight not in unique_Key_Features:
                unique_Key_Features.append(highlight)
        
        # Return Key_Features or fallback
        if unique_Key_Features:
            return ' , '.join(unique_Key_Features)
        else:
            return 'Energy efficient motor | Superior air delivery | Durable construction'

    def _extract_specifications_table(self, soup: BeautifulSoup) -> Dict[str, str]:
        """Extract specifications from table"""
        specs = {
            'BEE_Rating': 'N/A',
            'Sweep_Size': 'N/A',
            'Number_of_Blades': 'N/A',
            'RPM': 'N/A',
            'Air_Delivery': 'N/A',
            'Power_Consumption': 'N/A',
            'Body_Material': 'N/A',
            'Blade_Material': 'N/A',
            'Motor_Winding': 'N/A',
            'Warranty': 'N/A'
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
                    
                    if 'bee' in key or 'star rating' in key:
                        specs['BEE_Rating'] = f"{value} Star" if value.isdigit() else value
                    elif 'sweep' in key or 'size' in key:
                        specs['Sweep_Size_(mm)'] = value
                    elif 'blade' in key and 'number' in key:
                        specs['Number_of_Blades'] = value
                    elif 'speed' in key or 'rpm' in key:
                        specs['Speed_(RPM)'] = value
                    elif 'air delivery' in key or 'cmm' in key:
                        specs['Air_Delivery_(CMM)'] = value
                    elif 'power' in key or 'watt' in key:
                        specs['Power_Consumption_(Watt)'] = value
                    elif 'body material' in key:
                        specs['Body_Material'] = value
                    elif 'blade material' in key:
                        specs['Blade_Material'] = value
                    elif 'motor winding' in key:
                        specs['Motor_Winding'] = value
                    elif 'warranty' in key:
                        specs['Warranty'] = value
        
        # Also try to extract from product description area
        self._extract_specs_from_text(soup, specs)
        
        # Format specifications string
        spec_parts = []
        for key, value in specs.items():
            if value != 'N/A':
                clean_key = key.replace('_', ' ').title()
                spec_parts.append(f"{clean_key}: {value}")
        
        specs['Specifications'] = ' , '.join(spec_parts) if spec_parts else 'Standard specifications'
        
        return specs
    
    def _extract_specs_from_text(self, soup: BeautifulSoup, specs: Dict[str, str]):
        """Extract specs from product text/description"""
        text = soup.get_text().lower()
        
        # Try to extract sweep size
        if specs['Sweep_Size'] == 'N/A':
            sweep_match = re.search(r'(\d+)mm sweep', text)
            if sweep_match:
                specs['Sweep_Size'] = f"{sweep_match.group(1)}mm"
        
        # Try to extract blade count
        if specs['Number_of_Blades'] == 'N/A':
            blade_match = re.search(r'(\d+)\s+(?:aluminium|abs|plastic)\s+blades?', text)
            if blade_match:
                specs['Number_of_Blades'] = blade_match.group(1)
    
    def _extract_colors_from_page(self, soup: BeautifulSoup, fan_name: str) -> str:
        """Extract available colors from page"""
        colors = set()
        
        # First, look for the specific colorName span element
        color_elem = soup.find('span', id='colorName')
        if color_elem:
            color_text = color_elem.get_text().strip()
            if color_text:
                colors.add(color_text.title())
        
        # If no colorName span, look for color in prod__desc paragraph
        if not colors:
            desc_elem = soup.find('p', class_='prod__desc no-pipe')
            if desc_elem:
                desc_text = desc_elem.get_text().strip()
                # Extract color from text like "Sky Blue (With Copper Motor)"
                color_match = re.match(r'^([^(]+)', desc_text)
                if color_match:
                    color_text = color_match.group(1).strip()
                    if color_text:
                        colors.add(color_text.title())
        
        # If still no colors, extract from fan name
        if not colors:
            fan_name_lower = fan_name.lower()
            for color in self.color_keywords:
                if color in fan_name_lower:
                    colors.add(color.title())
        
        # Clean and return colors
        if colors:
            return ', '.join(sorted(colors))
        else:
            return 'Available in Multiple Colors'

    def _extract_image_url(self, soup: BeautifulSoup) -> str:
        """Extract main product image URL"""
        # Look for main product image
        img_elements = soup.find_all('img')
        
        for img in img_elements:
            src = img.get('src', '')
            alt = img.get('alt', '').lower()
            
            # Skip small icons and non-product images
            if any(skip in src.lower() for skip in ['icon', 'logo', 'menu', 'search', 'sticky']):
                continue
            
            # Look for product images from CMS
            if 'cms.polycab.com' in src and any(ext in src.lower() for ext in ['.png', '.jpg', '.jpeg', '.webp']):
                # Prefer images with product-like names or larger dimensions
                if any(term in src.lower() for term in ['_img_', 'product', 'fan']):
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
    
    def download_image(self, fan_name: str, image_url: str) -> str:
        """Download fan image"""
        try:
            print(f"🔽 Downloading image for: {fan_name}")
            
            filename = self.clean_filename(fan_name, '_image')
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
    
    def save_to_excel(self, fans_data: List[Dict[str, str]], filename: str = None):
        """Save fan data to Excel"""
        if filename is None:
            filename = f'polycab_{self.fan_type_slug.replace("-", "_")}_fans_complete.xlsx'
        
        print(f"\n💾 Saving fan data to Excel: {filename}")
        
        try:
            df = pd.DataFrame(fans_data)
            
            # Reorder columns for better presentation
            column_order = [
                'Name', 'Product_Type', 'Type', 'Brand', 'Model_Number',
                'Short_Description', 'Price', 'Colors', 'Sweep_Size', 'Number_of_Blades', 'RPM',
                'Air_Delivery', 'Power_Consumption', 'BEE_Rating',
                'Body_Material', 'Blade_Material', 'Motor_Winding',
                'Warranty', 'Specifications', 'Key_Features', 'Full_Description',
                'Product_URL', 'Image_Path', 'Image_Download_Status'
            ]

            
            # Ensure all columns exist
            for col in column_order:
                if col not in df.columns:
                    df[col] = 'N/A'
            
            # Reorder DataFrame columns
            df = df[column_order]
            
            with pd.ExcelWriter(filename, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name='Product Data', index=False)
                
                # Format worksheet
                workbook = writer.book
                worksheet = writer.sheets['Product Data']
                
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
            print(f"🪭 Total fans: {len(fans_data)}")
            
            # Summary statistics
            downloaded_images = sum(1 for f in fans_data if f['Image_Download_Status'] == 'Downloaded')
            
            print(f"🖼️  Images downloaded: {downloaded_images}/{len(fans_data)}")
            
        except Exception as e:
            print(f"❌ Error saving Excel: {e}")

    def run(self):
        """Main execution method"""
        print(f"🚀 Polycab {self.fan_display_name} Extractor")
        print("=" * 60)
        print(f"📁 Working directory: {self.base_dir}")
        
        try:
            # 1. Discover fan URLs
            fan_urls = self.discover_fan_urls()
            print(f"\n🔍 Found {len(fan_urls)} fan URLs")
            
            if not fan_urls:
                print("❌ No fan URLs found!")
                return
            
            # Show first few URLs
            print("\n📋 Sample URLs:")
            for i, url in enumerate(fan_urls[:3], 1):
                print(f"  {i}. {url}")
            
            if len(fan_urls) > 3:
                print(f"  ... and {len(fan_urls) - 3} more")
            
            # 2. Extract fan data
            all_fans_data = []
            
            for i, url in enumerate(fan_urls, 1):
                print(f"\n{'='*50}")
                print(f"[{i}/{len(fan_urls)}] Processing Product {i}")
                print(f"{'='*50}")
                
                fan_data = self.extract_fan_details(url)
                all_fans_data.append(fan_data)
                
                time.sleep(2)  # Be respectful to server
                
                # Intermediate save every 10 fans
                if i % 10 == 0:
                    temp_filename = f'polycab_{self.fan_type_slug.replace("-", "_")}_fans_partial_{i}.json'
                    temp_path = os.path.join(self.base_dir, temp_filename)
                    with open(temp_path, 'w', encoding='utf-8') as f:
                        json.dump(all_fans_data, f, indent=2, ensure_ascii=False)
                    print(f"💾 Intermediate save: {temp_filename}")
            
            # 3. Consolidate color variants
            if all_fans_data:
                consolidated_fans = self.consolidate_color_variants(all_fans_data)
                
                # Save final results
                excel_filename = os.path.join(self.base_dir, f'polycab_{self.fan_type_slug.replace("-", "_")}_fans_complete.xlsx')
                self.save_to_excel(consolidated_fans, excel_filename)
                
                # Save JSON
                json_filename = os.path.join(self.base_dir, f'polycab_{self.fan_type_slug.replace("-", "_")}_fans_complete.json')
                with open(json_filename, 'w', encoding='utf-8') as f:
                    json.dump(consolidated_fans, f, indent=2, ensure_ascii=False)
                
                print(f"\n🎉 Product Extraction Complete!")
                print(f"✅ Successfully processed: {len(consolidated_fans)} unique fans")
                print(f"📊 Files saved in: {self.base_dir}")
                
            else:
                print("❌ No fan data extracted!")
                
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
            import traceback
            traceback.print_exc()

def main():
    """Main function with all available fan types"""
    
    # Complete list of available fan types
    available_fan_types = {
        # Main fan types
        '1': ('ceiling-fan', 'Ceiling Product'),
        '2': ('exhaust-fan', 'Exhaust Product'),
        '3': ('pedestal-fan', 'Pedestal Product'),
        '4': ('wall-fan', 'Wall Product'),
        '5': ('table-fan', 'Table Product'),
        '6': ('air-circulator', 'Air Circulator'),
        '7': ('farrata-fan', 'Farrata Product'),
        
        # Custom option
        '8': ('custom', 'Custom (Enter your own)')
    }
    
    print("🪭 Polycab Comprehensive Product Extractor")
    print("=" * 50)
    print("📋 Available fan types:\n")
    
    # Display all fan categories
    for key in ['1', '2', '3', '4', '5', '6', '7']:
        slug, display_name = available_fan_types[key]
        print(f"  {key}. {display_name}")
    
    print(f"\n  8. Custom (Enter your own slug)")
    
    # Get user choice - supports multiple selections and ranges
    print("\n💡 Selection Options:")
    print("  • Single: 1")
    print("  • Multiple: 1,2,5")
    print("  • Range: 1-4")
    print("  • Mixed: 1,3-5,7")
    print("  • All: 1-7")
    
    choice_input = input(f"\nSelect fan type(s) (1-8): ").strip()
    
    # Parse the input to get list of choices
    selected_choices = parse_choice_input(choice_input, available_fan_types.keys())
    
    if not selected_choices:
        print("Invalid choice. Using default Ceiling Product.")
        selected_choices = ['1']
    
    # Display selected fan types
    print(f"\n🎯 Selected Product Types ({len(selected_choices)}):")
    selected_fans = []
    
    for choice in selected_choices:
        if choice in available_fan_types:
            fan_slug, display_name = available_fan_types[choice]
            if fan_slug == 'custom':
                fan_slug = input(f"Enter fan type slug for choice {choice}: ").strip()
                display_name = input(f"Enter display name for choice {choice}: ").strip()
            selected_fans.append((fan_slug, display_name))
            print(f"  ✅ {display_name} ({fan_slug})")
    
    print(f"\n📋 This will extract for {len(selected_fans)} fan type(s):")
    print("  ✅ Product details (name, specs, Key_Features, etc.)")
    print("  🎨 Color consolidation (merge color variants)")
    print("  🖼️  Product images")
    print("  💰 Price information")
    print("  📊 Technical specifications")
    print("  💾 Save everything to Excel with proper structure")
    print("  🔄 Multi-page crawling for complete data")
    
    # Confirmation
    confirm = input(f"\nProceed with comprehensive extraction for all {len(selected_fans)} fan types? (y/N): ").strip().lower()
    if confirm not in ['y', 'yes']:
        print("❌ Extraction cancelled.")
        return
    
    # Run the comprehensive extractor for each selected fan type
    total_fans = len(selected_fans)
    for i, (fan_slug, display_name) in enumerate(selected_fans, 1):
        print(f"\n{'='*60}")
        print(f"🔄 Processing {i}/{total_fans}: {display_name}")
        print(f"{'='*60}")
        
        try:
            extractor = PolycabFansExtractor(fan_slug, display_name)
            extractor.run()
            print(f"✅ Completed: {display_name}")
        except Exception as e:
            print(f"❌ Error processing {display_name}: {str(e)}")
            continue
    
    print(f"\n🎉 Batch extraction completed for {total_fans} fan types!")

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

def run_all_fans():
    """Quick function to run all fan types"""
    available_fan_types = {
        '1': ('ceiling-fan', 'Ceiling Product'),
        '2': ('exhaust-fan', 'Exhaust Product'),
        '3': ('pedestal-fan', 'Pedestal Product'),
        '4': ('wall-fan', 'Wall Product'),
        '5': ('table-fan', 'Table Product'),
        '6': ('air-circulator', 'Air Circulator'),
        '7': ('farrata-fan', 'Farrata Product'),
    }
    
    print("🪭 Polycab All Product Types Batch Extractor")
    print("=" * 50)
    print("📋 Will process the following fan types:\n")
    
    for key, (slug, display_name) in available_fan_types.items():
        print(f"  {key}. {display_name}")
    
    confirm = input(f"\nProceed with extraction for all {len(available_fan_types)} fan types? (y/N): ").strip().lower()
    if confirm not in ['y', 'yes']:
        print("❌ Extraction cancelled.")
        return
    
    # Run extraction for each fan type
    total_fans = len(available_fan_types)
    for i, (key, (fan_slug, display_name)) in enumerate(available_fan_types.items(), 1):
        print(f"\n{'='*60}")
        print(f"🔄 Processing {i}/{total_fans}: {display_name}")
        print(f"{'='*60}")
        
        try:
            extractor = PolycabFansExtractor(fan_slug, display_name)
            extractor.run()
            print(f"✅ Completed: {display_name}")
        except Exception as e:
            print(f"❌ Error processing {display_name}: {str(e)}")
            continue
    
    print(f"\n🎉 Batch extraction completed for all {total_fans} fan types!")

if __name__ == "__main__":
    # Option 1: Use the interactive main function
    main()
    
    # Option 2: Or use the run all function
    # run_all_fans()
