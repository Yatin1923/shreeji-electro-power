import Navbar from "@/components/navbar"
import { Hero } from "@/components/hero"
import { Clients } from "@/components/clients"
import { Products } from "@/components/products"
import { WhyChooseUs } from "@/components/why-choose-us"
import { Blogs } from "@/components/blogs"
import { Testimonials } from "@/components/testimonials"
import { Contact } from "@/components/contact"
import { SiteFooter } from "@/components/site-footer"

export default function Page() {
  return (
    <main className="bg-white">
      <Navbar active="Home" />
      <Hero />
      <Clients />
      <Products />
      <WhyChooseUs />
      <Blogs />
      <Testimonials />
      <Contact />
      <SiteFooter />
    </main>
  )
}
