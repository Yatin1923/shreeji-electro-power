"use client"
import Link from "next/link"
import Image from "next/image"
import Navbar from "@/components/navbar"
import { Breadcrumbs } from "@mui/material"
import { polycabProductService } from "@/services/polycab-product-service"
import { useRef, useState } from "react"
const MagnifyingImage = ({ src, alt, width, height, className }: {
    src: string;
    alt: string;
    width: number;
    height: number;
    className?: string;
}) => {
    const [showMagnifier, setShowMagnifier] = useState(false)
    const [magnifierPosition, setMagnifierPosition] = useState({ x: 0, y: 0 })
    const [imgPosition, setImgPosition] = useState({ x: 0, y: 0 })
    const imgRef = useRef<HTMLDivElement>(null)

    const handleMouseEnter = () => {
        setShowMagnifier(true)
    }

    const handleMouseLeave = () => {
        setShowMagnifier(false)
    }

    const handleMouseMove = (e: React.MouseEvent) => {
        if (imgRef.current) {
            const rect = imgRef.current.getBoundingClientRect()
            const x = e.clientX - rect.left
            const y = e.clientY - rect.top
            
            setMagnifierPosition({ x: e.clientX, y: e.clientY })
            setImgPosition({ x, y })
        }
    }

    return (
        <div className="relative">
            <div
                ref={imgRef}
                className="relative overflow-hidden cursor-crosshair"
                onMouseEnter={handleMouseEnter}
                onMouseLeave={handleMouseLeave}
                onMouseMove={handleMouseMove}
            >
                <Image
                    src={src}
                    alt={alt}
                    width={width}
                    height={height}
                    className={className}
                    priority
                />
            </div>

            {/* Magnifier */}
            {showMagnifier && (
                <div
                    className="fixed pointer-events-none z-50 border-2 border-gray-300 rounded-full shadow-lg bg-white"
                    style={{
                        left: `${magnifierPosition.x - 100}px`,
                        top: `${magnifierPosition.y - 100}px`,
                        width: "200px",
                        height: "200px",
                        backgroundImage: `url(${src})`,
                        backgroundSize: `${width * 2}px ${height * 2}px`,
                        backgroundPosition: `-${imgPosition.x * 2 - 100}px -${imgPosition.y * 2 - 100}px`,
                        backgroundRepeat: "no-repeat",
                    }}
                />
            )}
        </div>
    )
}
export default function ProductDetailPage({ params }: { params: { name: string } }) {
    const product = polycabProductService.getProductByName(decodeURIComponent(params.name))

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

    // Get image URL helper
    const getImageUrl = (imagePath: string | undefined) => {
        if (!imagePath) return "/placeholder.svg"
        return imagePath.startsWith('/') ? imagePath : `/${imagePath}`
    }

    // Parse key features from string
    const parseKeyFeatures = (featuresString: string) => {
        if (!featuresString) return []
        return featuresString.split(',').map(feature => feature.trim()).filter(feature => feature.length > 0)
    }
    const getCertificationIconUrl = (certName: string) => {
        // Convert certification name to lowercase and replace spaces with hyphens
        const formattedCertName = certName.toLowerCase().replace(/\s+/g, '-')
        return `/assets/${formattedCertName}-certification-icon.webp`
    }
    // Parse certifications from string
    const parseCertifications = (certificationsString: string) => {
        if (!certificationsString) return []
        return certificationsString.split(',').map(cert => cert.trim()).filter(cert => cert.length > 0)
    }

    const keyFeatures = parseKeyFeatures(product.Key_Features || "")
    const certifications = parseCertifications(product.Certifications || "")

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
                        <span className="text-gray-700">{product.Cable_Name}</span>
                    </Breadcrumbs>
                </div>

                {/* Main Product Section */}
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 mb-12">

                    {/* Left: Product Image */}
                    <div className="space-y-6">
                        <div className="bg-white border border-gray-200 rounded-lg p-8 flex items-center justify-center min-h-[400px]">
                            {/* <Image
                                src={getImageUrl(product.Image_Path)}
                                alt={product.Cable_Name}
                                width={400}
                                height={400}
                                className="max-w-full h-auto object-contain"
                                priority
                            /> */}
                             <MagnifyingImage
                                src={getImageUrl(product.Image_Path)}
                                alt={product.Cable_Name}
                                width={400}
                                height={400}
                                className="max-w-full h-auto object-contain"
                            />
                        </div>


                    </div>

                    {/* Right: Product Details */}
                    <div className="space-y-6">

                        <div className="flex flex-col gap-4">
                            <h1 className="text-3xl font-bold text-sky-600 mb-2">
                                {product.Cable_Name}
                            </h1>
                            {/* {product.Brand && (
                                <p className="text-sky-600 font-medium mb-2">{product.Brand}</p>
                            )} */}
                            {/* Download PDF Button */}
                            {product.Brochure_Path && (
                                <a
                                    href={getImageUrl(product.Brochure_Path)}
                                    download
                                    className="flex items-center underline gap-2 text-gray-600 hover:text-sky-600 transition-colors"
                                >
                                    <img src="/assets/pdf.jpg">
                                    </img>
                                    Download Data Sheet
                                </a>
                            )}
                            {product.Short_Description && (
                                <p className="text-gray-600 text-sm leading-relaxed mb-4">
                                    {product.Short_Description}
                                </p>
                            )}

                        </div>

                        {/* Key Features */}
                        {keyFeatures.length > 0 && (
                            <div>
                                <h3 className="text-lg font-semibold text-gray-900 mb-4">Key Features</h3>
                                <div className="grid grid-cols-2 gap-3">
                                    {keyFeatures.map((feature, index) => (
                                        <div key={index} className="">
                                            <div className="w-[37px] h-[6px] bg-sky-600 rounded-full mb-5"></div>
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

                {/* Product Information Grid */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mb-12">

                    {/* Product Type */}
                    <div className="bg-white border border-gray-200 rounded-lg p-6 flex flex-col items-center">
                        <h3 className="text-lg font-semibold text-gray-900 mb-2">Product Type</h3>
                        <p className="text-gray-600">{product.Product_Type || "N/A"}</p>
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
                                                    // Fallback to text if image doesn't exist
                                                    const target = e.target as HTMLElement;
                                                    target.style.display = 'none';
                                                }}
                                            />
                                        </div>
                                        {/* <span className="text-xs font-medium text-gray-600 text-center">
                                            {cert}
                                        </span> */}
                                    </div>
                                ))}
                            </div>
                        ) : null}
                    </div>

                    {/* Standards */}
                    <div className="bg-white border border-gray-200 rounded-lg p-6 flex flex-col items-center">
                        <h3 className="text-lg font-semibold text-gray-900 mb-2">Standards</h3>
                        <p className="text-gray-600">{product.Standards || "N/A"}</p>
                    </div>
                </div>



                {/* Similar Products Section */}
                {/* <section>
                    <h2 className="text-2xl font-bold text-gray-900 mb-8">Similar Cables</h2>
                    <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6">
                        {Array.from({ length: 8 }).map((_, index) => (
                            <div key={index} className="bg-white border border-gray-200 rounded-lg p-4 hover:shadow-lg transition-shadow">
                                <div className="aspect-square bg-gray-50 rounded-lg mb-4 flex items-center justify-center">
                                    <Image
                                        src="/placeholder.svg"
                                        alt="Similar product"
                                        width={150}
                                        height={150}
                                        className="object-contain"
                                    />
                                </div>
                                <h3 className="text-sm font-medium text-gray-900 line-clamp-2">
                                    Similar Product {index + 1}
                                </h3>
                            </div>
                        ))}
                    </div>
                </section> */}
            </div>
        </main>
    )
}
