"use client"
import { useState, useEffect } from "react" // Added React hooks for scroll detection
import AppBar from "@mui/material/AppBar"
import Toolbar from "@mui/material/Toolbar"
import Container from "@mui/material/Container"
import Stack from "@mui/material/Stack"
import Link from "@mui/material/Link"
import Typography from "@mui/material/Typography"
import { cn } from "@/lib/utils"
import NextLink from "next/link"

type NavItem = "Home" | "Blog" | "Product" | "Testimonial" | "Contact"

export interface NavbarProps {
  active?: NavItem
  onNavClick?: (item: NavItem) => void
}

const NAV_ITEMS: NavItem[] = ["Home", "Blog", "Product", "Testimonial", "Contact"]

export function Navbar({ active = "Home", onNavClick }: NavbarProps) {
  const [isScrolled, setIsScrolled] = useState(false)

  useEffect(() => {
    const handleScroll = () => {
      setIsScrolled(window.scrollY > 300)
    }

    window.addEventListener("scroll", handleScroll)
    return () => window.removeEventListener("scroll", handleScroll)
  }, [])

  return (
    <AppBar
      position={isScrolled ? "fixed" : "static"} // Conditionally apply fixed position based on scroll
      elevation={0}
      color=""
      className={cn(
        "bg-white shadow-md z-50", 
        "transition-all duration-200"
      )}
    >
      <Toolbar disableGutters className="min-h-[72px]">
        <Container maxWidth="xl" className="w-full">
          <div className="flex items-center justify-between gap-6 py-4">
            {/* Left: Logo + Brand */}
            <div className="flex items-center gap-4">
              <img
                src="https://hebbkx1anhila5yf.public.blob.vercel-storage.com/image-I8cISOWNnsD4QG4tvGcUiXZpBieyoy.png"
                alt="Shreeji Electro Power Pvt. Ltd. Logo"
                className="h-12 w-auto"
              />
            </div>

            {/* Right: Navigation */}
            <Stack direction="row" spacing={6} className="items-center">
              {NAV_ITEMS.map((item) => {
                const isActive = active === item
                const href =
                  item === "Home"
                    ? "/"
                    : item === "Blog"
                      ? "/#blogs"
                      : item === "Product"
                        ? "/product"
                        : item === "Testimonial"
                          ? "/#testimonials"
                          : "/#contact"
                return (
                  <Link
                    key={item}
                    component={NextLink}
                    href={href}
                    onClick={() => onNavClick?.(item)}
                    underline="none"
                    color="inherit"
                    aria-current={isActive ? "page" : undefined}
                    className={cn(
                      "text-lg transition-colors",
                      isActive ? "font-semibold text-slate-900" : "text-slate-700 hover:text-slate-900",
                    )}
                  >
                    {item}
                  </Link>
                )
              })}
            </Stack>
          </div>
        </Container>
      </Toolbar>
    </AppBar>
  )
}

export default Navbar
