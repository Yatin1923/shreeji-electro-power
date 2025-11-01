// strategies/fan-strategy.ts
import { fans } from "@/data/products";
import { FansSearchFilters, FanSearchResult } from "@/types/product";
import { Product, ProductStrategy } from "@/types/common";

export class FanStrategy implements ProductStrategy<Product, FansSearchFilters, FanSearchResult> {
  private fans: Product[] = fans;

  getAllProducts(): Product[] {
    return this.fans;
  }

  getProductByName(name: string): Product | undefined {
    return this.fans.find(fan => 
      fan.Name.toLowerCase() === name.toLowerCase()
    );
  }
  getProductType(): string {
    return 'fan';
  }
  searchProducts(
    filters: FansSearchFilters = {},
    page: number = 1,
    limit: number = 10
  ): FanSearchResult {
    let filteredProducts = [...this.fans];

    // Apply fan filters
    filteredProducts = filteredProducts.filter(fan => 
      this.matchesFanFilters(fan, filters)
    );

    // Pagination
    const startIndex = (page - 1) * limit;
    const endIndex = startIndex + limit;
    const paginatedProducts = filteredProducts.slice(startIndex, endIndex);

    // Get available filter options for the result
    const availableFilters = this.getFanFilterOptions(filteredProducts);

    return {
      fans: paginatedProducts,
      total: filteredProducts.length,
      page,
      limit,
      filters: availableFilters
    };
  }

  private matchesFanFilters(fan: Product, filters: FansSearchFilters): boolean {
    // Text search
    if (filters.search) {
      const searchTerm = filters.search.toLowerCase();
      const searchableText = [
        fan.Name,
        fan.Short_Description,
        fan.Full_Description,
        fan.Key_Features
      ].join(' ').toLowerCase();
      
      if (!searchableText.includes(searchTerm)) {
        return false;
      }
    }

    // Filter by type
    if (filters.type && filters.type.length > 0) {
      if (!filters.type.includes(fan.Type)) return false;
    }

    // Filter by colors
    if (filters.colors && filters.colors.length > 0) {
      const fanColors = fan.Color?.toLowerCase().split(',').map(c => c.trim());
      const hasColor = filters.colors.some(color =>
        fanColors?.some(fc => fc.includes(color.toLowerCase()))
      );
      if (!hasColor) return false;
    }

    // Filter by sweep size
    if (filters.sweepSize && filters.sweepSize.length > 0) {
      if (!filters.sweepSize.includes(fan.Sweep_Size??"")) return false;
    }

    // Filter by number of blades
    if (filters.numberOfBlades && filters.numberOfBlades.length > 0) {
      if (!filters.numberOfBlades.includes(fan.Number_of_Blades??"")) return false;
    }

    // Filter by BEE rating
    if (filters.beeRating && filters.beeRating.length > 0) {
      const fanRating = fan.BEE_Rating?.toLowerCase();
      const hasRating = filters.beeRating.some(rating =>
        fanRating?.includes(rating.toLowerCase())
      );
      if (!hasRating) return false;
    }

    // Filter by blade material
    if (filters.bladeMaterial && filters.bladeMaterial.length > 0) {
      if (!filters.bladeMaterial.includes(fan.Blade_Material??"")) return false;
    }

    // Filter by body material
    if (filters.bodyMaterial && filters.bodyMaterial.length > 0) {
      if (!filters.bodyMaterial.includes(fan.Body_Material??"")) return false;
    }

    // Price range filter
    if (filters.priceRange) {
      const price = this.extractNumericPrice(fan.Price??"");
      if (price !== null) {
        if (filters.priceRange.min && price < filters.priceRange.min) return false;
        if (filters.priceRange.max && price > filters.priceRange.max) return false;
      }
    }

    // Power consumption filter
    if (filters.powerConsumption) {
      const power = this.extractNumericValue(fan.Power_Consumption??"");
      if (power !== null) {
        if (filters.powerConsumption.min && power < filters.powerConsumption.min) return false;
        if (filters.powerConsumption.max && power > filters.powerConsumption.max) return false;
      }
    }

    // Air delivery filter
    if (filters.airDelivery) {
      const airDelivery = this.extractNumericValue(fan.Air_Delivery??"");
      if (airDelivery !== null) {
        if (filters.airDelivery.min && airDelivery < filters.airDelivery.min) return false;
        if (filters.airDelivery.max && airDelivery > filters.airDelivery.max) return false;
      }
    }

    // RPM filter
    if (filters.rpm) {
      const rpm = this.extractNumericValue(fan.RPM??"");
      if (rpm !== null) {
        if (filters.rpm.min && rpm < filters.rpm.min) return false;
        if (filters.rpm.max && rpm > filters.rpm.max) return false;
      }
    }

    return true;
  }

  private extractNumericPrice(priceStr: string): number | null {
    const match = priceStr.match(/[\d,]+/);
    if (match) {
      return parseInt(match[0].replace(/,/g, ''));
    }
    return null;
  }

  private extractNumericValue(valueStr: string): number | null {
    const match = valueStr.match(/(\d+(?:\.\d+)?)/);
    if (match) {
      return parseFloat(match[1]);
    }
    return null;
  }

  getFilterOptions(fanSubset: Product[] = this.fans) {
    return this.getFanFilterOptions(fanSubset);
  }

  public getFanFilterOptions(fanSubset: Product[] = this.fans) {
    const types = new Set<string>();
    const colors = new Set<string>();
    const sweepSizes = new Set<string>();
    const bladeNumbers = new Set<string>();
    const beeRatings = new Set<string>();
    const bladeMaterials = new Set<string>();
    const bodyMaterials = new Set<string>();
    let minPrice = Infinity;
    let maxPrice = 0;
    let minPower = Infinity;
    let maxPower = 0;
    let minAirDelivery = Infinity;
    let maxAirDelivery = 0;
    let minRpm = Infinity;
    let maxRpm = 0;

    fanSubset.forEach(fan => {
      types.add(fan.Type);
      
      // Extract colors
      fan.Color?.split(',').forEach(color => {
        const trimmedColor = color.trim();
        if (trimmedColor && trimmedColor !== 'Available in Multiple Color') {
          colors.add(trimmedColor);
        }
      });

      if (fan.Sweep_Size && fan.Sweep_Size !== 'N/A') sweepSizes.add(fan.Sweep_Size);
      if (fan.Number_of_Blades && fan.Number_of_Blades !== 'N/A') bladeNumbers.add(fan.Number_of_Blades);
      if (fan.BEE_Rating && fan.BEE_Rating !== 'N/A') beeRatings.add(fan.BEE_Rating);
      if (fan.Blade_Material && fan.Blade_Material !== 'N/A') bladeMaterials.add(fan.Blade_Material);
      if (fan.Body_Material && fan.Body_Material !== 'N/A') bodyMaterials.add(fan.Body_Material);

      // Extract numeric ranges
      const price = this.extractNumericPrice(fan.Price??"");
      if (price !== null) {
        minPrice = Math.min(minPrice, price);
        maxPrice = Math.max(maxPrice, price);
      }

      const power = this.extractNumericValue(fan.Power_Consumption??"");
      if (power !== null) {
        minPower = Math.min(minPower, power);
        maxPower = Math.max(maxPower, power);
      }

      const airDelivery = this.extractNumericValue(fan.Air_Delivery??"");
      if (airDelivery !== null) {
        minAirDelivery = Math.min(minAirDelivery, airDelivery);
        maxAirDelivery = Math.max(maxAirDelivery, airDelivery);
      }

      const rpm = this.extractNumericValue(fan.RPM??"");
      if (rpm !== null) {
        minRpm = Math.min(minRpm, rpm);
        maxRpm = Math.max(maxRpm, rpm);
      }
    });

    return {
      availableTypes: Array.from(types).sort(),
      availableColors: Array.from(colors).sort(),
      availableSweepSizes: Array.from(sweepSizes).sort(),
      availableBladeNumbers: Array.from(bladeNumbers).sort(),
      availableBEERatings: Array.from(beeRatings).sort(),
      availableBladeMaterials: Array.from(bladeMaterials).sort(),
      availableBodyMaterials: Array.from(bodyMaterials).sort(),
      priceRange: {
        min: minPrice === Infinity ? 0 : minPrice,
        max: maxPrice || 50000
      },
      powerConsumptionRange: {
        min: minPower === Infinity ? 0 : minPower,
        max: maxPower || 100
      },
      airDeliveryRange: {
        min: minAirDelivery === Infinity ? 0 : minAirDelivery,
        max: maxAirDelivery || 500
      },
      rpmRange: {
        min: minRpm === Infinity ? 0 : minRpm,
        max: maxRpm || 2000
      }
    };
  }

  getSimilarProducts(targetFan: Product, limit: number = 5): Product[] {
    return this.fans
      .filter(fan => fan.Name !== targetFan.Name)
      .map(fan => {
        let similarity = 0;
        let totalChecks = 0;

        // Compare sweep size
        totalChecks++;
        if (fan.Sweep_Size === targetFan.Sweep_Size) similarity++;

        // Compare number of blades
        totalChecks++;
        if (fan.Number_of_Blades === targetFan.Number_of_Blades) similarity++;

        // Compare type
        totalChecks++;
        if (fan.Type === targetFan.Type) similarity++;

        // Compare BEE rating
        totalChecks++;
        if (fan.BEE_Rating === targetFan.BEE_Rating) similarity++;

        return {
          fan,
          similarity: similarity / totalChecks
        };
      })
      .sort((a, b) => b.similarity - a.similarity)
      .slice(0, limit)
      .map(item => item.fan);
  }

  // Product-specific methods
  public getFansByType(type: string): Product[] {
    return this.fans.filter(fan =>
      fan.Type.toLowerCase().includes(type.toLowerCase())
    );
  }

  public getFansBySweepSize(sweepSize: string): Product[] {
    return this.fans.filter(fan => fan.Sweep_Size === sweepSize);
  }
}
