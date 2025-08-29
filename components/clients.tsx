"use client"

export function Clients() {
  return (
    <section className="bg-white">
      <div className="mx-auto max-w-6xl px-6 py-10 md:py-12">
        <div className="text-center">
          <h2 className="text-lg font-semibold text-slate-900">Our Clients</h2>
          <p className="mt-1 text-sm text-slate-600">We have been working with 500+ clients</p>
        </div>

        <div className="mt-8 grid grid-cols-4 gap-6 md:grid-cols-8">
          {Array.from({ length: 16 }).map((_, i) => (
            <img
              key={i}
              src={"/placeholder.svg?height=24&width=48&query=client%20logo"}
              alt={`Client ${i + 1}`}
              className="mx-auto h-6 w-12 opacity-70"
            />
          ))}
        </div>
      </div>
    </section>
  )
}
