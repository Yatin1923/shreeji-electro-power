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
import { unifiedProductService } from "@/services/unified-product-service"
import { Product } from "@/types/common"
import { BRANDS, BRAND_CATEGORIES, CABLE_SUBCATEGORIES, FAN_SUBCATEGORIES, LIGHTING_SUBCATEGORIES, SWITCH_SUBCATEGORIES, SWITCHGEAR_SUBCATEGORIES, MEDIUM_VOLTAGE_SUBCATEGORIES, LV_IEC_PANELS_SUBCATEGORIES, POWER_DISTRIBUTION_PRODUCTS_SUBCATEGORIES, MOTOR_MANAGEMENT_CONTROL_SUBCATEGORIES, INDUSTRIAL_AUTOMATION_CONTROL_SUBCATEGORIES, ENERGY_MANAGEMENT_PRODUCTS_SUBCATEGORIES, MCB_RCCB_DISTRIBUTION_BOARDS_SUBCATEGORIES, SWITCHES_ACCESSORIES_SUBCATEGORIES, PUMP_STARTERS_CONTROLLERS_SUBCATEGORIES, INDUSTRIAL_SIGNALLING_PRODUCTS } from "@/constants/polycab"
import { motion, AnimatePresence, Variants } from "framer-motion"
import { useProduct } from "./context/product-context"

// Add this before your component or in a separate file
const cardVariants: Variants = {
  hidden: {
    opacity: 0,
    y: 15,     // Reduced distance for faster travel
    scale: 0.98 // Less scale change for subtlety
  },
  visible: {
    opacity: 1,
    y: 0,
    scale: 1,
    transition: {
      type: "spring" as const,
      stiffness: 400,  // Very fast spring
      damping: 25      // Quick settle
    }
  },
  exit: {
    opacity: 0,
    y: -5,       // Reduced exit distance
    scale: 0.98,
    transition: {
      duration: 0.1  // Very fast exit
    }
  }
}

const containerVariants: Variants = {
  hidden: {
    opacity: 0
  },
  visible: {
    opacity: 1,
    transition: {
      staggerChildren: 0.03,  // Very fast stagger
      delayChildren: 0.02     // Almost immediate start
    }
  },
  exit: {
    opacity: 0,
    transition: {
      staggerChildren: 0.02,
      staggerDirection: -1
    }
  }
}


// Simplified category structure using just values
const categoryStructure = {
  "Cable": {
    subcategories: CABLE_SUBCATEGORIES
  },
  "Fan": {
    subcategories: FAN_SUBCATEGORIES
  },
  "Lighting": {
    subcategories: LIGHTING_SUBCATEGORIES
  },
  "Switchgear": {
    subcategories: SWITCHGEAR_SUBCATEGORIES
  },
  "Switch": {
    subcategories: SWITCH_SUBCATEGORIES
  },
  "Wire": {
    subcategories: null
  },
  "Industrial Signalling Products": {
    subcategories: INDUSTRIAL_SIGNALLING_PRODUCTS
  },
  "Pump Starters & Controllers": {
    subcategories: PUMP_STARTERS_CONTROLLERS_SUBCATEGORIES
  },
  "Motor Management & Control": {
    subcategories: MOTOR_MANAGEMENT_CONTROL_SUBCATEGORIES
  },
  "Industrial Automation & Control": {
    subcategories: INDUSTRIAL_AUTOMATION_CONTROL_SUBCATEGORIES
  },
  "Energy Management Products": {
    subcategories: ENERGY_MANAGEMENT_PRODUCTS_SUBCATEGORIES
  },
  "MCB, RCCB & Distribution Boards": {
    subcategories: MCB_RCCB_DISTRIBUTION_BOARDS_SUBCATEGORIES
  },
  "Power Distribution Products": {
    subcategories: POWER_DISTRIBUTION_PRODUCTS_SUBCATEGORIES
  },
  "Medium Voltage": {
    subcategories: MEDIUM_VOLTAGE_SUBCATEGORIES
  },
  "LV IEC Panels": {
    subcategories: LV_IEC_PANELS_SUBCATEGORIES
  },
  "Industrial Automation": {
    subcategories: INDUSTRIAL_AUTOMATION_CONTROL_SUBCATEGORIES
  },
  "Industrial Plug & Sockets": {
    subcategories: null
  },
  "LV Switchboards": {
    subcategories: null
  },
  "Metering System": {
    subcategories: null
  },
  "PF Correction": {
    subcategories: null
  },
  "Power Quality": {
    subcategories: null
  }
};


const ITEMS_PER_PAGE = 12;

export default function ProductPage() {
  const searchParams = useSearchParams()
  const initialBrand = searchParams.get("brand")

  const [brandSel, setBrandSel] = React.useState<string[]>(initialBrand ? [initialBrand] : [])
  const [catSel, setCatSel] = React.useState<string[]>([])
  const [subcategorySel, setSubcategorySel] = React.useState<Record<string, string[]>>({})
  const [page, setPage] = React.useState(1)
  const [products, setProducts] = React.useState<Product[]>([])
  const [total, setTotal] = React.useState(0)
  const [loading, setLoading] = React.useState(false)

  const toggle = (v: string, list: string[], set: (v: string[]) => void) =>
    set(list.includes(v) ? list.filter((x) => x !== v) : [...list, v])

  const [brandOpen, setBrandOpen] = React.useState(true)
  const [catOpen, setCatOpen] = React.useState(true)
  const [subcategoryOpen, setSubcategoryOpen] = React.useState<Record<string, boolean>>({})
  const [mobileFiltersOpen, setMobileFiltersOpen] = React.useState(false)
  const theme = useTheme()
  const isMobile = useMediaQuery(theme.breakpoints.down("md"))

  const [searchQuery, setSearchQuery] = React.useState("")
  const [searchDebounce, setSearchDebounce] = React.useState("")
  const [isEditingPage, setIsEditingPage] = React.useState(false);
  const [tempPage, setTempPage] = React.useState(page.toString());

  const [isRestored, setIsRestored] = React.useState(false)

  // Load state from sessionStorage on mount
  React.useEffect(() => {
    // If there's an initial brand from URL (e.g. from Home page), don't load from storage
    if (initialBrand) {
      setIsRestored(true)
      return
    }

    const savedState = sessionStorage.getItem('productPageFilters')
    if (savedState) {
      try {
        const parsed = JSON.parse(savedState)
        setBrandSel(parsed.brandSel || [])
        setCatSel(parsed.catSel || [])
        setSubcategorySel(parsed.subcategorySel || {})
        setPage(parsed.page || 1)
        if (parsed.searchQuery) {
          setSearchQuery(parsed.searchQuery)
          setSearchDebounce(parsed.searchQuery)
        }
      } catch (e) {
        console.error('Failed to parse saved filters', e)
      }
    }
    setIsRestored(true)
  }, [initialBrand])

  // Save state to sessionStorage whenever it changes
  React.useEffect(() => {
    if (!isRestored) return

    const stateToSave = {
      brandSel,
      catSel,
      subcategorySel,
      page,
      searchQuery: searchDebounce
    }
    sessionStorage.setItem('productPageFilters', JSON.stringify(stateToSave))
  }, [brandSel, catSel, subcategorySel, page, searchDebounce, isRestored])

  // Debounce search query
  React.useEffect(() => {
    const timer = setTimeout(() => {
      setSearchDebounce(searchQuery)
    }, 300)
    return () => clearTimeout(timer)
  }, [searchQuery])

  // Simplified function to match subcategories using display names
  const matchesSubcategory = (product: Product, category: string, subcategoryValue: string): boolean => {
    const productType = product.Product_Type.toLowerCase()
    const subcategoryLower = subcategoryValue.toLowerCase()
    if (productType === subcategoryLower) {
      return true
    }
    return false
  }

  // Enhanced product loading with subcategory filtering
  const loadProductsEnhanced = React.useCallback(async () => {
    setLoading(true)
    try {
      const allProducts = unifiedProductService.getAllProducts();
      let filteredProducts = [...allProducts]

      // Apply search filter
      if (searchDebounce) {
        const searchTerm = searchDebounce.toLowerCase()
        filteredProducts = filteredProducts.filter(product =>
          product.Name.toLowerCase().includes(searchTerm) ||
          product.Short_Description?.toLowerCase().includes(searchTerm) ||
          // product.Full_Description?.toLowerCase().includes(searchTerm) ||
          product.Key_Features?.toLowerCase().includes(searchTerm) ||
          product.Standards?.toLowerCase().includes(searchTerm)
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
          catSel.some(category => product.Type.toUpperCase().includes(category.toUpperCase()))
        )
      }

      // Apply subcategory filters with proper handling for categories without subcategories
      const hasSubcategoryFilters = Object.values(subcategorySel).some(
        arr => arr.length > 0
      )
      
      if (hasSubcategoryFilters) {
        filteredProducts = filteredProducts.filter(product => {
          const productCategory = product.Type?.toLowerCase()
          if (!productCategory) return false
      
          // Find matching category key from categoryStructure (case-insensitive)
          const categoryKey = Object.keys(categoryStructure).find(
            key => key.toLowerCase() === productCategory
          )
      
          const categoryHasSubcategories =
            categoryKey &&
            Array.isArray(categoryStructure[categoryKey as keyof typeof categoryStructure].subcategories) &&
            categoryStructure[categoryKey as keyof typeof categoryStructure].subcategories!.length > 0
      
          // Category has NO subcategories
          if (!categoryHasSubcategories) {
            return (
              catSel.length === 0 ||
              catSel.some(category =>
                productCategory.includes(category.toLowerCase())
              )
            )
          }
      
          // Category HAS subcategories
          return Object.entries(subcategorySel).some(
            ([category, selectedSubcats]) => {
              if (selectedSubcats.length === 0) return false
              if (productCategory !== category.toLowerCase()) return false
      
              return selectedSubcats.some(subcatValue =>
                matchesSubcategory(product, category, subcatValue)
              )
            }
          )
        })
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
  }, [page, brandSel, catSel, subcategorySel, searchDebounce])

  React.useEffect(() => {
    loadProductsEnhanced()
  }, [loadProductsEnhanced])

  // Reset to page 1 when filters change - REMOVED
  // Instead, we call setPage(1) in the handlers

  // Simplified subcategory toggle function using values
  const handleSubcategoryToggle = (category: string, subcategoryValue: string) => {
    const currentSubcats = subcategorySel[category] || []
    const newSubcats = currentSubcats.includes(subcategoryValue)
      ? currentSubcats.filter(item => item !== subcategoryValue)
      : [...currentSubcats, subcategoryValue]

    setSubcategorySel(prev => ({
      ...prev,
      [category]: newSubcats
    }))

    // Auto-select parent category if any subcategory is selected
    if (newSubcats.length > 0 && !catSel.includes(category)) {
      setCatSel([...catSel, category])
    }
    // Auto-deselect parent if no subcategories are selected
    else if (newSubcats.length === 0 && catSel.includes(category)) {
      setCatSel(catSel.filter(cat => cat !== category))
    }
    setPage(1)
  }
  const handlePageChange = (newPage: number) => {
    setPage(newPage);
  }
  // Simplified category toggle function
  const handleCategoryToggle = (category: string) => {
    const categoryConfig = categoryStructure[category as keyof typeof categoryStructure]

    if (categoryConfig?.subcategories) {
      const isCurrentlySelected = catSel.includes(category)
      const allSubcategories = [...categoryConfig.subcategories]
      const currentSubcats = subcategorySel[category] || []
      const hasAllSubcategories = currentSubcats.length === allSubcategories.length

      if (isCurrentlySelected && hasAllSubcategories) {
        // If fully selected, deselect everything
        setCatSel(catSel.filter(cat => cat !== category))
        setSubcategorySel(prev => ({
          ...prev,
          [category]: []
        }))
      } else {
        // If not selected or partially selected, select everything
        setCatSel([...catSel.filter(cat => cat !== category), category])
        setSubcategorySel(prev => ({
          ...prev,
          [category]: allSubcategories
        }))
      }
    } else {
      // Handle categories without subcategories normally
      setCatSel(catSel.includes(category)
        ? catSel.filter(cat => cat !== category)
        : [...catSel, category]
      )
    }
    setPage(1)
  }

  // Simplified checkbox state function
  const getCategoryCheckboxState = (category: string) => {
    const categoryConfig = categoryStructure[category as keyof typeof categoryStructure]

    if (!categoryConfig?.subcategories) {
      return { checked: catSel.includes(category), indeterminate: false }
    }

    const allSubcategories = [...categoryConfig.subcategories]
    const selectedSubcats = subcategorySel[category] || []
    const selectedCount = selectedSubcats.length
    const totalCount = allSubcategories.length

    return {
      checked: selectedCount > 0 && selectedCount === totalCount,
      indeterminate: selectedCount > 0 && selectedCount < totalCount
    }
  }

  // Toggle subcategory section open/closed
  const toggleSubcategoryOpen = (category: string) => {
    setSubcategoryOpen(prev => ({
      ...prev,
      [category]: !prev[category]
    }))
  }

  const totalPages = Math.ceil(total / ITEMS_PER_PAGE)

  // Get all selected filter labels for chips
  const getAllSelectedFilters = () => {
    const filters: { type: string; value: string; label: string; category?: string }[] = []

    // Add brand filters
    brandSel.forEach(brand => filters.push({ type: 'brand', value: brand, label: brand }))

    // Add main category filters
    catSel.forEach(cat => filters.push({ type: 'category', value: cat, label: cat }))

    // Add subcategory filters - simplified since value = label
    Object.entries(subcategorySel).forEach(([category, subcats]) => {
      subcats.forEach(subcat => {
        filters.push({ type: 'subcategory', value: subcat, label: subcat, category })
      })
    })

    return filters
  }

  const removeFilter = (filterType: string, value: string, category?: string) => {
    switch (filterType) {
      case 'brand':
        toggle(value, brandSel, setBrandSel)
        break
      case 'category':
        setCatSel(catSel.filter(cat => cat !== value))
        setSubcategorySel(prev => ({
          ...prev,
          ...prev,
          [value]: []
        }))
        setPage(1)
        break
      case 'subcategory':
        if (category) {
          handleSubcategoryToggle(category, value)
        }
        break
    }
  }
  const { setSelectedProduct } = useProduct();

  const handleProductClick = async (p: Product) => {
    try {
      setSelectedProduct(p);
    } catch (error) {
    }
  };

  const visibleCategories = React.useMemo(() => {
    if (brandSel.length === 0) return [];
  
    const allowedCategories = new Set<string>();
  
    brandSel.forEach(brand => {
      const categories = BRAND_CATEGORIES[brand.toUpperCase()];
      if (categories) {
        categories.forEach(cat =>
          allowedCategories.add(cat.toLowerCase())
        );
      }
    });
  
    return Object.keys(categoryStructure).filter(
      cat => allowedCategories.has(cat.toLowerCase())
    );
  }, [brandSel]);
  

  // Effect to clean up selected categories when available categories change
  React.useEffect(() => {
    if (!isRestored) return

    // If no brands are selected, clear all categories
    if (brandSel.length === 0) {
      if (catSel.length > 0 || Object.keys(subcategorySel).length > 0) {
        setCatSel([])
        setSubcategorySel({})
        setPage(1)
      }
      return
    }

    // Filter out categories that are no longer visible
    const newCatSel = catSel.filter(cat => visibleCategories.includes(cat))

    // Check if changes are needed
    if (newCatSel.length !== catSel.length) {
      setCatSel(newCatSel)

      // Clean up subcategories for removed categories
      const newSubcategorySel = { ...subcategorySel }
      let subcatChanged = false

      Object.keys(subcategorySel).forEach(cat => {
        if (!newCatSel.includes(cat)) {
          delete newSubcategorySel[cat]
          subcatChanged = true
        }
      })

      if (subcatChanged) {
        setSubcategorySel(newSubcategorySel)
      }
      setPage(1)
    }
  }, [visibleCategories, brandSel, isRestored, catSel, subcategorySel])

  const filtersContent = (
    <div className="w-[380px] p-4 bg-white rounded-lg h-fit sticky top-25">
      <div className="max-h-[80vh] overflow-auto">

        <div className="mb-3 flex items-center justify-between gap-2 text-neutral-700">
          <span className="p-2! text-[15px] font-semibold">Filters</span>
          {(brandSel.length > 0 || catSel.length > 0 || Object.values(subcategorySel).some(arr => arr.length > 0)) && (
            <Button
              size="small"
              onClick={() => {
                setBrandSel([])
                setCatSel([])
                setSubcategorySel({})
                setPage(1)
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
              {Object.entries(BRANDS).map(([key, value]) => (
                <FormControlLabel
                  key={key}
                  control={
                    <Checkbox
                      size="small"
                      checked={brandSel.includes(value)}
                      onChange={() => {
                        toggle(value, brandSel, setBrandSel)
                        setPage(1)
                      }}
                    />
                  }
                  label={<span className="text-[14px] text-neutral-700">{key}</span>}
                />
              ))}
            </div>
          </Collapse>
        </div>

        {/* Category filter with subcategories - simplified */}
        <AnimatePresence>
          {brandSel.length > 0 && visibleCategories.length>0 && (
            <motion.div
              initial={{ height: 0, opacity: 0 }}
              animate={{ height: "auto", opacity: 1 }}
              exit={{ height: 0, opacity: 0 }}
              className="overflow-hidden"
            >
              <div className="mt-6 border-t pt-4">
                <div
                  className="flex items-center justify-between cursor-pointer!"
                  onClick={() => setCatOpen(!catOpen)}
                >
                  <span className="text-[13px] uppercase tracking-wide text-neutral-500">
                    Category {(catSel.length > 0 || Object.values(subcategorySel).some(arr => arr.length > 0)) &&
                      `(${catSel.length + Object.values(subcategorySel).reduce((acc, arr) => acc + arr.length, 0)})`}
                  </span>
                  <IconButton size="small">
                    {catOpen ? <ExpandLessIcon fontSize="small" /> : <ExpandMoreIcon fontSize="small" />}
                  </IconButton>
                </div>
                <Collapse in={catOpen}>
                  <div className="mt-2 flex flex-col">
                    <AnimatePresence mode="popLayout">
                      {visibleCategories.map((category) => {
                        const categoryConfig = categoryStructure[category as keyof typeof categoryStructure]
                        const checkboxState = getCategoryCheckboxState(category)

                        return (
                          <motion.div
                            key={category}
                            initial={{ opacity: 0, height: 0 }}
                            animate={{ opacity: 1, height: "auto" }}
                            exit={{ opacity: 0, height: 0 }}
                            transition={{ duration: 0.2 }}
                            className="overflow-hidden"
                          >
                            <div className="flex items-center justify-between">
                              <FormControlLabel
                                control={
                                  <Checkbox
                                    size="small"
                                    checked={checkboxState.checked || catSel.includes(category)}
                                    indeterminate={checkboxState.indeterminate}
                                    onChange={() => handleCategoryToggle(category)}
                                  />
                                }
                                label={
                                  <div className="w-full">
                                    <span className="text-[14px] text-neutral-700 flex justify-between">{category}</span>
                                  </div>
                                }
                              />
                              {categoryConfig?.subcategories && categoryConfig.subcategories.length > 0 && (
                                <IconButton
                                  size="small"
                                  onClick={(e) => {
                                    e.stopPropagation()
                                    toggleSubcategoryOpen(category)
                                  }}
                                >
                                  {subcategoryOpen[category] ? <ExpandLessIcon fontSize="small" /> : <ExpandMoreIcon fontSize="small" />}
                                </IconButton>
                              )}
                            </div>

                            {/* Subcategories - simplified since we just use the values */}
                            {categoryConfig?.subcategories && (
                              <Collapse in={subcategoryOpen[category]}>
                                <div className="ml-8 mt-1 flex flex-col">
                                  {categoryConfig.subcategories.map((subcategoryValue) => (
                                    <FormControlLabel
                                      key={subcategoryValue}
                                      control={
                                        <Checkbox
                                          size="small"
                                          checked={(subcategorySel[category] || []).includes(subcategoryValue)}
                                          onChange={() => handleSubcategoryToggle(category, subcategoryValue)}
                                        />
                                      }
                                      label={<span className="text-[13px] text-neutral-600">{subcategoryValue}</span>}
                                    />
                                  ))}
                                </div>
                              </Collapse>
                            )}
                          </motion.div>
                        )
                      })}
                    </AnimatePresence>
                  </div>
                </Collapse>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </div>
  )

  return (
    <main className="bg-[#f5f8fb] min-h-screen">
      <Navbar active="Product" />

      <div className="mx-auto container px-6">
        {/* Breadcrumb row */}
        <div className="pt-6">
          <div className="mb-8">
            <Breadcrumbs
              separator="›"
              aria-label="breadcrumb"
              className="text-sm text-gray-500"
              sx={{
                '& .MuiBreadcrumbs-separator': {
                  mx: 1
                }
              }}
            >
              <Link href="/" className="hover:text-sky-600 transition-colors">
                Home
              </Link>
              <Link href="/product" className="hover:text-sky-600 transition-colors">
                Products
              </Link>
            </Breadcrumbs>
          </div>
        </div>

        {/* Main layout: Fixed sidebar + Content area */}
        <div className="mt-6 flex gap-6 min-h-[calc(100vh-200px)]">
          {/* Fixed Sidebar */}
          {!isMobile && (
            <aside className="flex-1">
              {filtersContent}
            </aside>
          )}

          {/* Main Content Area */}
          <div className="flex-2 min-w-0">
            {/* Search, chips, sort */}
            <div className="flex flex-wrap items-center gap-4 mb-4">
              <TextField
                size="small"
                placeholder="Search..."
                value={searchQuery}
                inputProps={{
                  style: { color: 'black' }
                }}
                className="w-[260px] bg-white rounded-md"
                InputProps={{
                  startAdornment: (
                    <InputAdornment position="start">
                      <SearchIcon fontSize="small" />
                    </InputAdornment>
                  ),
                }}
                onChange={(e) => {
                  setSearchQuery(e.target.value)
                  setPage(1)
                }}
              />
              <div className="flex flex-wrap gap-2">
                {getAllSelectedFilters().map((filter, index) => (
                  <Chip
                    key={`${filter.type}-${filter.value}-${index}`}
                    label={filter.label}
                    size="small"
                    color="info"
                    variant="outlined"
                    onDelete={() => removeFilter(filter.type, filter.value, filter.category)}
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
              {(searchDebounce || brandSel.length > 0 || catSel.length > 0 || Object.values(subcategorySel).some(arr => arr.length > 0)) && (
                <span className="ml-2">
                  {searchDebounce && `for "${searchDebounce}"`}
                  {(brandSel.length > 0 || catSel.length > 0 || Object.values(subcategorySel).some(arr => arr.length > 0)) && ' (filtered)'}
                </span>
              )}
            </div>

            {/* Product grid */}
            <section>
              <AnimatePresence mode="wait">
                {loading ? (
                  <motion.div
                    key="loading"
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    exit={{ opacity: 0 }}
                    className="flex justify-center items-center h-64"
                  >
                    <div className="flex flex-col items-center gap-4">
                      <motion.div
                        animate={{ rotate: 360 }}
                        transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
                        className="w-8 h-8 border-2 border-sky-600 border-t-transparent rounded-full"
                      />
                      <div className="text-neutral-500">Loading products...</div>
                    </div>
                  </motion.div>
                ) : products.length === 0 ? (
                  <motion.div
                    key="empty"
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, y: -20 }}
                    className="text-center py-12"
                  >
                    <div className="text-neutral-500 mb-2">No products found</div>
                    <Button
                      onClick={() => {
                        setSearchQuery('')
                        setBrandSel([])
                        setCatSel([])
                        setSubcategorySel({})
                      }}
                    >
                      Clear filters
                    </Button>
                  </motion.div>
                ) : (
                  <motion.div
                    key={`products-page-${page}`}
                    variants={containerVariants}
                    initial="hidden"
                    animate="visible"
                    exit="exit"
                    className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 xl:grid-cols-4 gap-6"
                  >
                    {products.map((p, i) => {
                      const primaryImg = p.Image_Path?.split(";")[0].trim()
                      const isPolycab = p.Brand?.toLowerCase().includes("polycab")
                      const isDowell = p.Brand?.toLowerCase().includes("dowell's")
                      const isLK = p.Brand?.toLowerCase().includes("lauritz knudsen")
                      const linkHref = `/product/${isPolycab ? p.Type :isLK?"LK":isDowell?"Dowell": p.Brand}/${encodeURIComponent(p.Name)}`

                      return (
                        <motion.div
                          key={`${p.Name}-${i}`}
                          variants={cardVariants}
                          whileHover={{
                            y: -3,
                            transition: { type: "spring", stiffness: 300 }
                          }}
                          whileTap={{ scale: 0.98 }}
                        >
                          <Card elevation={0} className="rounded-xl border border-neutral-200 shadow-sm bg-white h-full">
                            <div className="relative p-4">
                              <Link href={linkHref}
                                onClick={() => handleProductClick(p)}
                                className="block">
                                <motion.div
                                  className="mx-auto h-[180px] w-full overflow-hidden rounded-md bg-[#f4f6f8] flex items-center justify-center"
                                  whileHover={{ scale: 1.02 }}
                                  transition={{ type: "spring", stiffness: 300 }}
                                >
                                  <motion.img
                                    src={primaryImg || "/placeholder.svg"}
                                    alt={p.Name}
                                    className="h-[160px] w-auto object-contain"
                                    initial={{ scale: 0.8, opacity: 0 }}
                                    animate={{ scale: 1, opacity: 1 }}
                                    transition={{ delay: 0.2 + i * 0.05 }}
                                  />
                                </motion.div>
                              </Link>
                            </div>
                            <CardContent className="pt-0">
                              <Link
                                href={linkHref}
                                onClick={() => handleProductClick(p)}
                                className="text-[14px] font-semibold text-sky-700 hover:underline"
                              >
                                <motion.div
                                  initial={{ opacity: 0, y: 10 }}
                                  animate={{ opacity: 1, y: 0 }}
                                  transition={{ delay: 0.4 + i * 0.05 }}
                                >

                                  {p.Name.toUpperCase()}
                                </motion.div>
                              </Link>
                              <motion.div
                                initial={{ opacity: 0, y: 10 }}
                                animate={{ opacity: 1, y: 0 }}
                                transition={{ delay: 0.4 + i * 0.05 }}
                              >
                                {p.Wattage && (
                                  <motion.div
                                  >
                                    <Typography variant={"caption"} className="text-neutral-400">
                                      Wattage: {p.Wattage}
                                    </Typography>
                                    <br />
                                    <Typography variant={"caption"} className="text-neutral-400">
                                      {p.Color}
                                    </Typography>
                                  </motion.div>
                                )}
                                {p.Poles && (
                                  <motion.div
                                  >
                                    <Typography variant={"caption"} className="text-neutral-400">
                                      Pole: {p.Poles}
                                    </Typography>
                                  </motion.div>
                                )}

                                {p.Breaking_Capacity && (
                                  <motion.div
                                  >
                                    <Typography variant={"caption"} className="text-neutral-400">
                                      Breaking Capacity: {p.Breaking_Capacity}
                                    </Typography>
                                  </motion.div>
                                )}


                                <Typography variant={"caption"} className="text-neutral-400">
                                  {p.Short_Description?.length ?? 0 > 150 ? p.Short_Description?.slice(0, 150) + "…" : p.Short_Description}
                                </Typography>
                              </motion.div>

                              {'Sweep_Size' in p && (
                                <motion.div
                                  initial={{ opacity: 0, y: 10 }}
                                  animate={{ opacity: 1, y: 0 }}
                                  transition={{ delay: 0.4 + i * 0.05 }}
                                >
                                  <Typography variant={"caption"} className="text-neutral-400">
                                    Sweep Size: {p.Sweep_Size}
                                  </Typography>
                                  <br />
                                  <Typography variant={"caption"} className="text-neutral-400">
                                    Number of Blades: {p.Number_of_Blades}
                                  </Typography>
                                  <br />
                                  {/* <Typography variant="body2" className="mt-2! text-[14px] font-semibold! text-sky-700">
                                      {p.Price && `Price: ${p.Price}`}
                                    </Typography> */}
                                </motion.div>
                              )}


                            </CardContent>
                          </Card>
                        </motion.div>
                      )
                    })}
                  </motion.div>
                )}
              </AnimatePresence>

              {/* Animated Pagination */}
              {totalPages > 1 && (
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.5 }}
                  className="mt-8 flex items-center justify-between sticky bottom-0 bg-[#f5f8fb] py-4"
                >
                  <div className="flex items-center gap-2">
                    <motion.div
                      key={page}
                      initial={{ scale: 0.8 }}
                      animate={{ scale: 1 }}
                      transition={{ type: "spring", stiffness: 300 }}
                    >
                      {isEditingPage ? (
                        <TextField
                          size="small"
                          value={tempPage}
                          onChange={(e) => {
                            const value = e.target.value;
                            if (value === '' || /^\d+$/.test(value)) {
                              setTempPage(value);
                            }
                          }}
                          onBlur={() => {
                            const newPage = parseInt(tempPage, 10);
                            if (isNaN(newPage) || newPage < 1) {
                              handlePageChange(1);
                            } else if (newPage > totalPages) {
                              handlePageChange(totalPages);
                            } else {
                              handlePageChange(newPage);
                            }
                            setIsEditingPage(false);
                          }}
                          onKeyPress={(e: any) => {
                            if (e.key === 'Enter') {
                              e.target.blur();
                            } else if (e.key === 'Escape') {
                              setTempPage(page.toString());
                              setIsEditingPage(false);
                            }
                          }}
                          autoFocus
                          sx={{
                            '& .MuiOutlinedInput-root': {
                              minWidth: '42px',
                              width: '42px',
                              height: '32px',
                              '& input': {
                                textAlign: 'center',
                                padding: '4px',
                                color: '#0284c7',
                                fontSize: '14px',
                              }
                            }
                          }}
                          inputProps={{
                            min: 1,
                            max: totalPages,
                            style: { textAlign: 'center' }
                          }}
                        />
                      ) : (
                        <Button
                          variant="outlined"
                          size="small"
                          className="!min-w-[42px] rounded-md normal-case bg-sky-600 text-white hover:bg-sky-700 hover:border-sky-700"
                          onClick={() => {
                            setTempPage(page.toString());
                            setIsEditingPage(true);
                          }}
                        >
                          {String(page).padStart(2, "0")}
                        </Button>
                      )}
                    </motion.div>
                    <span className="text-[13px] text-neutral-500">of {totalPages}</span>
                    <motion.div whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }}>
                      <Button
                        variant="outlined"
                        size="small"
                        className="rounded-md min-w-0"
                        aria-label="prev"
                        onClick={() => handlePageChange(Math.max(page - 1, 1))}
                        disabled={page === 1 || loading}
                      >
                        <KeyboardArrowLeftIcon fontSize="small" />
                      </Button>
                    </motion.div>
                    <motion.div whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }}>
                      <Button
                        variant="outlined"
                        size="small"
                        className="rounded-md min-w-0"
                        aria-label="next"
                        onClick={() => handlePageChange(Math.min(page + 1, totalPages))}
                        disabled={page === totalPages || loading}
                      >
                        <KeyboardArrowRightIcon fontSize="small" />
                      </Button>
                    </motion.div>
                  </div>
                  <motion.div
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    className="text-sm text-neutral-500"
                  >
                    Showing {((page - 1) * ITEMS_PER_PAGE) + 1} to {Math.min(page * ITEMS_PER_PAGE, total)} of {total}
                  </motion.div>
                </motion.div>
              )}
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
