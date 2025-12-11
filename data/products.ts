// data/products.json
// Place your JSON array here (the data you provided)

// data/products.ts
import cablesData from './cables.json';
import fansData from './fans.json';
import lightingsData from './lightings.json';
import switchgearsData from './switchgears.json';
import switchesData from './switches.json';
import lkData from './lk_ea_products.json';
import wiresData from './wires.json';
import neptuneData from './neptune.json';
import dowellData from './dowell.json';
import { Product } from '@/types/common';

export const allProducts: Product[] = [...cablesData, ...fansData, ...lightingsData, ...switchgearsData, ...wiresData, ...switchesData, ...lkData, ...neptuneData, ...dowellData];
// export const allProducts: Product[] = [...dowellData];
export const cables: Product[] = cablesData;
export const fans: Product[] = fansData;
export const lightings: Product[] = lightingsData;
export const switchgears: Product[] = switchgearsData;
export const lk: Product[] = lkData;
export const neptune: Product[] = neptuneData;

