"use client"

import Link from "next/link"
import type { Product } from "@/lib/products"
import FavoriteBorderOutlined from "@mui/icons-material/FavoriteBorderOutlined"
import Star from "@mui/icons-material/Star"
import { IconButton } from "@mui/material"

export function ProductCard({ product }: { product: Product }) {
  return (
    <div className="relative rounded-xl bg-white shadow-sm ring-1 ring-black/5">
      {/* Wishlist heart */}
      <IconButton size="small" aria-label="add to wishlist" className="!absolute right-2 top-2 !bg-white/90">
        <FavoriteBorderOutlined fontSize="small" />
      </IconButton>

      <Link href={`/product/${product.slug}`} className="block px-4 pt-6 pb-2">
        <div className="mx-auto aspect-square w-full overflow-hidden rounded-lg bg-gray-50">
          {/* eslint-disable-next-line @next/next/no-img-element */}
          <img
            src={product.images[0] || "/placeholder.svg"}
            alt={product.title}
            className="h-full w-full object-contain"
          />
        </div>
      </Link>

      <div className="px-4 pb-4">
        <Link href={`/product/${product.slug}`} className="text-sm font-semibold text-sky-700 hover:underline">
          {product.title}
        </Link>
        <p className="mt-1 text-[11px] leading-5 text-gray-600">{product.subtitle}</p>

        <div className="mt-2 flex items-center gap-1">
          <Star className="h-4 w-4 !text-amber-500" />
          <span className="text-xs text-gray-700">{product.rating.toFixed(1)}</span>
          <span className="text-xs text-gray-400">({product.reviews} Reviews)</span>
        </div>
      </div>
    </div>
  )
}
