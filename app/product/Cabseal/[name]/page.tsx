"use client"
import Link from "next/link"
import Image from "next/image"
import Navbar from "@/components/navbar"
import { Breadcrumbs, Typography } from "@mui/material"
import { useRef, useState } from "react"
import { polycabCableService } from "@/services/product-service-factory"
import { unifiedProductService } from "@/services/unified-product-service"
import { Product } from "@/types/common"
import { MagnifyingImage } from "@/components/magnifyingImage"
import { useProduct } from "../../context/product-context"
import EnquireButton from "@/components/enquireButton"
import { AnimatePresence, motion } from "framer-motion"



export default function ProductDetailPage({ params }: { params: { name: string } }) {
    const { selectedProduct } = useProduct();
    let product: Product | null = selectedProduct
    // Add state for selected color
    const [selectedColorIndex, setSelectedColorIndex] = useState(0)

    if (!product) {
        return (
            <main className="bg-white min-h-screen">
                <Navbar active="Product" />
                <div className="mx-auto max-w-6xl px-6 py-12">
                    <p className="text-sm text-gray-600">Product not found.</p>
                    <Link href="/product" className="mt-2 inline-block text-sky-700 underline">
                        Back to Products
                    </Link>
                </div>
            </main>
        )
    }

    

    const parseImages = (imagesString: string) => {
        if (!imagesString) return []
        return imagesString.split(';').map(img => img.trim()).filter(img => img.length > 0)
    }

    // Parse specifications
  

   
    const images = parseImages(product.Image_Path || "")
    
    const [currentIndex, setCurrentIndex] = useState(0)
    console.log("Parsed colors:", images[currentIndex])

    const nextImage = () =>
    setCurrentIndex((prev) => (prev + 1) % images.length)

    const prevImage = () =>
    setCurrentIndex((prev) =>
        prev === 0 ? images.length - 1 : prev - 1
    )


    return (
        <main className="bg-white min-h-screen">
            <Navbar active="Product" />

            {/* Container */}
            <div className="mx-auto max-w-7xl px-4 py-6">

                {/* Breadcrumb */}
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
                        <span className="text-gray-700">{product.Name}</span>
                    </Breadcrumbs>
                </div>

                {/* Main Product Section */}
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 mb-12">

                    {/* Left: Product Image */}
                    <div className="space-y-6">
                        <div className="bg-white border h-[400px] border-gray-200 rounded-lg p-8 flex items-center justify-center min-h-[400px] relative overflow-hidden">
                            <AnimatePresence mode="wait">
                                <motion.div
                                    key={images[currentIndex]}
                                    initial={{ opacity: 0, x: 40 }}
                                    animate={{ opacity: 1, x: 0 }}
                                    exit={{ opacity: 0, x: -40 }}
                                    transition={{ duration: 0.3 }}
                                    className="absolute inset-0 flex items-center justify-center"
                                >
                                    {/* Mobile */}
                                    <Image
                                        src={'/'+images[currentIndex]}
                                        alt={`${product.Name}`}
                                        width={400}
                                        height={400}
                                        className="lg:hidden max-w-full h-auto object-contain"
                                        priority
                                    />

                                    {/* Desktop */}
                                    <MagnifyingImage
                                        src={'/'+images[currentIndex]}
                                        alt={`${product.Name}`}
                                        width={400}
                                        height={400}
                                        className="hidden lg:block max-w-full h-auto object-contain"
                                    />
                                </motion.div>
                            </AnimatePresence>

                            {/* Left Arrow */}
                            {images.length > 1 && (
                                <button
                                    onClick={prevImage}
                                    className="absolute left-3 top-1/2 -translate-y-1/2 bg-white/80 hover:bg-white rounded-full p-2 shadow"
                                >
                                    ‹
                                </button>
                            )}

                            {/* Right Arrow */}
                            {images.length > 1 && (
                                <button
                                    onClick={nextImage}
                                    className="absolute right-3 top-1/2 -translate-y-1/2 bg-white/80 hover:bg-white rounded-full p-2 shadow"
                                >
                                    ›
                                </button>
                            )}
                        </div>



                    </div>

                    {/* Right: Product Details */}
                    <div className="space-y-6">
                        <div className="flex flex-col gap-4">
                            <h1 className="text-3xl font-bold text-sky-600 mb-2">
                                {product.Name}
                            </h1>



                            {product.Short_Description && (
                                <p className="text-gray-600 text-sm leading-relaxed mb-4">
                                    {product.Short_Description}
                                </p>
                            )}

                            {/* {product.Price && (
                                <Typography variant="h6" className="text-sky-600 font-bold!">
                                    Price : <span className="">{product.Price}</span>
                                </Typography>
                            )} */}
                        </div>


                        <p className="text-gray-600 leading-relaxed">
                            {product.Full_Description}
                        </p>
                        <EnquireButton productName={product.Name} />
                    </div>
                </div>
                {product.Certifications &&
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mb-12">
                        {/* Product Type */}
                        <div className="bg-white border border-gray-200 rounded-lg p-6 flex flex-col items-center">
                            <h3 className="text-lg font-semibold text-gray-900 mb-2">Product Type</h3>
                            <p className="text-gray-600">{product.Product_Type}</p>
                        </div>
                    </div>
                }
            </div>
        </main>
    )
}
