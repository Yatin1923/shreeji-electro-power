"use client"
import Link from "next/link"
import Navbar from "@/components/navbar"
import { getProductById, getRelated } from "@/services/productService"
import { Key } from "react"
import { Breadcrumbs } from "@mui/material"

export default function ProductDetailPage({ params }: { params: { id: number } }) {
  const product = getProductById(params.id)
  console.log(product)

  if (!product) {
    return (
      <main className="bg-slate-50">
        <Navbar active="Product" />
        <div className="mx-auto max-w-6xl px-6 py-12">
          <p className="text-sm text-gray-600">Product not found.</p>
          <Link href="/product" className="mt-2 inline-block text-sky-700 underline">
            Back to Products
          </Link>
        </div>
      </main>
    )
  }


  return (
    <main className="bg-slate-50">
      <Navbar active="Product" />

      {/* Breadcrumb */}
        <div className="mx-auto container px-6 py-3 text-xs text-gray-500">
        <div className="py-6">
            <Breadcrumbs separator="›" aria-label="breadcrumb" className="text-[13px] text-neutral-500">
              <Link href="/" className="hover:underline">
                Homepage
              </Link>
              <Link href="/product" className="hover:underline">
                Products
              </Link>
              <span className="">{product.name}</span>
            </Breadcrumbs>
        </div>

        {/* Top section */}
        <div className="grid grid-cols-1 items-start gap-8 md:grid-cols-2">
          {/* Left: main image with small controls and thumbs */}
          <div>
            <div className="relative overflow-hidden rounded-xl bg-white p-8 shadow-sm ring-1 ring-gray-200">
              {/* eslint-disable-next-line @next/next/no-img-element */}
              <img
                src={product.images[0] || "/placeholder.svg"}
                alt={product.name}
                className="mx-auto aspect-square w-full max-w-[460px] object-contain"
              />
              <div className="absolute left-3 top-3 flex flex-col gap-2">
                <button className="rounded-md bg-white/90 px-2 py-1 text-xs shadow-sm ring-1 ring-gray-200">⤴</button>
                <button className="rounded-md bg-white/90 px-2 py-1 text-xs shadow-sm ring-1 ring-gray-200">♥</button>
              </div>
              <div className="absolute right-3 top-1/2 -translate-y-1/2 space-y-2">
                <button className="rounded-md bg-white/90 px-2 py-1 text-xs shadow-sm ring-1 ring-gray-200">‹</button>
                <button className="rounded-md bg-white/90 px-2 py-1 text-xs shadow-sm ring-1 ring-gray-200">›</button>
              </div>
            </div>

            {/* Thumbnails */}
            <div className="mt-6 grid grid-cols-2 gap-4 sm:grid-cols-3">
              {product.images.slice(1).map((src: any, i: Key | null | undefined) => (
                <div key={i} className="overflow-hidden rounded-lg bg-white p-3 shadow-sm ring-1 ring-gray-200">
                  {/* eslint-disable-next-line @next/next/no-img-element */}
                  <img
                    src={src || "/placeholder.svg"}
                    className="mx-auto h-28 object-contain"
                  />
                </div>
              ))}
            </div>
          </div>

          {/* Right: details */}
          <div>
            <h1 className="text-3xl font-extrabold tracking-wide text-sky-700">{product.name}</h1>
            {/* <div className="mt-1 text-sm text-gray-500">1230mm Sweep • {product.specs.blades} Aluminium Blades</div> */}
            <div className="mt-2 flex items-center gap-2">
              <span className="text-xs text-gray-500">1,238 Sold</span>
              <span className="text-gray-300">•</span>
              <svg className="h-4 w-4 text-amber-500" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">
                <path d="M12 17.27L18.18 21 16.54 13.97 22 9.24l-7.19-.62L12 2 9.19 8.62 2 9.24l5.46 4.73L5.82 21z" />
              </svg>
              <span className="text-xs text-gray-700">{product.rating.toFixed(1)}</span>
            </div>

            <hr className="my-4 border-gray-200" />

            <h2 className="text-sm font-bold text-sky-700">Description:</h2>
            <p className="mt-2 text-sm leading-6 text-gray-700">
              {product.description}
            </p>

            {/* <div className="mt-6">
              <h3 className="text-sm font-bold text-sky-700">
                Color: <span className="font-semibold text-gray-800">Royal Brown</span>
              </h3>
              <div className="mt-3 flex items-center gap-3">
                {product.colorOptions.map((c, i) => (
                  <button
                    key={c.name}
                    className={`overflow-hidden rounded-md border p-1 ${
                      i === 1 ? "border-sky-600 ring-2 ring-sky-100" : "border-gray-200"
                    }`}
                    aria-label={c.name}
                  >
                    <img src={c.image || "/placeholder.svg"} alt={c.name} className="h-14 w-20 object-contain" />
                  </button>
                ))}
              </div>
            </div> */}

            <div className="mt-6">
              <h3 className="text-sm font-bold text-sky-700">Highlights:</h3>
              <ul className="mt-2 list-disc space-y-2 pl-5 text-sm text-gray-700">
                <li>1 Star Rated</li>
                <li>Timeless Design with Antique Finish</li>
                <li>Remote Controlled Operations</li>
                <li>100% Copper Winding Motor</li>
                <li>Premium Wooden Finish Blades</li>
              </ul>
            </div>

            <button className="mt-6 inline-flex items-center gap-2 rounded-md bg-gray-900 px-4 py-2 text-xs font-medium text-white shadow-sm">
              + Add to Wishlist
            </button>
          </div>
        </div>

        {/* Specifications */}
        <section className="mt-12">
          <h3 className="text-base font-bold text-sky-700">Specifications</h3>
          {/* <div className="mt-4 overflow-hidden rounded-xl bg-white shadow-sm ring-1 ring-gray-200">
            {(
              [
                ["BEE Star Rating", product.specs.beeStar],
                ["Sweep Size (mm)", product.specs.sweepMm],
                ["Number of Blades", product.specs.blades],
                ["Speed (RPM)", product.specs.rpm],
                ["Air Delivery (CMM)", product.specs.cmm],
                ["Power (Watt)", product.specs.powerW],
                ["Body Material", product.specs.body],
                ["Blade Material", product.specs.bladeMaterial],
                ["Motor Winding", product.specs.motor],
                ["Warranty", product.specs.warranty],
              ] as const
            ).map(([label, value], i) => (
              <div
                key={label}
                className={`grid grid-cols-[1fr,140px] items-center px-4 py-3 text-sm ${
                  i !== 0 ? "border-t border-gray-200" : ""
                }`}
              >
                <div className="text-gray-700">{label}</div>
                <div className="text-right text-gray-800">{value as any}</div>
              </div>
            ))}
          </div> */}
        </section>

        {/* Related Products */}
        <section className="mt-10">
          <div className="mb-4 flex items-center justify-between">
            <h3 className="text-base font-semibold text-sky-700">Related Products</h3>
            <Link href="/product" className="text-sm text-sky-700 hover:underline">
              View All
            </Link>
          </div>
          <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-4">
            {/* {related.map((rp) => (
              <Link
                key={rp.id}
                href={`/product/${rp.id}`}
                className="rounded-xl bg-white shadow-sm ring-1 ring-black/5"
              >
                <div className="px-4 pt-6">
                  <img
                    src={rp.images[0] || "/placeholder.svg"}
                    alt={rp.name}
                    className="mx-auto aspect-square w-full object-contain"
                  />
                </div>
                <div className="px-4 pb-4">
                  <div className="text-sm font-semibold text-sky-700">{rp.name}</div>
                  <div className="mt-2 flex items-center gap-1">
                    <svg className="h-4 w-4 text-amber-500" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">
                      <path d="M12 17.27L18.18 21 16.54 13.97 22 9.24l-7.19-.62L12 2 9.19 8.62 2 9.24l5.46 4.73L5.82 21z" />
                    </svg>
                    <span className="text-xs text-gray-700">{rp.rating.toFixed(1)}</span>
                    <span className="text-xs text-gray-400">({rp.reviews} Reviews)</span>
                  </div>
                </div>
              </Link>
            ))} */}
          </div>
        </section>
      </div>
    </main>
  )
}
