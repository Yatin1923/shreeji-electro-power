"use client"
import Link from "next/link"
import Image from "next/image"
import Navbar from "@/components/navbar"
import { Breadcrumbs, Typography } from "@mui/material"
import { useRef, useState } from "react"
import { unifiedProductService } from "@/services/unified-product-service"
import { Product } from "@/types/common"
import { MagnifyingImage } from "@/components/magnifyingImage"
import { useProduct } from "../../context/product-context"



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

    // Helper functions
    const getImageUrl = (imagePath: string | undefined) => {
        if (!imagePath) return "/placeholder.svg"
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
    const parseSpecifications = (specStr: string) => {
        if (!specStr) return [];

        const lines = specStr.split("\n").map(l => l.trim()).filter(Boolean);

        // Find the line that is exactly "Detail" or "Details"
        const detailIndex = lines.findIndex(
            l => l.toLowerCase() === "detail" || l.toLowerCase() === "details"
        );

        // CASE 1: Found single-word "Detail" or "Details"
        if (detailIndex !== -1) {
            const afterDetails = lines.slice(detailIndex + 1);

            const result: any[] = [];

            for (let i = 0; i < afterDetails.length; i += 2) {
                const key = afterDetails[i];
                const value = afterDetails[i + 1] || "";
                result.push({
                    key: key.trim(),
                    value: value.trim(),
                    type: "pair"
                });
            }

            return result;
        }

        // CASE 2: No detail → bullet points
        return lines.map(s => ({
            value: s,
            type: "bullet"
        }));
    };

    const getSpecifications = () => {
        const parsedSpecs = parseSpecifications(product?.Specifications || "");

        return parsedSpecs.filter(spec =>
            spec.value &&
            spec.value.trim() !== "" &&
            spec.value.trim() !== "Description"
        );
    };

    const specifications = getSpecifications();

    const colors = parseColors(product.Color || "")
    const images = parseImages(product.Image_Path || "")
    const keyFeatures = parseKeyFeatures(product.Key_Features || "")
    const certifications = parseCertifications(product.Certifications || "")

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
                                                className={`p-3 text-left text-sm border rounded-lg transition-all hover:bg-gray-50 ${selectedColorIndex === index
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
                                    download={`${product.Name}-brochure.pdf`}
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

                        {/* CASE 1: KEY-VALUE PAIRS */}
                        {specifications.some(spec => spec.type === "pair") && (
                            <div className="rounded-lg overflow-hidden mb-6">
                                <div className="overflow-x-auto">
                                    <table className="w-full">
                                        <tbody className="divide-y divide-gray-200">
                                            {specifications
                                                .filter(spec => spec.type === "pair")
                                                .map((spec, index) => (
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
                        )}

                        {/* CASE 2: BULLET POINTS */}
                        {specifications.some(spec => spec.type === "bullet") &&

                            <div>
                                <div className="grid grid-cols-2 gap-3">
                                    {specifications.filter(spec => spec.type === "bullet").map((spec, index) => (
                                        <div key={index} className="flex gap-3">
                                            <div className="w-[6px] h-[30px] bg-sky-600 rounded-full mb-5 flex-shrink-0"></div>
                                            <div className="text-gray-700 leading-relaxed">{spec.value}</div>
                                        </div>
                                    ))}
                                </div>
                            </div>
                        }
                    </div>
                )}

            </div>
        </main>
    )
}
