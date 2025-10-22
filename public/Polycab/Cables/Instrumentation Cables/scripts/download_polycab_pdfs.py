import requests
import os

# PDF URLs with clean cable names (no product codes)
pdfs = {
    "Instrumentation_300_MC_ST.pdf": "https://cms.polycab.com/media/f5pjur3u/bsit00035_ds_01.pdf",
    "Instrumentation_500_MC_ST.pdf": "https://cms.polycab.com/media/440djjhp/bsit00036_ds_01.pdf",
    "Instrumentation_500_P_ST.pdf": "https://cms.polycab.com/media/oknbjagv/bsit00038_ds_01.pdf",
    "Instrumentation_300_T_ST.pdf": "https://cms.polycab.com/media/mfml3lc2/bsit00042_ds_01.pdf",
    "Instrumentation_500_ST_TiMF.pdf": "https://cms.polycab.com/media/2q1dz1ec/bsit00043_ds_01.pdf",
    "Instrumentation_300_P_ST.pdf": "https://cms.polycab.com/media/b3nlpn3m/bsit00106_ds_01.pdf",
    "Instrumentation_300_ST_PiMF.pdf": "https://cms.polycab.com/media/0iofiwgp/bsit00037_ds_01.pdf",
    "BMS_300_MC_C4.pdf": "https://cms.polycab.com/media/14ujggl5/bsbm00049_ds_01.pdf",
    "BMS_300_MC_A7.pdf": "https://cms.polycab.com/media/n43huen3/bsbm00050_ds_01.pdf",
    "BMS_500_MC_A7.pdf": "https://cms.polycab.com/media/yude4jt3/bsbm00052_ds_01.pdf"
}

def download_pdfs():
    # Create downloads directory
    if not os.path.exists("polycab_cables"):
        os.makedirs("polycab_cables")
    
    print("🚀 Starting Polycab Product Brochures Download...\n")
    
    for filename, url in pdfs.items():
        try:
            print(f"📄 Downloading {filename}...")
            response = requests.get(url, stream=True)
            response.raise_for_status()
            
            filepath = os.path.join("polycab_cables", filename)
            with open(filepath, 'wb') as file:
                for chunk in response.iter_content(chunk_size=8192):
                    file.write(chunk)
            
            # Get file size
            file_size = os.path.getsize(filepath)
            size_mb = file_size / (1024 * 1024)
            
            print(f"✅ {filename} ({size_mb:.1f} MB)")
            
        except requests.exceptions.RequestException as e:
            print(f"❌ Failed to download {filename}: {e}")
        except Exception as e:
            print(f"❌ Error with {filename}: {e}")

if __name__ == "__main__":
    download_pdfs()
    print(f"\n🎉 Download completed! Check the 'polycab_cables' folder.")
    print("📁 Files saved with clean cable names only.")
