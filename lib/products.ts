// Basic in-memory product dataset used by the product list and detail pages.

import { Product } from "@/scripts/convert-excel-to-json"
import products from "@/data/products.json"
// export type Product = {
//   id: string
//   slug: string
//   title: string
//   subtitle: string
//   brand: string
//   category: string
//   specs: {
//     beeStar: number
//     sweepMm: number
//     blades: number
//     rpm: number
//     cmm: number
//     powerW: number
//     body: string
//     bladeMaterial: string
//     motor: string
//     warranty: string
//   }
//   rating: number
//   reviews: number
//   images: string[] // first is primary
//   colorOptions: { name: string; image: string }[]
// }

const img = (q: string, w = 480, h = 480) => `/placeholder.svg?height=${h}&width=${w}&query=${encodeURIComponent(q)}`

// export const products: Product[] = [
//   {
//     id: "p1",
//     slug: "superia-sp01",
//     title: "SUPERIA SP01",
//     subtitle: "1230MM SWEEP • 3 ALUMINIUM BLADES",
//     brand: "Polycab",
//     category: "Fans",
//     specs: {
//       beeStar: 1,
//       sweepMm: 1200,
//       blades: 3,
//       rpm: 340,
//       cmm: 210,
//       powerW: 50,
//       body: "Aluminium Body",
//       bladeMaterial: "Aluminium Blades",
//       motor: "100% Copper",
//       warranty: "2 Years Product Warranty",
//     },
//     rating: 5,
//     reviews: 0,
//     images: [img("ceiling fan bronze"), img("ceiling fan brown"), img("ceiling fan walnut"), img("ceiling fan white")],
//     colorOptions: [
//       { name: "Royal Brown", image: img("fan royal brown", 96, 64) },
//       { name: "Walnut", image: img("fan walnut", 96, 64) },
//       { name: "Pearl White", image: img("fan pearl white", 96, 64) },
//     ],
//   },
//   {
//     id: "p2",
//     slug: "superia-sp04-bldc",
//     title: "SUPERIA SP04 BLDC",
//     subtitle: "1230MM SWEEP • 5 PLASTIC BLADES • WALNUT WOOD",
//     brand: "Polycab",
//     category: "Fans",
//     specs: {
//       beeStar: 1,
//       sweepMm: 1200,
//       blades: 5,
//       rpm: 330,
//       cmm: 205,
//       powerW: 42,
//       body: "Aluminium Body",
//       bladeMaterial: "Plastic Blades",
//       motor: "100% Copper",
//       warranty: "2 Years Product Warranty",
//     },
//     rating: 5,
//     reviews: 0,
//     images: [img("bldc ceiling fan walnut"), img("bldc ceiling fan top")],
//     colorOptions: [
//       { name: "Walnut", image: img("bldc fan walnut", 96, 64) },
//       { name: "Bronze", image: img("bldc fan bronze", 96, 64) },
//     ],
//   },
//   {
//     id: "p3",
//     slug: "divina-ul5-bldc",
//     title: "DIVINA UL5 BLDC",
//     subtitle: "1230MM SWEEP • 5 PLASTIC BLADES • WALNUT WOOD",
//     brand: "Hager",
//     category: "Fans",
//     specs: {
//       beeStar: 1,
//       sweepMm: 1200,
//       blades: 5,
//       rpm: 335,
//       cmm: 208,
//       powerW: 45,
//       body: "Aluminium Body",
//       bladeMaterial: "Plastic Blades",
//       motor: "100% Copper",
//       warranty: "2 Years Product Warranty",
//     },
//     rating: 5,
//     reviews: 0,
//     images: [img("divina bldc walnut"), img("divina bldc white")],
//     colorOptions: [
//       { name: "Walnut", image: img("divina walnut", 96, 64) },
//       { name: "White", image: img("divina white", 96, 64) },
//     ],
//   },
//   {
//     id: "p4",
//     slug: "superia-sp06",
//     title: "SUPERIA SP06",
//     subtitle: "1230MM SWEEP • 5 PLASTIC BLADES • WALNUT WOOD",
//     brand: "Polycab",
//     category: "Fans",
//     specs: {
//       beeStar: 1,
//       sweepMm: 1200,
//       blades: 5,
//       rpm: 332,
//       cmm: 206,
//       powerW: 49,
//       body: "Aluminium Body",
//       bladeMaterial: "Plastic Blades",
//       motor: "100% Copper",
//       warranty: "2 Years Product Warranty",
//     },
//     rating: 5,
//     reviews: 0,
//     images: [img("superia sp06"), img("superia sp06 brown")],
//     colorOptions: [
//       { name: "Walnut", image: img("superia sp06 walnut", 96, 64) },
//       { name: "Bronze", image: img("superia sp06 bronze", 96, 64) },
//     ],
//   },
// ]

export function getProductById(id: number): Product| undefined{
  console.log("Fetching product with ID:", id);
  var product = products.find(p => p.id ==id);
  console.log("Available products:", product);
  return product;
}

export function getRelated(id: number, limit = 4): Product[]|undefined {
  return products.filter((p) => p.id !== id).slice(0, limit)
}
