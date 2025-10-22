import requests
import os
from urllib.parse import urlparse

# Product image URLs with clean cable names
product_images = {
    "Instrumentation_300_MC_ST.png": "https://cms.polycab.com/media/ba3hycp2/bsit00035_img_01.png?format=webp",
    "Instrumentation_500_MC_ST.png": "https://cms.polycab.com/media/rhwex2kn/bsit00036_img_01.png?format=webp",
    "Instrumentation_300_ST_PiMF.png": "https://cms.polycab.com/media/jnnjvkzz/bsit00037_img_01.png?format=webp",
    "Instrumentation_500_P_ST.png": "https://cms.polycab.com/media/q44pfc4s/bsit00038_img_01.png?format=webp",
    "Instrumentation_500_ST_PiMF.png": "https://cms.polycab.com/media/5sulbxex/bsit00039_img_01.png?format=webp",  # NEW
    "Instrumentation_300_ST_TiMF.png": "https://cms.polycab.com/media/duaag5n1/bsit00041_img_01.png?format=webp",  # NEW
    "Instrumentation_300_T_ST.png": "https://cms.polycab.com/media/1q0hmakh/bsit00042_img_01.png?format=webp",
    "Instrumentation_500_ST_TiMF.png": "https://cms.polycab.com/media/uz0kwlej/bsit00043_img_01.png?format=webp",
    "Instrumentation_500_T_ST.png": "https://cms.polycab.com/media/vw1n51oh/bsit00044_img_01.png?format=webp",
    "Instrumentation_300_P_ST.png": "https://cms.polycab.com/media/s1vficn0/bsit00106_img_01.png?format=webp",
    "BMS_300_MC_C4.png": "https://cms.polycab.com/media/udkn0atc/bsbm00049_img_01.png?format=webp",
    "BMS_300_MC_A7.png": "https://cms.polycab.com/media/l2upb3p1/bsbm00050_img_01.png?format=webp",
    "BMS_500_MC_C4.png": "https://cms.polycab.com/media/pyekpdzq/bsbm00051_img_01.png?format=webp",
    "BMS_500_MC_A7.png": "https://cms.polycab.com/media/2otewuqz/bsbm00052_img_01.png?format=webp"
}

def download_images():
    # Create downloads directory
    if not os.path.exists("polycab_images"):
        os.makedirs("polycab_images")
    
    print("🖼️  Starting Polycab Product Images Download...\n")
    print(f"📊 Total images to download: {len(product_images)}\n")
    
    for filename, url in product_images.items():
        try:
            print(f"🖼️  Downloading {filename}...")
            
            # Set headers to mimic browser request
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            response = requests.get(url, stream=True, headers=headers)
            response.raise_for_status()
            
            filepath = os.path.join("polycab_images", filename)
            with open(filepath, 'wb') as file:
                for chunk in response.iter_content(chunk_size=8192):
                    file.write(chunk)
            
            # Get file size
            file_size = os.path.getsize(filepath)
            size_kb = file_size / 1024
            
            print(f"✅ {filename} ({size_kb:.1f} KB)")
            
        except requests.exceptions.RequestException as e:
            print(f"❌ Failed to download {filename}: {e}")
        except Exception as e:
            print(f"❌ Error with {filename}: {e}")

if __name__ == "__main__":
    download_images()
    print(f"\n🎉 Image download completed! Check the 'polycab_images' folder.")
    print("🖼️  Files saved as PNG format with clean cable names.")
    print("📱 Images are optimized WebP format from Polycab's CDN.")
