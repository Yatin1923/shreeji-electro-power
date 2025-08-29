"use client"

import type React from "react"
import { Card, CardContent } from "@mui/material"
import LanIcon from "@mui/icons-material/Lan"
import PublicIcon from "@mui/icons-material/Public"
import VerifiedIcon from "@mui/icons-material/Verified"

function Feature({
  icon,
  title,
  desc,
}: {
  icon: React.ReactNode
  title: string
  desc: string
}) {
  return (
    <Card elevation={0} className="rounded-xl border border-slate-200 bg-white">
      <CardContent className="p-6">
        <div className="flex items-start gap-4">
          <div className="rounded-lg bg-sky-50 p-3 text-sky-600">{icon}</div>
          <div>
            <h3 className="text-base font-semibold text-slate-900">{title}</h3>
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
      <div className="mx-auto max-w-6xl px-6 py-12">
        <h2 className="text-center text-lg font-semibold text-slate-900">Why Choose Us</h2>
        <div className="mt-8 grid grid-cols-1 gap-5 md:grid-cols-3">
          <Feature
            icon={<LanIcon fontSize="small" />}
            title="Distributed Network"
            desc="A strong distribution network across India ensures timely delivery and availability of electrical solutions."
          />
          <Feature
            icon={<PublicIcon fontSize="small" />}
            title="PAN India Presence"
            desc="We serve customers across every region of India, ensuring nationwide reach with consistent service."
          />
          <Feature
            icon={<VerifiedIcon fontSize="small" />}
            title="Certified, Reliable Products"
            desc="We deal only in verified, trusted, and quality-assured electrical products for long-term performance."
          />
        </div>
      </div>
    </section>
  )
}
