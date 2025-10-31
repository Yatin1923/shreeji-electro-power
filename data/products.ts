// data/products.json
// Place your JSON array here (the data you provided)

// data/products.ts
import cablesData from './cables.json';
import fansData from './fans.json';
import lightingsData from './lightings.json';
import { Product } from '@/types/common';

export const cables: Product[] = cablesData;
export const fans: Product[] = fansData;
export const lightings: Product[] = lightingsData;

