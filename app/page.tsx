"use client"
import Navbar from "@/components/navbar"
import { Hero } from "@/components/hero"
import { Clients } from "@/components/clients"
import { Products } from "@/components/products"
import { WhyChooseUs } from "@/components/why-choose-us"
import { Blogs } from "@/components/blogs"
import { Testimonials } from "@/components/testimonials"
import { Contact } from "@/components/contact"
import { SiteFooter } from "@/components/site-footer"
import { Providers } from "./app-theme"

export default function Page() {
  return (
      <main className="bg-white">
        <Navbar active="Home" />
        <Hero />
        <div className="xl:hidden">
          <Products />
          <Clients />
        </div>
        <div className="hidden xl:block">
          <Clients />
          <Products />
        </div>
        <WhyChooseUs />
        <Blogs />
        <Testimonials />
        <Contact />
        <SiteFooter />
      </main>
  )
}
