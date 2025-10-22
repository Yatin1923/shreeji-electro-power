
// types/common.ts
export interface Product {
    Name: string;
    Product_Type: string;
    Type: string;
    Brand: string;
    Key_Features: string;
    Short_Description: string;
    Full_Description: string;
    Image_Path: string;
    
    // Product
    Model_Number?: string;
    Specifications?: string;
    Colors?: string;
    Sweep_Size?: string;
    RPM?: string;
    Power_Consumption?: string;
    Air_Delivery?: string;
    BEE_Rating?: string;
    Number_of_Blades?: string;
    Blade_Material?: string;
    Body_Material?: string;
    Motor_Winding?: string;
    Warranty?: string;
    Price?: string;
    

    // Product
    Standards?: string;
    Certifications?: string;
    Product_URL?: string;
    Brochure_Path?: string;
    Image_Download_Status?: string;
    Brochure_Download_Status?: string;
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
  