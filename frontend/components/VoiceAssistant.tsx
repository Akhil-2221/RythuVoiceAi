"use client";
import { useEffect, useRef, useState } from "react";
import { Mic, Square, Loader2, Volume2, ImagePlus, AlertTriangle, BookOpen, Send } from "lucide-react";
import { Button } from "./Button";
import { cn } from "@/lib/utils";
import { t, type Lang } from "@/lib/i18n";
import { useRecorder } from "@/lib/useRecorder";
import { toWav16k } from "@/lib/wav";
import { voiceConversation, askText, speak, analyzePhoto, b64ToBlob, type Source } from "@/lib/api";

type Turn = { question: string; answer: string; sources: Source[]; kind?: "photo" };

export default function VoiceAssistant({ lang, autoplay, onDone }: { lang: Lang; autoplay: boolean; onDone: () => void }) {
  const L = t(lang);
  const { recording, seconds, level, start, stop } = useRecorder();
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [turn, setTurn] = useState<Turn | null>(null);
  const [playing, setPlaying] = useState(false);
  const audio = useRef<HTMLAudioElement | null>(null);
  const url = useRef<string | null>(null);
  const [needsTap, setNeedsTap] = useState(false);
  const [textQuestion, setTextQuestion] = useState("");
  const [photoNote, setPhotoNote] = useState("");

  useEffect(() => () => { audio.current?.pause(); if (url.current) URL.revokeObjectURL(url.current); }, []);

  const play = async (blob: Blob) => {
    if (url.current) URL.revokeObjectURL(url.current);
    url.current = URL.createObjectURL(blob);
    audio.current?.pause();
    const a = new Audio(url.current); audio.current = a;
    a.onplay = () => setPlaying(true); a.onended = a.onpause = () => setPlaying(false);
    try { await a.play(); setNeedsTap(false); } catch { setNeedsTap(true); } // browser blocked autoplay
  };

  async function toggle() {
    setError(null);
    if (busy) return;
    if (!recording) {
      try { audio.current?.pause(); await start(); }
      catch (e: any) { setError(e?.name === "NotAllowedError" ? L.micDenied : e.message); }
      return;
    }
    setBusy(true);
    try {
      const raw = await stop();
      const wav = await toWav16k(raw);
      const r = await voiceConversation(wav, lang);
      setTurn({ question: r.farmer_question, answer: r.ai_response, sources: r.sources || [] });
      if (r.audio_base64) { const b = b64ToBlob(r.audio_base64); if (autoplay) await play(b); else { url.current = URL.createObjectURL(b); audio.current = new Audio(url.current); } }
      else setError(L.answerSpeechError + (r.tts_error || "unknown"));
      onDone();
    } catch (e: any) { setError(e.message || "Something went wrong."); }
    finally { setBusy(false); }
  }

  async function submitText(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    const question = textQuestion.trim();
    if (!question || busy || recording) return;
    setError(null);
    setBusy(true);
    try {
      const result = await askText(question, lang);
      setTurn({ question, answer: result.answer, sources: result.sources || [] });
      setTextQuestion("");
      try {
        const audioBlob = await speak(result.answer, lang);
        if (autoplay) await play(audioBlob);
        else {
          if (url.current) URL.revokeObjectURL(url.current);
          url.current = URL.createObjectURL(audioBlob);
          audio.current = new Audio(url.current);
        }
      } catch (ttsError: any) {
        setError("Text answer is ready, but audio could not be generated: " + (ttsError.message || "TTS error"));
      }
      onDone();
    } catch (e: any) {
      setError(e.message || "Could not send your question.");
    } finally {
      setBusy(false);
    }
  }

  async function replay() {
    if (!turn) return;
    setError(null);
    if (audio.current && url.current) { audio.current.currentTime = 0; try { await audio.current.play(); setNeedsTap(false); } catch { setNeedsTap(true); } return; }
    try { setBusy(true); await play(await speak(turn.answer, lang)); } catch (e: any) { setError(e.message); } finally { setBusy(false); }
  }

  async function onPhoto(f?: File | null) {
    if (!f) return; setError(null); setBusy(true);
    try {
      if (!/^image\/(jpeg|png|webp)$/.test(f.type)) throw new Error("Please upload a JPG, PNG or WEBP image.");
      if (f.size > 5 * 1024 * 1024) throw new Error("Image must be 5 MB or smaller.");
      const a = await analyzePhoto(f, lang, photoNote.trim());
      setTurn({ question: "📷 " + f.name, answer: a, sources: [], kind: "photo" });
      setNeedsTap(false);
      try { const audioBlob = await speak(a, lang); if (autoplay) await play(audioBlob); else { if (url.current) URL.revokeObjectURL(url.current); url.current = URL.createObjectURL(audioBlob); audio.current = new Audio(url.current); } }
      catch (ttsError: any) { setError(L.answerSpeechError + (ttsError.message || "TTS error")); }
      onDone();
    } catch (e: any) { setError(e.message); } finally { setBusy(false); }
  }

  const status = recording ? `${L.listening} · ${seconds}s` : busy ? L.processing : L.tap;
  return (
    <section aria-label="Voice assistant" className="rounded-3xl bg-white p-5 shadow-lg ring-1 ring-leaf-100 sm:p-8">
      <form onSubmit={submitText} className="mb-6 space-y-3">
        <label htmlFor="farmer-question" className="block text-sm font-semibold text-leaf-900">
          {L.typeQuestion}
        </label>
        <textarea
          id="farmer-question"
          value={textQuestion}
          onChange={(e) => setTextQuestion(e.target.value)}
          maxLength={1000}
          rows={3}
          disabled={busy || recording}
          placeholder={L.placeholder}
          className="w-full resize-y rounded-xl border border-leaf-300 bg-white p-3 text-base text-leaf-950 outline-none focus:ring-2 focus:ring-leaf-500 disabled:opacity-60"
        />
        <div className="flex justify-end">
          <Button type="submit" disabled={!textQuestion.trim() || busy || recording}>
            <Send className="h-4 w-4" /> {L.send}
          </Button>
        </div>
      </form>

      <div className="mb-4 text-center text-sm font-semibold text-leaf-700">
        {L.orSpeak}
      </div>
      <div className="flex flex-col items-center gap-4">
        <div className="relative">
          {recording && <span className="absolute inset-0 rounded-full bg-red-500/40 animate-ring" style={{ transform: `scale(${1 + level})` }} />}
          <button onClick={toggle} disabled={busy} aria-pressed={recording} aria-label={status}
            className={cn("relative grid h-36 w-36 place-items-center rounded-full text-white shadow-xl transition active:scale-95 sm:h-44 sm:w-44",
              recording ? "bg-red-600" : "bg-leaf-700 hover:bg-leaf-800", busy && "opacity-70")}>
            {busy ? <Loader2 className="h-16 w-16 animate-spin" /> : recording ? <Square className="h-14 w-14 fill-white" /> : <Mic className="h-16 w-16" />}
          </button>
        </div>
        <p role="status" aria-live="polite" className="text-center text-lg font-semibold text-leaf-900">{status}</p>
        <div className="w-full max-w-md space-y-2">
          <label htmlFor="photo-note" className="block text-sm font-medium text-leaf-800">{L.photoNote}</label>
          <input id="photo-note" value={photoNote} onChange={(e) => setPhotoNote(e.target.value)} maxLength={200} placeholder={L.photoNotePlaceholder}
            disabled={busy} className="w-full rounded-xl border border-leaf-300 p-3 text-sm text-leaf-950 outline-none focus:ring-2 focus:ring-leaf-500" />
          <label className={cn("inline-flex cursor-pointer items-center gap-2 rounded-xl border-2 border-dashed border-leaf-300 px-4 py-2 text-sm font-medium text-leaf-800 hover:bg-leaf-50", busy && "pointer-events-none opacity-50")}>
            <ImagePlus className="h-4 w-4" /> {busy ? L.photoAnalyzing : L.photo}
            <input type="file" accept="image/jpeg,image/png,image/webp" capture="environment" className="sr-only" disabled={busy} onChange={(e) => { onPhoto(e.target.files?.[0]); e.target.value = ""; }} />
          </label>
        </div>
      </div>

      {error && <div role="alert" className="mt-5 flex gap-2 rounded-xl bg-red-50 p-3 text-red-800"><AlertTriangle className="h-5 w-5 shrink-0" />{error}</div>}

      {turn && (
        <div className="mt-6 space-y-3">
          <div className="rounded-2xl bg-grain-100 p-4"><p className="text-xs font-bold uppercase tracking-wide text-grain-700">{L.you}</p><p className="mt-1 text-lg">{turn.question}</p></div>
          <div className="rounded-2xl bg-leaf-50 p-4 ring-1 ring-leaf-200">
            <p className="text-xs font-bold uppercase tracking-wide text-leaf-700">{L.answer}</p>
            <p className="mt-1 whitespace-pre-line text-lg leading-relaxed">{turn.answer}</p>
            {turn.sources.length > 0 && (
              <div className="mt-3 border-t border-leaf-200 pt-2 text-sm text-leaf-800"><p className="flex items-center gap-1 font-semibold"><BookOpen className="h-4 w-4" />{L.sources}</p>
                <ul className="list-disc pl-5">{turn.sources.map((s, i) => <li key={i}>{s.url ? <a className="underline" href={s.url} target="_blank" rel="noreferrer">{s.title}</a> : s.title}{s.publisher ? ` – ${s.publisher}` : ""}{s.page ? `, p.${s.page}` : ""}</li>)}</ul></div>)}
            <div className="mt-4 flex flex-wrap gap-2">
              <Button onClick={replay} disabled={busy} variant={needsTap ? "primary" : "outline"}><Volume2 className="h-5 w-5" />{playing ? "…" : L.replay}</Button>
              <Button onClick={toggle} disabled={busy || recording} variant="ghost"><Mic className="h-5 w-5" />{L.followup}</Button>
            </div>
          </div>
        </div>
      )}
    </section>
  );
}
