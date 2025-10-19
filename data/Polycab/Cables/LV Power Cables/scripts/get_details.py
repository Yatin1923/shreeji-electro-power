import requests
import re
from urllib.parse import urljoin, urlparse
import time
import csv
import json
import os
from typing import Set, List, Dict
import pandas as pd

class PolycabComprehensiveExtractor:
    def __init__(self, cable_type_slug: str = "mv-power-cable", cable_display_name: str = "MV Power Cable"):
        """
        Initialize the comprehensive extractor with configurable cable type
        """
        self.base_url = "https://polycab.com"
        self.cms_base_url = "https://cms.polycab.com"
        self.api_endpoint = "/Products/GetCablesGridPartialByProductTypeSlug"
        self.cable_type_slug = cable_type_slug
        self.cable_display_name = cable_display_name
        
        # Create directories
        self.base_dir = f'polycab_{self.cable_type_slug.replace("-", "_")}'
        self.images_dir = os.path.join(self.base_dir, 'images')
        self.brochures_dir = os.path.join(self.base_dir, 'brochures')
        
        for directory in [self.base_dir, self.images_dir, self.brochures_dir]:
            if not os.path.exists(directory):
                os.makedirs(directory)
        
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Referer': f'https://polycab.com/cables/types/{cable_type_slug}',
        })
        
        # Known MV cable datasheet URLs (you can expand this for other cable types)
        self.known_datasheets = {
            "mv-power-cable": {
                "Polycab_MV_SC_Cu_EPR_ICEA_NEMA_25kV_Datasheet.pdf": "https://cms.polycab.com/media/todk30ms/iamv00257_ds_01.pdf",
                "Polycab_MV_IS_7098_II_3C_A2XWY_A2XFY_6_35_11kV_E_Datasheet.pdf": "https://cms.polycab.com/media/0xibfdde/ismv00208_ds_01.pdf",
                "Polycab_MV_3C_Cu_EPR_ICEA_NEMA_5kV_Datasheet.pdf": "https://cms.polycab.com/media/qw2ewi0v/iamv00264_ds_01.pdf",
                "Polycab_MV_IS_7098_II_3C_A2XWY_A2XFY_1_9_3_3kV_E_Datasheet.pdf": "https://cms.polycab.com/media/ctwcjagv/ismv00204_ds_01.pdf",
                "Polycab_MV_Cu_BS_6622_12_7_22kV_Datasheet.pdf": "https://cms.polycab.com/media/05pnp42w/bsmv00147_ds_01.pdf",
                "Polycab_MV_AL_BS_7835_19_33_36kV_Datasheet.pdf": "https://cms.polycab.com/media/rr1hpql2/bsmv00125_ds_01.pdf",
                "Polycab_MV_1T_Cu_XLPE_AS_NZS_6_35_11kV_Datasheet.pdf": "https://cms.polycab.com/media/sqcdw33r/anmv00245_ds_01.pdf",
                "Polycab_MV_SC_AL_XLPE_AS_NZS_3_8_6_6kV_Datasheet.pdf": "https://cms.polycab.com/media/lzjl5mbb/anmv00216_ds_01.pdf",
                "Polycab_MV_1_9_3_3kV_E_Single_Core_AL_Armoured_Datasheet.pdf": "https://cms.polycab.com/media/0p2a34fx/ismv00187_ds_01.pdf",
                "Polycab_MV_3_3_3_3kV_UE_Single_Core_AL_Armoured_Datasheet.pdf": "https://cms.polycab.com/media/wntb4o5h/ismv00188_ds_01.pdf"
            }
        }
    
    def discover_product_urls(self) -> List[str]:
        """Discover product URLs from API for the specified cable type"""
        product_urls = set()
        
        try:
            print(f"🔍 Fetching {self.cable_display_name} product URLs from Polycab API...")
            
            for page in range(1, 6):  # Try first 5 pages
                params = {
                    'sortOrder': 'NameAscending',
                    'pageSize': 300,
                    'pageNumber': page,
                    'productTypeSlug': self.cable_type_slug
                }
                
                api_url = f"{self.base_url}{self.api_endpoint}"
                response = self.session.get(api_url, params=params)
                
                if response.status_code == 200 and len(response.text) > 100:
                    print(f"✅ Page {page}: Got {len(response.text)} characters")
                    
                    href_patterns = self._get_url_patterns()
                    
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
                        break
                else:
                    print(f"❌ Page {page}: Failed or empty (status: {response.status_code})")
                    break
                
                time.sleep(1)
            
        except Exception as e:
            print(f"❌ Error discovering URLs: {e}")
        
        return list(product_urls)
    
    def _get_url_patterns(self) -> List[str]:
        """Get URL patterns based on cable type"""
        cable_type_short = self.cable_type_slug.split('-')[0].upper()
        
        patterns = [
            rf'href=["\']([^"\']*polycab-{self.cable_type_slug}[^"\']*p-\d+)["\']',
            rf'href=["\']([^"\']*{cable_type_short.lower()}[^"\']*p-\d+)["\']',
            rf'href=["\']([^"\']*{self.cable_type_slug}[^"\']*p-\d+)["\']',
            r'href=["\']([^"\']*p-\d+)["\']'
        ]
        
        return patterns
    
    def clean_filename(self, text: str, extension: str = "") -> str:
        """Create a clean filename from text"""
        clean_text = re.sub(r'[^\w\s-]', '', text)
        clean_text = re.sub(r'\s+', '_', clean_text.strip())
        clean_text = clean_text[:100]  # Limit length
        return f"{clean_text}{extension}"
    
    def extract_product_details(self, product_url: str) -> Dict[str, str]:
        """Extract detailed product information from a product page"""
        print(f"📄 Extracting: {product_url.split('/')[-1]}")
        
        product_data = {
            'Cable_Name': '',
            'Product_Type': self.cable_display_name,
            'Standards': '',
            'Certifications': '',
            'Key_Features': '',
            'Short_Description': '',
            'Full_Description': '',
            'Product_URL': product_url,
            'Image_Path': '',
            'Brochure_Path': '',
            'Image_Download_Status': 'Not Found',
            'Brochure_Download_Status': 'Not Found'
        }
        
        try:
            response = self.session.get(product_url, timeout=30)
            response.raise_for_status()
            
            html_content = response.text
            
            # Extract basic product info
            cable_name = self.extract_cable_name(html_content)
            product_data['Cable_Name'] = cable_name
            product_data['Standards'] = self.extract_standards(html_content)
            product_data['Certifications'] = self.extract_certifications(html_content)
            product_data['Key_Features'] = self.extract_features(html_content)
            
            short_desc, full_desc = self.extract_descriptions(html_content)
            product_data['Short_Description'] = short_desc
            product_data['Full_Description'] = full_desc
            
            # Extract and download image
            image_url = self.extract_image_url(html_content)
            if image_url:
                image_path = self.download_image(cable_name, image_url)
                if image_path:
                    product_data['Image_Path'] = image_path
                    product_data['Image_Download_Status'] = 'Downloaded'
                else:
                    product_data['Image_Download_Status'] = 'Failed'
            
            # Extract and download brochure
            brochure_url = self.extract_brochure_url(html_content, cable_name)
            if brochure_url:
                brochure_path = self.download_brochure(cable_name, brochure_url)
                if brochure_path:
                    product_data['Brochure_Path'] = brochure_path
                    product_data['Brochure_Download_Status'] = 'Downloaded'
                else:
                    product_data['Brochure_Download_Status'] = 'Failed'
            
            print(f"✅ Extracted: {cable_name[:50]}...")
            
        except Exception as e:
            print(f"❌ Error extracting from {product_url}: {e}")
            product_data['Cable_Name'] = f"Error: {str(e)}"
        
        return product_data
    
    def extract_image_url(self, html_content: str) -> str:
        """Extract main product image URL from HTML"""
        image_patterns = [
            r'<img[^>]*src=["\']([^"\']*cms\.polycab\.com[^"\']*\.(?:png|jpg|jpeg|webp))["\'][^>]*product',
            r'<img[^>]*src=["\']([^"\']*cms\.polycab\.com[^"\']*\.(?:png|jpg|jpeg|webp))["\'][^>]*main',
            r'<img[^>]*src=["\']([^"\']*cms\.polycab\.com[^"\']*\.(?:png|jpg|jpeg|webp))["\']',
            r'background-image:\s*url\(["\']?([^"\']*cms\.polycab\.com[^"\']*\.(?:png|jpg|jpeg|webp))["\']?\)',
            r'"image":\s*"([^"]*cms\.polycab\.com[^"]*\.(?:png|jpg|jpeg|webp))"'
        ]
        
        for pattern in image_patterns:
            match = re.search(pattern, html_content, re.IGNORECASE)
            if match:
                image_url = match.group(1)
                if not image_url.startswith('http'):
                    image_url = urljoin(self.base_url, image_url)
                return image_url
        
        return ""
    
    def extract_brochure_url(self, html_content: str, product_name: str) -> str:
        """Extract brochure/datasheet URL from HTML"""
        # First try to find brochure in the HTML content
        brochure_patterns = [
            r'href=["\']([^"\']*\.pdf[^"\']*)["\'][^>]*(?:download|datasheet|brochure)',
            r'href=["\']([^"\']*cms\.polycab\.com[^"\']*\.pdf[^"\']*)["\']',
            r'"download":\s*"([^"]*\.pdf[^"]*)"',
            r'href=["\']([^"\']*_ds_01\.pdf[^"\']*)["\']'
        ]
        
        for pattern in brochure_patterns:
            match = re.search(pattern, html_content, re.IGNORECASE)
            if match:
                brochure_url = match.group(1)
                if not brochure_url.startswith('http'):
                    brochure_url = urljoin(self.base_url, brochure_url)
                return brochure_url
        
        # If not found in HTML, try known datasheets for this cable type
        if self.cable_type_slug in self.known_datasheets:
            datasheets = self.known_datasheets[self.cable_type_slug]
            # Try to match by product name
            for filename, url in datasheets.items():
                if any(word in product_name.upper() for word in filename.upper().split('_')[2:5]):  # Match key terms
                    return url
        
        return ""
    
    def download_image(self, product_name: str, image_url: str) -> str:
        """Download product image and return local path"""
        try:
            filename = self.clean_filename(product_name, '_image')
            
            # Get file extension from URL
            parsed_url = urlparse(image_url)
            file_ext = os.path.splitext(parsed_url.path)[1] or '.png'
            filename += file_ext
            
            filepath = os.path.join(self.images_dir, filename)
            
            response = self.session.get(image_url, stream=True, timeout=30)
            response.raise_for_status()
            
            with open(filepath, 'wb') as file:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        file.write(chunk)
            
            file_size = os.path.getsize(filepath)
            if file_size < 1024:  # Less than 1KB, probably not valid
                os.remove(filepath)
                return ""
            
            print(f"🖼️  Downloaded image: {filename} ({file_size/1024:.1f} KB)")
            return filepath
            
        except Exception as e:
            print(f"❌ Failed to download image for {product_name}: {e}")
            return ""
    
    def download_brochure(self, product_name: str, brochure_url: str) -> str:
        """Download product brochure/datasheet and return local path"""
        try:
            filename = self.clean_filename(product_name, '_datasheet.pdf')
            filepath = os.path.join(self.brochures_dir, filename)
            
            response = self.session.get(brochure_url, stream=True, timeout=30)
            
            if response.status_code == 404:
                return ""
            
            response.raise_for_status()
            
            # Check if it's actually a PDF
            content_type = response.headers.get('content-type', '').lower()
            if 'pdf' not in content_type and 'octet-stream' not in content_type:
                return ""
            
            with open(filepath, 'wb') as file:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        file.write(chunk)
            
            file_size = os.path.getsize(filepath)
            if file_size < 1024:  # Less than 1KB, probably not valid
                os.remove(filepath)
                return ""
            
            print(f"📄 Downloaded brochure: {filename} ({file_size/1024/1024:.2f} MB)")
            return filepath
            
        except Exception as e:
            print(f"❌ Failed to download brochure for {product_name}: {e}")
            return ""
    
    def extract_cable_name(self, html_content: str) -> str:
        """Extract cable name from HTML"""
        title_match = re.search(r'<title>([^<]+)</title>', html_content, re.IGNORECASE)
        if title_match:
            title = title_match.group(1).strip()
            title = title.replace(' - Polycab', '').replace('Polycab - ', '')
            if 'polycab' in title.lower():
                return title.strip()
        
        cable_keywords = self.cable_type_slug.split('-')
        
        heading_patterns = [
            rf'<h1[^>]*>([^<]*polycab[^<]*{"|".join(cable_keywords)}[^<]*)</h1>',
            rf'<h2[^>]*>([^<]*polycab[^<]*{"|".join(cable_keywords)}[^<]*)</h2>',
            r'<h1[^>]*>([^<]*polycab[^<]*cable[^<]*)</h1>',
            r'<h2[^>]*>([^<]*polycab[^<]*cable[^<]*)</h2>'
        ]
        
        for pattern in heading_patterns:
            match = re.search(pattern, html_content, re.IGNORECASE)
            if match:
                return re.sub(r'<[^>]+>', '', match.group(1)).strip()
        
        return title.strip() if title_match else 'Unknown Cable'
    
    def extract_standards(self, html_content: str) -> str:
        """Extract standards from HTML"""
        standards = []
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
        
        unique_standards = list(dict.fromkeys(standards))[:5]
        return ', '.join(unique_standards)
    
    def extract_certifications(self, html_content: str) -> str:
        """Extract certifications from HTML"""
        certifications = []
        cert_keywords = ['CE', 'BIS', 'CPRI', 'UL', 'ISO', 'FQC']
        
        for keyword in cert_keywords:
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
        
        unique_certs = list(dict.fromkeys(certifications))
        return ', '.join(unique_certs) if unique_certs else 'Various (CE, BIS, CPRI)'
    
    def extract_features(self, html_content: str) -> str:
        """Extract key features from HTML"""
        features = []
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
            'treeing resistant': 'Treeing Resistant',
            'low smoke': 'Low Smoke',
            'zero halogen': 'Zero Halogen',
            'fire resistant': 'Fire Resistant'
        }
        
        content_lower = html_content.lower()
        for keyword, display_name in feature_map.items():
            if keyword in content_lower:
                features.append(display_name)
        
        return ', '.join(features[:6])
    
    def extract_descriptions(self, html_content: str) -> tuple:
        """Extract short and full descriptions"""
        desc_patterns = [
            r'<p[^>]*>([^<]*POLYCAB[^<]*suitable[^<]*cable[^<]*)</p>',
            r'<p[^>]*>([^<]*cable[^<]*suitable[^<]*network[^<]*)</p>',
            r'<p[^>]*>([^<]*insulated[^<]*conductor[^<]*cable[^<]*)</p>',
            r'<p[^>]*>([^<]*cable[^<]*kV[^<]*)</p>',
            r'<p[^>]*>([^<]*conductor[^<]*cable[^<]*applications[^<]*)</p>'
        ]
        
        descriptions = []
        for pattern in desc_patterns:
            matches = re.findall(pattern, html_content, re.IGNORECASE | re.DOTALL)
            for match in matches:
                clean_desc = re.sub(r'<[^>]+>', '', match).strip()
                clean_desc = re.sub(r'\s+', ' ', clean_desc)
                if 30 < len(clean_desc) < 300:
                    descriptions.append(clean_desc)
        
        unique_descriptions = []
        for desc in descriptions:
            if desc not in unique_descriptions:
                unique_descriptions.append(desc)
        
        short_description = unique_descriptions[0] if unique_descriptions else ''
        full_description = ' '.join(unique_descriptions[:3])
        
        return short_description, full_description
    
    def save_to_excel(self, products_data: List[Dict[str, str]], filename: str = None):
        """Save data to Excel file with enhanced formatting"""
        if filename is None:
            filename = f'polycab_{self.cable_type_slug.replace("-", "_")}_complete_data.xlsx'
        
        print(f"\n💾 Saving comprehensive data to Excel: {filename}")
        
        try:
            df = pd.DataFrame(products_data)
            
            # Create Excel writer with formatting
            with pd.ExcelWriter(filename, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name='Product Data', index=False)
                
                # Get the workbook and worksheet
                workbook = writer.book
                worksheet = writer.sheets['Product Data']
                
                # Adjust column widths
                for column in worksheet.columns:
                    max_length = 0
                    column = [cell for cell in column]
                    for cell in column:
                        try:
                            if len(str(cell.value)) > max_length:
                                max_length = len(str(cell.value))
                        except:
                            pass
                    adjusted_width = min(max_length + 2, 50)
                    worksheet.column_dimensions[column[0].column_letter].width = adjusted_width
            
            print(f"✅ Excel file saved: {filename}")
            print(f"📊 Total products: {len(products_data)}")
            
            # Print summary statistics
            downloaded_images = sum(1 for p in products_data if p['Image_Download_Status'] == 'Downloaded')
            downloaded_brochures = sum(1 for p in products_data if p['Brochure_Download_Status'] == 'Downloaded')
            
            print(f"🖼️  Images downloaded: {downloaded_images}/{len(products_data)}")
            print(f"📄 Brochures downloaded: {downloaded_brochures}/{len(products_data)}")
            
        except Exception as e:
            print(f"❌ Error saving Excel: {e}")
    
    def run(self):
        """Main execution method"""
        print(f"🚀 Polycab {self.cable_display_name} Comprehensive Extractor")
        print("=" * 70)
        print(f"📁 Working directory: {self.base_dir}")
        print(f"🖼️  Images directory: {self.images_dir}")
        print(f"📄 Brochures directory: {self.brochures_dir}")
        
        try:
            # 1. Discover product URLs
            product_urls = self.discover_product_urls()
            print(f"\n🔍 Found {len(product_urls)} product URLs")
            
            if not product_urls:
                print("❌ No product URLs found!")
                return
            
            # 2. Extract comprehensive product data
            all_products_data = []
            
            for i, url in enumerate(product_urls, 1):
                print(f"\n[{i}/{len(product_urls)}] Processing...")
                product_data = self.extract_product_details(url)
                all_products_data.append(product_data)
                
                # Be respectful to the server
                time.sleep(3)
                
                # Save intermediate results every 10 products
                if i % 10 == 0:
                    temp_filename = f'polycab_{self.cable_type_slug.replace("-", "_")}_partial_{i}.json'
                    temp_path = os.path.join(self.base_dir, temp_filename)
                    with open(temp_path, 'w', encoding='utf-8') as f:
                        json.dump(all_products_data, f, indent=2, ensure_ascii=False)
                    print(f"💾 Intermediate save: {temp_filename}")
            
            # 3. Save final comprehensive results
            if all_products_data:
                # Save to Excel (primary format)
                excel_filename = os.path.join(self.base_dir, f'polycab_{self.cable_type_slug.replace("-", "_")}_complete.xlsx')
                self.save_to_excel(all_products_data, excel_filename)
                
                # Save JSON backup
                json_filename = os.path.join(self.base_dir, f'polycab_{self.cable_type_slug.replace("-", "_")}_complete.json')
                with open(json_filename, 'w', encoding='utf-8') as f:
                    json.dump(all_products_data, f, indent=2, ensure_ascii=False)
                
                print(f"\n🎉 Comprehensive Extraction Complete!")
                print(f"✅ Successfully processed: {len(all_products_data)} products")
                print(f"📊 Files saved in: {self.base_dir}")
                
            else:
                print("❌ No product data extracted!")
                
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
            import traceback
            traceback.print_exc()

def main():
    """Main function with all available cable types"""
    
    # Complete list of available cable types
    available_cable_types = {
        # Main cable types
        '1': ('lv-power-cable', 'LV Power Cable'),
        '2': ('mv-power-cable', 'MV Power Cable'),
        '3': ('ehv-power-cable', 'EHV Power Cable'),
        '4': ('instrumentation-cable', 'Instrumentation Cable'),
        '5': ('communication-data-cable', 'Communication & Data Cable'),
        '6': ('renewable-energy', 'Renewable Energy Cable'),
        
        # Others subcategories
        '7': ('control-cable', 'Control Cable'),
        '8': ('fire-protection-cable', 'Fire Protection Cable'),
        '9': ('industrial-cable', 'Industrial Cable'),
        '10': ('rubber-cable', 'Rubber Cable'),
        '11': ('marine-offshoreonshore-cable', 'Marine & Offshore/Onshore Cable'),
        '12': ('high-temperature-cable', 'High Temperature Cable'),
        '13': ('defence', 'Defence Cable'),
        '14': ('domestic-appliance-and-lighting-cable', 'Domestic Appliance and Lighting Cable'),
        '15': ('building-wires', 'Building Wires'),
        '16': ('special-cable', 'Special Cable'),
        '17': ('aerial-bunched-cable', 'Aerial Bunched Cable'),
        
        # Custom option
        '18': ('custom', 'Custom (Enter your own)')
    }
    
    print("🔌 Polycab Comprehensive Cable Extractor")
    print("=" * 55)
    print("📋 Available cable types:\n")
    
    # Display main categories
    for key in ['1', '2', '3', '4', '5', '6']:
        slug, display_name = available_cable_types[key]
        print(f"  {key}. {display_name}")
    
    print("\n🔧 Other Cable Types:")
    for key in ['7', '8', '9', '10', '11', '12', '13', '14', '15', '16', '17']:
        slug, display_name = available_cable_types[key]
        print(f"  {key}. {display_name}")
    
    print(f"\n  18. Custom (Enter your own slug)")
    
    # Get user choice
    choice = input(f"\nSelect cable type (1-18): ").strip()
    
    if choice in available_cable_types:
        cable_slug, display_name = available_cable_types[choice]
        if cable_slug == 'custom':
            cable_slug = input("Enter cable type slug (e.g., 'mv-power-cable'): ").strip()
            display_name = input("Enter display name (e.g., 'MV Power Cable'): ").strip()
    else:
        print("Invalid choice. Using default MV Power Cable.")
        cable_slug, display_name = 'mv-power-cable', 'MV Power Cable'
    
    print(f"\n🎯 Selected: {display_name} ({cable_slug})")
    print("\n📋 This will extract:")
    print("  ✅ Product details (name, standards, features, etc.)")
    print("  🖼️  Product images")
    print("  📄 Product brochures/datasheets")
    print("  💾 Save everything to Excel with file paths")
    
    # Confirmation
    confirm = input("\nProceed with comprehensive extraction? (y/N): ").strip().lower()
    if confirm not in ['y', 'yes']:
        print("❌ Extraction cancelled.")
        return
    
    # Run the comprehensive extractor
    extractor = PolycabComprehensiveExtractor(cable_slug, display_name)
    extractor.run()

if __name__ == "__main__":
    main()
