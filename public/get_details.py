from bs4 import BeautifulSoup
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
                    
                    # Extract href URLs from HTML response
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
    
    def extract_image_url(self, html_content: str) -> str:
        """Extract main product image URL from HTML with improved patterns"""
        # More comprehensive image extraction patterns
        image_patterns = [
            # Primary product images
            r'<img[^>]*class=["\'][^"\']*product[^"\']*["\'][^>]*src=["\']([^"\']*cms\.polycab\.com[^"\']*\.(?:png|jpg|jpeg|webp|gif))["\']',
            r'<img[^>]*src=["\']([^"\']*cms\.polycab\.com[^"\']*\.(?:png|jpg|jpeg|webp|gif))["\'][^>]*class=["\'][^"\']*product[^"\']*["\']',
            
            # Main hero images
            r'<img[^>]*class=["\'][^"\']*hero[^"\']*["\'][^>]*src=["\']([^"\']*cms\.polycab\.com[^"\']*\.(?:png|jpg|jpeg|webp|gif))["\']',
            
            # Featured images
            r'<img[^>]*class=["\'][^"\']*featured[^"\']*["\'][^>]*src=["\']([^"\']*cms\.polycab\.com[^"\']*\.(?:png|jpg|jpeg|webp|gif))["\']',
            
            # Any cms.polycab.com image (broader pattern)
            r'<img[^>]*src=["\']([^"\']*cms\.polycab\.com[^"\']*\.(?:png|jpg|jpeg|webp|gif))["\']',
            
            # Background images in CSS
            r'background-image:\s*url\(["\']?([^"\']*cms\.polycab\.com[^"\']*\.(?:png|jpg|jpeg|webp|gif))["\']?\)',
            
            # Data attributes for lazy loading
            r'data-src=["\']([^"\']*cms\.polycab\.com[^"\']*\.(?:png|jpg|jpeg|webp|gif))["\']',
            r'data-image=["\']([^"\']*cms\.polycab\.com[^"\']*\.(?:png|jpg|jpeg|webp|gif))["\']',
            
            # JSON embedded in HTML
            r'"image":\s*"([^"]*cms\.polycab\.com[^"]*\.(?:png|jpg|jpeg|webp|gif))"',
            r'"imageUrl":\s*"([^"]*cms\.polycab\.com[^"]*\.(?:png|jpg|jpeg|webp|gif))"',
            r'"productImage":\s*"([^"]*cms\.polycab\.com[^"]*\.(?:png|jpg|jpeg|webp|gif))"',
            
            # Specific CMS patterns found on Polycab
            r'https://cms\.polycab\.com/media/[a-z0-9]{8}/[^"\']*\.(?:png|jpg|jpeg|webp|gif)',
            
            # Meta tags
            r'<meta[^>]*property=["\']og:image["\'][^>]*content=["\']([^"\']*cms\.polycab\.com[^"\']*\.(?:png|jpg|jpeg|webp|gif))["\']',
            
            # Picture elements
            r'<source[^>]*srcset=["\']([^"\']*cms\.polycab\.com[^"\']*\.(?:png|jpg|jpeg|webp|gif))["\']',
        ]
        
        for pattern in image_patterns:
            matches = re.findall(pattern, html_content, re.IGNORECASE)
            for match in matches:
                image_url = match.strip()
                if image_url:
                    # Make sure the URL is absolute
                    if not image_url.startswith('http'):
                        image_url = urljoin(self.base_url, image_url)
                    
                    # Verify it's a valid image URL
                    if self.is_valid_image_url(image_url):
                        print(f"🖼️  Found image URL: {image_url}")
                        return image_url
        
        print("⚠️  No image URL found in HTML content")
        return ""
    
    def is_valid_image_url(self, url: str) -> bool:
        """Quick check if URL looks like a valid image"""
        try:
            parsed = urlparse(url)
            if not parsed.netloc:
                return False
            
            # Check file extension
            path = parsed.path.lower()
            valid_extensions = ['.png', '.jpg', '.jpeg', '.webp', '.gif']
            
            return any(path.endswith(ext) for ext in valid_extensions)
        except:
            return False
    
    def download_image(self, product_name: str, image_url: str) -> str:
        """Download product image and return local path"""
        try:
            print(f"🔽 Attempting to download image for: {product_name}")
            print(f"🔗 Image URL: {image_url}")
            
            # Clean filename
            filename = self.clean_filename(product_name, '_image')
            
            # Get file extension from URL
            parsed_url = urlparse(image_url)
            file_ext = os.path.splitext(parsed_url.path)[1] or '.png'
            filename += file_ext
            
            filepath = os.path.join(self.images_dir, filename)
            
            # Download with specific headers for images
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Accept': 'image/webp,image/apng,image/*,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.9',
                'Referer': 'https://polycab.com/',
            }
            
            response = self.session.get(image_url, stream=True, timeout=30, headers=headers)
            response.raise_for_status()
            
            # Check content type
            content_type = response.headers.get('content-type', '').lower()
            print(f"📄 Content-Type: {content_type}")
            
            if not any(img_type in content_type for img_type in ['image/', 'octet-stream']):
                print(f"⚠️  Warning: Unexpected content type: {content_type}")
            
            with open(filepath, 'wb') as file:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        file.write(chunk)
            
            file_size = os.path.getsize(filepath)
            if file_size < 500:  # Less than 500 bytes, probably not valid
                os.remove(filepath)
                print(f"❌ Removed {filename} - too small ({file_size} bytes)")
                return ""
            
            print(f"✅ Downloaded image: {filename} ({file_size/1024:.1f} KB)")
            return filepath
            
        except Exception as e:
            print(f"❌ Failed to download image for {product_name}: {e}")
            return ""
    
    def extract_product_details(self, product_url: str) -> Dict[str, str]:
        """Extract detailed product information from a product page"""
        print(f"\n📄 Extracting: {product_url}")
        
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
            print(f"🔍 Looking for images for: {cable_name}")
            image_url = self.extract_image_url(html_content)
            if image_url:
                image_path = self.download_image(cable_name, image_url)
                if image_path:
                    product_data['Image_Path'] = image_path
                    product_data['Image_Download_Status'] = 'Downloaded'
                else:
                    product_data['Image_Download_Status'] = 'Failed'
            else:
                print("⚠️  No image URL found")
            
            # Extract and download brochure
            print(f"📚 Looking for brochures for: {cable_name}")
            brochure_url = self.extract_brochure_url(html_content, cable_name)
            if brochure_url:
                brochure_path = self.download_brochure(cable_name, brochure_url)
                if brochure_path:
                    product_data['Brochure_Path'] = brochure_path
                    product_data['Brochure_Download_Status'] = 'Downloaded'
                else:
                    product_data['Brochure_Download_Status'] = 'Failed'
            else:
                print("⚠️  No brochure URL found")
            
            print(f"✅ Extracted: {cable_name[:50]}...")
            
        except Exception as e:
            print(f"❌ Error extracting from {product_url}: {e}")
            product_data['Cable_Name'] = f"Error: {str(e)}"
        
        return product_data
    
    def extract_brochure_url(self, html_content: str, product_name: str) -> str:
        """Extract brochure/datasheet URL from HTML"""
        # First try to find brochure in the HTML content
        brochure_patterns = [
            r'href=["\']([^"\']*\.pdf[^"\']*)["\'][^>]*(?:download|datasheet|brochure)',
            r'href=["\']([^"\']*cms\.polycab\.com[^"\']*\.pdf[^"\']*)["\']',
            r'"download":\s*"([^"]*\.pdf[^"]*)"',
            r'href=["\']([^"\']*_ds_01\.pdf[^"\']*)["\']',
            r'data-href=["\']([^"\']*\.pdf[^"\']*)["\']',
            # More specific patterns for Polycab
            r'https://cms\.polycab\.com/media/[a-z0-9]{8}/[^"\']*\.pdf',
        ]
        
        for pattern in brochure_patterns:
            match = re.search(pattern, html_content, re.IGNORECASE)
            if match:
                brochure_url = match.group(1)
                if not brochure_url.startswith('http'):
                    brochure_url = urljoin(self.base_url, brochure_url)
                print(f"📄 Found brochure URL: {brochure_url}")
                return brochure_url
        
        # If not found in HTML, try known datasheets for this cable type
        if self.cable_type_slug in self.known_datasheets:
            datasheets = self.known_datasheets[self.cable_type_slug]
            # Try to match by product name
            for filename, url in datasheets.items():
                if any(word in product_name.upper() for word in filename.upper().split('_')[2:5]):  # Match key terms
                    print(f"📄 Using known datasheet: {filename}")
                    return url
        
        return ""
    
    def download_brochure(self, product_name: str, brochure_url: str) -> str:
        """Download product brochure/datasheet and return local path"""
        try:
            print(f"🔽 Attempting to download brochure for: {product_name}")
            print(f"🔗 Brochure URL: {brochure_url}")
            
            filename = self.clean_filename(product_name, '_datasheet.pdf')
            filepath = os.path.join(self.brochures_dir, filename)
            
            response = self.session.get(brochure_url, stream=True, timeout=30)
            
            if response.status_code == 404:
                print("❌ Brochure not found (404)")
                return ""
            
            response.raise_for_status()
            
            # Check if it's actually a PDF
            content_type = response.headers.get('content-type', '').lower()
            print(f"📄 Content-Type: {content_type}")
            
            if 'pdf' not in content_type and 'octet-stream' not in content_type:
                print(f"⚠️  Warning: Unexpected content type: {content_type}")
            
            with open(filepath, 'wb') as file:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        file.write(chunk)
            
            file_size = os.path.getsize(filepath)
            if file_size < 1024:  # Less than 1KB, probably not valid
                os.remove(filepath)
                print(f"❌ Removed {filename} - too small ({file_size} bytes)")
                return ""
            
            print(f"✅ Downloaded brochure: {filename} ({file_size/1024/1024:.2f} MB)")
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
    
    from bs4 import BeautifulSoup
    import re

    def extract_standards(self, html_content: str) -> str:
        """Extract standards from HTML using HTML parsing"""
        soup = BeautifulSoup(html_content, 'html.parser')
        standards = []
        
        # Method 1: Look for "Standards" section specifically
        feature_divs = soup.find_all('div', class_='feature')
        
        for feature in feature_divs:
            title = feature.find('h3', class_='feature__title')
            if title and 'standards' in title.get_text().lower():
                body = feature.find('p', class_='feature__body')
                if body:
                    standard_text = body.get_text().strip()
                    if standard_text:
                        # Split by common separators and clean
                        parts = re.split(r'[,;]', standard_text)
                        standards.extend([part.strip() for part in parts if part.strip()])
        
        print(f"🔍 Found standards section, extracted: {standards}")
        return ', '.join(standards[:5])  # Limit to 5 standards

    
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
        """Extract key features from HTML using HTML parsing"""
        soup = BeautifulSoup(html_content, 'html.parser')
        features = []
        
        # Method 1: Look for structured highlights section
        highlight_elements = soup.find_all('p', class_='prod__highlight')
        
        for element in highlight_elements:
            feature_text = element.get_text().strip()
            if feature_text:
                # Clean and standardize the text
                cleaned_feature = self._clean_feature_text(feature_text)
                if cleaned_feature:
                    features.append(cleaned_feature)
        
        # Remove duplicates while preserving order
        unique_features = list(dict.fromkeys(features))
        print(f"🔍 Extracted features: {unique_features}")
        
        return ', '.join(unique_features)

    def _clean_feature_text(self, text: str) -> str:
        """Clean and standardize feature text"""
        # Remove trailing periods and extra whitespace
        cleaned = text.strip().rstrip('.')
        
        # Capitalize first letter if needed
        if cleaned and cleaned[0].islower():
            cleaned = cleaned[0].upper() + cleaned[1:]
        
        return cleaned

    

    def extract_descriptions(self, html_content: str) -> tuple:
        """Extract short and full descriptions using HTML parsing"""
        soup = BeautifulSoup(html_content, 'html.parser')
        
        short_description = ''
        full_description = ''
        
        # Extract short description
        short_desc_elem = soup.find('p', class_='prod__short')
        if not short_desc_elem:
            # Fallback: look for other possible short description classes
            short_desc_elem = soup.find('p', class_=lambda x: x and 'short' in x)
        
        if short_desc_elem:
            short_description = short_desc_elem.get_text().strip()
            # Clean up extra whitespace
            short_description = ' '.join(short_description.split())
        
        # Extract full/long description  
        long_desc_elem = soup.find('p', class_='prod__longdesc')
        if not long_desc_elem:
            # Fallback: look for other possible long description classes
            long_desc_elem = soup.find('p', class_=lambda x: x and ('long' in x or 'desc' in x))
        
        if long_desc_elem:
            full_description = long_desc_elem.get_text().strip()
            # Clean up extra whitespace
            full_description = ' '.join(full_description.split())
        
        # If no full description found, use short description as fallback
        if not full_description and short_description:
            full_description = short_description
        
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
            
            # Show discovered URLs
            print("\n📋 Discovered URLs:")
            for i, url in enumerate(product_urls[:5], 1):  # Show first 5
                print(f"  {i}. {url}")
            
            if len(product_urls) > 5:
                print(f"  ... and {len(product_urls) - 5} more")
            
            # 2. Extract comprehensive product data
            all_products_data = []
            
            for i, url in enumerate(product_urls, 1):
                print(f"\n{'='*60}")
                print(f"[{i}/{len(product_urls)}] Processing Product {i}")
                print(f"{'='*60}")
                product_data = self.extract_product_details(url)
                all_products_data.append(product_data)
                
                # Be respectful to the server
                time.sleep(3)
                
                # Save intermediate results every 5 products
                if i % 5 == 0:
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
    
    # Get user choice - now supports multiple selections and ranges
    print("\n💡 Selection Options:")
    print("  • Single: 5")
    print("  • Multiple: 8,9,10")
    print("  • Range: 8-17")
    print("  • Mixed: 1,8-12,15")
    
    choice_input = input(f"\nSelect cable type(s) (1-18): ").strip()
    
    # Parse the input to get list of choices
    selected_choices = parse_choice_input(choice_input, available_cable_types.keys())
    
    if not selected_choices:
        print("Invalid choice. Using default MV Power Cable.")
        selected_choices = ['2']
    
    # Display selected cable types
    print(f"\n🎯 Selected Cable Types ({len(selected_choices)}):")
    selected_cables = []
    
    for choice in selected_choices:
        if choice in available_cable_types:
            cable_slug, display_name = available_cable_types[choice]
            if cable_slug == 'custom':
                cable_slug = input(f"Enter cable type slug for choice {choice}: ").strip()
                display_name = input(f"Enter display name for choice {choice}: ").strip()
            selected_cables.append((cable_slug, display_name))
            print(f"  ✅ {display_name} ({cable_slug})")
    
    print(f"\n📋 This will extract for {len(selected_cables)} cable type(s):")
    print("  ✅ Product details (name, standards, features, etc.)")
    print("  🖼️  Product images (with improved detection)")
    print("  📄 Product brochures/datasheets")
    print("  💾 Save everything to Excel with file paths")
    
    # Confirmation
    confirm = input(f"\nProceed with comprehensive extraction for all {len(selected_cables)} cable types? (y/N): ").strip().lower()
    if confirm not in ['y', 'yes']:
        print("❌ Extraction cancelled.")
        return
    
    # Run the comprehensive extractor for each selected cable type
    total_cables = len(selected_cables)
    for i, (cable_slug, display_name) in enumerate(selected_cables, 1):
        print(f"\n{'='*60}")
        print(f"🔄 Processing {i}/{total_cables}: {display_name}")
        print(f"{'='*60}")
        
        try:
            extractor = PolycabComprehensiveExtractor(cable_slug, display_name)
            extractor.run()
            print(f"✅ Completed: {display_name}")
        except Exception as e:
            print(f"❌ Error processing {display_name}: {str(e)}")
            continue
    
    print(f"\n🎉 Batch extraction completed for {total_cables} cable types!")

def parse_choice_input(choice_input, valid_keys):
    """Parse user input for multiple selections and ranges"""
    choices = []
    
    try:
        # Split by comma for multiple selections
        parts = [part.strip() for part in choice_input.split(',')]
        
        for part in parts:
            if '-' in part:
                # Handle range (e.g., "8-17")
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

def run_batch_8_to_17():
    """Quick function to run specifically cables 8-17"""
    available_cable_types = {
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
    }
    
    print("🔌 Polycab Batch Extractor (Cables 8-17)")
    print("=" * 55)
    print("📋 Will process the following cable types:\n")
    
    for key, (slug, display_name) in available_cable_types.items():
        print(f"  {key}. {display_name}")
    
    confirm = input(f"\nProceed with extraction for all {len(available_cable_types)} cable types? (y/N): ").strip().lower()
    if confirm not in ['y', 'yes']:
        print("❌ Extraction cancelled.")
        return
    
    # Run extraction for each cable type
    total_cables = len(available_cable_types)
    for i, (key, (cable_slug, display_name)) in enumerate(available_cable_types.items(), 1):
        print(f"\n{'='*60}")
        print(f"🔄 Processing {i}/{total_cables}: {display_name}")
        print(f"{'='*60}")
        
        try:
            extractor = PolycabComprehensiveExtractor(cable_slug, display_name)
            extractor.run()
            print(f"✅ Completed: {display_name}")
        except Exception as e:
            print(f"❌ Error processing {display_name}: {str(e)}")
            continue
    
    print(f"\n🎉 Batch extraction completed for all {total_cables} cable types!")

if __name__ == "__main__":
    # Option 1: Use the enhanced main function and input "8-17"
    main()
    
    # Option 2: Or use the dedicated function for 8-17
    # run_batch_8_to_17()
