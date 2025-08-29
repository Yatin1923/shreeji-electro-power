"use client"

import { Button, Card, CardContent } from "@mui/material"

function BrandTile({ i }: { i: number }) {
  const tints = ["bg-rose-50", "bg-sky-50", "bg-slate-50"]
  return (
    <Card elevation={1} className="rounded-xl">
      <CardContent className={`p-5 md:p-6 ${tints[i % tints.length]}`}>
        <img
          src={"/placeholder.svg?height=48&width=220&query=brand%20logo%20tile"}
          alt={`Brand ${i}`}
          className="mx-auto h-12 w-full object-contain"
        />
      </CardContent>
    </Card>
  )
}

export function Hero() {
  return (
    <section className="bg-slate-50">
      <div className="mx-auto max-w-6xl px-6">
        <div className="grid grid-cols-1 gap-10 py-10 md:grid-cols-2 md:gap-12 md:py-12">
          {/* Left copy */}
          <div className="flex flex-col justify-center">
            <h1 className="text-pretty text-3xl font-bold leading-tight text-slate-900 md:text-4xl">
              Tired of managing multiple vendors for electrical supply?
            </h1>
            <p className="mt-3 max-w-prose text-slate-600">
              We bring India&apos;s top electrical brands under one roof — with seamless service and expert support.
            </p>

            <div className="mt-6 flex items-center gap-3">
              <Button variant="contained" className="!bg-sky-600 !px-5 !py-2.5 !normal-case hover:!bg-sky-700">
                Contact us
              </Button>
              <Button
                variant="outlined"
                className="!border-slate-900 !text-slate-900 !px-4 !py-2.5 !normal-case hover:!bg-slate-900 hover:!text-white"
              >
                Our Products
              </Button>
            </div>

            {/* Stats */}
            <div className="mt-8 grid grid-cols-3 gap-6 text-sm">
              {[
                { k: "20+", v: "Years of Expertise" },
                { k: "500+", v: "Products" },
                { k: "3000+", v: "Clients Served" },
              ].map((s, idx) => (
                <div key={s.k} className="flex items-center gap-3">
                  <img src={"/placeholder.svg?height=28&width=28&query=icon"} alt="" className="h-7 w-7 opacity-80" />
                  <div>
                    <div className="text-base font-semibold text-slate-900">{s.k}</div>
                    <div className="text-slate-600">{s.v}</div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Right brand grid (staggered 2 x 3) */}
          <div className="grid grid-cols-2 items-start gap-4 sm:gap-5">
            {Array.from({ length: 6 }).map((_, i) => (
              <div key={i} className={i % 2 ? "mt-8" : ""}>
                <BrandTile i={i} />
              </div>
            ))}
          </div>
        </div>
      </div>
    </section>
  )
}
