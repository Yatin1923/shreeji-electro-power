"use client"

import { Button, TextField } from "@mui/material"

export function Contact() {
  return (
    <section id="contact" className="bg-slate-900 text-slate-200">
      <div className="mx-auto max-w-6xl px-6 py-12 md:py-14">
        <h2 className="text-3xl font-bold leading-tight">
          Get in <span className="text-sky-400">Touch</span>
        </h2>

        <div className="mt-8 grid grid-cols-1 gap-8 md:grid-cols-2">
          {/* Left form */}
          <div>
            <form className="space-y-4">
              <TextField label="Full name" fullWidth size="small" />
              <TextField label="Email" type="email" fullWidth size="small" />
              <TextField label="Phone number" type="tel" fullWidth size="small" />
              <TextField label="How did you find us?" fullWidth size="small" />
              <Button
                type="submit"
                variant="contained"
                className="!bg-sky-600 hover:!bg-sky-700 !normal-case"
                fullWidth
              >
                Send
              </Button>
            </form>

            {/* quick contacts */}
            <div className="mt-6 grid grid-cols-3 gap-4 text-xs text-slate-300">
              <div>
                <div className="font-semibold text-white">Phone</div>
                <div>+91 9420654539</div>
              </div>
              <div>
                <div className="font-semibold text-white">Fax</div>
                <div>+91 265 1234</div>
              </div>
              <div>
                <div className="font-semibold text-white">Email</div>
                <div>support@shreejielectropower.com</div>
              </div>
            </div>
          </div>

          {/* Right map */}
          <div className="overflow-hidden rounded-xl border border-white/10">
            <img
              src={"/placeholder.svg?height=360&width=640&query=map"}
              alt="Map"
              className="h-full w-full object-cover"
            />
          </div>
        </div>
      </div>
    </section>
  )
}
