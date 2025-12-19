
// types/common.ts
export interface Product {
  Name: string;
  Product_Type: string;
  Type: string;
  Brand: string;
  Key_Features?: string | null;
  Benefits?: string | null;
  Short_Description?: string | null;
  Full_Description?: string | null;
  Image_Path?: string | null;
  Color?: string | null;

  // Fan
  Model_Number?: string | null;
  Specifications?: string | null;
  Sweep_Size?: string | null;
  RPM?: string | null;
  Power_Consumption?: string | null;
  Air_Delivery?: string | null;
  BEE_Rating?: string | null;
  Number_of_Blades?: string | null;
  Blade_Material?: string | null;
  Body_Material?: string | null;
  Motor_Winding?: string | null;
  Warranty?: string | null;
  Price?: string | null;


  // Cable
  Standards?: string | null;
  Certifications?: string | null;
  Product_URL?: string | null;
  Brochure_Path?: string | null;
  Image_Download_Status?: string | null;
  Brochure_Download_Status?: string | null;

  // Lighting
  Wattage?: any | null;

  // Switchgear
  Amperage?: string | null;
  Voltage?: string | null;
  Poles?: string | null;
  Breaking_Capacity?: string | null;
  Trip_Curve?: string | null;
  Sensitivity?: string | null;
  Application?: string | null;
  MCB_Type?: string | null;
  IP_Rating?: string | null;
  Operating_Temperature?: string | null;
  Contact_Material?: string | null;
  Mounting_Type?: string | null;
  Module?: string | null;
  GenCurrentRating?: string | null;

  // Wire
  Product_Series?: string | null;
  Size_Sq_MM?: string | null;
  Length?: string | null;
  Insulation_Type?: string | null;
  Heat_Resistance?: string | null;
  Copper_Grade?: string | null;
  Technology?: string | null;
  Fire_Safety?: string | null;
  Moisture_Resistance?: string | null;
  Abrasion_Resistance?: string | null;
  Eco_Certifications?: string | null;
  Current_Carrying_Capacity?: string | null;
  Product_Life?: string | null;
  Voltage_Rating?: string | null;
  Conductor_Type?: string | null;

  // Solar
  Power_Rating?: string | null;
}

export interface SearchFilters {
  search?: string;
  [key: string]: any;
}

export interface BaseSearchResult<T> {
  total: number;
  page: number;
  limit: number;
}

// Add more as you expand

export interface UnifiedSearchFilters {
  search?: string;
  productTypes?: string[]; // 'cable', 'fan', etc.
  brands?: string[];

  // Product-specific filters (optional)
  standards?: string[];
  certifications?: string[];
  features?: string[];
  cableProductType?: string[];

  // Product-specific filters (optional)
  fanType?: string[];
  colors?: string[];
  sweepSize?: string[];
  numberOfBlades?: string[];
  beeRating?: string[];
  bladeMaterial?: string[];
  bodyMaterial?: string[];
  priceRange?: {
    min?: number;
    max?: number;
  };
  powerConsumption?: {
    min?: number;
    max?: number;
  };
  airDelivery?: {
    min?: number;
    max?: number;
  };
  rpm?: {
    min?: number;
    max?: number;
  };
}

export interface UnifiedSearchResult {
  products: Array<{
    product: Product;
    productType: 'cable' | 'fan'; // Add more as you expand
  }>;
  total: number;
  page: number;
  limit: number;
  breakdown: {
    cables: number;
    fans: number;
    // Add more as you expand
  };
  filters?: {
    availableProductTypes: string[];
    availableBrands: string[];
    // Dynamic filters based on available products
    [key: string]: any;
  };
}

export interface ProductStrategy<T extends Product, F extends SearchFilters, R extends BaseSearchResult<T>> {
  getAllProducts(): T[];
  getProductByName(name: string): T | undefined;
  searchProducts(filters: F, page: number, limit: number): R;
  getFilterOptions(subset?: T[]): any;
  getSimilarProducts(target: T, limit: number): T[];
  getProductStats?(): any;
  getProductType(): string; // New method to identify product type
}
