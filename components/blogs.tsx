"use client"

import { Box, Button, Card, CardActions, CardContent, Typography } from "@mui/material"
import { motion } from "motion/react"
import { slideInLeft } from "./animations"

type Blog = {
  id: number
  title: string
  date: string
  readTime: string
  image: string
  excerpt: string
  href: string
}

const blogs: Blog[] = [
  {
    id: 1,
    title: "How To Measure & Install Exhaust Fans For Your Bathroom & Kitchen",
    date: "June 18, 2025",
    readTime: "5 min read",
    image: "/assets/blogs/blog1.png",
    excerpt:
      "Exhaust fans are the most convenient element at home and in well-ventilated rooms to improve air quality and remove odors. Here are the fundamentals and a simple checklist to get it done properly.",
    href: "/blog/how-to-measure-and-install-exhaust-fans",
  },
  {
    id: 2,
    title: "5 Hacks To Use Your Pedestal Fan Efficiently",
    date: "June 20, 2025",
    readTime: "4 min read",
    image: "/assets/blogs/blog2.png",
    excerpt:
      "Pedestal fans are simple yet versatile. With these hacks, you can maximize their efficiency and cooling power during hot days.",
    href: "/blog/5-hacks-to-use-your-pedestal-fan",
  },
]

function BlogCard({ blog, index }: { blog: Blog; index: number }) {
  return (
    <motion.div
      variants={slideInLeft}
      initial="hidden"
      whileInView="show"
      custom={index}
    >
      <Card elevation={0} className="overflow-hidden !rounded-xl border border-slate-200 bg-white flex flex-col">
        <img src={blog.image} alt="Blog cover" className="h-[50%] w-full object-cover" />
        <CardContent className="!p-5 flex flex-col justify-between gap-5 h-[50%]">
          <Box>
            <div className="text-xs text-slate-500">
              {blog.date} · {blog.readTime}
            </div>
            <Typography variant="body2" className="mt-2 text-base font-semibold text-slate-900">
              {blog.title}
            </Typography>
            <Typography variant="caption" className="mt-2 line-clamp-3 text-sm text-slate-600">
              {blog.excerpt}
            </Typography>
          </Box>
          <CardActions className="!p-0">
            <Button size="small" variant="contained" href={blog.href}>
              Read more
            </Button>
          </CardActions>
        </CardContent>
      </Card>
    </motion.div>
  )
}

export function Blogs() {
  return (
    <section id="blogs" className="bg-white">
      <div className="container mx-auto my-40 px-4">
        <div className="grid grid-cols-1 gap-8 md:grid-cols-4">
          {/* Left section */}
          <div className="md:col-span-1">
            <Box>
              <Typography variant="body1" className="text-xs uppercase tracking-wide text-slate-500">
                Our Articles & News
              </Typography>
              <Typography variant="h4" className="mt-1 text-3xl font-bold leading-tight text-slate-900">
                Blogs
              </Typography>
            </Box>
            {/* <Button variant="contained" className="!mt-6 rounded-md !bg-slate-900 px-4 py-2 text-sm text-white">
              View all
            </Button> */}
          </div>

          {/* Blog cards */}
          <div className="md:col-span-3 grid grid-cols-1 gap-6 md:grid-cols-3">
            {blogs.map((blog, index) => (
              <BlogCard key={blog.id} blog={blog} index={index} />
            ))}
          </div>
        </div>
      </div>
    </section>
  )
}
