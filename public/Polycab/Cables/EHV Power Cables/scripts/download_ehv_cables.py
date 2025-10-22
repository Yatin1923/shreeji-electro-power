import requests
import os
import re
from urllib.parse import urlparse

def clean_filename(filename):
    """Clean filename for safe saving"""
    # Remove special characters and replace spaces with underscores
    cleaned = re.sub(r'[<>:"/\\|?*]', '', filename)
    cleaned = re.sub(r'\s+', '_', cleaned)
    return cleaned.strip()

def fetch_ehv_products():
    """Fetch EHV cable products from Polycab API"""
    url = "https://polycab.com/Products/GetCablesGridPartialByProductTypeSlug"
    params = {
        'sortOrder': 'NameAscending',
        'pageSize': 50,  # Increased to get all products
        'pageNumber': 1,
        'productTypeSlug': 'ehv-power-cable'
    }
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate, br',
        'DNT': '1',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
    }
    
    try:
        response = requests.get(url, params=params, headers=headers)
        response.raise_for_status()
        return response.text
    except Exception as e:
        print(f"❌ Error fetching products: {e}")
        return None

def extract_products_from_html(html_content):
    """Extract product names and image URLs from HTML"""
    products = {}
    
    # Pattern to match image URLs and product names
    img_pattern = r'src="([^"]*cms\.polycab\.com[^"]*\.png[^"]*)"[^>]*alt="[^"]*"[^>]*>\s*####\s*([^<\n]+)'
    matches = re.findall(img_pattern, html_content)
    
    for img_url, product_name in matches:
        # Clean the image URL (remove webp format parameter)
        clean_url = img_url.replace('?format=webp', '')
        
        # Clean product name
        clean_name = product_name.strip()
        
        # Create filename
        filename = clean_filename(clean_name) + ".png"
        
        products[filename] = clean_url
    
    return products

# EHV Power Product product images - extracted from the API
product_images = {
    "Polycab_EHV_Cu_Al_COR_110kV.png": "https://cms.polycab.com/media/251neydq/iceh00329_img_01.png",
    "Polycab_EHV_Cu_CS+PAL_110kV.png": "https://cms.polycab.com/media/ksgpdwwh/iceh00321_img_01.png",
    "Polycab_EHV_AL_CS+PAL_220kV.png": "https://cms.polycab.com/media/xfxlokhr/iceh00338_img_01.png",
    "Polycab_EHV_AL_PB_110kV.png": "https://cms.polycab.com/media/tt4cboph/iceh00348_img_01.png",
    "Polycab_EHV_AL_Al_COR_110kV.png": "https://cms.polycab.com/media/a1pg500y/iceh00344_img_01.png",
    "Polycab_EHV_Cu_CS+PB_110kV.png": "https://cms.polycab.com/media/hp3nruzr/iceh00325_img_01.png",
    "Polycab_EHV_Cu_CS+PAL_66kV.png": "https://cms.polycab.com/media/53mc5j1i/iceh00320_img_01.png",
    "Polycab_EHV_AL_CS+PB_110kV.png": "https://cms.polycab.com/media/dkipsxnn/iceh00340_img_01.png",
    "Polycab_EHV_Cu_PB_220kV.png": "https://cms.polycab.com/media/ojinc1o1/iceh00335_img_01.png",
    "Polycab_EHV_AL_PB_132kV.png": "https://cms.polycab.com/media/fqcdj12y/iceh00349_img_01.png",
    "Polycab_EHV_Cu_Al_COR_132kV.png": "https://cms.polycab.com/media/xsxer3vi/iceh00330_img_01.png",
    "Polycab_EHV_Cu_CS+PB_66kV.png": "https://cms.polycab.com/media/n1xl004n/iceh00324_img_01.png",
    "Polycab_EHV_Cu_CS+PAL_132kV.png": "https://cms.polycab.com/media/koadycfs/iceh00322_img_01.png",
    "Polycab_EHV_AL_CS+PAL_132kV.png": "https://cms.polycab.com/media/egmliu5t/iceh00337_img_01.png",
    "Polycab_EHV_AL_CS+PAL_110kV.png": "https://cms.polycab.com/media/fwsn0mrr/iceh00336_img_01.png",
    "Polycab_EHV_AL_CS+PB_132kV.png": "https://cms.polycab.com/media/ehebjoci/iceh00341_img_01.png",
    "Polycab_EHV_Cu_Al_COR_66kV.png": "https://cms.polycab.com/media/d3ebei3i/iceh00328_img_01.png",
    "Polycab_EHV_AL_CS+PB_66kV.png": "https://cms.polycab.com/media/twmbudio/iceh00339_img_01.png",
    "Polycab_EHV_AL_Al_COR_66kV.png": "https://cms.polycab.com/media/pjxdqt0k/iceh00343_img_01.png",
    "Polycab_EHV_Cu_PB_66kV.png": "https://cms.polycab.com/media/lcrlg5jv/iceh00332_img_01.png",
    "Polycab_EHV_AL_CS+PB_220kV.png": "https://cms.polycab.com/media/atpkq1ex/iceh00342_img_01.png",
    "Polycab_EHV_AL_Al_COR_132kV.png": "https://cms.polycab.com/media/5urd0ift/iceh00345_img_01.png",
    "Polycab_EHV_Cu_Al_COR_220kV.png": "https://cms.polycab.com/media/d0en3uof/iceh00331_img_01.png",
    "Polycab_EHV_Cu_CS+PB_132kV.png": "https://cms.polycab.com/media/lqra1zdy/iceh00326_img_01.png",
    "Polycab_EHV_Cu_CS+PB_220kV.png": "https://cms.polycab.com/media/lzwowqpf/iceh00327_img_01.png",
    "Polycab_EHV_Cu_CS+PAL_220kV.png": "https://cms.polycab.com/media/4s3lqj4i/iceh00323_img_01.png",
    "Polycab_EHV_Cu_PB_132kV.png": "https://cms.polycab.com/media/tdmnt4ui/iceh00334_img_01.png",
    "Polycab_EHV_AL_PB_66kV.png": "https://cms.polycab.com/media/cwbpdxxg/iceh00347_img_01.png",
    "Polycab_EHV_Cu_PB_110kV.png": "https://cms.polycab.com/media/kvvhsr04/iceh00333_img_01.png",
    "Polycab_EHV_AL_PB_220kV.png": "https://cms.polycab.com/media/xabffurp/iceh00350_img_01.png"
}

def download_images():
    """Download all EHV cable images"""
    # Create downloads directory
    if not os.path.exists("polycab_ehv_images"):
        os.makedirs("polycab_ehv_images")
    
    print("⚡ Starting Polycab EHV Power Product Images Download...\n")
    print(f"📊 Total images to download: {len(product_images)}\n")
    
    success_count = 0
    failed_count = 0
    
    for filename, url in product_images.items():
        try:
            print(f"🖼️  Downloading {filename}...")
            
            # Set headers to mimic browser request
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept': 'image/webp,image/apng,image/*,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.9',
                'Accept-Encoding': 'gzip, deflate, br',
                'DNT': '1',
                'Connection': 'keep-alive',
                'Sec-Fetch-Dest': 'image',
                'Sec-Fetch-Mode': 'no-cors',
                'Sec-Fetch-Site': 'cross-site'
            }
            
            response = requests.get(url, stream=True, headers=headers, timeout=30)
            response.raise_for_status()
            
            filepath = os.path.join("polycab_ehv_images", filename)
            with open(filepath, 'wb') as file:
                for chunk in response.iter_content(chunk_size=8192):
                    file.write(chunk)
            
            # Get file size
            file_size = os.path.getsize(filepath)
            size_kb = file_size / 1024
            
            print(f"✅ {filename} ({size_kb:.1f} KB)")
            success_count += 1
            
        except requests.exceptions.RequestException as e:
            print(f"❌ Failed to download {filename}: {e}")
            failed_count += 1
        except Exception as e:
            print(f"❌ Error with {filename}: {e}")
            failed_count += 1

    print(f"\n🎉 Download Summary:")
    print(f"✅ Successful: {success_count}/{len(product_images)}")
    print(f"❌ Failed: {failed_count}/{len(product_images)}")
    print(f"📁 Images saved in: 'polycab_ehv_images' folder")
    print("⚡ All Polycab EHV power cable images downloaded!")
    print("🖼️  Files saved as PNG format with clean cable names.")
    
    # Display voltage breakdown
    voltage_breakdown = {}
    for filename in product_images.keys():
        if "66kV" in filename:
            voltage_breakdown["66kV"] = voltage_breakdown.get("66kV", 0) + 1
        elif "110kV" in filename:
            voltage_breakdown["110kV"] = voltage_breakdown.get("110kV", 0) + 1
        elif "132kV" in filename:
            voltage_breakdown["132kV"] = voltage_breakdown.get("132kV", 0) + 1
        elif "220kV" in filename:
            voltage_breakdown["220kV"] = voltage_breakdown.get("220kV", 0) + 1
    
    print(f"\n📈 Voltage Level Breakdown:")
    for voltage, count in voltage_breakdown.items():
        print(f"   {voltage}: {count} cables")

def dynamic_download():
    """Alternative method: Fetch and download dynamically from API"""
    print("🔄 Fetching latest EHV products from API...")
    
    html_content = fetch_ehv_products()
    if not html_content:
        print("❌ Failed to fetch products from API")
        return
    
    dynamic_products = extract_products_from_html(html_content)
    
    if not dynamic_products:
        print("❌ No products found in API response")
        return
    
    print(f"✅ Found {len(dynamic_products)} products from API")
    
    # Use the dynamically fetched products
    global product_images
    product_images = dynamic_products
    
    download_images()

if __name__ == "__main__":
    # Choose download method
    print("Choose download method:")
    print("1. Static list (faster, pre-defined)")
    print("2. Dynamic from API (latest, might be slower)")
    
    choice = input("Enter choice (1 or 2, default=1): ").strip()
    
    if choice == "2":
        dynamic_download()
    else:
        download_images()
