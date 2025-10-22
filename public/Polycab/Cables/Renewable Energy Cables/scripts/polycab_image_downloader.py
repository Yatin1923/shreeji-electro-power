import requests
import os
from urllib.parse import urlparse

# Product image URLs with clean cable names
product_images = {
    "Polycab_Solar_H1Z2Z2-K_BSEN_50618.png": "https://cms.polycab.com/media/sfpp20ks/enre00417_img_01.png",
    "Polycab_Solar_H1Z2Z2-K_BSEN_50618-Twin_AT.png": "https://cms.polycab.com/media/5bhnx3fq/enre00420_img_01.png",
    "Polycab_Solar_AS_NZS_5000_PVC.png": "https://cms.polycab.com/media/rfmjugyc/anre00408_img_01.png",
    "Polycab_Solar_AS_NZS_5000_RFH-Twist.png": "https://cms.polycab.com/media/051paf3r/anre00412_img_01.png",
    "Polycab_Solar_H1Z2Z2-K_BSEN_50618-Twin.png": "https://cms.polycab.com/media/foldabpb/enre00419_img_01.png",
    "Polycab_Solar_AS_NZS_5000_PVC-AT.png": "https://cms.polycab.com/media/k3odnrkj/anre00405_img_01.png",
    "Polycab_Solar_H1Z2Z2-K_BSEN_50618-AT.png": "https://cms.polycab.com/media/tz4kutn3/enre00418_img_01.png",
    "Polycab_Solar_AS_NZS_5000_RFH-AT.png": "https://cms.polycab.com/media/bonjaywo/anre00410_img_01.png",
    "Polycab_AL_Solar_UL_4703_2000V_AC.png": "https://cms.polycab.com/media/gyfpssoh/ulpc00077_img_01.png",
    "Polycab_Solar_AS_NZS_5000_XLPO.png": "https://cms.polycab.com/media/tqzlf4qg/anre00413_img_01.png",
    "Polycab_Solar_AS_NZS_5000_RFH-Twist_AT.png": "https://cms.polycab.com/media/kxkhnwx5/anre00411_img_01.png",
    "Polycab_Cu_Solar_UL_4703_2000V_AC.png": "https://cms.polycab.com/media/dalnhbck/ulpc00076_img_01.png",
    "Polycab_Solar_AS_NZS_5000_XLPO-AT.png": "https://cms.polycab.com/media/zujaow2g/anre00414_img_01.png",
    "Polycab_Solar_AS_NZS_5000_XLPO-Twist.png": "https://cms.polycab.com/media/bhld0tae/anre00415_img_01.png",
    "Polycab_Solar_AS_NZS_5000_PVC-Twist.png": "https://cms.polycab.com/media/nkvpf4zh/anre00407_img_01.png",
    "Polycab_Solar_AS_NZS_5000_XLPO-Twist_AT.png": "https://cms.polycab.com/media/yrbjccu5/anre00416_img_01.png",
    "Polycab_Solar_AS_NZS_5000_PVC-Twist_AT.png": "https://cms.polycab.com/media/ps3ct50b/anre00406_img_01.png",
    "Polycab_Solar_AS_NZS_5000_RFH.png": "https://cms.polycab.com/media/25ta14zb/anre00409_img_01.png"
}

def download_images():
    # Create downloads directory
    if not os.path.exists("polycab_renewable_images"):
        os.makedirs("polycab_renewable_images")
    
    print("🔋 Starting Polycab Renewable Energy Product Images Download...\n")
    print(f"📊 Total images to download: {len(product_images)}\n")
    
    success_count = 0
    failed_count = 0
    
    for filename, url in product_images.items():
        try:
            print(f"🖼️  Downloading {filename}...")
            
            # Set headers to mimic browser request
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            response = requests.get(url, stream=True, headers=headers)
            response.raise_for_status()
            
            filepath = os.path.join("polycab_renewable_images", filename)
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
    print(f"📁 Images saved in: 'polycab_renewable_images' folder")
    print("🔋 All Polycab renewable energy cable images downloaded!")
    print("🖼️  Files saved as PNG format with clean cable names.")

if __name__ == "__main__":
    download_images()
