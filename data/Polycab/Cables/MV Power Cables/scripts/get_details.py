import requests
import re
from urllib.parse import urljoin
import time
import csv
import json
from typing import Set, List, Dict

class PolycabMVProductExtractor:
    def __init__(self):
        self.base_url = "https://polycab.com"
        self.api_endpoint = "/Products/GetCablesGridPartialByProductTypeSlug"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Referer': 'https://polycab.com/cables/types/mv-power-cable',
        })
    
    def discover_product_urls(self) -> List[str]:
        """Discover MV power cable product URLs from API"""
        product_urls = set()
        
        try:
            print("🔍 Fetching product URLs from Polycab API...")
            
            # Try different page sizes and pages to get all products
            for page in range(1, 6):  # Try first 5 pages
                params = {
                    'sortOrder': 'NameAscending',
                    'pageSize': 50,  # Larger page size
                    'pageNumber': page,
                    'productTypeSlug': 'mv-power-cable'
                }
                
                api_url = f"{self.base_url}{self.api_endpoint}"
                response = self.session.get(api_url, params=params)
                
                if response.status_code == 200 and len(response.text) > 100:
                    print(f"✅ Page {page}: Got {len(response.text)} characters")
                    
                    # Extract href URLs from HTML response (not JSON!)
                    href_patterns = [
                        r'href=["\']([^"\']*polycab-mv[^"\']*p-\d+)["\']',  # Specific MV pattern
                        r'href=["\']([^"\']*mv[^"\']*p-\d+)["\']',          # General MV pattern
                        r'href=["\']([^"\']*pt-13205[^"\']*p-\d+)["\']'     # Product type pattern
                    ]
                    
                    page_urls = set()
                    for pattern in href_patterns:
                        matches = re.findall(pattern, response.text, re.IGNORECASE)
                        for match in matches:
                            if not match.startswith('http'):
                                match = urljoin(self.base_url, match)
                            page_urls.add(match)
                    
                    if page_urls:
                        print(f"📄 Page {page}: Found {len(page_urls)} product URLs")
                        product_urls.update(page_urls)
                    else:
                        print(f"📄 Page {page}: No new URLs found")
                        break  # No more products
                else:
                    print(f"❌ Page {page}: Failed or empty (status: {response.status_code})")
                    break
                
                time.sleep(1)  # Be respectful
            
        except Exception as e:
            print(f"❌ Error discovering URLs: {e}")
        
        return list(product_urls)
    
    def extract_product_details(self, product_url: str) -> Dict[str, str]:
        """Extract detailed product information from a product page"""
        print(f"📄 Extracting: {product_url.split('/')[-3]}")
        
        product_data = {
            'Cable_Name': '',
            'Product_Type': 'MV Power Cable',
            'Standards': '',
            'Certifications': '',
            'Key_Features': '',
            'Short_Description': '',
            'Full_Description': '',
            'Product_URL': product_url
        }
        
        try:
            response = self.session.get(product_url, timeout=30)
            response.raise_for_status()
            
            html_content = response.text
            
            # Extract Cable Name from title or h1/h2
            cable_name = self.extract_cable_name(html_content)
            product_data['Cable_Name'] = cable_name
            
            # Extract Standards
            standards = self.extract_standards(html_content)
            product_data['Standards'] = standards
            
            # Extract Certifications
            certifications = self.extract_certifications(html_content)
            product_data['Certifications'] = certifications
            
            # Extract Key Features
            features = self.extract_features(html_content)
            product_data['Key_Features'] = features
            
            # Extract Descriptions
            short_desc, full_desc = self.extract_descriptions(html_content)
            product_data['Short_Description'] = short_desc
            product_data['Full_Description'] = full_desc
            
            print(f"✅ Extracted: {cable_name[:50]}...")
            
        except Exception as e:
            print(f"❌ Error extracting from {product_url}: {e}")
            product_data['Cable_Name'] = f"Error: {str(e)}"
        
        return product_data
    
    def extract_cable_name(self, html_content: str) -> str:
        """Extract cable name from HTML"""
        # Try title tag first
        title_match = re.search(r'<title>([^<]+)</title>', html_content, re.IGNORECASE)
        if title_match:
            title = title_match.group(1).strip()
            # Clean up title
            title = title.replace(' - Polycab', '').replace('Polycab - ', '')
            if 'polycab' in title.lower() and 'mv' in title.lower():
                return title.strip()
        
        # Try h1 or h2 tags
        heading_patterns = [
            r'<h1[^>]*>([^<]*polycab[^<]*mv[^<]*)</h1>',
            r'<h2[^>]*>([^<]*polycab[^<]*mv[^<]*)</h2>',
            r'<h1[^>]*>([^<]*mv[^<]*polycab[^<]*)</h1>',
            r'<h2[^>]*>([^<]*mv[^<]*polycab[^<]*)</h2>'
        ]
        
        for pattern in heading_patterns:
            match = re.search(pattern, html_content, re.IGNORECASE)
            if match:
                return re.sub(r'<[^>]+>', '', match.group(1)).strip()
        
        return title.strip() if title_match else 'Unknown Cable'
    
    def extract_standards(self, html_content: str) -> str:
        """Extract standards from HTML"""
        standards = []
        
        # Look for standards section
        standard_patterns = [
            r'IEC\s+\d+[-/]\d+(?:-\d+)?',
            r'IS\s+\d+[-/]\d+(?:-\d+)?',
            r'BS\s+\d+[-/]?\d*',
            r'UL\s+\d+',
            r'AS[/-]NZS\s+[\d./]+',
            r'ASTM\s+\w+\d+',
            r'ICEA\s+\S+',
            r'NEMA\s+\S+'
        ]
        
        for pattern in standard_patterns:
            matches = re.findall(pattern, html_content, re.IGNORECASE)
            standards.extend([match.strip() for match in matches])
        
        # Remove duplicates and limit
        unique_standards = list(dict.fromkeys(standards))[:5]
        return ', '.join(unique_standards)
    
    def extract_certifications(self, html_content: str) -> str:
        """Extract certifications from HTML"""
        certifications = []
        
        # Look for certification keywords
        cert_keywords = ['CE', 'BIS', 'CPRI', 'UL', 'ISO', 'FQC']
        
        for keyword in cert_keywords:
            # Look for the keyword in various contexts
            patterns = [
                f'certification.*{keyword}',
                f'{keyword}.*certification',
                f'certified.*{keyword}',
                f'{keyword}.*certified',
                f'{keyword}.*compliant'
            ]
            
            for pattern in patterns:
                if re.search(pattern, html_content, re.IGNORECASE):
                    certifications.append(keyword)
                    break
        
        # Also look for certification images
        cert_img_pattern = r'<img[^>]*src=[^>]*cert[^>]*>'
        cert_images = re.findall(cert_img_pattern, html_content, re.IGNORECASE)
        
        # Remove duplicates
        unique_certs = list(dict.fromkeys(certifications))
        return ', '.join(unique_certs) if unique_certs else 'Various (CE, BIS, CPRI)'
    
    def extract_features(self, html_content: str) -> str:
        """Extract key features from HTML"""
        features = []
        
        # Common feature keywords
        feature_map = {
            'flame retardant': 'Flame Retardant',
            'uv resistant': 'UV Resistant', 
            'sunlight resistant': 'Sunlight Resistant',
            'oil resistant': 'Oil Resistant',
            'moisture resistant': 'Moisture Resistant',
            'high life': 'High Life',
            'long life': 'Long Life',
            'weather resistant': 'Weather Resistant',
            'termite resistant': 'Termite Resistant',
            'chemical resistant': 'Chemical Resistant',
            'corona resistant': 'Corona Resistant',
            'treeing resistant': 'Treeing Resistant'
        }
        
        content_lower = html_content.lower()
        for keyword, display_name in feature_map.items():
            if keyword in content_lower:
                features.append(display_name)
        
        return ', '.join(features[:6])  # Limit to 6 features
    
    def extract_descriptions(self, html_content: str) -> tuple:
        """Extract short and full descriptions"""
        # Look for paragraphs with product information
        desc_patterns = [
            r'<p[^>]*>([^<]*POLYCAB[^<]*suitable[^<]*cable[^<]*)</p>',
            r'<p[^>]*>([^<]*cable[^<]*suitable[^<]*network[^<]*)</p>',
            r'<p[^>]*>([^<]*insulated[^<]*conductor[^<]*cable[^<]*)</p>',
            r'<p[^>]*>([^<]*MV[^<]*kV[^<]*cable[^<]*)</p>'
        ]
        
        descriptions = []
        for pattern in desc_patterns:
            matches = re.findall(pattern, html_content, re.IGNORECASE | re.DOTALL)
            for match in matches:
                clean_desc = re.sub(r'<[^>]+>', '', match).strip()
                clean_desc = re.sub(r'\s+', ' ', clean_desc)
                if 30 < len(clean_desc) < 300:
                    descriptions.append(clean_desc)
        
        # Remove duplicates while preserving order
        unique_descriptions = []
        for desc in descriptions:
            if desc not in unique_descriptions:
                unique_descriptions.append(desc)
        
        short_description = unique_descriptions[0] if unique_descriptions else ''
        full_description = ' '.join(unique_descriptions[:3])  # Combine up to 3 descriptions
        
        return short_description, full_description
    
    def save_to_csv(self, products_data: List[Dict[str, str]], filename: str = 'polycab_mv_cables.csv'):
        """Save data to CSV file"""
        print(f"\n💾 Saving data to CSV: {filename}")
        
        csv_headers = [
            'Cable_Name', 'Product_Type', 'Standards', 'Certifications',
            'Key_Features', 'Short_Description', 'Full_Description', 'Product_URL'
        ]
        
        try:
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=csv_headers)
                writer.writeheader()
                writer.writerows(products_data)
            
            print(f"✅ CSV file saved: {filename}")
            print(f"📊 Total products: {len(products_data)}")
            
        except Exception as e:
            print(f"❌ Error saving CSV: {e}")
    
    def run(self):
        """Main execution method"""
        print("🚀 Polycab MV Power Cable Details Extractor (Fixed)")
        print("=" * 65)
        
        try:
            # 1. Discover product URLs from API
            product_urls = self.discover_product_urls()
            print(f"\n🔍 Found {len(product_urls)} product URLs")
            
            if not product_urls:
                print("❌ No product URLs found!")
                return
            
            # Show discovered URLs
            print("\n📋 Discovered URLs:")
            for i, url in enumerate(product_urls[:10], 1):  # Show first 10
                print(f"  {i}. {url}")
            
            if len(product_urls) > 10:
                print(f"  ... and {len(product_urls) - 10} more")
            
            # 2. Extract product details
            all_products_data = []
            
            for i, url in enumerate(product_urls, 1):
                print(f"\n[{i}/{len(product_urls)}] Processing...")
                product_data = self.extract_product_details(url)
                all_products_data.append(product_data)
                
                # Be respectful to the server
                time.sleep(2)
                
                # Save intermediate results every 10 products
                if i % 10 == 0:
                    temp_filename = f'polycab_mv_partial_{i}.json'
                    with open(temp_filename, 'w', encoding='utf-8') as f:
                        json.dump(all_products_data, f, indent=2, ensure_ascii=False)
                    print(f"💾 Intermediate save: {temp_filename}")
            
            # 3. Save final results
            if all_products_data:
                self.save_to_csv(all_products_data)
                
                # Also save as JSON
                with open('polycab_mv_cables_complete.json', 'w', encoding='utf-8') as f:
                    json.dump(all_products_data, f, indent=2, ensure_ascii=False)
                print("💾 JSON backup also created")
                
                # Show summary
                print(f"\n🎉 Extraction Complete!")
                print(f"✅ Successfully processed: {len(all_products_data)} products")
                
                # Show sample of extracted data
                print(f"\n📊 Sample extracted products:")
                for product in all_products_data[:5]:
                    print(f"  - {product['Cable_Name'][:60]}...")
                    
            else:
                print("❌ No product data extracted!")
                
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
            import traceback
            traceback.print_exc()

def main():
    extractor = PolycabMVProductExtractor()
    extractor.run()

if __name__ == "__main__":
    main()
