// scripts/convert-excel-to-json.ts
import * as fs from "fs";
import * as XLSX from "xlsx";

export type Product = {
  id: number;
  name: string;
  category?: string;
  subcatergory?: string;
  images: string[];
  rating: number;
  reviews: number;
};

function main() {
  // 1. Load Excel file
  const workbook = XLSX.readFile("data/Shreeji Total Products.xlsx");
  const sheet = workbook.Sheets[workbook.SheetNames[0]];
  const rows = XLSX.utils.sheet_to_json<any>(sheet);

  // 2. Map Excel rows → Product objects
  console.log(rows);
  const products: Product[] = rows.map((row, i) => ({
    id: i + 1,
    name: row.Name,
    category: row.Categories,
    subcatergory:row.SubCategories,
    images:[],
    rating:Math.ceil(Math.random()*5),
    reviews:Math.floor(Math.random()*100)
  }));
console.log(products);
  // 3. Save to JSON file
  fs.writeFileSync("data/products.json", JSON.stringify(products, null, 2));
  console.log("✅ products.json generated!");
}

main();
