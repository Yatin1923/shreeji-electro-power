export const BRANDS = {
  "Polycab": "Polycab",
  "Lauritz Knudsen": "Lauritz Knudsen",
  "Neptune": "Neptune",
  "Dowell's": "Dowell's",
  "Cabseal": "Cabseal",
};

// Subcategory constants
export const CABLE_SUBCATEGORIES = [
  'LV Power Cable',
  'MV Power Cable',
  'EHV Power Cable',
  'Instrumentation Cable',
  'Communication & Data Cable',
  'Renewable Energy Cable',
  'Control Cable',
  'Fire Protection Cable',
  'Industrial Cable',
  'Rubber Cable',
  'Marine & Offshore/Onshore Cable',
  'High Temperature Cable',
  'Defence Cable',
  'Domestic Appliance and Lighting Cable',
  'Building Wires',
  'Special Cable',
  'Aerial Bunched Cable',
] as const;

export const FAN_SUBCATEGORIES = [
  'Ceiling Fan',
  'Table Fan',
  'Wall Fan',
  'Pedestal Fan',
  'Exhaust Fan',
  'Air Circulator',
  'Farrata Fan',
] as const;

export const LIGHTING_SUBCATEGORIES = [
  'LED Bulb',
  'Downlight',
  'Panel Light',
  'LED Batten',
  'Outdoor Lights',
  'Rope and Strip Lights'
] as const;
export const SWITCHGEAR_SUBCATEGORIES = [
  'RCBO',
  'RCCB',
  'ACCL',
  'ISOLATOR',
  'MCB Changeover Switch',
  'MCB (Miniature Circuit Breaker)',
  'Distribution Board'
] as const;
export const SWITCH_SUBCATEGORIES = [
  'Levana',
  'Etira',
  'Accessories',
  'Plastic Modular Boxes',
] as const;

// LK (Lauritz Knudsen) Subcategories
export const MEDIUM_VOLTAGE_SUBCATEGORIES = [
  'Air Insulated Switchgear - AIS',
  'Ring Main Unit - RMU',
  'Compact Sub-Station - CSS',
  'Vacuum Contactor Units - VCU',
  'E-House',
  'Vacuum Circuit Breaker - VCB',
] as const;

export const LV_IEC_PANELS_SUBCATEGORIES = [
  'PCC and MCC Panels',
  'Sub-Main Distribution Board - SMDB',
] as const;

export const POWER_DISTRIBUTION_PRODUCTS_SUBCATEGORIES = [
  'Air Circuit Breaker - ACB',
  'Moulded Case Circuit Breaker - MCCB',
  'Switch Disconnectors & Switch Disconnector Fuses - SDF',
  'Busbar Trunking - BBT',
  'Change Over Switch - COS',
] as const;

export const MOTOR_MANAGEMENT_CONTROL_SUBCATEGORIES = [
  'Contactors',
  'Industrial Starter',
  'Motor Protection Circuit Breaker',
  'Electronic Motor Protection Relays',
  'Over Load Relay - OLR',
] as const;

export const INDUSTRIAL_AUTOMATION_CONTROL_SUBCATEGORIES = [
  'AC Drive',
  'Soft Starters',
  'Programmable Logic Controller - PLC',
  'Human-Machine Interface - HMI',
  'Servo',
  'Gateways',
] as const;

export const ENERGY_MANAGEMENT_PRODUCTS_SUBCATEGORIES = [
  'Power Quality and Power Factor Correction',
  'APFC Relays',
  'Digital Panel Meters',
  'Tariff Meter',
] as const;

export const MCB_RCCB_DISTRIBUTION_BOARDS_SUBCATEGORIES = [
  'Distribution Board - DB',
  'Miniature Circuit Breaker - MCB',
  'Residual Current Operated Circuit Breaker - RCBO',
  'Residual Current Circuit breaker - RCCB',
  '1Phase & 3Phase Automatic Changeover with Current Limiter - ACCL',
  'Surge Protective Devices - SPD',
  'Modular Change Over',
  'Modular Contactor',
  'Isolators',
] as const;

export const SWITCHES_ACCESSORIES_SUBCATEGORIES = [
  'Modular Switches',
  'Home Automation',
] as const;

export const PUMP_STARTERS_CONTROLLERS_SUBCATEGORIES = [
  'Starter',
  'Controller',
  'Solar Solutions',
  'Pump Starter and Controller Spare & Accessories',
] as const;

export const INDUSTRIAL_SIGNALLING_PRODUCTS = [
  'Time Switches',
  'Timers',
  'Monitoring Devices',
  'Push buttons & Indicating Lamps',
] as const;

export const BRAND_CATEGORIES: Record<string, string[]> = {
  "POLYCAB": [
    "CABLE",
    "FAN",
    "LIGHTING",
    "SWITCHGEAR",
    "SWITCH",
    "WIRE",
    "SOLAR",
  ],
  "LAURITZ KNUDSEN": [
    "MEDIUM VOLTAGE",
    "LV IEC PANELS",
    "POWER DISTRIBUTION PRODUCTS",
    "MOTOR MANAGEMENT & CONTROL",
    "INDUSTRIAL AUTOMATION & CONTROL",
    "ENERGY MANAGEMENT PRODUCTS",
    "MCB, RCCB & DISTRIBUTION BOARDS",
    "SWITCHES & ACCESSORIES",
    "PUMP STARTERS & CONTROLLERS",
    "INDUSTRIAL SIGNALLING PRODUCTS"
  ],
  "NEPTUNE": [
    "Industrial Plug & Sockets",
    "LV Switchboards",
    "Metering System",
    "PF Correction",
    "Power Quality"
  ]
};
