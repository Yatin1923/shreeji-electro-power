// services/unified-product-service.ts
import { allProducts, cables, fans, lightings, switchgears } from '@/data/products';
import { CableStrategy } from './polycab-cable-service';
import { FanStrategy } from './polycab-fan-service';
import { Product, UnifiedSearchFilters, UnifiedSearchResult } from '@/types/common';

export class UnifiedProductService {
  private static instance: UnifiedProductService;
  
  private cableStrategy: CableStrategy;
  private fanStrategy: FanStrategy;
  
  public constructor() {
    this.cableStrategy = new CableStrategy();
    this.fanStrategy = new FanStrategy();
  }

  public static getInstance(): UnifiedProductService {
    if (!UnifiedProductService.instance) {
      UnifiedProductService.instance = new UnifiedProductService();
    }
    return UnifiedProductService.instance;
  }

  // Get all products from all categories
  public getAllProducts():Product[]{
    return [...allProducts];
    return [...switchgears];
  }

  // Get total count of all products
  public getTotalProductCount(): {
    total: number;
    breakdown: {
      cables: number;
      fans: number;
      lightings:number;
      switchgears:number;
    };
  } {

    return {
      total: allProducts.length,
      breakdown: {
        cables:cables.length,
        fans:fans.length,
        lightings:lightings.length,
        switchgears:switchgears.length

      }
    };
  }


  // Get product by name across all types
  public getProductByName(name: string):Product | undefined {
    // Try cables first
    const cable = cables.find(cable => 
      cable.Name.toLowerCase() === name.toLowerCase());
    if (cable) {
      return cable;
    }

    // Try fans
    const fan = fans.find(fan => 
      fan.Name.toLowerCase() === name.toLowerCase());
    if (fan) {
      return fan;
    }
    const lighting = lightings.find(lighting => 
      lighting.Name.toLowerCase() == name.toLowerCase());
    if (lighting) {
      return lighting;
    }
    const switchgear = switchgears.find(switchgear => 
      switchgear.Name.toLowerCase() == name.toLowerCase());
    if (switchgear) {
      return switchgear;
    }

    return undefined;
  }

  // Get products by category
  public getProductsByType(productType: 'cable' | 'fan'): Array<{
    product: Product;
    productType: 'cable' | 'fan';
  }> {
    if (productType === 'cable') {
      return this.cableStrategy.getAllProducts().map(cable => ({
        product: cable as Product,
        productType: 'cable' as const
      }));
    } else if (productType === 'fan') {
      return this.fanStrategy.getAllProducts().map(fan => ({
        product: fan as Product,
        productType: 'fan' as const
      }));
    }
    return [];
  }

  // Get similar products across all types
  public getSimilarProducts(
    targetProduct: Product,
    targetType: 'cable' | 'fan',
    limit: number = 5
  ): Array<{
    product: Product;
    productType: 'cable' | 'fan';
  }> {
    if (targetType === 'cable') {
      const similar = this.cableStrategy.getSimilarProducts(targetProduct, limit);
      return similar.map(cable => ({
        product: cable as Product,
        productType: 'cable' as const
      }));
    } else if (targetType === 'fan') {
      const similar = this.fanStrategy.getSimilarProducts(targetProduct as Product, limit);
      return similar.map(fan => ({
        product: fan as Product,
        productType: 'fan' as const
      }));
    }
    return [];
  }

  // Get comprehensive statistics
  public getAllProductStats() {
    const cableStats = this.cableStrategy.getProductStats?.() || {};
    const fanStats = this.fanStrategy.getFanFilterOptions?.() || {};
    
    return {
      overview: this.getTotalProductCount(),
      cables: cableStats,
      fans: fanStats
    };
  }

  // Helper methods
  private matchesGlobalSearch(item: { product: Product; productType: 'cable' | 'fan' }, searchTerm: string): boolean {
    const term = searchTerm.toLowerCase();
    
    if (item.productType === 'cable') {
      const cable = item.product as Product;
      return (
        cable.Name.toLowerCase().includes(term) ||
        cable.Short_Description.toLowerCase().includes(term) ||
        cable.Full_Description.toLowerCase().includes(term) ||
        cable.Key_Features.toLowerCase().includes(term) ||
        cable.Product_Type.toLowerCase().includes(term) ||
        cable.Brand.toLowerCase().includes(term)
      );
    } else if (item.productType === 'fan') {
      const fan = item.product as Product;
      return (
        fan.Name.toLowerCase().includes(term) ||
        fan.Short_Description.toLowerCase().includes(term) ||
        fan.Full_Description.toLowerCase().includes(term) ||
        fan.Key_Features.toLowerCase().includes(term) ||
        fan.Type.toLowerCase().includes(term) ||
        fan.Brand.toLowerCase().includes(term)
      );
    }
    
    return false;
  }

  private matchesCableFilters(cable: Product, filters: UnifiedSearchFilters): boolean {
    // Apply cable-specific filters
    if (filters.standards?.length) {
      const hasStandard = filters.standards.some(standard =>
        cable.Standards?.toLowerCase().includes(standard.toLowerCase())
      );
      if (!hasStandard) return false;
    }

    if (filters.certifications?.length) {
      const hasCertification = filters.certifications.some(cert =>
        cable.Certifications?.toLowerCase().includes(cert.toLowerCase())
      );
      if (!hasCertification) return false;
    }

    if (filters.features?.length) {
      const hasFeature = filters.features.some(feature =>
        cable.Key_Features.toLowerCase().includes(feature.toLowerCase())
      );
      if (!hasFeature) return false;
    }

    if (filters.cableProductType?.length) {
      if (!filters.cableProductType.includes(cable.Product_Type)) return false;
    }

    return true;
  }

  private matchesFanFilters(fan: Product, filters: UnifiedSearchFilters): boolean {
    // Apply fan-specific filters
    if (filters.fanType?.length) {
      if (!filters.fanType.includes(fan.Type)) return false;
    }

    if (filters.colors?.length) {
      const fanColors = fan.Colors?.toLowerCase().split(',').map(c => c.trim());
      const hasColor = filters.colors.some(color =>
        fanColors?.some(fc => fc.includes(color.toLowerCase()))
      );
      if (!hasColor) return false;
    }

    if (filters.sweepSize?.length) {
      if (!filters.sweepSize.includes(fan.Sweep_Size??"")) return false;
    }

    // Add other fan filters as needed...
    
    return true;
  }

  private getUnifiedFilterOptions(products: Product[]) {
    const productTypes = new Set<string>();
    const brands = new Set<string>();

    // Get cable-specific options
    const cables = products.filter(p => 'Name' in p) as Product[];
    const cableOptions = cables.length > 0 ? this.cableStrategy.getFilterOptions(cables) : {};

    // Get fan-specific options
    const fans = products.filter(p => 'Name' in p) as Product[];
    const fanOptions = fans.length > 0 ? this.fanStrategy.getFilterOptions(fans) : {};

    products.forEach(product => {
      if ('Name' in product) {
        productTypes.add('cable');
      } else if ('Name' in product) {
        productTypes.add('fan');
      }
      brands.add(product.Brand);
    });

    return {
      availableProductTypes: Array.from(productTypes),
      availableBrands: Array.from(brands).sort(),
      ...cableOptions,
      ...fanOptions
    };
  }
}

export const unifiedProductService = UnifiedProductService.getInstance();
