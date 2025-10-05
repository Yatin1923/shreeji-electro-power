import requests
import os
import re
import time
from urllib.parse import urlparse

def clean_filename(filename):
    """Clean filename for safe saving"""
    # Remove special characters and replace spaces with underscores
    cleaned = re.sub(r'[<>:"/\\|?*]', '', filename)
    cleaned = re.sub(r'\s+', '_', cleaned)
    return cleaned.strip()

# EHV Cable product page URLs for dynamic extraction
ehv_product_urls = {
    "Polycab_EHV_Cu_Al_COR_110kV": "https://polycab.com/polycab-ehv-cu-al-cor-110kv/pt-13207/p-55353",
    "Polycab_EHV_Cu_CS+PAL_110kV": "https://polycab.com/polycab-ehv-cu-cspluspal-110kv/pt-13207/p-55337",
    "Polycab_EHV_AL_CS+PAL_220kV": "https://polycab.com/polycab-ehv-al-cspluspal-220kv/pt-13207/p-55371",
    "Polycab_EHV_AL_PB_110kV": "https://polycab.com/polycab-ehv-al-pb-110kv/pt-13207/p-55391",
    "Polycab_EHV_AL_Al_COR_110kV": "https://polycab.com/polycab-ehv-al-al-cor-110kv/pt-13207/p-55383",
    "Polycab_EHV_Cu_CS+PB_110kV": "https://polycab.com/polycab-ehv-cu-cspluspb-110kv/pt-13207/p-55345",
    "Polycab_EHV_Cu_CS+PAL_66kV": "https://polycab.com/polycab-ehv-cu-cspluspal-66kv/pt-13207/p-55335",
    "Polycab_EHV_AL_CS+PB_110kV": "https://polycab.com/polycab-ehv-al-cspluspb-110kv/pt-13207/p-55375",
    "Polycab_EHV_Cu_PB_220kV": "https://polycab.com/polycab-ehv-cu-pb-220kv/pt-13207/p-55365",
    "Polycab_EHV_AL_PB_132kV": "https://polycab.com/polycab-ehv-al-pb-132kv/pt-13207/p-55393",
    "Polycab_EHV_Cu_Al_COR_132kV": "https://polycab.com/polycab-ehv-cu-al-cor-132kv/pt-13207/p-55355",
    "Polycab_EHV_Cu_CS+PB_66kV": "https://polycab.com/polycab-ehv-cu-cspluspb-66kv/pt-13207/p-55343",
    "Polycab_EHV_Cu_CS+PAL_132kV": "https://polycab.com/polycab-ehv-cu-cspluspal-132kv/pt-13207/p-55339",
    "Polycab_EHV_AL_CS+PAL_132kV": "https://polycab.com/polycab-ehv-al-cspluspal-132kv/pt-13207/p-55369",
    "Polycab_EHV_AL_CS+PAL_110kV": "https://polycab.com/polycab-ehv-al-cspluspal-110kv/pt-13207/p-55367",
    "Polycab_EHV_AL_CS+PB_132kV": "https://polycab.com/polycab-ehv-al-cspluspb-132kv/pt-13207/p-55377",
    "Polycab_EHV_Cu_Al_COR_66kV": "https://polycab.com/polycab-ehv-cu-al-cor-66kv/pt-13207/p-55351",
    "Polycab_EHV_AL_CS+PB_66kV": "https://polycab.com/polycab-ehv-al-cspluspb-66kv/pt-13207/p-55373",
    "Polycab_EHV_AL_Al_COR_66kV": "https://polycab.com/polycab-ehv-al-al-cor-66kv/pt-13207/p-55381",
    "Polycab_EHV_Cu_PB_66kV": "https://polycab.com/polycab-ehv-cu-pb-66kv/pt-13207/p-55359",
    "Polycab_EHV_AL_CS+PB_220kV": "https://polycab.com/polycab-ehv-al-cspluspb-220kv/pt-13207/p-55379",
    "Polycab_EHV_AL_Al_COR_132kV": "https://polycab.com/polycab-ehv-al-al-cor-132kv/pt-13207/p-55385",
    "Polycab_EHV_Cu_Al_COR_220kV": "https://polycab.com/polycab-ehv-cu-al-cor-220kv/pt-13207/p-55357",
    "Polycab_EHV_Cu_CS+PB_132kV": "https://polycab.com/polycab-ehv-cu-cspluspb-132kv/pt-13207/p-55347",
    "Polycab_EHV_Cu_CS+PB_220kV": "https://polycab.com/polycab-ehv-cu-cspluspb-220kv/pt-13207/p-55349",
    "Polycab_EHV_Cu_CS+PAL_220kV": "https://polycab.com/polycab-ehv-cu-cspluspal-220kv/pt-13207/p-55341",
    "Polycab_EHV_Cu_PB_132kV": "https://polycab.com/polycab-ehv-cu-pb-132kv/pt-13207/p-55363",
    "Polycab_EHV_AL_PB_66kV": "https://polycab.com/polycab-ehv-al-pb-66kv/pt-13207/p-55389",
    "Polycab_EHV_Cu_PB_110kV": "https://polycab.com/polycab-ehv-cu-pb-110kv/pt-13207/p-55361",
    "Polycab_EHV_AL_PB_220kV": "https://polycab.com/polycab-ehv-al-pb-220kv/pt-13207/p-55395"
}

# Corrected/Confirmed EHV Cable Data Sheet URLs (extracted from actual product pages)
confirmed_ehv_datasheets = {
    "Polycab_EHV_Cu_Al_COR_110kV_Image.pdf": "https://cms.polycab.com/media/mbol5dj1/iceh00329_img_01.pdf",
    "Polycab_EHV_Cu_Al_COR_110kV_DataSheet.pdf": "https://cms.polycab.com/media/b3knrekt/iceh00329_ds_01.pdf",
    "Polycab_EHV_Cu_CS+PAL_110kV_DataSheet.pdf": "https://cms.polycab.com/media/sbef4gtl/iceh00321_ds_01.pdf",
    "Polycab_EHV_Cu_CS+PAL_66kV_DataSheet.pdf": "https://cms.polycab.com/media/451ioeuf/iceh00320_ds_01.pdf",  # Corrected
    "Polycab_EHV_Cu_CS+PB_66kV_DataSheet.pdf": "https://cms.polycab.com/media/efabbbge/iceh00324_ds_01.pdf",  # Corrected
    "Polycab_EHV_Cu_CS+PAL_132kV_DataSheet.pdf": "https://cms.polycab.com/media/01vogfaz/iceh00322_ds_01.pdf",  # Corrected
    "Polycab_EHV_AL_PB_220kV_Image.pdf": "https://cms.polycab.com/media/gtofdlfa/iceh00350_img_01.pdf",
    "Polycab_EHV_AL_PB_220kV_DataSheet.pdf": "https://cms.polycab.com/media/4toohig2/iceh00350_ds_01.pdf"
}

def extract_pdf_links_from_page(url, product_name):
    """Extract PDF download links from a product page"""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'DNT': '1',
        'Connection': 'keep-alive',
    }
    
    try:
        print(f"🔍 Checking {product_name}...")
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        
        # Extract PDF links - looking for CMS PDF URLs
        pdf_links = []
        pdf_pattern = r'href="([^"]*cms\.polycab\.com[^"]*\.pdf[^"]*)"'
        matches = re.findall(pdf_pattern, response.text)
        
        for pdf_url in matches:
            if pdf_url not in pdf_links:
                pdf_links.append(pdf_url)
        
        if pdf_links:
            print(f"  ✅ Found {len(pdf_links)} PDF(s)")
        else:
            print(f"  ❌ No PDFs found")
        
        return pdf_links
    
    except Exception as e:
        print(f"  ❌ Error extracting PDFs from {url}: {e}")
        return []

def download_confirmed_datasheets():
    """Download confirmed working EHV cable datasheets"""
    # Create downloads directory
    if not os.path.exists("polycab_ehv_datasheets_confirmed"):
        os.makedirs("polycab_ehv_datasheets_confirmed")
    
    print("📄 Starting Polycab EHV Power Cable Data Sheets Download (Confirmed URLs)...\n")
    print(f"📊 Total confirmed documents to download: {len(confirmed_ehv_datasheets)}\n")
    
    success_count = 0
    failed_count = 0
    
    for filename, url in confirmed_ehv_datasheets.items():
        try:
            print(f"📋 Downloading {filename}...")
            
            # Set headers to mimic browser request
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept': 'application/pdf,application/octet-stream,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.9',
                'Accept-Encoding': 'gzip, deflate, br',
                'DNT': '1',
                'Connection': 'keep-alive',
                'Referer': 'https://polycab.com/',
                'Sec-Fetch-Dest': 'document',
                'Sec-Fetch-Mode': 'no-cors',
                'Sec-Fetch-Site': 'same-site'
            }
            
            response = requests.get(url, stream=True, headers=headers, timeout=30)
            response.raise_for_status()
            
            filepath = os.path.join("polycab_ehv_datasheets_confirmed", filename)
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
    print(f"✅ Successful: {success_count}/{len(confirmed_ehv_datasheets)}")
    print(f"❌ Failed: {failed_count}/{len(confirmed_ehv_datasheets)}")
    print(f"📁 Documents saved in: 'polycab_ehv_datasheets_confirmed' folder")

def dynamic_download_all():
    """Dynamically download all available EHV datasheets"""
    # Create downloads directory
    if not os.path.exists("polycab_ehv_datasheets_dynamic"):
        os.makedirs("polycab_ehv_datasheets_dynamic")
    
    print("🔄 Dynamic EHV Power Cable Data Sheets Download...\n")
    print(f"📊 Total products to check: {len(ehv_product_urls)}\n")
    
    all_pdfs = {}
    
    print("🔍 Extracting PDF links from product pages...\n")
    for product_name, product_url in ehv_product_urls.items():
        pdf_links = extract_pdf_links_from_page(product_url, product_name)
        
        for i, pdf_url in enumerate(pdf_links):
            if "_ds_" in pdf_url:
                filename = f"{product_name}_DataSheet.pdf"
            elif "_img_" in pdf_url:
                filename = f"{product_name}_Image.pdf"
            else:
                filename = f"{product_name}_Document_{i+1}.pdf"
            
            all_pdfs[filename] = pdf_url
        
        time.sleep(1)  # Be respectful to the server
    
    if not all_pdfs:
        print("❌ No PDFs found")
        return
    
    print(f"\n📄 Found {len(all_pdfs)} PDF documents total")
    print(f"🚀 Starting downloads...\n")
    
    # Download PDFs
    success_count = 0
    failed_count = 0
    
    for filename, url in all_pdfs.items():
        try:
            print(f"📋 Downloading {filename}...")
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept': 'application/pdf,*/*;q=0.8',
                'Referer': 'https://polycab.com/',
            }
            
            response = requests.get(url, stream=True, headers=headers, timeout=30)
            response.raise_for_status()
            
            filepath = os.path.join("polycab_ehv_datasheets_dynamic", filename)
            with open(filepath, 'wb') as file:
                for chunk in response.iter_content(chunk_size=8192):
                    file.write(chunk)
            
            file_size = os.path.getsize(filepath)
            size_kb = file_size / 1024
            
            print(f"✅ {filename} ({size_kb:.1f} KB)")
            success_count += 1
            
            time.sleep(0.5)
            
        except Exception as e:
            print(f"❌ Failed to download {filename}: {e}")
            failed_count += 1
    
    print(f"\n🎉 Dynamic Download Summary:")
    print(f"✅ Successful: {success_count}/{len(all_pdfs)}")
    print(f"❌ Failed: {failed_count}/{len(all_pdfs)}")
    print(f"📁 Documents saved in: 'polycab_ehv_datasheets_dynamic' folder")
    
    # Display breakdown
    datasheet_count = len([f for f in all_pdfs.keys() if "DataSheet" in f])
    image_count = len([f for f in all_pdfs.keys() if "Image" in f])
    other_count = len(all_pdfs) - datasheet_count - image_count
    
    print(f"\n📈 Document Type Breakdown:")
    print(f"   📋 Data Sheets: {datasheet_count}")
    print(f"   🖼️  Product Images: {image_count}")
    print(f"   📄 Other Documents: {other_count}")

if __name__ == "__main__":
    print("Choose download method:")
    print("1. Confirmed working URLs only (faster, guaranteed)")
    print("2. Dynamic discovery (comprehensive, all available PDFs)")
    
    choice = input("Enter choice (1 or 2, default=2): ").strip()
    
    if choice == "1":
        download_confirmed_datasheets()
    else:
        dynamic_download_all()
