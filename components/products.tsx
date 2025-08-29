"use client"

import { Card, CardContent } from "@mui/material"

function ProductTile({ name, tint }: { name: string; tint: string }) {
  return (
    <Card elevation={1} className="rounded-xl">
      <CardContent className={`p-6 ${tint}`}>
        <img
          src={"/placeholder.svg?height=40&width=160&query=product%20brand%20logo"}
          alt={`${name} logo`}
          className="mx-auto h-10 w-full object-contain"
        />
      </CardContent>
    </Card>
  )
}

export function Products() {
  return (
    <section className="bg-slate-50">
      <div className="mx-auto max-w-6xl px-6 py-10 md:py-12">
        <h2 className="text-center text-lg font-semibold text-slate-900">Our Products</h2>
        <div className="mt-6 grid grid-cols-2 gap-4 sm:grid-cols-3 md:grid-cols-6">
          <ProductTile name="POLYCAB" tint="bg-rose-50" />
          <ProductTile name="hager" tint="bg-sky-50" />
          <ProductTile name="Lauritz" tint="bg-slate-50" />
          <ProductTile name="Cabelseal" tint="bg-rose-50" />
          <ProductTile name="NEPTUNE" tint="bg-slate-50" />
          <ProductTile name="dowell's" tint="bg-rose-50" />
        </div>
      </div>
    </section>
  )
}
