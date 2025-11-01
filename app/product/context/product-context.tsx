// app/product/context/product-context.tsx
"use client";

import { Product } from '@/types/common';
import { createContext, useContext, useState, useEffect, ReactNode } from 'react';

interface ProductContextType {
  selectedProduct: Product | null;
  setSelectedProduct: (product: Product | null) => void;
  isLoading: boolean;
}

const ProductContext = createContext<ProductContextType | undefined>(undefined);

interface ProductProviderProps {
  children: ReactNode;
}

export const ProductProvider: React.FC<ProductProviderProps> = ({ children }) => {
  const [selectedProduct, setSelectedProduct] = useState<Product | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  // Restore from sessionStorage on mount
  useEffect(() => {
    const stored = sessionStorage.getItem('selectedProduct');
    if (stored) {
      try {
        const product = JSON.parse(stored);
        setSelectedProduct(product);
      } catch (error) {
        console.error('Failed to parse stored product:', error);
        sessionStorage.removeItem('selectedProduct');
      }
    }
    setIsLoading(false);
  }, []);

  // Persist to sessionStorage whenever selectedProduct changes
  const handleSetSelectedProduct = (product: Product | null) => {
    setSelectedProduct(product);
    if (product) {
      sessionStorage.setItem('selectedProduct', JSON.stringify(product));
    } else {
      sessionStorage.removeItem('selectedProduct');
    }
  };

  return (
    <ProductContext.Provider value={{ 
      selectedProduct, 
      setSelectedProduct: handleSetSelectedProduct,
      isLoading 
    }}>
      {children}
    </ProductContext.Provider>
  );
};

export const useProduct = (): ProductContextType => {
  const context = useContext(ProductContext);
  if (context === undefined) {
    throw new Error('useProduct must be used within a ProductProvider');
  }
  return context;
};

export type { Product };
