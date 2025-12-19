"use client"

import {
  createContext,
  useContext,
  useEffect,
  useState,
} from "react"
import { usePathname } from "next/navigation"
import { Product } from "@/types/common"
import { unifiedProductService } from "@/services/unified-product-service"

interface ProductContextType {
  selectedProduct: Product | null
  setSelectedProduct: (product: Product) => void
}

const ProductContext = createContext<ProductContextType | null>(null)

export function ProductProvider({ children }: { children: React.ReactNode }) {
  const [selectedProduct, setSelectedProduct] = useState<Product | null>(null)
  const pathname = usePathname()

  useEffect(() => {
    if (selectedProduct) return

    /**
     * Example path:
     * /product/Wire/Polycabprimma
     */
    const segments = pathname.split("/").filter(Boolean)

    const productName = segments[segments.length - 1]
    if (!productName) return

    const decodedName = decodeURIComponent(productName)

    const product = unifiedProductService.getProductByName(decodedName)

    if (product) {
      setSelectedProduct(product)
    }
  }, [pathname, selectedProduct])

  return (
    <ProductContext.Provider
      value={{ selectedProduct, setSelectedProduct }}
    >
      {children}
    </ProductContext.Provider>
  )
}

export function useProduct() {
  const context = useContext(ProductContext)
  if (!context) {
    throw new Error("useProduct must be used within ProductProvider")
  }
  return context
}
