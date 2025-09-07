"use client"

import { Box, Typography } from "@mui/material"
import { Swiper, SwiperSlide } from "swiper/react";
import { Autoplay } from "swiper/modules";
import "swiper/css";
export function Clients() {
  return (
    <section className="bg-white">
      <div className="mx-auto container py-10 md:py-12">
        <div className="text-center">
          <Typography variant="h4" typeof="h1" className="text-lg font-semibold text-slate-900">Our Clients</Typography>
          <p className="mt-1 text-sm text-slate-600">We have been working with 500+ clients</p>
        </div>
        <AutoCarousel></AutoCarousel>
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
