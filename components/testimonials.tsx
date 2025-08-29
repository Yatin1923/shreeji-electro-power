"use client"

function TestimonialCard() {
  return (
    <div className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
      <div className="flex items-center gap-3">
        <img src={"/placeholder.svg?height=40&width=40&query=avatar"} alt="Avatar" className="h-10 w-10 rounded-full" />
        <div>
          <div className="text-sm font-semibold text-slate-900">Leo</div>
          <div className="text-xs text-slate-500">Lead Designer</div>
        </div>
        <div className="ml-auto text-xs text-amber-500">★★★★★</div>
      </div>
      <h3 className="mt-4 text-base font-semibold text-slate-900">It was a very good experience</h3>
      <p className="mt-2 text-sm text-slate-600">
        Lorem ipsum dolor sit amet, consectetur adipiscing elit. Curabitur varius, nunc nec turpis molestie, massa nibh
        iaculis.
      </p>
    </div>
  )
}

export function Testimonials() {
  return (
    <section id="testimonials" className="bg-slate-50">
      <div className="mx-auto max-w-6xl px-6 py-14">
        <h2 className="text-center text-xl font-semibold text-slate-900">What Our Clients Say About Us</h2>
        <div className="mt-8 grid grid-cols-1 gap-6 md:grid-cols-3">
          <TestimonialCard />
          <TestimonialCard />
          <TestimonialCard />
        </div>

        <div className="mt-6 flex items-center justify-center gap-2 text-slate-400">
          {Array.from({ length: 6 }).map((_, i) => (
            <span key={i} className={`h-2 w-2 rounded-full ${i === 2 ? "bg-slate-600" : "bg-slate-300"}`} />
          ))}
        </div>
      </div>
    </section>
  )
}
