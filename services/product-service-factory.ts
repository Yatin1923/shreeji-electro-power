// services/product-service-factory.ts
import { CableStrategy } from './polycab-cable-service';
import { FanStrategy } from './polycab-fan-service';
import { GenericProductService } from './product-service';
import { UnifiedProductService } from './unified-product-service';
import { Product, Product, CablesSearchFilters, FansSearchFilters, CableSearchResult, FanSearchResult } from '@/types/product';

export enum ProductType {
  CABLE = 'cable',
  FAN = 'fan',
  ALL = 'all' // New option for all products
}

export class ProductServiceFactory {
  private static cableService: GenericProductService<Product, CablesSearchFilters, CableSearchResult> | null = null;
  private static fanService: GenericProductService<Product, FansSearchFilters, FanSearchResult> | null = null;
  private static unifiedService: UnifiedProductService | null = null;

  public static getCableService(): GenericProductService<Product, CablesSearchFilters, CableSearchResult> {
    if (!this.cableService) {
      this.cableService = new GenericProductService(new CableStrategy());
    }
    return this.cableService;
  }

  public static getFanService(): GenericProductService<Product, FansSearchFilters, FanSearchResult> {
    if (!this.fanService) {
      this.fanService = new GenericProductService(new FanStrategy());
    }
    return this.fanService;
  }

  public static getUnifiedService(): UnifiedProductService {
    if (!this.unifiedService) {
      this.unifiedService = new UnifiedProductService();
    }
    return this.unifiedService;
  }

  public static getService(productType: ProductType) {
    switch (productType) {
      case ProductType.CABLE:
        return this.getCableService();
      case ProductType.FAN:
        return this.getFanService();
      case ProductType.ALL:
        return this.getUnifiedService();
      default:
        throw new Error(`Unsupported product type: ${productType}`);
    }
  }
}

// Export individual services for backward compatibility
export const polycabCableService = ProductServiceFactory.getCableService();
export const polycabFanService = ProductServiceFactory.getFanService();
export const polycabUnifiedService = ProductServiceFactory.getUnifiedService();
