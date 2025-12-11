"use client"

import { Typography } from "@mui/material"
import { Swiper, SwiperSlide } from "swiper/react"
import { Pagination, Navigation, Autoplay } from "swiper/modules"

// Import Swiper styles
import "swiper/css"
import "swiper/css/pagination"
import "swiper/css/navigation"

type Testimonial = {
  id: number
  name: string
  role: string
  avatar?: string
  rating: number
  title: string
  content: string
}
const testimonials: Testimonial[] = [
  {
    id: 1,
    name: "Parth Acharya",
    role: "Customer",
    // avatar: "/assets/testimonials/avatar1.png",
    rating: 5,
    title: "Supportive and quick response",
    content:
      "The sales team is extremely supportive and kind. I needed Polycab cables and their response was very quick. I definitely recommend Shreeji Electro Power for their professional and cooperative service."
  },
  {
    id: 2,
    name: "Deep Modi",
    role: "Customer",
    // avatar: "/assets/testimonials/avatar1.png",
    rating: 5,
    title: "High performance and excellent quality",
    content:
      "High-performance and efficient! I definitely recommend them. The product quality is consistently outstanding and always exceeds expectations. The staff is very helpful and customer-friendly."
  },
  {
    id: 3,
    name: "Darshan Patel",
    role: "Customer",
    // avatar: "/assets/testimonials/avatar1.png",
    rating: 4,
    title: "Good coordinating staff",
    content:
      "The coordinating staff is very good. They provided an instant reply and offered reasonable pricing. Great experience overall."
  },
  {
    id: 4,
    name: "Aatish Thakur",
    role: "Customer",
    // avatar: "/assets/testimonials/avatar1.png",
    rating: 5,
    title: "Best price and fast dispatch",
    content:
      "Good quality material with competitive pricing and very quick dispatch. Highly satisfied with their service and professionalism."
  }
];

function TestimonialCard({ testimonial }: { testimonial: Testimonial }) {
  return (
    <div className="rounded-2xl border border-slate-200 bg-white p-8 flex flex-col h-full min-h-[270px]">
      <div className="flex items-center gap-4">
        {testimonial.avatar && (
          <img
            src={testimonial.avatar}
            alt="Avatar"
            className="h-14 w-14 rounded-full"
          />
        )}
        <div>
          <div className="text-base font-semibold text-slate-900">
            {testimonial.name}
          </div>
          <div className="text-sm text-slate-500">{testimonial.role}</div>
        </div>
        <div className="ml-auto text-sm text-amber-500">
          {"★".repeat(testimonial.rating)}
          {"☆".repeat(5 - testimonial.rating)}
        </div>
      </div>

      <h3 className="mt-5 text-lg font-semibold text-slate-900">
        {testimonial.title}
      </h3>

      {/* flex-grow allows this text to stretch so all cards equalize */}
      <p className="mt-3 text-base text-slate-600 flex-grow">
        {testimonial.content}
      </p>
    </div>
  );
}



export function Testimonials() {
  return (
    <section id="testimonials" className="bg-slate-50 scroll-mt-32">
      <div className="mx-auto max-w-7xl px-6 py-16 relative">
        <Typography variant="h4" className="text-center text-2xl font-bold text-slate-900">
          What Our Clients Say About Us
        </Typography>

        <Swiper
          modules={[Pagination, Navigation, Autoplay]}
          pagination={{ clickable: true }}
          autoplay={{
            delay: 3000,
            disableOnInteraction: false,
          }}
          loop
          spaceBetween={32}
          slidesPerView={1}
          breakpoints={{
            768: { slidesPerView: 2, navigation: true },
            1024: { slidesPerView: 3, navigation: true },
          }}
          className="mt-10"
        >
          {testimonials.map((t) => (
            <SwiperSlide key={t.id} className="flex h-full">
              <TestimonialCard testimonial={t} />
            </SwiperSlide>

          ))}
        </Swiper>

      </div>
    </section>
  )
}
