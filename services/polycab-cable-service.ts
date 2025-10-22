// strategies/cable-strategy.ts
import { cables } from "@/data/products";
import {  CablesSearchFilters, CableSearchResult } from "@/types/product";
import { Product, ProductStrategy } from "@/types/common";

export class CableStrategy implements ProductStrategy<Product, CablesSearchFilters, CableSearchResult> {
  private cables: Product[] = cables;

  getAllProducts(): Product[] {
    return this.cables;
  }
  getProductType(): string {
    return 'cable';
  }
  getProductByName(name: string): Product | undefined {
    return this.cables.find(cable => 
      cable.Name.toLowerCase() === name.toLowerCase()
    );
  }

  searchProducts(
    filters: CablesSearchFilters = {},
    page: number = 1,
    limit: number = 10
  ): CableSearchResult {
    let filteredCables = [...this.cables];

    // Text search across multiple fields
    if (filters.search) {
      const searchTerm = filters.search.toLowerCase();
      filteredCables = filteredCables.filter(cable =>
        cable.Name.toLowerCase().includes(searchTerm) ||
        cable.Short_Description.toLowerCase().includes(searchTerm) ||
        cable.Full_Description.toLowerCase().includes(searchTerm) ||
        cable.Key_Features.toLowerCase().includes(searchTerm)
      );
    }

    // Filter by standards
    if (filters.standards && filters.standards.length > 0) {
      filteredCables = filteredCables.filter(cable =>
        filters.standards!.some(standard =>
          cable.Standards?.toLowerCase().includes(standard.toLowerCase())
        )
      );
    }

    // Filter by certifications
    if (filters.certifications && filters.certifications.length > 0) {
      filteredCables = filteredCables.filter(cable =>
        filters.certifications!.some(cert =>
          cable.Certifications?.toLowerCase().includes(cert.toLowerCase())
        )
      );
    }

    // Filter by features
    if (filters.features && filters.features.length > 0) {
      filteredCables = filteredCables.filter(cable =>
        filters.features!.some(feature =>
          cable.Key_Features.toLowerCase().includes(feature.toLowerCase())
        )
      );
    }

    // Filter by cable type
    if (filters.productType && filters.productType.length > 0) {
      filteredCables = filteredCables.filter(cable =>
        filters.productType!.includes(cable.Product_Type)
      );
    }

    // Pagination
    const startIndex = (page - 1) * limit;
    const endIndex = startIndex + limit;
    const paginatedCables = filteredCables.slice(startIndex, endIndex);

    return {
      cables: paginatedCables,
      total: filteredCables.length,
      page,
      limit
    };
  }

  getFilterOptions(subset: Product[] = this.cables) {
    const standards = new Set<string | undefined>();
    const certifications = new Set<string | undefined>();
    const features = new Set<string | undefined>();
    const cableTypes = new Set<string | undefined>();

    subset.forEach(cable => {
      // Extract standards
      cable.Standards?.split(',').forEach((std: string) => 
        standards.add(std.trim())
      );

      // Extract certifications
      cable.Certifications?.split(',').forEach((cert: string) => 
        certifications.add(cert.trim())
      );

      // Extract features
      cable.Key_Features.split(',').forEach((feature: string) => 
        features.add(feature.trim())
      );

      cableTypes.add(cable.Product_Type);
    });

    return {
      standards: Array.from(standards).sort(),
      certifications: Array.from(certifications).sort(),
      features: Array.from(features).sort(),
      cableTypes: Array.from(cableTypes).sort()
    };
  }

  getSimilarProducts(targetCable: Product, limit: number = 5): Product[] {
    const targetFeatures = targetCable.Key_Features.toLowerCase().split(',').map((f: string) => f.trim());
    
    const similarCables = this.cables
      .filter(cable => cable.Name !== targetCable.Name)
      .map(cable => {
        const cableFeatures = cable.Key_Features.toLowerCase().split(',').map((f: string) => f.trim());
        const commonFeatures = targetFeatures.filter((feature: string | any[]) =>
          cableFeatures.some((pf: any) => pf.includes(feature) || feature.includes(pf))
        );
        
        return {
          cable,
          similarity: commonFeatures.length / Math.max(targetFeatures.length, cableFeatures.length)
        };
      })
      .sort((a, b) => b.similarity - a.similarity)
      .slice(0, limit)
      .map(item => item.cable);

    return similarCables;
  }

  getProductStats() {
    const stats = {
      totalCables: this.cables.length,
      byStandard: {} as Record<string, number>,
      byCertification: {} as Record<string, number>,
      byCableType: {} as Record<string, number>
    };

    this.cables.forEach(cable => {
      // Count by standards
      cable.Standards?.split(',').forEach((std: string) => {
        const standard = std.trim();
        stats.byStandard[standard] = (stats.byStandard[standard] || 0) + 1;
      });

      // Count by certifications
      cable.Certifications?.split(',').forEach((cert: string) => {
        const certification = cert.trim();
        stats.byCertification[certification] = (stats.byCertification[certification] || 0) + 1;
      });

      // Count by cable type
      stats.byCableType[cable.Product_Type] = (stats.byCableType[cable.Product_Type] || 0) + 1;
    });

    return stats;
  }

  public getCablesByStandard(standard: string): Product[] {
    return this.cables.filter(cable =>
      cable.Standards?.toLowerCase().includes(standard.toLowerCase())
    );
  }

  public getCablesByCertification(certification: string): Product[] {
    return this.cables.filter(cable =>
      cable.Certifications?.toLowerCase().includes(certification.toLowerCase())
    );
  }
}
