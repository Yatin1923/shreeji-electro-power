"use client"

import { Card, CardContent, Link, Typography } from "@mui/material"
import { hover, motion } from "motion/react"
import { fadeInUp } from "./animations"

function ProductTile({ i }: { i: number }) {
  // const companyLogos = [
  //   { src: "/assets/companyLogos/dowells.png", alt: "Dowell's" },
  //   { src: "/assets/companyLogos/hager.png", alt: "Hager" },
  //   { src: "/assets/companyLogos/neptune.png", alt: "Neptune" },
  //   { src: "/assets/companyLogos/cabseal.png", alt: "Cabseal" },
  //   { src: "/assets/companyLogos/lauritz-knudsen.png", alt: "Lauritz Knudsen" },
  //   { src: "/assets/companyLogos/polycab.png", alt: "Polycab" },
  // ]
  const companyLogos = [
    { src: "/assets/companyLogos/polycab.png", alt: "Polycab",brand: "Polycab",backgroundColor:"#FBE0E0" },
    { src: "/assets/companyLogos/lauritz-knudsen.png", alt: "Lauritz Knudsen" ,brand: "L&K SWITCHGEAR",backgroundColor:"#C7DBE6" },
    { src: "/assets/companyLogos/neptune.png", alt: "Neptune",brand: "Neptune",backgroundColor:"#D9F2FB" },
    { src: "/assets/companyLogos/dowells.png", alt: "Dowell's",brand: "Dowell's",backgroundColor:"#FCDFED" },
    { src: "/assets/companyLogos/hager.png", alt: "Hager",brand: "Hagers",backgroundColor: "#F7DCD7"},
    { src: "/assets/companyLogos/cabseal.png", alt: "Cabseal",brand: "Cabseal",backgroundColor: "#C8D3E7"},
  ]
  // const cardColors = [
  //   "#FCDFED", 
  //   "#F7DCD7",
  //   "#D9F2FB", 
  //   "#C8D3E7", 
  //   "#C7DBE6", 
  //   "#FBE0E0", 
  // ]

  const logo = companyLogos[i % companyLogos.length]

  return (
    <Link href={`/product?brand=${encodeURIComponent(logo.brand.toUpperCase())}`}>
    <Card elevation={12} className="!rounded-[20px] cursor-pointer shadow-2xl w-full max-w-[220px] aspect-[220/250]" style={{ backgroundColor:logo.backgroundColor }}>
      <CardContent className="flex justify-center items-center h-full ">
        <img src={logo.src || "/placeholder.svg"} alt={logo.alt} className="max-w-full max-h-80" />
      </CardContent>
    </Card>
    </Link>
  )
}

export function Products() {
  const container = {
    hidden: { opacity: 0 },
    show: {
      opacity: 1,
      transition: {
        staggerChildren: 0.2, // delay between tiles
      },
    },
  };
  
  const item = {
    hidden: { opacity: 0, y: 40 },
    show: { opacity: 1, y: 0, transition: { duration: 0.5 } },
    hover: { scale: 1.5, transition: { duration: 0.3 } }
  };
  return (
    <section className="bg-slate-50">
      <div className="mx-auto container px-4 py-10 md:py-12">
      <motion.div className="text-center"  variants={fadeInUp}
      initial="hidden"
      whileInView="show"
      custom={0.2} >
        <Typography variant="h4" className="text-center text-lg font-semibold text-slate-900">Our Products</Typography>
      </motion.div>
        <motion.div  variants={container}
          initial="hidden"
          whileInView="show"
          className="mt-15 grid grid-cols-2 gap-4 sm:grid-cols-3 md:grid-cols-6 justify-items-center">
          {Array.from({ length: 6 }).map((_, i) => (
                <motion.div key={i} variants={item} whileHover={{scale: 1.1}} className="">
                  <ProductTile i={i} />
                </motion.div>
              ))}
        </motion.div>
      </div>
    </section>
  )
}
