// services/polycab-product-service.ts
import { products } from '@/data/products';
import { Product, ProductSearchFilters, ProductSearchResult } from '../types/product';
export class PolycabProductService {
  private static instance: PolycabProductService;
  private products: Product[] = products;

  public static getInstance(): PolycabProductService {
    if (!PolycabProductService.instance) {
      PolycabProductService.instance = new PolycabProductService();
    }
    return PolycabProductService.instance;
  }

  // Get all products
  public getAllProducts(): Product[] {
    return this.products;
  }

  // Get product by cable name
  public getProductByName(cableName: string): Product | undefined {
    return this.products.find(product => 
      product.Cable_Name.toLowerCase() === cableName.toLowerCase()
    );
  }

  // Search products with filters and pagination
  public searchProducts(
    filters: ProductSearchFilters = {},
    page: number = 1,
    limit: number = 10
  ): ProductSearchResult {
    let filteredProducts = [...this.products];

    // Text search across multiple fields
    if (filters.search) {
      const searchTerm = filters.search.toLowerCase();
      filteredProducts = filteredProducts.filter(product =>
        product.Cable_Name.toLowerCase().includes(searchTerm) ||
        product.Short_Description.toLowerCase().includes(searchTerm) ||
        product.Full_Description.toLowerCase().includes(searchTerm) ||
        product.Key_Features.toLowerCase().includes(searchTerm)
      );
    }

    // Filter by standards
    if (filters.standards && filters.standards.length > 0) {
      filteredProducts = filteredProducts.filter(product =>
        filters.standards!.some(standard =>
          product.Standards.toLowerCase().includes(standard.toLowerCase())
        )
      );
    }

    // Filter by certifications
    if (filters.certifications && filters.certifications.length > 0) {
      filteredProducts = filteredProducts.filter(product =>
        filters.certifications!.some(cert =>
          product.Certifications.toLowerCase().includes(cert.toLowerCase())
        )
      );
    }

    // Filter by features
    if (filters.features && filters.features.length > 0) {
      filteredProducts = filteredProducts.filter(product =>
        filters.features!.some(feature =>
          product.Key_Features.toLowerCase().includes(feature.toLowerCase())
        )
      );
    }

    // Filter by product type
    if (filters.productType && filters.productType.length > 0) {
      filteredProducts = filteredProducts.filter(product =>
        filters.productType!.includes(product.Product_Type)
      );
    }

    // Pagination
    const startIndex = (page - 1) * limit;
    const endIndex = startIndex + limit;
    const paginatedProducts = filteredProducts.slice(startIndex, endIndex);

    return {
      products: paginatedProducts,
      total: filteredProducts.length,
      page,
      limit
    };
  }

  // Get unique values for filters
  public getFilterOptions() {
    const standards = new Set<string>();
    const certifications = new Set<string>();
    const features = new Set<string>();
    const productTypes = new Set<string>();

    this.products.forEach(product => {
      // Extract standards
      product.Standards.split(',').forEach(std => 
        standards.add(std.trim())
      );

      // Extract certifications
      product.Certifications.split(',').forEach(cert => 
        certifications.add(cert.trim())
      );

      // Extract features
      product.Key_Features.split(',').forEach(feature => 
        features.add(feature.trim())
      );

      productTypes.add(product.Product_Type);
    });

    return {
      standards: Array.from(standards).sort(),
      certifications: Array.from(certifications).sort(),
      features: Array.from(features).sort(),
      productTypes: Array.from(productTypes).sort()
    };
  }

  // Get products by standard
  public getProductsByStandard(standard: string): Product[] {
    return this.products.filter(product =>
      product.Standards.toLowerCase().includes(standard.toLowerCase())
    );
  }

  // Get products by certification
  public getProductsByCertification(certification: string): Product[] {
    return this.products.filter(product =>
      product.Certifications.toLowerCase().includes(certification.toLowerCase())
    );
  }

  // Get similar products based on features
  public getSimilarProducts(targetProduct: Product, limit: number = 5): Product[] {
    const targetFeatures = targetProduct.Key_Features.toLowerCase().split(',').map(f => f.trim());
    
    const similarProducts = this.products
      .filter(product => product.Cable_Name !== targetProduct.Cable_Name)
      .map(product => {
        const productFeatures = product.Key_Features.toLowerCase().split(',').map(f => f.trim());
        const commonFeatures = targetFeatures.filter(feature =>
          productFeatures.some(pf => pf.includes(feature) || feature.includes(pf))
        );
        
        return {
          product,
          similarity: commonFeatures.length / Math.max(targetFeatures.length, productFeatures.length)
        };
      })
      .sort((a, b) => b.similarity - a.similarity)
      .slice(0, limit)
      .map(item => item.product);

    return similarProducts;
  }

  // Get products statistics
  public getProductStats() {
    const stats = {
      totalProducts: this.products.length,
      byStandard: {} as Record<string, number>,
      byCertification: {} as Record<string, number>,
      byProductType: {} as Record<string, number>
    };

    this.products.forEach(product => {
      // Count by standards
      product.Standards.split(',').forEach(std => {
        const standard = std.trim();
        stats.byStandard[standard] = (stats.byStandard[standard] || 0) + 1;
      });

      // Count by certifications
      product.Certifications.split(',').forEach(cert => {
        const certification = cert.trim();
        stats.byCertification[certification] = (stats.byCertification[certification] || 0) + 1;
      });

      // Count by product type
      stats.byProductType[product.Product_Type] = (stats.byProductType[product.Product_Type] || 0) + 1;
    });

    return stats;
  }
}

// Export singleton instance
export const polycabProductService = PolycabProductService.getInstance();
