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
  Collapse,
  useTheme,
  useMediaQuery,
  Drawer,
  Typography,
} from "@mui/material"
import SearchIcon from "@mui/icons-material/Search"
import FavoriteBorderIcon from "@mui/icons-material/FavoriteBorder"
import StarIcon from "@mui/icons-material/Star"
import KeyboardArrowLeftIcon from "@mui/icons-material/KeyboardArrowLeft"
import KeyboardArrowRightIcon from "@mui/icons-material/KeyboardArrowRight"
import SortIcon from "@mui/icons-material/Sort"
import React from "react"
import { Product } from "@/scripts/convert-excel-to-json"
import { getProducts } from "@/services/productService"

import ExpandMoreIcon from "@mui/icons-material/ExpandMore"
import ExpandLessIcon from "@mui/icons-material/ExpandLess"


// ⬇️ Import your product service

const brands = [
  "CABSEAL",
  "DOWELL'S",
  "HAGERS",
  "L&K SWITCHGEAR",
  "NEPTUNE",
  "POLYCAB",]
const categories = [
  "CABLES",
  "COMMUNICATION CABLES",
  "ENERGY CABLES",
  "SPECIAL CABLES",
  "CONDUITS & ACCESSORIES",
  "FANS",
  "HOME-SMARTAUTOMATION",
  "HOMEAPPLIANCE",
  "LIGHTS & LUMINARIES",
  "PUMP",
  "SOLAR",
  "SWITCHES",
  "SWITCHGEAR",
  "TELECOM",
  "WIRES",
  "SUMIP"
]


export default function ProductPage() {
  const [brandSel, setBrandSel] = React.useState<string[]>([])
  const [catSel, setCatSel] = React.useState<string[]>([])
  const [page, setPage] = React.useState(1)
  const [products, setProducts] = React.useState<Product[]>([])
  const [total, setTotal] = React.useState(0)

  const toggle = (v: string, list: string[], set: (v: string[]) => void) =>
    set(list.includes(v) ? list.filter((x) => x !== v) : [...list, v])
  const [brandOpen, setBrandOpen] = React.useState(true)
  const [catOpen, setCatOpen] = React.useState(true)
  const [mobileFiltersOpen, setMobileFiltersOpen] = React.useState(false)
  const theme = useTheme()
  const isMobile = useMediaQuery(theme.breakpoints.down("md"))

  const [searchQuery, setSearchQuery] = React.useState("")

  React.useEffect(() => {
    const res = getProducts({
      page,
      limit: 9,
      filters: {
        brand: brandSel.length ? brandSel : undefined,
        category: catSel.length ? catSel : undefined,
        search: searchQuery || undefined,
      },
      sortBy: "rating",
      sortOrder: "desc",
    })
    setProducts(res.data)
    setTotal(res.total)
  }, [page, brandSel, catSel,searchQuery])
  React.useEffect(() => {
    setPage(1)
  }, [brandSel, catSel])

  const totalPages = Math.ceil(total / 9)
  const filtersContent = (
    <div className="w-[260px] p-4">
      <div className="mb-3 flex items-center gap-2 text-neutral-700">
        <span className="text-[15px] font-semibold">Filters</span>
      </div>

      {/* Brand filter */}
      <div className="border-t pt-4">
        <div
          className="flex items-center justify-between cursor-pointer"
          onClick={() => setBrandOpen(!brandOpen)}
        >
          <span className="text-[13px] uppercase tracking-wide text-neutral-500">Brand</span>
          <IconButton size="small">
            {brandOpen ? <ExpandLessIcon fontSize="small" /> : <ExpandMoreIcon fontSize="small" />}
          </IconButton>
        </div>
        <Collapse in={brandOpen}>
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
        </Collapse>
      </div>

      {/* Category filter */}
      <div className="mt-6 border-t pt-4">
        <div
          className="flex items-center justify-between cursor-pointer"
          onClick={() => setCatOpen(!catOpen)}
        >
          <span className="text-[13px] uppercase tracking-wide text-neutral-500">Category</span>
          <IconButton size="small">
            {catOpen ? <ExpandLessIcon fontSize="small" /> : <ExpandMoreIcon fontSize="small" />}
          </IconButton>
        </div>
        <Collapse in={catOpen}>
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
        </Collapse>
      </div>
    </div>
  )


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
              onChange={(e) => setSearchQuery(e.target.value)}
            />
            <div className="flex flex-wrap gap-2">
              {brandSel.map((b) => (
                <Chip key={b} label={b} size="small" color="info" variant="outlined" />
              ))}
              {catSel.map((c) => (
                <Chip key={c} label={c} size="small" color="info" variant="outlined" />
              ))}
            </div>
            <div className="ml-auto flex gap-2">
              {/* Show Filters button only on mobile */}
              {isMobile && (
                <Button
                  variant="outlined"
                  size="small"
                  startIcon={<SortIcon />}
                  onClick={() => setMobileFiltersOpen(true)}
                >
                  Filters
                </Button>
              )}
              {/* <Button variant="outlined" size="small" startIcon={<SortIcon />}>
                Sort
              </Button> */}
            </div>
          </div>
        </div>

        {/* Main content: sidebar + grid */}
        <div className="mt-6 flex gap-6">
          {/* Sidebar */}
          {!isMobile && <aside>{filtersContent}</aside>}
          {/* <aside>
            <div className="mb-3 flex items-center gap-2 text-neutral-700">
              <svg width="18" height="18" viewBox="0 0 24 24" className="text-neutral-600">
                <path fill="currentColor" d="M3 5h18v2l-7 7v5l-4-2v-3L3 7z" />
              </svg>
              <span className="text-[15px] font-semibold">Filters</span>
            </div>
            <div className="border-t pt-4">
              <div className="flex items-center justify-between cursor-pointer" onClick={() => setBrandOpen(!brandOpen)}>
                <span className="text-[13px] uppercase tracking-wide text-neutral-500">Brand</span>
                <IconButton size="small">
                  {brandOpen ? <ExpandLessIcon fontSize="small" /> : <ExpandMoreIcon fontSize="small" />}
                </IconButton>
              </div>

              <Collapse in={brandOpen}>
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
              </Collapse>
            </div>

            <div className="mt-6 border-t pt-4">
              <div className="flex items-center justify-between cursor-pointer" onClick={() => setCatOpen(!catOpen)}>
                <span className="text-[13px] uppercase tracking-wide text-neutral-500">Category</span>
                <IconButton size="small">
                  {catOpen ? <ExpandLessIcon fontSize="small" /> : <ExpandMoreIcon fontSize="small" />}
                </IconButton>
              </div>

              <Collapse in={catOpen}>
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
              </Collapse>
            </div>

          </aside> */}

          {/* Product grid */}
          <section>
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
              {products.map((p) => {
                const primaryImg = p.images?.[0]
                return (
                  <Card key={p.id} elevation={0} className="rounded-xl border border-neutral-200 shadow-sm bg-white">
                    <div className="relative p-4">
                      <IconButton className="!absolute right-2 top-2" size="small" aria-label="favorite">
                        <FavoriteBorderIcon fontSize="small" />
                      </IconButton>
                      <Link href={`/product/${p.id}`} className="block">
                        <div className="mx-auto h-[180px] w-full overflow-hidden rounded-md bg-[#f4f6f8] flex items-center justify-center">
                          {/* eslint-disable-next-line @next/next/no-img-element */}
                          <img
                            src={primaryImg || "/placeholder.svg"}
                            alt={p.name}
                            className="h-[160px] w-auto object-contain"
                          />
                        </div>
                      </Link>
                    </div>
                    <CardContent className="pt-0">
                      <Link
                        href={`/product/${p.id}`}
                        className="text-[14px] font-semibold text-sky-700 hover:underline"
                      >
                        {p.name}
                      </Link>
                      <br />
                      <Typography variant={"caption"} className="text-neutral-400">{p.description}</Typography>
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

            {/* Pagination */}
            <div className="mt-8 flex items-center justify-between sticky bottom-0 bg-[#f5f8fb] py-4">
              {/* <Button
                variant="outlined"
                size="medium"
                endIcon={<KeyboardArrowRightIcon />}
                className="rounded-md normal-case"
                onClick={() => setPage((prev) => Math.min(prev + 1, totalPages))}
                disabled={page === totalPages}
              >
                Next page
              </Button> */}

              <div className="flex items-center gap-2">
                <Button
                  variant="outlined"
                  size="small"
                  className="!min-w-[42px] rounded-md normal-case bg-sky-600 text-white hover:bg-sky-700 hover:border-sky-700"
                >
                  {String(page).padStart(2, "0")}
                </Button>
                <span className="text-[13px] text-neutral-500">of {totalPages}</span>
                <Button
                  variant="outlined"
                  size="small"
                  className="rounded-md min-w-0"
                  aria-label="prev"
                  onClick={() => setPage((prev) => Math.max(prev - 1, 1))}
                  disabled={page === 1}
                >
                  <KeyboardArrowLeftIcon fontSize="small" />
                </Button>
                <Button
                  variant="outlined"
                  size="small"
                  className="rounded-md min-w-0"
                  aria-label="next"
                  onClick={() => setPage((prev) => Math.min(prev + 1, totalPages))}
                  disabled={page === totalPages}
                >
                  <KeyboardArrowRightIcon fontSize="small" />
                </Button>
              </div>
            </div>

            <div className="h-12" />
          </section>
        </div>
      </div>
       {/* Drawer for mobile filters */}
       <Drawer
        anchor="left"
        open={mobileFiltersOpen}
        onClose={() => setMobileFiltersOpen(false)}
      >
        {filtersContent}
      </Drawer>
    </main>
  )
}
