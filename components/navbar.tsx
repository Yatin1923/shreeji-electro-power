"use client"
import { useState, useEffect } from "react"
import AppBar from "@mui/material/AppBar"
import Toolbar from "@mui/material/Toolbar"
import Container from "@mui/material/Container"
import Stack from "@mui/material/Stack"
import Link from "@mui/material/Link"
import IconButton from "@mui/material/IconButton"
import Drawer from "@mui/material/Drawer"
import List from "@mui/material/List"
import ListItem from "@mui/material/ListItem"
import ListItemButton from "@mui/material/ListItemButton"
import ListItemText from "@mui/material/ListItemText"
import MenuIcon from "@mui/icons-material/Menu"
import CloseIcon from "@mui/icons-material/Close"
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
  const [mobileOpen, setMobileOpen] = useState(false)

  useEffect(() => {
    const handleScroll = () => setIsScrolled(window.scrollY > 300)
    window.addEventListener("scroll", handleScroll)
    return () => window.removeEventListener("scroll", handleScroll)
  }, [])

  const toggleDrawer = (open: boolean) => () => setMobileOpen(open)

  return (
    <AppBar position="sticky" color="default">
      <Toolbar disableGutters className="min-h-[72px]">
        <Container maxWidth="xl" className="w-full">
          <div className="flex items-center justify-between gap-6 py-4">
            {/* Left: Logo */}
            <div className="flex items-center gap-4">
              <img src="/assets/logo.png" alt="Shreeji Electro Power Pvt. Ltd. Logo" className="h-12 w-auto" />
            </div>

            {/* Desktop Navigation */}
            <Stack direction="row" spacing={6} className="items-center md:!flex !hidden">
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

            {/* Mobile Menu Icon */}
            <IconButton
              edge="end"
              color="inherit"
              aria-label="menu"
              onClick={toggleDrawer(true)}
              className="md:!hidden"
            >
              <MenuIcon />
            </IconButton>
          </div>
        </Container>
      </Toolbar>

      {/* Mobile Drawer */}
      <Drawer anchor="right" open={mobileOpen} onClose={toggleDrawer(false)}>
        <div className="w-64 flex flex-col h-full">
          <div className="flex justify-between items-center p-4 border-b">
            <span className="font-semibold text-lg">Menu</span>
            <IconButton onClick={toggleDrawer(false)}>
              <CloseIcon />
            </IconButton>
          </div>
          <List>
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
                <ListItem key={item} disablePadding>
                  <ListItemButton
                    component={NextLink}
                    href={href}
                    onClick={() => {
                      onNavClick?.(item)
                      setMobileOpen(false)
                    }}
                  >
                    <ListItemText
                      primary={item}
                      primaryTypographyProps={{
                        className: cn(
                          "text-lg",
                          isActive ? "font-semibold text-slate-900" : "text-slate-700 hover:text-slate-900",
                        ),
                      }}
                    />
                  </ListItemButton>
                </ListItem>
              )
            })}
          </List>
        </div>
      </Drawer>
    </AppBar>
  )
}

export default Navbar
