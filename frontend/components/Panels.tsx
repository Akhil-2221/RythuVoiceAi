"use client";
import { useState } from "react";
import { Trash2, CloudRain, Sprout, Droplets, Bug, Landmark, Wheat, Mountain, MapPin } from "lucide-react";
import { Button } from "./Button";
import { t, type Lang } from "@/lib/i18n";
import { getWeather, type Message, type Weather } from "@/lib/api";

export function HistoryPanel({ items, lang, onClear }: { items: Message[]; lang: Lang; onClear: () => void }) {
  const L = t(lang);
  return (
    <div className="rounded-3xl bg-white p-5 shadow ring-1 ring-leaf-100">
      <div className="flex items-center justify-between"><h2 className="font-display text-xl font-bold text-leaf-900">{L.history}</h2>
        {items.length > 0 && <Button variant="ghost" className="min-h-10 px-3 py-1 text-sm" onClick={onClear}><Trash2 className="h-4 w-4" />{L.clear}</Button>}</div>
      {items.length === 0 ? <p className="mt-3 text-leaf-700">{L.empty}</p> :
        <ul className="mt-3 max-h-[28rem] space-y-3 overflow-y-auto">{[...items].reverse().map((m) => (
          <li key={m.id} className="rounded-xl bg-leaf-50 p-3"><p className="text-xs text-leaf-700">{m.created_at} · {m.language}</p>
            <p className="font-semibold">{m.question}</p><p className="mt-1 text-sm text-soil-700">{m.answer}</p></li>))}</ul>}
    </div>);
}

const INFO = [
  { i: Sprout, k: "Crops", d: "Cotton, paddy, chilli, maize, groundnut and more – cultivation and harvesting questions." },
  { i: Bug, k: "Pests & diseases", d: "Describe symptoms or send a photo. We suggest what it MAY be and when to see an expert." },
  { i: Mountain, k: "Soil health", d: "Soil, nutrients and fertilizer guidance. Exact doses come only from verified sources." },
  { i: Droplets, k: "Irrigation", d: "Water management and timing for different crop stages." },
  { i: Wheat, k: "Harvesting", d: "When and how to harvest and store your crop." },
  { i: Landmark, k: "Schemes", d: "Government scheme help – verify details with your agriculture office." },
];
export function InfoSection({ lang }: { lang: Lang }) {
  const L = t(lang);
  const labels = [ [L.crops, L.cropsDesc], [L.pests, L.pestsDesc], [L.soil, L.soilDesc], [L.irrigation, L.irrigationDesc], [L.harvest, L.harvestDesc], [L.schemes, L.schemesDesc] ];
  return (<div className="grid gap-3 sm:grid-cols-2">{INFO.map(({ i: I }, index) => (
    <div key={index} className="flex gap-3 rounded-2xl bg-white p-4 shadow-sm ring-1 ring-leaf-100"><I className="h-7 w-7 shrink-0 text-leaf-600" />
      <div><p className="font-bold text-leaf-900">{labels[index][0]}</p><p className="text-sm text-soil-700">{labels[index][1]}</p></div></div>))}</div>);
}

export function SettingsPanel({ lang, autoplay, setAutoplay }: { lang: Lang; autoplay: boolean; setAutoplay: (v: boolean) => void }) {
  return (<div className="rounded-3xl bg-white p-5 shadow ring-1 ring-leaf-100"><h2 className="font-display text-xl font-bold text-leaf-900">{t(lang).settings}</h2>
    <label className="mt-3 flex min-h-12 cursor-pointer items-center justify-between gap-3"><span>{t(lang).autoplay}</span>
      <input type="checkbox" className="h-6 w-6 accent-leaf-700" checked={autoplay} onChange={(e) => setAutoplay(e.target.checked)} /></label></div>);
}

export function WeatherCard({ lang }: { lang: Lang }) {
  const L = t(lang);
  const [w, setW] = useState<Weather | null>(null);
  const [err, setErr] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  const [place, setPlace] = useState("");

  const loadPlace = async (name: string) => {
    if (!name.trim()) { setErr(L.locationDenied); return; }
    setBusy(true); setErr(null);
    try { setW(await getWeather(undefined, undefined, name.trim())); }
    catch (e: any) { setErr(e.message || L.locationDenied); }
    finally { setBusy(false); }
  };
  const loadLocation = () => {
    if (!navigator.geolocation) { setErr(L.locationDenied); return; }
    setBusy(true); setErr(null);
    navigator.geolocation.getCurrentPosition(
      async (p) => { try { setW(await getWeather(p.coords.latitude, p.coords.longitude)); } catch (e: any) { setErr(e.message); } finally { setBusy(false); } },
      () => { setErr(L.locationDenied); setBusy(false); }, { timeout: 12000, maximumAge: 300000 }
    );
  };
  return (<div className="rounded-3xl bg-white p-5 shadow ring-1 ring-leaf-100">
    <h2 className="flex items-center gap-2 font-display text-xl font-bold text-leaf-900"><CloudRain className="h-5 w-5" />{L.weather}</h2>
    <div className="mt-3 flex flex-wrap gap-2">
      <Button variant="outline" onClick={loadLocation} disabled={busy}><MapPin className="h-4 w-4" />{busy ? "…" : L.useLocation}</Button>
    </div>
    <form className="mt-3 flex gap-2" onSubmit={(e) => { e.preventDefault(); loadPlace(place); }}>
      <input aria-label={L.cityPlaceholder} value={place} onChange={(e) => setPlace(e.target.value)} placeholder={L.cityPlaceholder}
        className="min-w-0 flex-1 rounded-xl border border-leaf-300 px-3 py-2 text-sm text-leaf-950" />
      <Button type="submit" variant="primary" disabled={busy || !place.trim()}>{L.search}</Button>
    </form>
    {err && <p role="alert" className="mt-2 text-sm text-red-700">{err}</p>}
    {w && <div className="mt-4 text-sm">
      <p className="font-semibold">{w.place} · Open-Meteo</p>
      {w.current && <div className="mt-2 grid grid-cols-2 gap-2 rounded-xl bg-grain-100 p-3 sm:grid-cols-4">
        <div><p className="text-xs text-soil-700">{L.current}</p><p className="text-lg font-bold">{Math.round(w.current.temperature_2m)}°C</p></div>
        <div><p className="text-xs text-soil-700">{L.humidity}</p><p className="text-lg font-bold">{w.current.relative_humidity_2m}%</p></div>
        <div><p className="text-xs text-soil-700">{L.wind}</p><p className="text-lg font-bold">{Math.round(w.current.wind_speed_10m)} km/h</p></div>
        <div><p className="text-xs text-soil-700">{L.rain}</p><p className="text-lg font-bold">{w.current.precipitation} mm</p></div>
      </div>}
      <ul className="mt-2 space-y-1">{w.days.map((d) => <li key={d.date} className="flex flex-wrap justify-between gap-2 rounded-lg bg-leaf-50 px-3 py-2"><span>{d.date}</span><span>{Math.round(d.min)}–{Math.round(d.max)}°C · 🌧 {d.rain_prob ?? 0}% ({d.rain_mm ?? 0} mm)</span></li>)}</ul>
      {w.alerts.includes("rain_expected") && <p className="mt-2 rounded-lg bg-grain-100 p-2">{lang === "te-IN" ? "వర్షం వచ్చే అవకాశం ఉంది: పిచికారీ వాయిదా వేసి పంటను రక్షించండి." : lang === "hi-IN" ? "बारिश की संभावना है: छिड़काव टालें और उपज सुरक्षित रखें।" : "Rain is likely: consider delaying spraying and protect harvested produce."}</p>}
      {w.alerts.includes("heat") && <p className="mt-2 rounded-lg bg-grain-100 p-2">{lang === "te-IN" ? "ఎండ ఎక్కువగా ఉండవచ్చు: నీటి నిర్వహణపై శ్రద్ధ వహించండి." : lang === "hi-IN" ? "गर्मी अधिक हो सकती है: सिंचाई पर ध्यान दें।" : "High temperatures expected: pay attention to irrigation."}</p>}
      <p className="mt-2 text-xs text-soil-600">Weather data: Open-Meteo</p>
    </div>}
  </div>);
}
