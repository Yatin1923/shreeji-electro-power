// data/products.json
// Place your JSON array here (the data you provided)

// data/products.ts
import cablesData from './cables.json';
import fansData from './fans.json';
import lightingsData from './lightings.json';
import switchgearsData from './switchgear.json';
import wiresData from './wire.json';
import { Product } from '@/types/common';

export const allProducts: Product[] = [...cablesData, ...fansData, ...lightingsData, ...switchgearsData,...wiresData];
// export const allProducts: Product[] = [...wiresData];
export const cables: Product[] = cablesData;
export const fans: Product[] = fansData;
export const lightings: Product[] = lightingsData;
export const switchgears: Product[] = switchgearsData;

