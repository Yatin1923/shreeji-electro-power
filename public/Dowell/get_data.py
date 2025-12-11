import fitz  # PyMuPDF
import json
import os

# ====== CONFIG ======
PDF_PATH = "dowell.pdf"
IMAGE_DIR = "Dowell/images"
os.makedirs(IMAGE_DIR, exist_ok=True)

# ====== PRODUCT DEFINITIONS ======
products = [
    {
        "Name": "Tube Terminals – Medium Duty",
        "Product_Type": "Terminal",
        "Standards": "BS 4579, IEC 61238",
        "Key_Features": "Oxygen-free high conductivity copper; Electrolytic aluminium IS 5082; Tin plating available; Sizes 2.5–1000 sq.mm",
        "Short_Description": "Medium-duty tube terminals for copper and aluminium conductors.",
        "Full_Description": "Dowell medium-duty tube terminals are made using oxygen-free high conductivity copper and electrolytic aluminium IS-5082 grade. Available with tin plating and tested as per BS 4579/IEC 61238 for reliability."
    },
    {
        "Name": "In-Line Connectors",
        "Product_Type": "Connector",
        "Standards": "IS 191, IS 5082",
        "Key_Features": "EC grade copper; Electrolytic aluminium; Natural and electro-tinned finish",
        "Short_Description": "Durable inline connectors for copper and aluminium cables.",
        "Full_Description": "Dowell in-line connectors are manufactured from EC grade copper and electrolytic aluminium IS-5082. They support a wide conductor-size range and are available in both natural and electro-tinned finishes."
    },
    {
        "Name": "Copper Terminals",
        "Product_Type": "Terminal",
        "Standards": "IS 191",
        "Key_Features": "Ring, fork and pin types; Insulated/non-insulated; Electro-tinned finish",
        "Short_Description": "Copper terminals available in ring, fork and pin variants.",
        "Full_Description": "Dowell copper terminals are manufactured from IS-191 grade copper and are available in multiple configurations with insulated, non-insulated and pre-insulated options."
    },
    {
        "Name": "Bimetallic Lugs & Connectors",
        "Product_Type": "Lug/Connector",
        "Standards": "IEC 61238",
        "Key_Features": "Copper-aluminium friction welded; Suitable for AL–CU termination; Compact design",
        "Short_Description": "Bimetallic lugs suitable for terminating aluminium cables on copper bus bars.",
        "Full_Description": "Dowell friction-welded bimetallic lugs are designed for safe transition between aluminium cables and copper bus bars. Tested as per IEC-61238."
    },
    {
        "Name": "Sector Shape Lugs & Connectors",
        "Product_Type": "Lug/Connector",
        "Standards": "IS 191, IS 5082",
        "Key_Features": "Compact sector profile; Suitable for 2–4 core cables; No pinholes",
        "Short_Description": "Lugs designed for sector-shaped aluminium or copper conductors.",
        "Full_Description": "Dowell sector-shape lugs fit sector-type cables used in 2, 3, 3.5, and 4-core systems. Manufactured using IS-191 copper and IS-5082 aluminium."
    },
    {
        "Name": "Aluminium Ferrules",
        "Product_Type": "Ferrule",
        "Standards": "IS 5082",
        "Key_Features": "Suitable for XLPE conductors; Natural finish; Sizes 25–1000 sq.mm",
        "Short_Description": "Aluminium ferrules for XLPE conductor termination.",
        "Full_Description": "Dowell aluminium ferrules are manufactured from IS-5082 grade aluminium and designed for terminating aluminium XLPE conductors."
    },
    {
        "Name": "Aluminium Corrosion Inhibiting Compound",
        "Product_Type": "Compound",
        "Standards": "GTZ-8785",
        "Key_Features": "High moisture sealing; Non-corrosive; High temperature drop point",
        "Short_Description": "Inhibiting compound for aluminium conductor termination.",
        "Full_Description": "Dowell aluminium corrosion inhibiting compound offers excellent sealing properties, prevents corrosion and is suitable for ferrule and conductor preparation."
    },
    {
        "Name": "Single and Double Compression Glands",
        "Product_Type": "Gland",
        "Standards": "IP67, BS 6121, IEC 60079-0",
        "Key_Features": "Weatherproof & flameproof; Brass/Aluminium/SS options; For armoured & unarmoured cables",
        "Short_Description": "Compression glands for industrial cable terminations.",
        "Full_Description": "Dowell compression glands offer IP67 ingress protection and are available in brass, aluminium, stainless steel and polyamide variants for armoured and unarmoured cables."
    },
    {
        "Name": "Earth Tag",
        "Product_Type": "Accessory",
        "Standards": "N/A",
        "Key_Features": "Ensures earth continuity; Brass/Aluminium; Multiple sizes",
        "Short_Description": "Earth tags for safe grounding of cable glands.",
        "Full_Description": "Dowell earth tags ensure safe grounding between cable glands and equipment. Available in multiple sizes and materials."
    },
    {
        "Name": "Shrouds",
        "Product_Type": "Accessory",
        "Standards": "N/A",
        "Key_Features": "High-grade PVC; LSF & LSZH options; Enhances IP rating",
        "Short_Description": "Protective shrouds for cable glands.",
        "Full_Description": "Dowell high-grade PVC shrouds provide weather and corrosion protection for cable glands and enhance IP ratings."
    },
    {
        "Name": "Smart Crimping Tools",
        "Product_Type": "Tool",
        "Standards": "N/A",
        "Key_Features": "Hydraulic & mechanical; Supports 0.5–1000 sq.mm; Many die options",
        "Short_Description": "Crimping tools for various conductor sizes.",
        "Full_Description": "Dowell smart crimping tools come in hydraulic and mechanical variants supporting conductor sizes from 0.5 sq.mm to 1000 sq.mm."
    }
]

# ====== IMAGE EXTRACTION ======
print("Extracting images...")

doc = fitz.open(PDF_PATH)
image_files = []

img_index = 0
for page_index in range(len(doc)):
    page = doc[page_index]
    images = page.get_images(full=True)

    for img in images:
        xref = img[0]
        pix = fitz.Pixmap(doc, xref)

        # Create clean filename
        if img_index < len(products):
            clean_name = products[img_index]["Name"].replace(" ", "_").replace("–", "-")
        else:
            clean_name = f"extra_image_{img_index}"

        image_path = f"{IMAGE_DIR}/{clean_name}.png"

        # Save PNG
        if pix.n < 5:  # RGB or Gray
            pix.save(image_path)
        else:
            pix2 = fitz.Pixmap(fitz.csRGB, pix)
            pix2.save(image_path)
            pix2 = None

        image_files.append(image_path)
        img_index += 1

# Assign extracted images to products
for i, product in enumerate(products):
    product["Type"] = "CABLE ACCESSORIES"
    product["Brand"] = "Dowell"
    product["Product_URL"] = ""
    product["Brochure_Path"] = ""
    product["Brochure_Download_Status"] = "Pending"

    if i < len(image_files):
        product["Image_Path"] = image_files[i]
        product["Image_Download_Status"] = "Extracted"
    else:
        product["Image_Path"] = ""
        product["Image_Download_Status"] = "Missing"

# ====== WRITE JSON ======
with open("dowell_products.json", "w") as f:
    json.dump(products, f, indent=4)

print("DONE! Images saved to /images and JSON generated as dowell_products.json")
