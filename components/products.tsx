"use client"

import { Card, CardContent, Typography } from "@mui/material"

function ProductTile({ i }: { i: number }) {
  const companyLogos = [
    { src: "/assets/companyLogos/dowells.png", alt: "Dowell's" },
    { src: "/assets/companyLogos/hager.png", alt: "Hager" },
    { src: "/assets/companyLogos/neptune.png", alt: "Neptune" },
    { src: "/assets/companyLogos/cabseal.png", alt: "Cabseal" },
    { src: "/assets/companyLogos/lauritz-knudsen.png", alt: "Lauritz Knudsen" },
    { src: "/assets/companyLogos/polycab.png", alt: "Polycab" },
  ]

  const cardColors = [
    "#FCDFED", 
    "#F7DCD7",
    "#D9F2FB", 
    "#C8D3E7", 
    "#C7DBE6", 
    "#FBE0E0", 
  ]

  const logo = companyLogos[i % companyLogos.length]
  const backgroundColor = cardColors[i % cardColors.length]

  return (
    <Card elevation={12} className="!rounded-[20px] max-w-[220px] shadow-2xl" style={{ backgroundColor }}>
      <CardContent className="flex justify-center items-center min-h-[250px] ">
        <img src={logo.src || "/placeholder.svg"} alt={logo.alt} className="max-w-full max-h-80" />
      </CardContent>
    </Card>
  )
}

export function Products() {
  return (
    <section className="bg-slate-50">
      <div className="mx-auto container py-15">
        <Typography variant="h4" className="text-center text-lg font-semibold text-slate-900">Our Products</Typography>
        <div className="mt-15 grid grid-cols-2 gap-4 sm:grid-cols-3 md:grid-cols-6">
        {Array.from({ length: 6 }).map((_, i) => (
              <div key={i}>
                <ProductTile i={i} />
              </div>
            ))}
          {/* <ProductTile  />
          <ProductTile  />
          <ProductTile  />
          <ProductTile  />
          <ProductTile  />
          <ProductTile /> */}
        </div>
      </div>
    </section>
  )
}
