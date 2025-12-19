"use client"

import { useEffect, useState } from "react"
import { Box, Button, Card, CardContent, Link, Typography, useMediaQuery, useTheme } from "@mui/material"
import { AnimatePresence, motion } from "motion/react"
import { log } from "console"

export function BrandTile({ i }: { i: number }) {
  const companyLogos = [
    { src: "/assets/companyLogos/polycab.png", alt: "Polycab", brand: "Polycab", backgroundColor: "#FBE0E0" },
    { src: "/assets/companyLogos/lauritz-knudsen.png", alt: "Lauritz Knudsen", brand: "Lauritz Knudsen", backgroundColor: "#C7DBE6" },
    { src: "/assets/companyLogos/neptune.png", alt: "Neptune", brand: "Neptune", backgroundColor: "#D9F2FB" },
    { src: "/assets/companyLogos/dowells.png", alt: "Dowell's", brand: "Dowell's", backgroundColor: "#FCDFED" },
    { alt: "Seppl Panel", brand: "Seppl", backgroundColor: "#F7DCD7" },
    { src: "/assets/companyLogos/cabseal.png", alt: "Cabseal", brand: "Cabseal", backgroundColor: "#C8D3E7" },
  ]

  const logo = companyLogos[i % companyLogos.length]

  return (
    <Link href={`/product?brand=${encodeURIComponent(logo.brand)}`} className="no-underline! text-inherit h-[100%]">
      <Card
        elevation={12}
        
        className="
        cursor-pointer opacity-90 !rounded-[20px] max-w-[220px] h-[100%] aspect-[220/250]"
        style={{ backgroundColor: logo.backgroundColor }}
      >
        <CardContent className="flex justify-center items-center h-full">
          {logo.src &&
            <img src={logo.src} alt={logo.alt} className="max-w-full max-h-80" />
          }
          {logo.brand === "Seppl" && (
            <div className="flex flex-col items-center justify-center scale-100 sm:scale-105">
            <span className="text-3xl sm:text-4xl lg:text-5xl font-black tracking-wide text-[#c23219]">
              SEPPL
            </span>
            <span className="text-xl sm:text-2xl lg:text-3xl font-black tracking-[0.35em] text-[#d8705e] mt-1 pl-[0.35em]">
              PANEL
            </span>
          </div>
          
          )}

        </CardContent>
      </Card>
    </Link>
  )
}

export function Hero() {
  const theme = useTheme()
  const isMobile = useMediaQuery(theme.breakpoints.down("md"))

  const heroSlides = !isMobile ? [
    {
      image: "assets/hero-bg2.jpg",
      title: "Tired of managing multiple vendors for electrical supply?",
      subtitle:
        "We bring India’s top electrical brands under one roof — with seamless service and expert support.",
      primaryCta: "Contact us",
      secondaryCta: "Our Products",
      theme: "light", // 👈 dark text
      overlay: "bg-black/40",
    },
    {
      image: "assets/hero-bg1.jpg",
      title: "Reliable electrical solutions for every project",
      subtitle:
        "From residential to industrial needs, we deliver quality products backed by trusted brands.",
      primaryCta: "Get a Quote",
      secondaryCta: "Browse Products",
      theme: "light",
      overlay: "bg-black/40",
    },
  ] :
    [
      {
        image: "assets/hero-bg2.jpg",
        title: "Tired of managing multiple vendors for electrical supply?",
        subtitle:
          "We bring India’s top electrical brands under one roof — with seamless service and expert support.",
        primaryCta: "Contact us",
        secondaryCta: "Our Products",
        theme: "dark", // 👈 dark text
        overlay: "bg-black/40",
      },
    ]

  const [bgIndex, setBgIndex] = useState(0)
  const currentSlide = heroSlides[bgIndex]
  const textColor =
    currentSlide.theme === "light" ? "text-white" : "text-slate-900"

  const subTextColor =
    currentSlide.theme === "light" ? "text-slate-200" : "text-slate-700"
  const primaryBtnClass =
    currentSlide.theme === "light"
      ? "!bg-sky-500 hover:!bg-sky-600"
      : "!bg-sky-600 hover:!bg-sky-700"

  const secondaryBtnClass =
    currentSlide.theme === "light"
      ? "!border-white !text-white hover:!bg-white hover:!text-slate-900"
      : "!border-slate-900 !text-slate-900 hover:!bg-slate-900 hover:!text-white"


  useEffect(() => {
    if (isMobile) return;
    const interval = setInterval(() => {
      setBgIndex((prev) => (prev + 1) % heroSlides.length)
    }, 5000)
    return () => clearInterval(interval)
  }, [isMobile])

  return (
    <section className="relative min-h-[95vh] overflow-hidden bg-slate-50">

      {!isMobile ?
        <>
          <AnimatePresence>
            <motion.div
              key={bgIndex}
              className="absolute inset-0 bg-cover bg-top pointer-events-none"
              style={{
                backgroundImage: `url(${heroSlides[bgIndex].image})`,
                // backgroundSize: "contain",
                // backgroundRepeat: "no-repeat",
                // backgroundSize: "100% 100%",
                zIndex: 0,
              }}
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              transition={{ duration: 1.2, ease: "easeInOut" }}
            />
          </AnimatePresence>


          {/* 🔹 OVERLAY */}
          <div
            className={`absolute inset-0 ${currentSlide.overlay} pointer-events-none`}
            style={{ zIndex: 1 }}
          />
        </>

        : null}

      {/* 🔹 CONTENT (STATIC) */}
      <Box
        className="relative container mx-auto min-h-[95vh] flex items-center"
        style={{ zIndex: 10 }}
      >
        <div className="flex justify-center items-center h-full">

          {/* LEFT CONTENT */}
          <motion.div
            key={bgIndex}
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 1.2, ease: "easeInOut" }}
            className="flex flex-col justify-center gap-5 w-[70%]"
          >
            <Typography
              variant="h2"
              className={`font-extrabold !text-3xl md:!text-5xl lg:!text-6xl ${textColor}`}
            >
              {heroSlides[bgIndex].title}
            </Typography>

            <Typography variant="h6" color="primary"
              className={`max-w-prose ${subTextColor}`}
            >
              {heroSlides[bgIndex].subtitle}
            </Typography>

            <div className="mt-6 flex flex-col sm:flex-row gap-3">
              <Button
                variant="contained"
                href="#contact"
                className={`
      ${primaryBtnClass}
      !text-sm sm:!text-base
      !px-4 sm:!px-6
      !py-2 sm:!py-3
      whitespace-nowrap
    `}
              >
                Contact us
              </Button>

              <Button
                variant="outlined"
                href="product"
                className={`
      ${secondaryBtnClass}
      !text-sm sm:!text-base
      !px-4 sm:!px-6
      !py-2 sm:!py-3
      whitespace-nowrap
    `}
              >
                Our Products
              </Button>
            </div>


            <div
              className="
              mt-8
              grid grid-cols-2 gap-4
              sm:flex sm:gap-6

            "
            >
              {[
                { k: "25+", v: "Years of Expertise", img: "/assets/stats/experience.png" },
                { k: "1500+", v: "Products", img: "/assets/stats/totalproducts.png" },
                { k: "4000+", v: "Clients Served", img: "/assets/stats/clientserved.png" },
              ].map((s, idx) => (
                <div
                  key={s.k}
                  className={`
        flex items-center gap-3 justify-center 
        ${idx === 2 ? "col-span-2 justify-center sm:col-span-1 sm:justify-start" : ""}
      `}
                >
                  {/* Icon */}
                  <img
                    src={s.img}
                    alt={s.v}
                    className="h-8 w-8 sm:h-10 sm:w-10 opacity-80 flex-shrink-0"
                  />

                  {/* Text */}
                  <div>
                    <Typography
                      variant="h6"
                      className={`text-base sm:text-lg font-bold ${textColor}`}
                    >
                      {s.k}
                    </Typography>
                    <div className={`text-sm sm:text-base ${subTextColor}`}>
                      {s.v}
                    </div>
                  </div>
                </div>
              ))}
            </div>

          </motion.div>

          {/* RIGHT GRID */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 1.2, ease: "easeInOut" }}
            className="hidden xl:grid grid-cols-2 gap-5 w-[30%]"
          >
            {Array.from({ length: 6 }).map((_, i) => (
              <BrandTile key={i} i={i} />
            ))}
          </motion.div>

        </div>
      </Box>
    </section>
  )
}
