"use client"

import type React from "react"
import { Card, CardContent, Typography } from "@mui/material"
import LanIcon from "@mui/icons-material/Lan"
import PublicIcon from "@mui/icons-material/Public"
import VerifiedIcon from "@mui/icons-material/Verified"

function Feature({
  icon,
  title,
  desc,
}: {
  icon: string
  title: string
  desc: string
}) {
  return (
    <Card elevation={2} className="!rounded-[20px] border-0 bg-white">
      <CardContent className="p-6">
        <div className="flex flex-col items-center justify-center text-center gap-8">
          {/* <div className="rounded-lg bg-sky-50 p-3 text-sky-600">{icon}</div> */}
          <img src={icon}></img>
          <div>
            <Typography variant="h5" className="text-base font-semibold text-slate-900">{title}</Typography>
            <p className="mt-2 text-sm text-slate-600">{desc}</p>
          </div>
        </div>
      </CardContent>
    </Card>
  )
}

export function WhyChooseUs() {
  return (
    <section className="bg-white">
      <div className="mx-auto container py-10 md:py-12">
        <Typography variant="h4" className="text-center text-lg font-semibold text-slate-900">Why Choose Us</Typography>
        <div className="mt-8 grid grid-cols-1 gap-5 md:grid-cols-3">
          <Feature
            icon="/assets/whyChooseUs/distributedNetwork.png"
            title="Distributed Network"
            desc="A strong distribution network across India ensures timely delivery and availability of electrical solutions."
          />
          <Feature
            icon="/assets/whyChooseUs/panIndia.png"
            title="PAN India Presence"
            desc="We serve customers across every region of India, ensuring nationwide reach with consistent service."
          />
          <Feature
            icon="/assets/whyChooseUs/certifiedReliable.png"
            title="Certified, Reliable Products"
            desc="We deal only in verified, trusted, and quality-assured electrical products for long-term performance."
          />
        </div>
      </div>
    </section>
  )
}
