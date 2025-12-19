"use client"
import Navbar from "@/components/navbar"
import { blogs } from "@/data/blogs"
import { Breadcrumbs } from "@mui/material"
import Link from "next/link"
interface PageProps {
  params: { slug: string }
}

export default function BlogPostPage({ params }: PageProps) {
  const blog = blogs.find((b) => b.slug === params.slug)

  if (!blog) {
    return (
      <main className="p-10 text-center text-slate-700">
        <h1 className="text-3xl font-bold">Blog not found</h1>
      </main>
    )
  }

  return (
    <main className="bg-white">
      <Navbar active="Home" />

      <div className="mx-auto max-w-4xl px-6 pt-8 pb-16">
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
            <Link href="/#blogs" className="hover:text-sky-600 transition-colors">
              Blog
            </Link>
            <span className="text-gray-700">{blog.title}</span>
          </Breadcrumbs>
        </div>
        {/* Title */}
        <h1 className="mt-6 text-balance text-5xl font-extrabold leading-tight text-slate-900">
          {blog.title}
        </h1>

        {/* Hero image */}
        <div className="mt-6 overflow-hidden rounded-xl border border-slate-200">
          <img src={blog.image} alt={blog.title} className="w-full object-cover" />
        </div>

        {/* Meta */}
        <div className="mt-3 text-sm text-slate-500">
          {blog.date} · {blog.readTime}
        </div>

        {/* Blog Content (dangerouslySetInnerHTML) */}
        <div
          className="mt-6 prose prose-slate max-w-none"
          dangerouslySetInnerHTML={{ __html: blog.content }}
        />
      </div>
    </main>
  )
}
