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
import KeyboardArrowLeftIcon from "@mui/icons-material/KeyboardArrowLeft"
import KeyboardArrowRightIcon from "@mui/icons-material/KeyboardArrowRight"
import SortIcon from "@mui/icons-material/Sort"
import React from "react"
import ExpandMoreIcon from "@mui/icons-material/ExpandMore"
import ExpandLessIcon from "@mui/icons-material/ExpandLess"
import { useSearchParams } from "next/navigation"
import { Product } from "@/types/product"
import { polycabProductService } from '../../services/polycab-product-service';

const brands = [
  // "CABSEAL",
  // "DOWELL'S",
  // "HAGERS",
  // "L&K SWITCHGEAR",
  // "NEPTUNE",
  "POLYCAB",
]

// Enhanced categories with subcategories
const categoryStructure = {
  "CABLES": {
    subcategories: {
      'lv-power-cable': 'LV Power Cable',
      'mv-power-cable': 'MV Power Cable',
      'ehv-power-cable': 'EHV Power Cable',
      'instrumentation-cable': 'Instrumentation Cable',
      'communication-data-cable': 'Communication & Data Cable',
      'renewable-energy': 'Renewable Energy Cable',
      'control-cable': 'Control Cable',
      'fire-protection-cable': 'Fire Protection Cable',
      'industrial-cable': 'Industrial Cable',
      'rubber-cable': 'Rubber Cable',
      'marine-offshoreonshore-cable': 'Marine & Offshore/Onshore Cable',
      'high-temperature-cable': 'High Temperature Cable',
      'defence': 'Defence Cable',
      'domestic-appliance-and-lighting-cable': 'Domestic Appliance and Lighting Cable',
      'building-wires': 'Building Wires',
      'special-cable': 'Special Cable',
      'aerial-bunched-cable': 'Aerial Bunched Cable',
    }
  },
  // "COMMUNICATION CABLES": {},
  // "ENERGY CABLES": {},
  // "SPECIAL CABLES": {},
  // "CONDUITS & ACCESSORIES": {},
  // "FANS": {},
  // "HOME-SMARTAUTOMATION": {},
  // "HOMEAPPLIANCE": {},
  // "LIGHTS & LUMINARIES": {},
  // "PUMP": {},
  // "SOLAR": {},
  // "SWITCHES": {},
  // "SWITCHGEAR": {},
  // "TELECOM": {},
  // "WIRES": {},
  // "SUMIP": {}
}

const ITEMS_PER_PAGE = 9;

export default function ProductPage() {
  const searchParams = useSearchParams()
  const initialBrand = searchParams.get("brand")

  const [brandSel, setBrandSel] = React.useState<string[]>(initialBrand ? [initialBrand] : [])
  const [catSel, setCatSel] = React.useState<string[]>([])
  const [cableSubcatSel, setCableSubcatSel] = React.useState<string[]>([])
  const [page, setPage] = React.useState(1)
  const [products, setProducts] = React.useState<Product[]>([])
  const [total, setTotal] = React.useState(0)
  const [loading, setLoading] = React.useState(false)

  const toggle = (v: string, list: string[], set: (v: string[]) => void) =>
    set(list.includes(v) ? list.filter((x) => x !== v) : [...list, v])

  const [brandOpen, setBrandOpen] = React.useState(true)
  const [catOpen, setCatOpen] = React.useState(true)
  const [cablesSubOpen, setCablesSubOpen] = React.useState(false)
  const [mobileFiltersOpen, setMobileFiltersOpen] = React.useState(false)
  const theme = useTheme()
  const isMobile = useMediaQuery(theme.breakpoints.down("md"))

  const [searchQuery, setSearchQuery] = React.useState("")
  const [searchDebounce, setSearchDebounce] = React.useState("")

  // Debounce search query
  React.useEffect(() => {
    const timer = setTimeout(() => {
      setSearchDebounce(searchQuery)
    }, 300)
    return () => clearTimeout(timer)
  }, [searchQuery])

  // Function to map cable subcategory to product matching
  const matchesCableSubcategory = (product: Product, subcategoryKey: string): boolean => {
    const subcategoryName = categoryStructure.CABLES.subcategories[subcategoryKey as keyof typeof categoryStructure.CABLES.subcategories]
    const productName = product.Cable_Name.toLowerCase()
    const productType = product.Product_Type.toLowerCase()
    const shortDesc = product.Short_Description.toLowerCase()

    switch (subcategoryKey) {
      case 'lv-power-cable':
        return productType.toLowerCase().includes('lv power')
      case 'mv-power-cable':
        return productType.toLowerCase().includes('mv power')
      case 'ehv-power-cable':
        return productType.toLowerCase().includes('ehv power')
      case 'instrumentation-cable':
        return productType.toLowerCase().includes('instrumentation cable')
      case 'communication-data-cable':
        return productType.includes('communication & data')
      case 'renewable-energy':
        return productType.includes('renewable energy')
      case 'control-cable':
        return productType.includes('control') || shortDesc.includes('control')
      case 'fire-protection-cable':
        return productType.includes('fire') || shortDesc.includes('fire') ||
          productType.includes('frls') || shortDesc.includes('frls')
      case 'industrial-cable':
        return productType.includes('industrial') || shortDesc.includes('industrial')
      case 'rubber-cable':
        return productType.includes('rubber') || shortDesc.includes('rubber')
      case 'marine-offshoreonshore-cable':
        return productType.includes('marine') || productType.includes('offshore') ||
          shortDesc.includes('marine') || shortDesc.includes('offshore')
      case 'high-temperature-cable':
        return productType.includes('high temp') || shortDesc.includes('high temp') ||
          productType.includes('temperature') || shortDesc.includes('temperature')
      case 'defence':
        return productType.includes('defence') || productType.includes('defense') ||
          shortDesc.includes('defence') || shortDesc.includes('defense')
      case 'domestic-appliance-and-lighting-cable':
        return productType.includes('appliance') || productType.includes('lighting') ||
          shortDesc.includes('appliance') || shortDesc.includes('lighting')
      case 'building-wires':
        return productType.includes('building') || productType.includes('wire') ||
          shortDesc.includes('building') || shortDesc.includes('wire')
      case 'special-cable':
        return productType.includes('special') || shortDesc.includes('special')
      case 'aerial-bunched-cable':
        return productType.includes('aerial') || productType.includes('bunched') ||
          shortDesc.includes('aerial') || shortDesc.includes('bunched')
      default:
        return false
    }
  }

  // Enhanced product loading with subcategory filtering
  const loadProductsEnhanced = React.useCallback(async () => {
    setLoading(true)
    try {
      const allProducts = polycabProductService.getAllProducts()
      let filteredProducts = [...allProducts]
      // Apply search filter
      if (searchDebounce) {
        const searchTerm = searchDebounce.toLowerCase()
        filteredProducts = filteredProducts.filter(product =>
          product.Cable_Name.toLowerCase().includes(searchTerm) ||
          product.Short_Description.toLowerCase().includes(searchTerm) ||
          product.Full_Description.toLowerCase().includes(searchTerm) ||
          product.Key_Features.toLowerCase().includes(searchTerm) ||
          product.Standards.toLowerCase().includes(searchTerm)
        )
      }

      // Apply brand filter
      if (brandSel.length > 0) {
        filteredProducts = filteredProducts.filter(product =>
          brandSel.some(brand =>
            product.Brand.toUpperCase().includes(brand.toUpperCase())
          )
        )
      }

      // Apply main category filter
      if (catSel.length > 0) {
        filteredProducts = filteredProducts.filter(product =>
          catSel.some(category => product.Type.toUpperCase().includes(category.toUpperCase()) )
        )
      }

      // Apply cable subcategory filter
      if (cableSubcatSel.length > 0) {
        filteredProducts = filteredProducts.filter(product =>
          cableSubcatSel.some(subcatKey => matchesCableSubcategory(product, subcatKey))
        )
      }

      // Apply pagination
      const startIndex = (page - 1) * ITEMS_PER_PAGE
      const endIndex = startIndex + ITEMS_PER_PAGE
      const paginatedProducts = filteredProducts.slice(startIndex, endIndex)

      setProducts(paginatedProducts)
      setTotal(filteredProducts.length)
    } catch (error) {
      console.error('Error loading products:', error)
    } finally {
      setLoading(false)
    }
  }, [page, brandSel, catSel, cableSubcatSel, searchDebounce])

  React.useEffect(() => {
    loadProductsEnhanced()
  }, [loadProductsEnhanced])

  // Reset to page 1 when filters change
  React.useEffect(() => {
    setPage(1)
  }, [brandSel, catSel, cableSubcatSel, searchDebounce])
  const handleSubcategoryToggle = (subcategoryKey: string) => {
    const newSelection = cableSubcatSel.includes(subcategoryKey)
      ? cableSubcatSel.filter(item => item !== subcategoryKey)
      : [...cableSubcatSel, subcategoryKey];
    
    setCableSubcatSel(newSelection);
    
    // Auto-select parent category if any subcategory is selected
    if (newSelection.length > 0 && !catSel.includes("CABLES")) {
      setCatSel([...catSel, "CABLES"]);
    }
    // Auto-deselect parent if no subcategories are selected
    else if (newSelection.length === 0 && catSel.includes("CABLES")) {
      setCatSel(catSel.filter(cat => cat !== "CABLES"));
    }
  };
  
  const handleCategoryToggle = (category: string) => {
    if (category === "CABLES") {
      const isCurrentlySelected = catSel.includes(category);
      const allSubcategories = Object.keys(categoryStructure.CABLES?.subcategories || {});
      const hasAllSubcategories = cableSubcatSel.length === allSubcategories.length;
      
      if (isCurrentlySelected && hasAllSubcategories) {
        // If fully selected, deselect everything
        setCatSel(catSel.filter(cat => cat !== category));
        setCableSubcatSel([]);
      } else {
        // If not selected or partially selected, select everything
        setCatSel([...catSel.filter(cat => cat !== category), category]);
        setCableSubcatSel(allSubcategories);
      }
    } else {
      // Handle other categories normally
      setCatSel(catSel.includes(category) 
        ? catSel.filter(cat => cat !== category)
        : [...catSel, category]
      );
    }
  };
  
  const getCablesCheckboxState = () => {
    const allSubcategories = Object.keys(categoryStructure.CABLES?.subcategories || {});
    const selectedCount = cableSubcatSel.length;
    const totalCount = allSubcategories.length;
    
    return {
      checked: selectedCount > 0 && selectedCount === totalCount,
      indeterminate: selectedCount > 0 && selectedCount < totalCount
    };
  };

  const totalPages = Math.ceil(total / ITEMS_PER_PAGE)

  // Get all selected filter labels for chips
  const getAllSelectedFilters = () => {
    const filters: { type: string; value: string; label: string }[] = []

    // Add brand filters
    brandSel.forEach(brand => filters.push({ type: 'brand', value: brand, label: brand }))

    // Add main category filters
    catSel.forEach(cat => filters.push({ type: 'category', value: cat, label: cat }))

    // Add cable subcategory filters
    cableSubcatSel.forEach(subcat => {
      const label = categoryStructure.CABLES.subcategories[subcat as keyof typeof categoryStructure.CABLES.subcategories]
      filters.push({ type: 'cableSubcategory', value: subcat, label })
    })

    return filters
  }

  const removeFilter = (filterType: string, value: string) => {
    switch (filterType) {
      case 'brand':
        toggle(value, brandSel, setBrandSel)
        break
      case 'category':
        handleCategoryToggle(value)
        break
      case 'cableSubcategory':
        toggle(value, cableSubcatSel, setCableSubcatSel)
        break
    }
  }

  const filtersContent = (
    <div className="w-[280px] p-4 bg-white rounded-lg h-fit sticky top-6">
      <div className="mb-3 flex items-center justify-between gap-2 text-neutral-700">
        <span className="p-2! text-[15px] font-semibold">Filters</span>
        {(brandSel.length > 0 || catSel.length > 0 || cableSubcatSel.length > 0) && (
          <Button
            size="small"
            onClick={() => {
              setBrandSel([])
              setCatSel([])
              setCableSubcatSel([])
            }}
            className="ml-auto text-xs p-2!"
          >
            Clear All
          </Button>
        )}
      </div>

      {/* Brand filter */}
      <div className="border-t pt-4">
        <div
          className="flex items-center justify-between cursor-pointer"
          onClick={() => setBrandOpen(!brandOpen)}
        >
          <span className="text-[13px] uppercase tracking-wide text-neutral-500">
            Brand {brandSel.length > 0 && `(${brandSel.length})`}
          </span>
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

      {/* Category filter with subcategories */}
      <div className="mt-6 border-t pt-4">
        <div
          className="flex items-center justify-between cursor-pointer!"
          onClick={() => setCatOpen(!catOpen)}
        >
          <span className="text-[13px] uppercase tracking-wide text-neutral-500">
            Category {(catSel.length > 0 || cableSubcatSel.length > 0) && `(${catSel.length + cableSubcatSel.length})`}
          </span>
          <IconButton size="small">
            {catOpen ? <ExpandLessIcon fontSize="small" /> : <ExpandMoreIcon fontSize="small" />}
          </IconButton>
        </div>
        <Collapse in={catOpen}>
          <div className="mt-2 flex flex-col ju">
            {Object.keys(categoryStructure).map((category) => (
              <div key={category} className="">
                <div className="flex items-center justify-between">
                  <FormControlLabel
                    control={
                      <Checkbox
                        size="small"
                        checked={category === "CABLES" ? getCablesCheckboxState().checked || catSel.includes(category) : catSel.includes(category)}
                        indeterminate={category === "CABLES" ? getCablesCheckboxState().indeterminate : false}
                        onChange={() => handleCategoryToggle(category)}
                      />
                    }
                    label={
                      <div className="w-full">
                        <span className="text-[14px] text-neutral-700 flex justify-between">{category}</span>
                      </div>
                    }
                  />
                  {category === "CABLES" && Object.keys(categoryStructure.CABLES.subcategories).length > 0 && (
                    <IconButton
                      size="small"
                      onClick={(e) => {
                        e.stopPropagation()
                        setCablesSubOpen(!cablesSubOpen)
                      }}
                    >
                      {cablesSubOpen ? <ExpandLessIcon fontSize="small" /> : <ExpandMoreIcon fontSize="small" />}
                    </IconButton>
                  )}
                </div>

                {/* Cable subcategories */}
                {category === "CABLES" && (
                  <Collapse in={cablesSubOpen}>
                    <div className="ml-8 mt-1 flex flex-col">
                      {Object.entries(categoryStructure.CABLES.subcategories).map(([key, label]) => (
                        <FormControlLabel
                          key={key}
                          control={
                            <Checkbox
                              size="small"
                              checked={cableSubcatSel.includes(key)}
                              onChange={() => {toggle(key, cableSubcatSel, setCableSubcatSel); handleSubcategoryToggle(key)}}
                            />
                          }
                          label={<span className="text-[13px] text-neutral-600">{label}</span>}
                        />
                      ))}
                    </div>
                  </Collapse>
                )}
              </div>
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

        {/* Main layout: Fixed sidebar + Content area */}
        <div className="mt-6 flex gap-6 min-h-[calc(100vh-200px)]">
          {/* Fixed Sidebar */}
          {!isMobile && (
            <aside className="flex-shrink-0">
              {filtersContent}
            </aside>
          )}

          {/* Main Content Area */}
          <div className="flex-1 min-w-0">
            {/* Search, chips, sort */}
            <div className="flex flex-wrap items-center gap-4 mb-4">
              <TextField
                size="small"
                placeholder="Search..."
                value={searchQuery}
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
                {getAllSelectedFilters().map((filter, index) => (
                  <Chip
                    key={`${filter.type}-${filter.value}-${index}`}
                    label={filter.label}
                    size="small"
                    color="info"
                    variant="outlined"
                    onDelete={() => removeFilter(filter.type, filter.value)}
                  />
                ))}
              </div>
              <div className="ml-auto flex gap-2">
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
              </div>
            </div>

            {/* Results summary */}
            <div className="text-sm text-neutral-600 mb-6">
              {loading ? 'Loading...' : `Showing ${products.length} of ${total} results`}
              {(searchDebounce || brandSel.length > 0 || catSel.length > 0 || cableSubcatSel.length > 0) && (
                <span className="ml-2">
                  {searchDebounce && `for "${searchDebounce}"`}
                  {(brandSel.length > 0 || catSel.length > 0 || cableSubcatSel.length > 0) && ' (filtered)'}
                </span>
              )}
            </div>

            {/* Product grid */}
            <section>
              {loading ? (
                <div className="flex justify-center items-center h-64">
                  <div className="text-neutral-500">Loading products...</div>
                </div>
              ) : products.length === 0 ? (
                <div className="text-center py-12">
                  <div className="text-neutral-500 mb-2">No products found</div>
                  <Button
                    onClick={() => {
                      setSearchQuery('')
                      setBrandSel([])
                      setCatSel([])
                      setCableSubcatSel([])
                    }}
                  >
                    Clear filters
                  </Button>
                </div>
              ) : (
                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
                  {products.map((p) => {
                    const primaryImg = p.Image_Path
                    return (
                      <Card key={p.Cable_Name} elevation={0} className="rounded-xl border border-neutral-200 shadow-sm bg-white">
                        <div className="relative p-4">
                          <Link href={`/product/${encodeURIComponent(p.Cable_Name)}`} className="block">
                            <div className="mx-auto h-[180px] w-full overflow-hidden rounded-md bg-[#f4f6f8] flex items-center justify-center">
                              <img
                                src={primaryImg || "/placeholder.svg"}
                                alt={p.Cable_Name}
                                className="h-[160px] w-auto object-contain"
                              />
                            </div>
                          </Link>
                        </div>
                        <CardContent className="pt-0">
                          <Link
                            href={`/product/${encodeURIComponent(p.Cable_Name)}`}
                            className="text-[14px] font-semibold text-sky-700 hover:underline"
                          >
                            {p.Cable_Name}
                          </Link>
                          <br />
                          <Typography variant={"caption"} className="text-neutral-400">
                            {p.Short_Description}
                          </Typography>
                        </CardContent>
                      </Card>
                    )
                  })}
                </div>
              )}

              {/* Pagination */}
              {totalPages > 1 && (
                <div className="mt-8 flex items-center justify-between sticky bottom-0 bg-[#f5f8fb] py-4">
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
                      disabled={page === 1 || loading}
                    >
                      <KeyboardArrowLeftIcon fontSize="small" />
                    </Button>
                    <Button
                      variant="outlined"
                      size="small"
                      className="rounded-md min-w-0"
                      aria-label="next"
                      onClick={() => setPage((prev) => Math.min(prev + 1, totalPages))}
                      disabled={page === totalPages || loading}
                    >
                      <KeyboardArrowRightIcon fontSize="small" />
                    </Button>
                  </div>
                  <div className="text-sm text-neutral-500">
                    Showing {((page - 1) * ITEMS_PER_PAGE) + 1} to {Math.min(page * ITEMS_PER_PAGE, total)} of {total}
                  </div>
                </div>
              )}

              <div className="h-12" />
            </section>
          </div>
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
