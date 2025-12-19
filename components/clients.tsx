"use client"

import { Box, Typography } from "@mui/material"
import { Swiper, SwiperSlide } from "swiper/react";
import { Autoplay } from "swiper/modules";
import "swiper/css";
import { motion } from "motion/react";
import { fadeInUp } from "./animations";
export function Clients() {
  return (
    <section className="bg-white">
      <div className="mx-auto container px-4 py-10 md:py-12">
        <motion.div className="text-center" variants={fadeInUp}
          initial="hidden"
          whileInView="show"
          custom={0.2} >
          <Typography variant="h4" typeof="h1" className="text-lg font-semibold text-slate-900">Our Clients</Typography>
          <p className="mt-1 text-sm text-slate-600">We have been working with 500+ clients</p>
        </motion.div>
        <motion.div variants={fadeInUp}
          initial="hidden"
          whileInView="show"
          custom={0.2} >
          <AutoCarousel></AutoCarousel>
        </motion.div>
      </div>
    </section>
  )



  function AutoCarousel() {
    const logosRow1 = Array.from({ length: 35 }, (_, i) => `/assets/ClientLogos/customer-company-${i + 1}.png`);
    const logosRow2 = Array.from({ length: 35 }, (_, i) => `/assets/ClientLogos/customer-company-${i + 36}.png`);

    return (
      <Box className="mt-10">
        <Swiper
          modules={[Autoplay]}
          spaceBetween={20}
          slidesPerView={8}  // show 5 logos at a time
          loop={true}
          freeMode={true}    // smooth infinite flow
          speed={3000}       // adjust for smoothness
          autoplay={{
            delay: 0,
            disableOnInteraction: false,
          }}
          breakpoints={{
            0: {
              slidesPerView: 4, // 👈 Mobile (default from 0px)
            },
            640: {
              slidesPerView: 6, // 👈 Tablet
            },
            1024: {
              slidesPerView: 8, // 👈 Desktop
            },
          }}     
        >
          {logosRow1.map((src, index) => (
            <SwiperSlide key={index}>
              <div className="flex justify-center items-center h-24">
                <img src={src} alt={`Customer Logo ${index + 1}`} className="h-full object-contain" />
              </div>
            </SwiperSlide>
          ))}
        </Swiper>
        <br />
        <Swiper
          modules={[Autoplay]}
          spaceBetween={20}
          slidesPerView={8}  // show 5 logos at a time
          loop={true}
          freeMode={true}    // smooth infinite flow
          speed={3000}       // adjust for smoothness
          autoplay={{
            delay: 0,
            reverseDirection: true,
            disableOnInteraction: false,
          }}
          breakpoints={{
            0: {
              slidesPerView: 4, // 👈 Mobile (default from 0px)
            },
            640: {
              slidesPerView: 6, // 👈 Tablet
            },
            1024: {
              slidesPerView: 8, // 👈 Desktop
            },
          }}        
        >
          {logosRow2.map((src, index) => (
            <SwiperSlide key={index}>
              <div className="flex justify-center items-center h-24">
                <img src={src} alt={`Customer Logo ${index + 1}`} className="h-full object-contain" />
              </div>
            </SwiperSlide>
          ))}
        </Swiper>
      </Box>

    );
  };


}
