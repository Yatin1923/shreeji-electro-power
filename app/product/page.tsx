"use client"

import Navbar from "@/components/navbar"
import Link from "next/link"
import {
  Breadcrumbs,
  Chip,
  Button,
  TextField,
  InputAdornment,
  Checkbox,
  FormControlLabel,
  Card,
  CardContent,
  IconButton,
} from "@mui/material"
import SearchIcon from "@mui/icons-material/Search"
import FavoriteBorderIcon from "@mui/icons-material/FavoriteBorder"
import StarIcon from "@mui/icons-material/Star"
import KeyboardArrowLeftIcon from "@mui/icons-material/KeyboardArrowLeft"
import KeyboardArrowRightIcon from "@mui/icons-material/KeyboardArrowRight"
import SortIcon from "@mui/icons-material/Sort"
import React from "react"
import { products as productData } from "@/lib/products"

type Product = {
  id: number
  title: string
  model: string
  spec1: string
  spec2: string
  img: string
}

const brands = ["Dowell's", "Polycab", "Hager", "Cabcseal", "Lauritz Knudsen"]
const categories = [
  "Cables",
  "Home smart appliances",
  "Home appliances",
  "Lights",
  "Pump",
  "Solar",
  "Switches",
  "Switchgear",
  "Telecom",
  "Fans",
  "Conduits & Accessories",
  "Wires",
]

export default function ProductPage() {
  const [brandSel, setBrandSel] = React.useState<string[]>(["Polycab"])
  const [catSel, setCatSel] = React.useState<string[]>(["Fans"])
  const toggle = (v: string, list: string[], set: (v: string[]) => void) =>
    set(list.includes(v) ? list.filter((x) => x !== v) : [...list, v])

  return (
    <main className="bg-[#f5f8fb] min-h-screen">
      <Navbar active="Product" />

      <div className="mx-auto max-w-[1140px] px-6">
        {/* Breadcrumb row */}
        <div className="pt-6">
          <Breadcrumbs separator="›" aria-label="breadcrumb" className="text-[13px] text-neutral-500">
            <Link href="/" className="hover:underline">
              Homepage
            </Link>
            <span className="text-neutral-700">Products</span>
          </Breadcrumbs>
        </div>

        {/* Search, chips, sort */}
        <div className="mt-4 grid grid-cols-1 md:grid-cols-[280px_1fr] gap-6">
          <div className="hidden md:block" />
          <div className="flex flex-wrap items-center gap-4">
            <TextField
              size="small"
              placeholder="Search..."
              className="w-[260px] bg-white rounded-md"
              InputProps={{
                startAdornment: (
                  <InputAdornment position="start">
                    <SearchIcon fontSize="small" />
                  </InputAdornment>
                ),
              }}
            />
            <div className="flex flex-wrap gap-2">
              <Chip label="Polycab" size="small" color="info" variant="outlined" />
              <Chip label="Fans" size="small" color="info" variant="outlined" />
            </div>
            <div className="ml-auto">
              <Button variant="outlined" size="small" startIcon={<SortIcon />} className="rounded-md normal-case">
                Sort
              </Button>
            </div>
          </div>
        </div>

        {/* Main content: sidebar + grid */}
        <div className="mt-6 grid grid-cols-1 md:grid-cols-[280px_1fr] gap-6">
          {/* Sidebar */}
          <aside>
            <div className="mb-3 flex items-center gap-2 text-neutral-700">
              <svg width="18" height="18" viewBox="0 0 24 24" className="text-neutral-600">
                <path fill="currentColor" d="M3 5h18v2l-7 7v5l-4-2v-3L3 7z" />
              </svg>
              <span className="text-[15px] font-semibold">Filters</span>
            </div>

            <div className="border-t pt-4">
              <div className="flex items-center justify-between">
                <span className="text-[13px] uppercase tracking-wide text-neutral-500">Brand</span>
              </div>
              <div className="mt-2 flex flex-col">
                {brands.map((b) => (
                  <FormControlLabel
                    key={b}
                    control={
                      <Checkbox
                        size="small"
                        checked={brandSel.includes(b)}
                        onChange={() => toggle(b, brandSel, setBrandSel)}
                      />
                    }
                    label={<span className="text-[14px] text-neutral-700">{b}</span>}
                  />
                ))}
              </div>
            </div>

            <div className="mt-6 border-t pt-4">
              <div className="flex items-center justify-between">
                <span className="text-[13px] uppercase tracking-wide text-neutral-500">Category</span>
              </div>
              <div className="mt-2 flex flex-col">
                {categories.map((c) => (
                  <FormControlLabel
                    key={c}
                    control={
                      <Checkbox
                        size="small"
                        checked={catSel.includes(c)}
                        onChange={() => toggle(c, catSel, setCatSel)}
                      />
                    }
                    label={<span className="text-[14px] text-neutral-700">{c}</span>}
                  />
                ))}
              </div>
            </div>
          </aside>

          {/* Product grid */}
          <section>
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
              {productData.map((p) => {
                const parts = p.subtitle.split("•").map((s) => s.trim())
                const primaryImg = p.images?.[0] || "/diverse-products-still-life.png"
                return (
                  <Card key={p.id} elevation={0} className="rounded-xl border border-neutral-200 shadow-sm bg-white">
                    <div className="relative p-4">
                      <IconButton className="!absolute right-2 top-2" size="small" aria-label="favorite">
                        <FavoriteBorderIcon fontSize="small" />
                      </IconButton>
                      <Link href={`/product/${p.slug}`} className="block">
                        <div className="mx-auto h-[180px] w-full overflow-hidden rounded-md bg-[#f4f6f8] flex items-center justify-center">
                          {/* eslint-disable-next-line @next/next/no-img-element */}
                          <img
                            src={primaryImg || "/placeholder.svg"}
                            alt={p.title}
                            className="h-[160px] w-auto object-contain"
                          />
                        </div>
                      </Link>
                    </div>
                    <CardContent className="pt-0">
                      <Link
                        href={`/product/${p.slug}`}
                        className="text-[14px] font-semibold text-sky-700 hover:underline"
                      >
                        {p.title}
                      </Link>
                      <div className="mt-1 text-[11px] uppercase text-neutral-500">{parts[0]}</div>
                      <div className="mt-1 text-[11px] text-neutral-600">{parts[1]}</div>
                      <div className="text-[11px] text-neutral-600">{parts[2]}</div>
                      <div className="mt-2 flex items-center gap-1 text-[12px] text-neutral-600">
                        <StarIcon className="text-amber-400" fontSize="small" />
                        <span>{p.rating.toFixed(1)}</span>
                        <span className="text-neutral-400">({p.reviews} Reviews)</span>
                      </div>
                    </CardContent>
                  </Card>
                )
              })}
            </div>

            {/* Bottom controls */}
            <div className="mt-8 flex items-center justify-between">
              <Button
                variant="outlined"
                size="medium"
                endIcon={<KeyboardArrowRightIcon />}
                className="rounded-md normal-case"
              >
                Next page
              </Button>

              <div className="flex items-center gap-2">
                <Button
                  variant="outlined"
                  size="small"
                  className="!min-w-[42px] rounded-md normal-case bg-sky-600 text-white hover:bg-sky-700 hover:border-sky-700"
                >
                  01
                </Button>
                <span className="text-[13px] text-neutral-500">of 3</span>
                <Button variant="outlined" size="small" className="rounded-md min-w-0" aria-label="prev">
                  <KeyboardArrowLeftIcon fontSize="small" />
                </Button>
                <Button variant="outlined" size="small" className="rounded-md min-w-0" aria-label="next">
                  <KeyboardArrowRightIcon fontSize="small" />
                </Button>
              </div>
            </div>

            <div className="h-12" />
          </section>
        </div>
      </div>
    </main>
  )
}
