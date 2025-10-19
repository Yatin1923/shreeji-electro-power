// types/product.ts
export interface Product {
    Cable_Name: string;
    Product_Type: string;
    Standards: string;
    Certifications: string;
    Key_Features: string;
    Short_Description: string;
    Full_Description: string;
    Product_URL: string;
    Image_Path: string;
    Brochure_Path: string;
    Image_Download_Status: string;
    Brochure_Download_Status: string;
  }
  
  export interface ProductSearchFilters {
    search?: string;
    standards?: string[];
    certifications?: string[];
    features?: string[];
    productType?: string[];
  }
  
  export interface ProductSearchResult {
    products: Product[];
    total: number;
    page: number;
    limit: number;
  }
  