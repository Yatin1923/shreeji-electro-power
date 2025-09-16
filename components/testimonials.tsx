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
  avatar: string
  rating: number
  title: string
  content: string
}

const testimonials: Testimonial[] = [
  {
    id: 1,
    name: "Leo",
    role: "Lead Designer",
    avatar: "/assets/testimonials/avatar1.png",
    rating: 5,
    title: "It was a very good experience",
    content:
      "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Curabitur varius, nunc nec turpis molestie, massa nibh iaculis.",
  },
  {
    id: 2,
    name: "Sophia",
    role: "Project Manager",
    avatar: "/assets/testimonials/avatar1.png",
    rating: 4,
    title: "Professional and reliable team",
    content:
      "The team delivered the project on time and exceeded our expectations. Communication was excellent throughout.",
  },
  {
    id: 3,
    name: "David",
    role: "CTO",
    avatar: "/assets/testimonials/avatar1.png",
    rating: 5,
    title: "Highly recommend them!",
    content:
      "From start to finish, everything went smoothly. The final product was top-notch, and support has been great.",
  },
  {
    id: 1,
    name: "Leo",
    role: "Lead Designer",
    avatar: "/assets/testimonials/avatar1.png",
    rating: 5,
    title: "It was a very good experience",
    content:
      "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Curabitur varius, nunc nec turpis molestie, massa nibh iaculis.",
  },
  {
    id: 2,
    name: "Sophia",
    role: "Project Manager",
    avatar: "/assets/testimonials/avatar1.png",
    rating: 4,
    title: "Professional and reliable team",
    content:
      "The team delivered the project on time and exceeded our expectations. Communication was excellent throughout.",
  },
  {
    id: 3,
    name: "David",
    role: "CTO",
    avatar: "/assets/testimonials/avatar1.png",
    rating: 5,
    title: "Highly recommend them!",
    content:
      "From start to finish, everything went smoothly. The final product was top-notch, and support has been great.",
  },
]

function TestimonialCard({ testimonial }: { testimonial: Testimonial }) {
  return (
    <div className="rounded-2xl border border-slate-200 bg-white p-8 shadow-md">
      <div className="flex items-center gap-4">
        <img src={testimonial.avatar} alt="Avatar" className="h-14 w-14 rounded-full" />
        <div>
          <div className="text-base font-semibold text-slate-900">{testimonial.name}</div>
          <div className="text-sm text-slate-500">{testimonial.role}</div>
        </div>
        <div className="ml-auto text-sm text-amber-500">
          {"★".repeat(testimonial.rating)}{"☆".repeat(5 - testimonial.rating)}
        </div>
      </div>
      <h3 className="mt-5 text-lg font-semibold text-slate-900">{testimonial.title}</h3>
      <p className="mt-3 text-base text-slate-600">{testimonial.content}</p>
    </div>
  )
}

export function Testimonials() {
  return (
    <section id="testimonials" className="bg-slate-50">
      <div className="mx-auto max-w-7xl px-6 py-16 relative">
        <Typography variant="h4" className="text-center text-2xl font-bold text-slate-900">
          What Our Clients Say About Us
        </Typography>

        <Swiper
          modules={[Pagination, Navigation, Autoplay]}
          pagination={{ clickable: true }}
          navigation
          autoplay={{
            delay: 3000,
            disableOnInteraction: false,
          }}
          loop
          spaceBetween={32}
          slidesPerView={1}
          breakpoints={{
            768: { slidesPerView: 2 },
            1024: { slidesPerView: 3 },
          }}
          className="mt-10"
        >
          {testimonials.map((t) => (
            <SwiperSlide key={t.id}>
              <TestimonialCard testimonial={t} />
            </SwiperSlide>
          ))}
        </Swiper>

      </div>
    </section>
  )
}
