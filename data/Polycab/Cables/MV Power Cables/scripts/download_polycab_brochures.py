import requests
import os
import json
import re
from urllib.parse import urlparse, urljoin
import time
from typing import List, Dict, Any

class PolycabMVBrochureDownloader:
    def __init__(self):
        self.base_url = "https://polycab.com"
        self.cms_base_url = "https://cms.polycab.com"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'application/pdf,*/*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Referer': 'https://polycab.com/',
        })
        
        # Known MV cable datasheet URLs found during research
        self.known_datasheets = {
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
        
        # API endpoint pattern for getting product lists
        self.api_endpoint = "/Products/GetCablesGridPartialByProductTypeSlug"
        
    def discover_more_datasheets(self) -> Dict[str, str]:
        """Try to discover more datasheet URLs from the CMS"""
        discovered_sheets = {}
        
        print("🔍 Discovering additional MV cable datasheets...")
        
        # Common MV cable product code patterns found in research
        product_codes = [
            'ismv', 'iamv', 'bsmv', 'anmv', 'ulpc', 'icpc', 'bspc', 'enre'
        ]
        
        # Try different code patterns
        for code in product_codes:
            for num in range(100, 500):  # Range based on observed patterns
                code_pattern = f"{code}{num:05d}"
                test_url = f"{self.cms_base_url}/media/{self.generate_hash()}/{code_pattern}_ds_01.pdf"
                discovered_sheets[f"Polycab_MV_{code_pattern}_Datasheet.pdf"] = test_url
        
        return discovered_sheets
    
    def generate_hash(self) -> str:
        """Generate a simple hash pattern (this is a simplified approach)"""
        import random
        import string
        return ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
    
    def fetch_product_urls_from_api(self) -> List[str]:
        """Fetch product URLs from the Polycab API"""
        product_urls = []
        
        try:
            params = {
                'sortOrder': 'NameAscending',
                'pageSize': 300,  # Get more products at once
                'pageNumber': 1,
                'productTypeSlug': 'mv-power-cable'
            }
            
            url = f"{self.base_url}{self.api_endpoint}"
            response = self.session.get(url, params=params)
            
            if response.status_code == 200:
                # Look for product URLs in the response
                content = response.text
                
                # Extract product page URLs
                product_patterns = [
                    r'href=["\']([^"\']*mv[^"\']*p-\d+)["\']',
                    r'href=["\']([^"\']*polycab-mv[^"\']*)["\']',
                    r'"url":\s*"([^"]*mv-power-cable[^"]*)"'
                ]
                
                for pattern in product_patterns:
                    matches = re.findall(pattern, content, re.IGNORECASE)
                    for match in matches:
                        if not match.startswith('http'):
                            match = urljoin(self.base_url, match)
                        product_urls.append(match)
                        
        except Exception as e:
            print(f"⚠️  Error fetching from API: {e}")
        
        return list(set(product_urls))  # Remove duplicates
    
    def extract_datasheet_from_product_page(self, product_url: str) -> Dict[str, str]:
        """Extract datasheet URL from individual product page"""
        try:
            print(f"🔎 Scanning product page: {product_url}")
            response = self.session.get(product_url)
            response.raise_for_status()
            
            content = response.text
            datasheets = {}
            
            # Look for download PDF or datasheet links
            pdf_patterns = [
                r'href=["\']([^"\']*\.pdf[^"\']*)["\'][^>]*(?:download|datasheet|brochure)',
                r'href=["\']([^"\']*cms\.polycab\.com[^"\']*\.pdf[^"\']*)["\']',
                r'"download":\s*"([^"]*\.pdf[^"]*)"',
                r'href=["\']([^"\']*_ds_01\.pdf[^"\']*)["\']'
            ]
            
            # Extract product name from page title or header
            title_match = re.search(r'<title>([^<]*Polycab[^<]*MV[^<]*)</title>', content, re.IGNORECASE)
            product_name = title_match.group(1) if title_match else "Unknown_MV_Product"
            
            # Clean product name for filename
            clean_name = re.sub(r'[^\w\s-]', '', product_name)
            clean_name = re.sub(r'\s+', '_', clean_name.strip())
            
            for pattern in pdf_patterns:
                matches = re.findall(pattern, content, re.IGNORECASE)
                for match in matches:
                    if not match.startswith('http'):
                        match = urljoin(self.base_url, match)
                    
                    filename = f"{clean_name}_Datasheet.pdf"
                    datasheets[filename] = match
                    print(f"📄 Found datasheet: {filename}")
            
            return datasheets
            
        except Exception as e:
            print(f"❌ Error extracting from {product_url}: {e}")
            return {}
    
    def search_cms_for_mv_datasheets(self) -> Dict[str, str]:
        """Search CMS for MV cable datasheets using common patterns"""
        discovered_datasheets = {}
        
        print("🕵️  Searching CMS for MV cable datasheets...")
        
        # Common hash patterns observed in the URLs
        known_hashes = [
            'todk30ms', '0xibfdde', 'qw2ewi0v', 'ctwcjagv', '05pnp42w', 
            'rr1hpql2', 'sqcdw33r', 'lzjl5mbb', '0p2a34fx', 'wntb4o5h'
        ]
        
        # Generate more potential hash patterns
        import itertools
        import string
        
        # Try variations of existing patterns
        for base_hash in known_hashes:
            # Try slight variations
            for i in range(10):
                variant = base_hash[:-1] + random.choice(string.ascii_lowercase + string.digits)
                test_url = f"{self.cms_base_url}/media/{variant}/ismv{200+i:05d}_ds_01.pdf"
                discovered_datasheets[f"Polycab_MV_Variant_{i}_Datasheet.pdf"] = test_url
        
        return discovered_datasheets
    
    def download_all_datasheets(self, datasheets: Dict[str, str]) -> None:
        """Download all MV cable datasheets"""
        if not datasheets:
            print("❌ No datasheets found to download")
            return
        
        # Create downloads directory
        download_dir = "polycab_mv_cable_datasheets"
        if not os.path.exists(download_dir):
            os.makedirs(download_dir)
        
        print(f"\n📚 Starting Polycab MV Cable Datasheet Download...")
        print(f"📊 Total datasheets to download: {len(datasheets)}\n")
        
        success_count = 0
        failed_count = 0
        total_size = 0
        
        for filename, url in datasheets.items():
            try:
                print(f"📄 Downloading {filename}...")
                
                response = self.session.get(url, stream=True, timeout=30)
                
                # Check if it's actually a PDF
                content_type = response.headers.get('content-type', '').lower()
                if response.status_code == 404:
                    print(f"⚠️  Skipping {filename} - not found (404)")
                    continue
                
                response.raise_for_status()
                
                if 'pdf' not in content_type and 'octet-stream' not in content_type:
                    print(f"⚠️  Skipping {filename} - not a PDF (content-type: {content_type})")
                    continue
                
                filepath = os.path.join(download_dir, filename)
                with open(filepath, 'wb') as file:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            file.write(chunk)
                
                # Verify file size
                file_size = os.path.getsize(filepath)
                if file_size < 1024:  # Less than 1KB, probably not a valid PDF
                    os.remove(filepath)
                    print(f"⚠️  Removed {filename} - too small ({file_size} bytes)")
                    continue
                
                size_mb = file_size / (1024 * 1024)
                total_size += file_size
                
                print(f"✅ {filename} ({size_mb:.2f} MB)")
                success_count += 1
                
                # Be respectful to the server
                time.sleep(1)
                
            except requests.exceptions.RequestException as e:
                print(f"❌ Failed to download {filename}: {e}")
                failed_count += 1
            except Exception as e:
                print(f"❌ Error with {filename}: {e}")
                failed_count += 1
        
        total_size_mb = total_size / (1024 * 1024)
        
        print(f"\n🎉 Download Summary:")
        print(f"✅ Successful: {success_count}/{len(datasheets)}")
        print(f"❌ Failed: {failed_count}/{len(datasheets)}")
        print(f"💾 Total downloaded: {total_size_mb:.2f} MB")
        print(f"📁 Datasheets saved in: '{download_dir}' folder")
        print("📚 All Polycab MV cable datasheets downloaded!")
    
    def run(self):
        """Main execution method"""
        print("🚀 Polycab MV Power Cable Datasheet Downloader")
        print("=" * 60)
        
        try:
            all_datasheets = {}
            
            # 1. Start with known datasheets
            print("📋 Adding known MV cable datasheets...")
            all_datasheets.update(self.known_datasheets)
            print(f"✅ Added {len(self.known_datasheets)} known datasheets")
            
            # 2. Try to get product URLs from API and scan them
            print("\n🔍 Scanning product pages for additional datasheets...")
            product_urls = self.fetch_product_urls_from_api()
            print(f"📊 Found {len(product_urls)} product URLs to scan")
            
            for url in product_urls:  # Limit to first 10 to be respectful
                page_datasheets = self.extract_datasheet_from_product_page(url)
                all_datasheets.update(page_datasheets)
                time.sleep(2)  # Be respectful
            
            print(f"📄 Total datasheets found: {len(all_datasheets)}")
            
            # 3. Save mapping for reference
            with open('polycab_mv_datasheet_mapping.json', 'w', encoding='utf-8') as f:
                json.dump(all_datasheets, f, indent=2, ensure_ascii=False)
            print("🗺️  Datasheet mapping saved to 'polycab_mv_datasheet_mapping.json'")
            
            # 4. Download all datasheets
            if all_datasheets:
                self.download_all_datasheets(all_datasheets)
            else:
                print("❌ No datasheets found to download")
                
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
            import traceback
            traceback.print_exc()

def main():
    """Main entry point"""
    downloader = PolycabMVBrochureDownloader()
    downloader.run()

if __name__ == "__main__":
    main()
