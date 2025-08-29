"use client"
import AppBar from "@mui/material/AppBar"
import Toolbar from "@mui/material/Toolbar"
import Container from "@mui/material/Container"
import Stack from "@mui/material/Stack"
import Link from "@mui/material/Link"
import Typography from "@mui/material/Typography"
import Box from "@mui/material/Box"
import { cn } from "@/lib/utils"
import NextLink from "next/link"

type NavItem = "Home" | "Blog" | "Product" | "Testimonial" | "Contact"

export interface NavbarProps {
  active?: NavItem
  onNavClick?: (item: NavItem) => void
}

const NAV_ITEMS: NavItem[] = ["Home", "Blog", "Product", "Testimonial", "Contact"]

export function Navbar({ active = "Home", onNavClick }: NavbarProps) {
  return (
    <AppBar position="static" elevation={0} color="transparent" className="bg-slate-50">
      <Toolbar disableGutters className="min-h-[72px]">
        <Container maxWidth="xl" className="w-full">
          <div className="flex items-center justify-between gap-6 py-4">
            {/* Left: Logo + Brand */}
            <div className="flex items-center gap-4">
              {/* You can replace this box with your own logo.
                 If you'd like to embed the provided reference image directly, use the Source URL below.
                 <img src="https://hebbkx1anhila5yf.public.blob.vercel-storage.com/image-TDMQfkRUF7nTvHf8ArvlOQCS5DZOUR.png" alt="Brand logo" className="h-10 w-auto" /> */}
              <Box
                aria-hidden
                className="flex h-10 w-10 items-center justify-center rounded-full border-2 border-[#00a0da]/70"
              >
                <div className="h-6 w-6 rounded-full bg-slate-300" />
              </Box>
              <Typography
                component="span"
                className={cn("text-pretty text-xl font-extrabold uppercase tracking-wide", "text-[#008bd1]")}
              >
                SHREEJI ELECTRO POWER PVT. LTD.
              </Typography>
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
