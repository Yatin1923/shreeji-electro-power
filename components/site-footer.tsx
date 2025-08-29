"use client"

export function SiteFooter() {
  return (
    <footer className="bg-slate-900 text-slate-300">
      <div className="mx-auto max-w-6xl px-6 py-12">
        <div className="grid grid-cols-1 gap-10 md:grid-cols-3">
          <div>
            <div className="flex items-center gap-2">
              <img src={"/placeholder.svg?height=28&width=28&query=logo"} alt="" className="h-7 w-7 rounded-full" />
              <div className="font-semibold text-sky-400">SHREEJI ELECTRO POWER PVT. LTD.</div>
            </div>
            <p className="mt-3 text-sm leading-6 text-slate-400">
              Shreeji Electro Power Pvt. Ltd. has been involved in trading business as a distributor of electrical goods
              and materials. Partnerships include POLYCAB, HAGER, L&amp;T, DOWELL, SUMIP and NEPTUNE.
            </p>
          </div>

          <div>
            <div className="font-semibold text-white">Address</div>
            <p className="mt-3 text-sm text-slate-400">
              308/B/1A, Makarpura GIDC, Opp. Telephone Exchange, Vadodara - 390010 Gujarat, India
            </p>
            <div className="mt-3 text-sm">
              <div>+91 9420654539</div>
              <div>+91 9054753539</div>
              <div>support@shreejielectropower.com</div>
              <div>inquiry@shreejielectropower.com</div>
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <img
              src={"/placeholder.svg?height=80&width=160&query=badge"}
              alt="Badge"
              className="h-20 w-full rounded-md bg-white/5 object-contain"
            />
            <img
              src={"/placeholder.svg?height=80&width=160&query=badge"}
              alt="Badge"
              className="h-20 w-full rounded-md bg-white/5 object-contain"
            />
            <img
              src={"/placeholder.svg?height=80&width=160&query=badge"}
              alt="Badge"
              className="h-20 w-full rounded-md bg-white/5 object-contain"
            />
          </div>
        </div>
      </div>

      <div className="border-t border-white/10">
        <div className="mx-auto max-w-6xl px-6 py-4 text-xs text-slate-400">
          © Copyrights 2025 | All Rights Reserved by shreejielectropower.com
        </div>
      </div>
    </footer>
  )
}
