// data/products.json
// Place your JSON array here (the data you provided)

// data/products.ts
import productsData from './products.json';
import { Product } from '../types/product';

export const products: Product[] = productsData;
