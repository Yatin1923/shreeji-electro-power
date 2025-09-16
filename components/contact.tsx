"use client"

import { Button, TextField, Typography } from "@mui/material"

export function Contact() {
  return (
    <section id="contact" className="bg-slate-900 text-slate-200 rounded-t-[8srem]">
      <div className="mx-auto max-w-6xl px-6 py-12 md:py-14">
        <Typography variant="h4" className="text-3xl font-bold leading-tight">
          Get in <span className="text-sky-400">Touch</span>
        </Typography>

        <div className="mt-8 grid grid-cols-1 gap-8 md:grid-cols-2">
          {/* Left form */}
          <div>
            <form className="flex flex-col gap-8">
              <TextField label="Full name" fullWidth size="medium" />
              <TextField label="Email" type="email" fullWidth size="medium" />
              <TextField label="Phone number" type="tel" fullWidth size="medium" />
              <TextField label="How did you find us?" fullWidth size="medium" />
              <Button
                type="submit"
                variant="contained"
                size="large"
                className="!bg-sky-600 hover:!bg-sky-700 !normal-case"
                fullWidth
              >
                Send
              </Button>
            </form>

            {/* quick contacts */}
            <div className="mt-6 flex justify-between text-slate-300">
              <div>
                <Typography className="font-semibold text-white">Phone</Typography>
                <Typography>+91 9420654539</Typography>
              </div>
              <div>
                <Typography className="font-semibold text-white">Fax</Typography>
                <Typography>+91 265 1234</Typography>
              </div>
              <div>
                <Typography className="font-semibold text-white">Email</Typography>
                <Typography>support@shreejielectropower.com</Typography>
              </div>
            </div>
          </div>

          {/* Right map */}
          <div className="overflow-hidden rounded-xl border border-white/10">
            <iframe
              src="https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d3692.6417902620733!2d73.18917607626365!3d22.253665944582306!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x395fc42d2d1ba5c3%3A0x40a4be2bf02f817d!2sSHREEJI%20ELECTRO%20POWER%20PVT.%20LTD.!5e0!3m2!1sen!2sin!4v1757958350673!5m2!1sen!2sin"
              width="100%"
              height="100%"
              style={{ border: 0 }}
              allowFullScreen
              loading="lazy"
              referrerPolicy="no-referrer-when-downgrade"
            />
          </div>

        </div>
      </div>
    </section>
  )
}
