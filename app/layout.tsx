import type React from "react"
import type { Metadata } from "next"
import { GeistSans } from "geist/font/sans"
import { GeistMono } from "geist/font/mono"
import { Analytics } from "@vercel/analytics/next"
import { GoogleAnalytics } from '@next/third-parties/google'
import { Suspense } from "react"
import "./globals.css"
import { Providers } from "./app-theme"

export const metadata: Metadata = {
  title: "ShreejiElectroPower",
  description: "",
  icons:{
    icon: "/assets/favicon.webp"
  }
}

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode
}>) {
  return (
    <html lang="en" className="scroll-smooth">
      <body className={`font-sans ${GeistSans.variable} ${GeistMono.variable}`}>
        <Providers>
          <Suspense fallback={null}>{children}</Suspense>
          <Analytics />
          <GoogleAnalytics gaId="G-XYZ" />
        </Providers>
      </body>
    </html>
  )
}
