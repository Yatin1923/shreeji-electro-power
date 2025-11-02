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



export default function ProductDetailPage({ params }: { params: { name: string } }) {
    let product: Product | undefined = unifiedProductService.getProductByName(decodeURIComponent(params.name))
    console.log(product);
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

    // Helper functions
    const getImageUrl = (imagePath: string | undefined) => {
        if (!imagePath) return "/placeholder.svg"
        imagePath = imagePath.includes('Polycab/Cables/') ? imagePath: "Polycab/Cables/"+imagePath;

        return imagePath.startsWith('/') ? imagePath : `/${imagePath}`
    }

    const parseKeyFeatures = (featuresString: string) => {
        if (!featuresString) return []
        return featuresString.split(',').map(feature => feature.trim()).filter(feature => feature.length > 0)
    }

    const getCertificationIconUrl = (certName: string) => {
        const formattedCertName = certName.toLowerCase().replace(/\s+/g, '-')
        return `/assets/${formattedCertName}-certification-icon.webp`
    }

    const parseCertifications = (certificationsString: string) => {
        if (!certificationsString) return []
        return certificationsString.split(',').map(cert => cert.trim()).filter(cert => cert.length > 0)
    }

    // Parse colors and images
    const parseColors = (colorsString: string) => {
        if (!colorsString) return []
        return colorsString.split(',').map(color => color.trim()).filter(color => color.length > 0)
    }

    const parseImages = (imagesString: string) => {
        if (!imagesString) return []
        return imagesString.split(';').map(img => img.trim()).filter(img => img.length > 0)
    }

    // Parse specifications
    const parseSpecifications = (specificationsString: string) => {
        if (!specificationsString) return []
        return specificationsString.split(',').map(spec => {
            const [key, ...valueParts] = spec.split(':')
            if (key && valueParts.length > 0) {
                return {
                    key: key.trim(),
                    value: valueParts.join(':').trim()
                }
            }
            return null
        }).filter(spec => spec !== null)
    }

    // Get comprehensive specifications
    const getSpecifications = () => {
        const specs: { key: string; value: string }[] = []
        
        // First, add parsed specifications from the Specifications string
        const parsedSpecs = parseSpecifications(product?.Specifications || "")
        specs.push(...parsedSpecs)
        return specs.filter(spec => spec.value && spec.value.trim() !== '')
    }

    const colors = parseColors(product.Color || "")
    const images = parseImages(product.Image_Path || "")
    const keyFeatures = parseKeyFeatures(product.Key_Features || "")
    const certifications = parseCertifications(product.Certifications || "")
    const specifications = getSpecifications()

    // Get current image based on selected color
    const getCurrentImage = () => {
        if (images.length > selectedColorIndex) {
            return getImageUrl(images[selectedColorIndex])
        }
        return getImageUrl(images[0] || "")
    }

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
                        <div className="bg-white border border-gray-200 rounded-lg p-8 flex items-center justify-center min-h-[400px]">
                            <Image
                                src={getCurrentImage()}
                                alt={`${product.Name} - ${colors[selectedColorIndex] || ''}`}
                                width={400}
                                height={400}
                                className="lg:hidden max-w-full h-auto object-contain"
                                priority
                            />
                            <MagnifyingImage
                                src={getCurrentImage()}
                                alt={`${product.Name} - ${colors[selectedColorIndex] || ''}`}
                                width={400}
                                height={400}
                                className="hidden lg:block max-w-full h-auto object-contain"
                            />
                        </div>

                        {/* Color Selection Section */}
                        {colors.length > 1 && (
                            <div className="bg-white border border-gray-200 rounded-lg p-6">
                                <h3 className="text-lg font-semibold text-gray-900 mb-4">Available Color</h3>
                                <div className="space-y-4">
                                    {/* Selected Color Display */}
                                    <div className="text-sm text-gray-600">
                                        Selected: <span className="font-medium text-gray-900">{colors[selectedColorIndex]}</span>
                                    </div>
                                    
                                    {/* Color Options Grid */}
                                    <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
                                        {colors.map((color, index) => (
                                            <button
                                                key={index}
                                                onClick={() => setSelectedColorIndex(index)}
                                                className={`p-3 text-left text-sm border rounded-lg transition-all hover:bg-gray-50 ${
                                                    selectedColorIndex === index 
                                                        ? 'border-sky-500 bg-sky-50 text-sky-700' 
                                                        : 'border-gray-200 text-gray-700'
                                                }`}
                                            >
                                                <div className="flex items-center space-x-2">
                                                    {images[index] && (
                                                        <div className="w-8 h-8 border border-gray-200 rounded overflow-hidden flex-shrink-0">
                                                            <Image
                                                                src={getImageUrl(images[index])}
                                                                alt={color}
                                                                width={32}
                                                                height={32}
                                                                className="w-full h-full object-cover"
                                                            />
                                                        </div>
                                                    )}
                                                    <span className="font-medium">{color}</span>
                                                </div>
                                            </button>
                                        ))}
                                    </div>
                                </div>
                            </div>
                        )}
                    </div>

                    {/* Right: Product Details */}
                    <div className="space-y-6">
                        <div className="flex flex-col gap-4">
                            <h1 className="text-3xl font-bold text-sky-600 mb-2">
                                {product.Name}
                            </h1>
                            
                            {/* Download PDF Button */}
                            {product.Brochure_Path && (
                                <a
                                    href={getImageUrl(product.Brochure_Path)}
                                    download
                                    className="flex items-center underline gap-2 text-gray-600 hover:text-sky-600 transition-colors"
                                >
                                    <img src="/assets/pdf.jpg" alt="PDF" />
                                    Download Data Sheet
                                </a>
                            )}
                            
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

                        {/* Key Features */}
                        {keyFeatures.length > 0 && (
                            <div>
                                <h3 className="text-lg font-semibold text-gray-900 mb-4">Key Features</h3>
                                <div className="grid grid-cols-2 gap-3">
                                    {keyFeatures.map((feature, index) => (
                                        <div key={index} className="flex gap-3">
                                            <div className="w-[6px] h-[30px] bg-sky-600 rounded-full mb-5 "></div>
                                            <div className="text-gray-700 leading-relaxed">{feature}</div>
                                        </div>
                                    ))}
                                </div>
                            </div>
                        )}
                        <p className="text-gray-600 leading-relaxed">
                            {product.Full_Description}
                        </p>
                    </div>
                </div>
                {product.Certifications &&
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mb-12">
                        {/* Product Type */}
                        <div className="bg-white border border-gray-200 rounded-lg p-6 flex flex-col items-center">
                            <h3 className="text-lg font-semibold text-gray-900 mb-2">Product Type</h3>
                            <p className="text-gray-600">{product.Product_Type}</p>
                        </div>

                        {/* Certifications */}
                        <div className="bg-white border border-gray-200 rounded-lg p-6 flex flex-col items-center">
                            <h3 className="text-lg font-semibold text-gray-900 mb-4">Certifications</h3>
                            {certifications.length > 0 ? (
                                <div className="flex items-center justify-center">
                                    {certifications.map((cert, index) => (
                                        <div key={index} className="flex flex-col items-center justify-center p-3 rounded-lg">
                                            <div className="w-12 h-12 mb-2 relative">
                                                <Image
                                                    src={getCertificationIconUrl(cert)}
                                                    alt={`${cert} certification`}
                                                    fill
                                                    className="object-contain"
                                                    onError={(e) => {
                                                        const target = e.target as HTMLElement;
                                                        target.style.display = 'none';
                                                    }}
                                                />
                                            </div>
                                        </div>
                                    ))}
                                </div>
                            ) : null}
                        </div>

                        {/* Standards */}
                        <div className="bg-white border border-gray-200 rounded-lg p-6 flex flex-col items-center">
                            <h3 className="text-lg font-semibold text-gray-900 mb-2">Standards</h3>
                            <p className="text-gray-600">{product.Standards}</p>
                        </div>
                    </div>
                }

                {/* Specifications Table */}
                {specifications.length > 0 && (
                    <div className="mb-12">
                        <h2 className="text-2xl font-bold text-sky-600 mb-6">Specifications</h2>
                        <div className=" rounded-lg overflow-hidden">
                            <div className="overflow-x-auto">
                                <table className="w-full">
                                    <tbody className="divide-y divide-gray-200">
                                        {specifications.map((spec, index) => (
                                            <tr key={index} className="hover:bg-gray-50 transition-colors">
                                                <td className="px-6 py-4 text-sm font-medium text-gray-900">
                                                    {spec.key}
                                                </td>
                                                <td className="px-6 py-4 text-sm text-gray-600">
                                                    {spec.value}
                                                </td>
                                            </tr>
                                        ))}
                                    </tbody>
                                </table>
                            </div>
                        </div>
                    </div>
                )}
            </div>
        </main>
    )
}
