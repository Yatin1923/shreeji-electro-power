import requests
import os
from bs4 import BeautifulSoup
import re
import time

# Failed products with their page URLs
failed_products = {
    "Polycab_Solar_AS_NZS_5000_XLPO-AT_DataSheet.pdf": "https://polycab.com/polycab-solar-as-nzs-5000-xlpo-at/c-4971/p-55523",
    "Polycab_Solar_AS_NZS_5000_XLPO-Twist_DataSheet.pdf": "https://polycab.com/polycab-solar-as-nzs-5000-xlpo-twist/s-16816/p-55525",
    "Polycab_Solar_AS_NZS_5000_XLPO-Twist_AT_DataSheet.pdf": "https://polycab.com/polycab-solar-as-nzs-5000-xlpo-twist-at/s-16816/p-55527",
    "Polycab_Solar_AS_NZS_5000_PVC-Twist_AT_DataSheet.pdf": "https://polycab.com/polycab-solar-as-nzs-5000-pvc-twist-at/s-16816/p-55507",
    "Polycab_Solar_AS_NZS_5000_RFH_DataSheet.pdf": "https://polycab.com/polycab-solar-as-nzs-5000-rfh/s-16816/p-55513"
}

def get_pdf_url_from_page(product_url):
    """Extract PDF URL from product page"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Cache-Control': 'max-age=0'
        }
        
        session = requests.Session()
        session.headers.update(headers)
        
        response = session.get(product_url, timeout=30)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Look for PDF links with various patterns
        pdf_patterns = [
            'a[href*=".pdf"]',
            'a[href*="datasheet"]',
            'a[href*="spec"]',
            'a[href*="ds_01"]',
            '[href*="polycorpstorage"]',
            '[href*="cms.polycab.com"][href*=".pdf"]'
        ]
        
        for pattern in pdf_patterns:
            elements = soup.select(pattern)
            for element in elements:
                href = element.get('href')
                if href and '.pdf' in href.lower():
                    # Make absolute URL if relative
                    if href.startswith('//'):
                        href = 'https:' + href
                    elif href.startswith('/'):
                        href = 'https://polycab.com' + href
                    elif not href.startswith('http'):
                        href = 'https://polycab.com/' + href
                    return href
        
        # Alternative: look for text containing "Download" or "PDF"
        download_links = soup.find_all('a', string=re.compile(r'download|pdf|datasheet|spec', re.IGNORECASE))
        for link in download_links:
            href = link.get('href')
            if href:
                if href.startswith('//'):
                    href = 'https:' + href
                elif href.startswith('/'):
                    href = 'https://polycab.com' + href
                return href
        
        return None
        
    except Exception as e:
        print(f"   ❌ Error extracting PDF URL: {str(e)[:60]}...")
        return None

def download_pdf_with_session(pdf_url, filename):
    """Download PDF using session with multiple retry strategies"""
    strategies = [
        # Strategy 1: Standard headers
        {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'application/pdf,application/octet-stream,*/*;q=0.9',
            'Referer': 'https://polycab.com/',
            'Connection': 'keep-alive'
        },
        # Strategy 2: Minimal headers
        {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        },
        # Strategy 3: Different user agent
        {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15'
        },
        # Strategy 4: Mobile user agent
        {
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_7_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.2 Mobile/15E148 Safari/604.1'
        }
    ]
    
    for i, headers in enumerate(strategies, 1):
        try:
            print(f"   🔄 Strategy {i}: Trying with different headers...")
            
            session = requests.Session()
            session.headers.update(headers)
            
            response = session.get(pdf_url, stream=True, timeout=30)
            response.raise_for_status()
            
            # Check content type
            content_type = response.headers.get('content-type', '').lower()
            print(f"      Content-Type: {content_type}")
            
            filepath = os.path.join("polycab_failed_brochures", filename)
            
            with open(filepath, 'wb') as file:
                for chunk in response.iter_content(chunk_size=8192):
                    file.write(chunk)
            
            # Basic PDF validation
            with open(filepath, 'rb') as f:
                header = f.read(4)
                if header == b'%PDF':
                    return True, os.path.getsize(filepath)
                else:
                    print(f"      ⚠️  Downloaded file is not a valid PDF")
                    os.remove(filepath)
                    continue
                    
        except requests.exceptions.HTTPError as e:
            print(f"      ❌ HTTP Error {e.response.status_code}: {e}")
        except Exception as e:
            print(f"      ❌ Error: {str(e)[:50]}...")
    
    return False, 0

def download_failed_brochures():
    # Create downloads directory
    if not os.path.exists("polycab_failed_brochures"):
        os.makedirs("polycab_failed_brochures")
    
    print("🔧 Retry Download for Failed Polycab Brochures...\n")
    print(f"📊 Failed brochures to retry: {len(failed_products)}\n")
    
    success_count = 0
    failed_count = 0
    total_size_kb = 0
    
    for filename, product_url in failed_products.items():
        print(f"📄 Retrying {filename}...")
        print(f"   🔗 Product page: {product_url}")
        
        # Extract PDF URL from product page
        pdf_url = get_pdf_url_from_page(product_url)
        
        if pdf_url:
            print(f"   ✅ Found PDF URL: {pdf_url}")
            
            # Try downloading with different strategies
            success, file_size = download_pdf_with_session(pdf_url, filename)
            
            if success:
                size_kb = file_size / 1024
                total_size_kb += size_kb
                print(f"✅ {filename} ({size_kb:.1f} KB)")
                success_count += 1
            else:
                print(f"❌ Failed to download {filename}")
                failed_count += 1
        else:
            print(f"   ❌ Could not find PDF URL on product page")
            failed_count += 1
        
        # Respectful delay
        time.sleep(3)
        print()
    
    # Convert total size
    if total_size_kb > 1024:
        total_size_mb = total_size_kb / 1024
        size_display = f"{total_size_mb:.1f} MB"
    else:
        size_display = f"{total_size_kb:.1f} KB"

    print(f"🎉 Retry Summary:")
    print(f"✅ Successful: {success_count}/{len(failed_products)}")
    print(f"❌ Still failed: {failed_count}/{len(failed_products)}")
    print(f"📁 Total size: {size_display}")
    print(f"📂 Brochures saved in: 'polycab_failed_brochures' folder")
    
    if failed_count > 0:
        print(f"\n💡 For remaining failures, try:")
        print(f"   • Check product pages manually")
        print(f"   • Contact Polycab support")
        print(f"   • PDFs might not be available for these products")

if __name__ == "__main__":
    download_failed_brochures()
