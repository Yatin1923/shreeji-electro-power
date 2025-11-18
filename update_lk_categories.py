import json

# Category mapping based on LK website structure
# Format: "current_product_type": ("new_type", "new_product_type")
category_mapping = {
    # Pump Starters and Controllers
    "Starter": ("Pump Starters and Controllers", "Starter"),
    "Controller": ("Pump Starters and Controllers", "Controller"),
    "Solar Solutions": ("Pump Starters and Controllers", "Solar Solutions"),
    "Pump Starter And Controller Spare Accessories": ("Pump Starters and Controllers", "Pump Starter and Controller Spare & Accessories"),
    
    # Medium Voltage
    "Air Insulated Switchgear Ais": ("Medium Voltage", "Air Insulated Switchgear - AIS"),
    "Ring Main Unit Rmu": ("Medium Voltage", "Ring Main Unit - RMU"),
    "Compact Sub Station Css Or Packaged Sub Stations Pss": ("Medium Voltage", "Compact Sub-Station - CSS"),
    "Vacuum Circuit Breaker Vcb": ("Medium Voltage", "Vacuum Circuit Breaker - VCB"),
    
    # LV IEC Panels
    "Pcc And Mcc Panels": ("LV IEC Panels", "PCC and MCC Panels"),
    "Sub Main Distribution Board Smdb": ("LV IEC Panels", "Sub-Main Distribution Board - SMDB"),
    
    # Power Distribution products
    "Air Circuit Breaker Acb": ("Power Distribution products", "Air Circuit Breaker - ACB"),
    "Moulded Case Circuit Breaker Mccb": ("Power Distribution products", "Moulded Case Circuit Breaker - MCCB"),
    "Switch Disconnectors Switch Disconnector Fuses Sdf": ("Power Distribution products", "Switch Disconnectors & Switch Disconnector Fuses - SDF"),
    "Busbar Trunking Bbt": ("Power Distribution products", "Busbar Trunking - BBT"),
    
    # Motor Management & Control
    "Industrial Starter": ("Motor Management & Control", "Industrial Starter"),
    "Motor Protection Circuit Breaker": ("Motor Management & Control", "Motor Protection Circuit Breaker"),
    "Electronic Motor Protection Relays": ("Motor Management & Control", "Electronic Motor Protection Relays"),
    
    # Industrial Automation & Control
    "Ac Drive": ("Industrial Automation & Control", "AC Drive"),
    "Soft Starters": ("Industrial Automation & Control", "Soft Starters"),
    
    # Energy Management Products
    "Power Quality And Power Factor Correction": ("Energy Management Products", "Power Quality and Power Factor Correction"),
    "Apfc Relays": ("Energy Management Products", "APFC Relays"),
    
    # MCB, RCCB & Distribution Boards
    "Miniature Circuit Breaker Mcb": ("MCB, RCCB & Distribution Boards", "Miniature Circuit Breaker - MCB"),
    "Residual Current Operated Circuit Breaker Rcbo": ("MCB, RCCB & Distribution Boards", "Residual Current Operated Circuit Breaker - RCBO"),
    "Residual Current Circuit Breaker Rccb": ("MCB, RCCB & Distribution Boards", "Residual Current Circuit breaker - RCCB"),
    "1Phase 3Phase Automatic Changeover With Current Limiter Accl": ("MCB, RCCB & Distribution Boards", "1Phase & 3Phase Automatic Changeover with Current Limiter - ACCL"),
    "Modular Contactor": ("MCB, RCCB & Distribution Boards", "Modular Contactor"),
    "Surge Protective Devices Spd": ("MCB, RCCB & Distribution Boards", "Surge Protective Devices - SPD"),
    "Isolators": ("MCB, RCCB & Distribution Boards", "Isolators"),
    
    # Panel Accessories
    "Time Switches": ("Panel Accessories", "Time Switches"),
    "Push Buttons Indicating Lamps": ("Panel Accessories", "Push buttons & Indicating Lamps"),
}

# Read the JSON file
with open('/Users/yatinchokshi/Desktop/shreeji-electro-power/data/lk_ea_products.json', 'r') as f:
    products = json.load(f)

# Update each product
updated_count = 0
for product in products:
    current_product_type = product.get('Product_Type', '')
    
    if current_product_type in category_mapping:
        new_type, new_product_type = category_mapping[current_product_type]
        product['Type'] = new_type
        product['Product_Type'] = new_product_type
        updated_count += 1
        print(f"Updated: {product['Name']}")
        print(f"  Old: Type='{product.get('Type', 'LK')}', Product_Type='{current_product_type}'")
        print(f"  New: Type='{new_type}', Product_Type='{new_product_type}'")
        print()

# Write the updated JSON back to file
with open('/Users/yatinchokshi/Desktop/shreeji-electro-power/data/lk_ea_products.json', 'w') as f:
    json.dump(products, f, indent=2, ensure_ascii=False)

print(f"\nTotal products updated: {updated_count} out of {len(products)}")
