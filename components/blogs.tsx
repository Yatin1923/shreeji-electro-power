"use client"

import { Button, Card, CardActions, CardContent } from "@mui/material"
import NextLink from "next/link"

function BlogCard() {
  return (
    <Card elevation={0} className="overflow-hidden rounded-xl border border-slate-200 bg-white">
      <img
        src={"/placeholder.svg?height=160&width=560&query=blog%20cover"}
        alt="Blog cover"
        className="h-40 w-full object-cover"
      />
      <CardContent className="p-5">
        <div className="text-xs text-slate-500">June 18, 2025 · 5 min read</div>
        <h3 className="mt-2 text-base font-semibold text-slate-900">
          How To Measure & Install Exhaust Fans For Your Bathroom & Kitchen
        </h3>
        <p className="mt-2 line-clamp-3 text-sm text-slate-600">
          Exhaust fans are the most convenient element at home and in well‑ventilated rooms to improve air quality and
          remove odors. Here are the fundamentals and a simple checklist to get it done properly.
        </p>
      </CardContent>
      <CardActions className="px-5 pb-5">
        <Button
          size="small"
          component={NextLink}
          href="/blog/5-hacks-to-use-your-pedestal-fan"
          className="!bg-sky-600 !text-white !normal-case hover:!bg-sky-700"
        >
          Read more
        </Button>
      </CardActions>
    </Card>
  )
}

export function Blogs() {
  return (
    <section id="blogs" className="bg-white">
      <div className="mx-auto max-w-6xl px-6 py-12">
        <div className="grid grid-cols-1 gap-8 md:grid-cols-4">
          <div className="md:col-span-1">
            <div className="text-xs uppercase tracking-wide text-slate-500">Our Articles & News</div>
            <h2 className="mt-1 text-3xl font-bold leading-tight text-slate-900">Blogs</h2>
            <button className="mt-6 rounded-md bg-slate-900 px-4 py-2 text-sm text-white">View all</button>
          </div>
          <div className="md:col-span-3 grid grid-cols-1 gap-6 md:grid-cols-3">
            <BlogCard />
            <BlogCard />
            <BlogCard />
          </div>
        </div>
      </div>
    </section>
  )
}
