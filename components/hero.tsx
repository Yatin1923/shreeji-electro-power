"use client"

import { Box, Button, Card, CardContent, Typography } from "@mui/material"
import { motion } from "motion/react"
function BrandTile({ i }: { i: number }) {
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
    <Card elevation={12} className="cursor-pointer !rounded-[20px] max-w-[220px] aspect-[220/250] shadow-2xl" style={{ backgroundColor }}>
      <CardContent className="flex justify-center items-center h-full">
        <img src={logo.src || "/placeholder.svg"} alt={logo.alt} className="max-w-full max-h-80" />
      </CardContent>
    </Card>
  )
}

export function Hero() {
  return (
    <section className="bg-slate-50 ">
      <Box className="container mx-auto min-h-[95vh] flex items-center px-4 py-10">
        <div className="xl:flex justify-center items-center h-full">
          {/* Left copy */}
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0, transition: { duration: 0.5 } }} className="flex flex-col justify-center gap-5">
            <Typography
              variant="h2"
              className="text-pretty font-extrabold !text-5xl leading-tight text-slate-900 md:!text-5xl lg:!text-6xl"
            >
              Tired of managing multiple vendors for electrical supply?
            </Typography>

            <Typography variant="h6" color="primary" className="max-w-pros">
              We bring India&apos;s top electrical brands under one roof — with seamless service and expert support.
            </Typography>

            <div className="mt-6 flex items-center gap-3">
              <Button variant="contained" href="#contact" className="!bg-sky-600 font-extrabold text-9xl !px-5 !py-2.5 !normal-case hover:!bg-sky-700">
                Contact us
              </Button>
              <Button
                variant="outlined"
                href="product"
                className="!border-slate-900 !text-slate-900 !px-4 !py-2.5 !normal-case hover:!bg-slate-900 hover:!text-white"
              >
                Our Products
              </Button>
            </div>

            {/* Stats */}
            <div className="mt-8 flex gap-5">
              {[
                { k: "20+", v: "Years of Expertise", img: "/assets/stats/experience.png" },
                { k: "500+", v: "Products", img: "/assets/stats/totalproducts.png" },
                { k: "3000+", v: "Clients Served", img: "/assets/stats/clientserved.png" },
              ].map((s, idx) => (
                <div key={s.k} className="flex items-center gap-3">
                  <div>
                    <img src={s.img} className="h-full !min-h-8 !max-h-12 w-full !min-w-8 !max-w-12 opacity-80" />
                  </div>
                  <div>
                    <Typography variant="h6" className="text-base font-bold text-slate-900">{s.k}</Typography>
                    <div className="text-slate-600">{s.v}</div>
                  </div>
                </div>
              ))}
            </div>
          </motion.div>

          {/* Right brand grid (staggered 2 x 3) */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0, transition: { duration: 0.5 } }}
            className="hidden xl:grid grid-cols-2 items-start gap-4 sm:gap-5 w-[50%]"
          >
            {Array.from({ length: 6 }).map((_, i) => {
              const isStaggered = i % 2 === 1 // cards with mt-8
              return (
                <motion.div
                  key={i}
                  className={isStaggered ? "mt-8" : ""}
                  // animate={{
                  //   y: isStaggered ? [0, 20, 0] : [0, -20, 0],
                  // }}
                  transition={{
                    duration: 4, // speed of float
                    repeat: Infinity,
                    repeatType: "mirror",
                    ease: "easeInOut",
                  }}
                >
                  <BrandTile i={i} />
                </motion.div>
              )
            })}
          </motion.div>

        </div>
      </Box>

    </section>
  )
}
