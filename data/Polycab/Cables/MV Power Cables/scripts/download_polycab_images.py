import requests
import os
import json
import re
from urllib.parse import urlparse, urljoin
import time
from typing import List, Dict, Any

class PolycabImageDownloader:
    def __init__(self):
        self.base_url = "https://polycab.com"
        self.api_endpoint = "/Products/GetCablesGridPartialByProductTypeSlug"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Referer': 'https://polycab.com/',
            'Origin': 'https://polycab.com'
        })
        
    def clean_filename(self, product_name: str, image_url: str) -> str:
        """Create a clean filename from product name and image URL"""
        # Clean the product name
        clean_name = re.sub(r'[^\w\s-]', '', product_name)
        clean_name = re.sub(r'\s+', '_', clean_name.strip())
        clean_name = clean_name[:100]  # Limit length
        
        # Get file extension from URL
        parsed_url = urlparse(image_url)
        file_ext = os.path.splitext(parsed_url.path)[1] or '.png'
        
        return f"Polycab_MV_{clean_name}{file_ext}"
    
    def fetch_products_page(self, page_number: int = 1, page_size: int = 250) -> Dict[str, Any]:
        """Fetch a single page of products from the API"""
        params = {
            'sortOrder': 'NameAscending',
            'pageSize': page_size,
            'pageNumber': page_number,
            'productTypeSlug': 'mv-power-cable'
        }
        
        url = self.base_url + self.api_endpoint
        
        try:
            response = self.session.get(url, params=params)
            response.raise_for_status()
            
            # Try to parse as JSON, fallback to HTML parsing if needed
            try:
                return response.json()
            except json.JSONDecodeError:
                # If it's HTML, try to extract JSON from script tags or data attributes
                return self.parse_html_response(response.text)
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Error fetching page {page_number}: {e}")
            return {}
    
    def parse_html_response(self, html_content: str) -> Dict[str, Any]:
        """Parse HTML response to extract product data"""
        # This is a fallback method - we'll need to adapt based on actual response
        products = []
        
        # Look for image URLs in the HTML
        image_pattern = r'https://cms\.polycab\.com/media/[^"\']*\.(?:png|jpg|jpeg|gif|webp)'
        image_urls = re.findall(image_pattern, html_content, re.IGNORECASE)
        
        # Look for product names (this may need adjustment based on actual HTML structure)
        name_pattern = r'Polycab MV[^<>"]*(?:kV|AL|Cu|XLPE|EPR|PVC)'
        product_names = re.findall(name_pattern, html_content, re.IGNORECASE)
        
        # Combine names and images
        for i, name in enumerate(product_names):
            product = {
                'name': name.strip(),
                'image_url': image_urls[i] if i < len(image_urls) else None
            }
            products.append(product)
        
        return {
            'products': products,
            'total_count': len(products),
            'has_more': False  # We'll assume single page for HTML parsing
        }
    
    def fetch_all_products(self) -> List[Dict[str, Any]]:
        """Fetch all products from all pages"""
        all_products = []
        page = 1
        
        print("🔍 Fetching product data from Polycab API...")
        
        while True:
            print(f"📄 Fetching page {page}...")
            data = self.fetch_products_page(page)
            
            if not data or 'products' not in data:
                # Try alternative approach - look for products in different data structure
                if 'results' in data:
                    products = data['results']
                elif isinstance(data, list):
                    products = data
                else:
                    print(f"⚠️  No products found on page {page}")
                    break
            else:
                products = data['products']
            
            if not products:
                print(f"✅ No more products found. Stopping at page {page-1}")
                break
            
            all_products.extend(products)
            print(f"📦 Found {len(products)} products on page {page}")
            
            # Check if there are more pages
            has_more = data.get('has_more', False) or len(products) == 50
            if not has_more:
                break
                
            page += 1
            time.sleep(1)  # Be respectful to the server
        
        return all_products
    
    def extract_product_images(self, products: List[Dict[str, Any]]) -> Dict[str, str]:
        """Extract image URLs and create clean filenames"""
        product_images = {}
        
        for product in products:
            # Try different possible keys for product name and image URL
            name = (product.get('name') or 
                   product.get('title') or 
                   product.get('product_name') or 
                   product.get('displayName') or 
                   'Unknown_Product')
            
            # Try different possible keys for image URL
            image_url = (product.get('image_url') or 
                        product.get('imageUrl') or 
                        product.get('image') or 
                        product.get('thumbnail') or 
                        product.get('productImage'))
            
            if image_url:
                # Make sure the URL is absolute
                if not image_url.startswith('http'):
                    image_url = urljoin(self.base_url, image_url)
                
                filename = self.clean_filename(name, image_url)
                product_images[filename] = image_url
        
        return product_images
    
    def download_images(self, product_images: Dict[str, str]) -> None:
        """Download all product images"""
        if not product_images:
            print("❌ No product images found to download")
            return
        
        # Create downloads directory
        download_dir = "polycab_mv_power_cable_images"
        if not os.path.exists(download_dir):
            os.makedirs(download_dir)
        
        print(f"\n⚡ Starting Polycab MV Power Cable Images Download...")
        print(f"📊 Total images to download: {len(product_images)}\n")
        
        success_count = 0
        failed_count = 0
        
        for filename, url in product_images.items():
            try:
                print(f"🖼️  Downloading {filename}...")
                
                response = self.session.get(url, stream=True)
                response.raise_for_status()
                
                filepath = os.path.join(download_dir, filename)
                with open(filepath, 'wb') as file:
                    for chunk in response.iter_content(chunk_size=8192):
                        file.write(chunk)
                
                # Get file size
                file_size = os.path.getsize(filepath)
                size_kb = file_size / 1024
                
                print(f"✅ {filename} ({size_kb:.1f} KB)")
                success_count += 1
                
                # Small delay to be respectful
                time.sleep(0.5)
                
            except requests.exceptions.RequestException as e:
                print(f"❌ Failed to download {filename}: {e}")
                failed_count += 1
            except Exception as e:
                print(f"❌ Error with {filename}: {e}")
                failed_count += 1
        
        print(f"\n🎉 Download Summary:")
        print(f"✅ Successful: {success_count}/{len(product_images)}")
        print(f"❌ Failed: {failed_count}/{len(product_images)}")
        print(f"📁 Images saved in: '{download_dir}' folder")
        print("⚡ All Polycab MV power cable images downloaded!")
    
    def run(self):
        """Main execution method"""
        try:
            # Fetch all products
            products = self.fetch_all_products()
            print(f"\n📦 Total products found: {len(products)}")
            
            if not products:
                print("❌ No products found. The API might have changed or requires authentication.")
                print("💡 You might need to:")
                print("   - Check if the API endpoint is still valid")
                print("   - Add authentication headers if required")
                print("   - Use browser developer tools to inspect the actual API calls")
                return
            
            # Extract image URLs
            product_images = self.extract_product_images(products)
            print(f"🖼️  Images found: {len(product_images)}")
            
            if product_images:
                # Save product data to JSON for reference
                with open('polycab_mv_products.json', 'w', encoding='utf-8') as f:
                    json.dump(products, f, indent=2, ensure_ascii=False)
                print("💾 Product data saved to 'polycab_mv_products.json'")
                
                # Download images
                self.download_images(product_images)
            else:
                print("❌ No product images found in the data")
                print("🔍 Saving raw product data for inspection...")
                with open('polycab_mv_products_raw.json', 'w', encoding='utf-8') as f:
                    json.dump(products, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            print(f"❌ Unexpected error: {e}")

def main():
    """Main entry point"""
    print("🚀 Polycab MV Power Cable Image Downloader")
    print("=" * 50)
    
    downloader = PolycabImageDownloader()
    downloader.run()

if __name__ == "__main__":
    main()
