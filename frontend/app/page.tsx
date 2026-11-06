import Link from "next/link";
import { Mic, Languages, BookCheck, ShieldCheck, Sprout, ArrowRight } from "lucide-react";

const features = [
  { i: Languages, t: "Telugu · Hindi · English", d: "Speak in your own language and hear the answer back." },
  { i: BookCheck, t: "Source-grounded advice", d: "Answers draw on ICAR / university / KVK documents when available, with citations." },
  { i: ShieldCheck, t: "Safe by design", d: "No invented pesticide doses or scheme details. Experts recommended when needed." },
];
export default function Landing() {
  return (
    <main className="field-bg min-h-screen">
      <nav className="mx-auto flex max-w-6xl items-center justify-between px-4 py-5">
        <span className="flex items-center gap-2 font-display text-2xl font-bold text-leaf-800"><Sprout className="h-7 w-7" />RythuVoice AI</span>
        <Link href="/assistant" className="rounded-xl bg-leaf-700 px-4 py-2 font-semibold text-white hover:bg-leaf-800">Open assistant</Link>
      </nav>
      <section className="mx-auto grid max-w-6xl items-center gap-10 px-4 py-12 md:grid-cols-2 md:py-20">
        <div>
          <p className="mb-3 inline-block rounded-full bg-grain-100 px-3 py-1 text-sm font-bold text-grain-700">రైతు · किसान · Farmer</p>
          <h1 className="font-display text-4xl font-bold leading-tight text-leaf-900 sm:text-6xl">Ask your field a question.<br />Hear the answer.</h1>
          <p className="mt-5 max-w-lg text-lg text-soil-700">A voice-first AI farming assistant for crops, pests, soil, irrigation, fertilizers and schemes – built for the smartphone in your pocket.</p>
          <Link href="/assistant" className="mt-8 inline-flex items-center gap-2 rounded-2xl bg-leaf-700 px-7 py-4 text-lg font-bold text-white shadow-lg hover:bg-leaf-800"><Mic className="h-6 w-6" />Start speaking<ArrowRight className="h-5 w-5" /></Link>
        </div>
        <ol className="space-y-3 rounded-3xl bg-white p-6 shadow-xl ring-1 ring-leaf-100">
          {["Tap the microphone and ask in your language", "Prisma STT shows what you said", "AI + agricultural sources prepare guidance", "Timbre voice reads the answer aloud"].map((s, n) => (
            <li key={n} className="flex items-center gap-4"><span className="grid h-10 w-10 shrink-0 place-items-center rounded-full bg-leaf-700 font-bold text-white">{n + 1}</span><span className="text-lg">{s}</span></li>))}
        </ol>
      </section>
      <section className="mx-auto grid max-w-6xl gap-4 px-4 pb-20 md:grid-cols-3">
        {features.map(({ i: I, t, d }) => (<div key={t} className="rounded-2xl bg-white p-6 shadow-sm ring-1 ring-leaf-100"><I className="h-8 w-8 text-leaf-600" /><h3 className="mt-3 text-xl font-bold text-leaf-900">{t}</h3><p className="mt-1 text-soil-700">{d}</p></div>))}
      </section>
      <footer className="border-t border-leaf-100 py-6 text-center text-sm text-soil-700">RythuVoice AI gives general guidance, not a diagnosis. Consult your local KVK or agriculture officer for field decisions.</footer>
    </main>);
}
