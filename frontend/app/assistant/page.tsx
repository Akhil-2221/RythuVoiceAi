"use client";
import { useCallback, useEffect, useState } from "react";
import Link from "next/link";
import { Sprout } from "lucide-react";
import VoiceAssistant from "@/components/VoiceAssistant";
import { HistoryPanel, InfoSection, SettingsPanel, WeatherCard } from "@/components/Panels";
import { LANGS, type Lang } from "@/lib/i18n";
import { clearHistory, getHistory, getPrefs, savePrefs, type Message } from "@/lib/api";
import { cn } from "@/lib/utils";

export default function Dashboard() {
  const [lang, setLang] = useState<Lang>("te-IN");
  const [autoplay, setAutoplay] = useState(true);
  const [items, setItems] = useState<Message[]>([]);
  const [ready, setReady] = useState(false);
  const [offline, setOffline] = useState(false);

  const refresh = useCallback(() => getHistory().then((m) => { setItems(m); setOffline(false); }).catch(() => setOffline(true)), []);
  useEffect(() => { getPrefs().then((p) => { setLang(p.language); setAutoplay(p.autoplay); }).catch(() => setOffline(true)).finally(() => setReady(true)); refresh(); }, [refresh]);
  useEffect(() => { if (ready) savePrefs({ language: lang, autoplay }).catch(() => {}); }, [lang, autoplay, ready]);

  return (
    <main className="field-bg min-h-screen pb-16">
      <header className="mx-auto flex max-w-6xl items-center justify-between px-4 py-4">
        <Link href="/" className="flex items-center gap-2 font-display text-xl font-bold text-leaf-800"><Sprout className="h-6 w-6" />RythuVoice AI</Link>
      </header>
      <div className="mx-auto grid max-w-6xl gap-5 px-4 lg:grid-cols-[1.4fr_1fr]">
        <div className="space-y-5">
          <div role="radiogroup" aria-label="Language" className="grid grid-cols-3 gap-2">
            {LANGS.map((l) => (<button key={l.code} role="radio" aria-checked={lang === l.code} onClick={() => setLang(l.code)}
              className={cn("min-h-14 rounded-2xl px-2 text-lg font-bold ring-2 transition", lang === l.code ? "bg-leaf-700 text-white ring-leaf-700" : "bg-white text-leaf-900 ring-leaf-200 hover:ring-leaf-400")}>{l.native}</button>))}
          </div>
          {offline && <p role="alert" className="rounded-xl bg-red-50 p-3 text-red-800">Cannot reach the RythuVoice server. Check NEXT_PUBLIC_API_BASE_URL and that the backend is running.</p>}
          <VoiceAssistant lang={lang} autoplay={autoplay} onDone={refresh} />
          <InfoSection lang={lang} />
        </div>
        <aside className="space-y-5">
          <HistoryPanel items={items} lang={lang} onClear={async () => { await clearHistory(); refresh(); }} />
          <WeatherCard lang={lang} />
          <SettingsPanel lang={lang} autoplay={autoplay} setAutoplay={setAutoplay} />
        </aside>
      </div>
    </main>);
}
