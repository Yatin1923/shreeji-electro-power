import { Product, BaseSearchResult, ProductStrategy, SearchFilters } from "@/types/common";

// services/generic-product-service.ts
export class GenericProductService<
  T extends Product, 
  F extends SearchFilters, 
  R extends BaseSearchResult<T>
> {
  private strategy: ProductStrategy<T, F, R>;

  constructor(strategy: ProductStrategy<T, F, R>) {
    this.strategy = strategy;
  }

  public getAllProducts(): T[] {
    return this.strategy.getAllProducts();
  }

  public getProductByName(name: string): T | undefined {
    return this.strategy.getProductByName(name);
  }

  public searchProducts(
    filters: F = {} as F,
    page: number = 1,
    limit: number = 10
  ): R {
    return this.strategy.searchProducts(filters, page, limit);
  }

  public getFilterOptions(subset?: T[]): any {
    return this.strategy.getFilterOptions(subset);
  }

  public getSimilarProducts(target: T, limit: number = 5): T[] {
    return this.strategy.getSimilarProducts(target, limit);
  }

  public getProductStats(): any {
    return this.strategy.getProductStats?.() || {};
  }
}
