// scripts/convert-excel-to-json.ts
import * as fs from "fs";
import * as XLSX from "xlsx";

export type Product = {
  id: number;
  name: string;
  brand?: string;
  category?: string;
  description?:string;
  images: string[];
  rating: number;
  reviews: number;
};
export type EhvCable = {
  id: number;
  name: string;
  brand: string;
  category: string;
  productType: string;
  voltageRating: string;
  conductorMaterial: string;
  conductorType: string;
  sheathType: string;
  maxVoltage: number;
  standards: string;
  keyFeatures: string;
  shortDescription: string;
  fullDescription: string;
  images: string[];
  rating: number;
  reviews: number;
}


function main() {
  // 1. Load Excel file
  // const workbook = XLSX.readFile("data/Shreeji Total Products.xlsx");
  const workbook = XLSX.readFile("data/Polycab/Cables/EHV Power Cables/data.xlsx");
  const sheet = workbook.Sheets[workbook.SheetNames[0]];
  const rows = XLSX.utils.sheet_to_json<any>(sheet);

  // 2. Map Excel rows → Product objects
  console.log(rows);
  const products: Product[] = rows.map((row, i) => ({
    id: i + 1,
    name: row.Name,
    brand: row.Brand,
    category:row.Category,
    description:row.ShortDescription,
    images:[],
    rating:Math.ceil(Math.random()*5),
    reviews:Math.floor(Math.random()*100)
  }));
  const ehvCables: EhvCable[] = rows.map((row, i) => ({
    id: i + 1,
    name: row.Cable_Name || '',
    brand: 'Polycab', 
    category: 'EHV Power Cables', 
    productType: row.Product_Type || '',
    voltageRating: row.Voltage_Rating || '',
    conductorMaterial: row.Conductor_Material || '',
    conductorType: row.Conductor_Type || '',
    sheathType: row.Sheath_Type || '',
    maxVoltage: parseFloat(row['Max_Voltage_(kV)']) || 0,
    standards: row.Standards || '',
    keyFeatures: row.Key_Features || '',
    shortDescription: row.Short_Description || '',
    fullDescription: row.Full_Description || '',
    images: row.Image_Url ? [row.Image_Url] : [],
    rating: Math.ceil(Math.random() * 5),
    reviews: Math.floor(Math.random() * 100)
  }));
console.log(ehvCables);
  // 3. Save to JSON file
  fs.writeFileSync("data/products.json", JSON.stringify(ehvCables, null, 2));
  console.log("✅ products.json generated!");
}

main();
