import type { Lang } from "./i18n";
export const API = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000";

export type Source = { title: string; publisher?: string | null; url?: string | null; page?: number | null };
export type VoiceResult = { farmer_question: string; ai_response: string; sources: Source[]; audio_base64: string | null; tts_error?: string | null };
export type Message = { id: number; language: Lang; kind: string; question: string; answer: string; sources: Source[]; created_at: string };

export function farmerId(): string {
  let id = localStorage.getItem("rv_farmer_id");
  if (!id) { id = "f_" + crypto.randomUUID().replace(/-/g, ""); localStorage.setItem("rv_farmer_id", id); }
  return id;
}
const hdr = () => ({ "X-Farmer-Id": farmerId() });

async function parse(r: Response) {
  if (!r.ok) {
    let d = `Request failed (${r.status})`;
    try { const j = await r.json(); d = typeof j.detail === "string" ? j.detail : d; } catch {}
    throw new Error(d);
  }
  return r;
}
export async function askText(question: string, language: Lang): Promise<{ answer: string; sources: Source[] }> {
  const r = await parse(await fetch(`${API}/api/chat/ask`, {
    method: "POST",
    headers: { ...hdr(), "Content-Type": "application/json" },
    body: JSON.stringify({ question, language }),
  }));
  const data = await r.json();
  return { answer: data.answer, sources: data.sources || [] };
}

export async function voiceConversation(wav: Blob, language: Lang): Promise<VoiceResult> {
  const fd = new FormData(); fd.append("audio", wav, "recording.wav"); fd.append("language", language);
  const r = await parse(await fetch(`${API}/api/voice/conversation`, { method: "POST", body: fd, headers: hdr() }));
  return r.json();
}
export async function speak(text: string, language: Lang): Promise<Blob> {
  const r = await parse(await fetch(`${API}/api/voice/speak`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ text, language }) }));
  return r.blob();
}
export async function getHistory(): Promise<Message[]> {
  return (await (await parse(await fetch(`${API}/api/history`, { headers: hdr() }))).json()).messages;
}
export async function clearHistory() { await parse(await fetch(`${API}/api/history`, { method: "DELETE", headers: hdr() })); }
export async function getPrefs(): Promise<{ language: Lang; autoplay: boolean }> {
  return (await parse(await fetch(`${API}/api/preferences`, { headers: hdr() }))).json();
}
export async function savePrefs(p: { language: Lang; autoplay: boolean }) {
  await parse(await fetch(`${API}/api/preferences`, { method: "PUT", headers: { ...hdr(), "Content-Type": "application/json" }, body: JSON.stringify(p) }));
}
export async function analyzePhoto(file: File, language: Lang, note: string): Promise<string> {
  const fd = new FormData(); fd.append("image", file); fd.append("language", language); fd.append("note", note);
  return (await (await parse(await fetch(`${API}/api/vision/analyze`, { method: "POST", body: fd, headers: hdr() }))).json()).analysis;
}
export type Weather = { place: string; current?: { temperature_2m: number; relative_humidity_2m: number; precipitation: number; wind_speed_10m: number }; days: { date: string; max: number; min: number; rain_mm: number; rain_prob: number }[]; alerts: string[] };
export async function getWeather(lat?: number, lon?: number, place?: string): Promise<Weather> {
  const params = new URLSearchParams();
  if (typeof lat === "number" && typeof lon === "number") { params.set("lat", String(lat)); params.set("lon", String(lon)); }
  else if (place) params.set("place", place);
  else throw new Error("Provide a location or place name.");
  return (await parse(await fetch(`${API}/api/weather?${params.toString()}`))).json();
}
export const b64ToBlob = (b64: string, type = "audio/wav") => {
  const bin = atob(b64); const u = new Uint8Array(bin.length);
  for (let i = 0; i < bin.length; i++) u[i] = bin.charCodeAt(i);
  return new Blob([u], { type });
};
