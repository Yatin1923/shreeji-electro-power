// Basic in-memory product dataset used by the product list and detail pages.

import { Product } from "@/scripts/convert-excel-to-json"
import products from "@/data/products.json"

export function getProductById(id: number): Product | undefined{
  console.log("Fetching product with ID:", id);
  var product = products.find(p => p.id ==id);
  console.log("Available products:", product);
  return product;
}

export function getRelated(id: number, limit = 4): Product[]|undefined {
  return products.filter((p) => p.id !== id).slice(0, limit)
}
type GetProductsOptions = {
  page?: number; // which page (default 1)
  limit?: number; // items per page (default 10)
  sortBy?: keyof Product; // field to sort (e.g., "name" | "rating" | "reviews")
  sortOrder?: "asc" | "desc"; // ascending or descending
  filters?: {
    category?: string[];
    brand?: string[];
    search?:string;
    minRating?: number;
    maxRating?: number;
  };

};
export function getProducts(options: GetProductsOptions = {}) {
  const {
    page = 1,
    limit = 10,
    sortBy,
    sortOrder = "asc",
    filters = {},
  } = options;

  let result = [...products];
  console.log(filters);
  if (filters.category?.length) {
    result = result.filter((p) => filters.category!.includes(p.category as string));
  }

  // brand filter
  if (filters.brand?.length) {
    result = result.filter((p) => filters.brand!.includes(p.brand as string));
  }

  if (filters.minRating !== undefined) {
    result = result.filter((p) => p.rating >= filters.minRating!);
  }

  if (filters.maxRating !== undefined) {
    result = result.filter((p) => p.rating <= filters.maxRating!);
  }
  if (filters.search?.trim()) {
    const searchLower = filters.search.trim().toLowerCase();
    result = result.filter((p) => p.name.toLowerCase().includes(searchLower));
  }

  // Apply sorting
  if (sortBy) {
    result.sort((a, b) => {
      const aValue = a[sortBy];
      const bValue = b[sortBy];

      if (aValue === undefined || bValue === undefined) return 0;

      if (typeof aValue === "number" && typeof bValue === "number") {
        return sortOrder === "asc" ? aValue - bValue : bValue - aValue;
      }

      if (typeof aValue === "string" && typeof bValue === "string") {
        return sortOrder === "asc"
          ? aValue.localeCompare(bValue)
          : bValue.localeCompare(aValue);
      }

      return 0;
    });
  }

  // Pagination
  const startIndex = (page - 1) * limit;
  const paginated = result.slice(startIndex, startIndex + limit);

  return {
    total: result.length,
    page,
    limit,
    data: paginated,
  };
}