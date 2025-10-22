
// export interface Product extends Product {
//     Certifications: string;
//     Product_URL: string;
//     Brochure_Path: string;
//     Image_Download_Status: string;
//     Brochure_Download_Status: string;
//   }
//   export interface Product extends Product {
//     Model_Number: string;
//     Specifications: string;
//     Colors: string;
//     Sweep_Size: string;
//     RPM: string;
//     Power_Consumption: string;
//     Air_Delivery: string;
//     BEE_Rating: string;
//     Number_of_Blades: string;
//     Blade_Material: string;
//     Body_Material: string;
//     Motor_Winding: string;
//     Warranty: string;
//     Price: string;
//   }

import { Product } from "./common";

  
  export interface CablesSearchFilters {
    search?: string;
    standards?: string[];
    certifications?: string[];
    features?: string[];
    productType?: string[];
  }
  
  export interface CableSearchResult {
    cables: Product[];
    total: number;
    page: number;
    limit: number;
  }

  export interface FansSearchFilters {
    search?: string;
    type?: string[];           // ceiling-fan, table-fan, wall-fan, etc.
    colors?: string[];         // white, brown, black, etc.
    sweepSize?: string[];      // 600mm, 1200mm, etc.
    numberOfBlades?: string[]; // 3, 4, 5, 6
    priceRange?: {
      min?: number;
      max?: number;
    };
    beeRating?: string[];      // 1, 2, 3, 4, 5 star
    bladeMaterial?: string[];  // Aluminium, ABS, Plastic, etc.
    bodyMaterial?: string[];   // Aluminium, Steel, etc.
    motorType?: string[];      // BLDC, Induction, etc.
    brand?: string[];          // Polycab
    warranty?: string[];       // 2 Year, 3 Year, etc.
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
  
  export interface FanSearchResult {
    fans: Product[];
    total: number;
    page: number;
    limit: number;
    filters?: {
      availableTypes: string[];
      availableColors: string[];
      availableSweepSizes: string[];
      availableBladeNumbers: string[];
      availableBEERatings: string[];
      availableBladeMaterials: string[];
      availableBodyMaterials: string[];
      priceRange: {
        min: number;
        max: number;
      };
      powerConsumptionRange: {
        min: number;
        max: number;
      };
      airDeliveryRange: {
        min: number;
        max: number;
      };
      rpmRange: {
        min: number;
        max: number;
      };
    };
  }