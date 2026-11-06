"use client";
import { useRef, useState, useCallback } from "react";

export function useRecorder() {
  const [recording, setRecording] = useState(false);
  const [seconds, setSeconds] = useState(0);
  const [level, setLevel] = useState(0);
  const rec = useRef<MediaRecorder | null>(null);
  const chunks = useRef<Blob[]>([]);
  const timer = useRef<ReturnType<typeof setInterval>>();
  const raf = useRef<number>();
  const stream = useRef<MediaStream | null>(null);
  const actx = useRef<AudioContext | null>(null);

  const cleanup = () => {
    clearInterval(timer.current); if (raf.current) cancelAnimationFrame(raf.current);
    stream.current?.getTracks().forEach((t) => t.stop()); actx.current?.close().catch(() => {}); setLevel(0);
  };

  const start = useCallback(async () => {
    if (!navigator.mediaDevices?.getUserMedia) throw new Error("Microphone not supported (needs HTTPS or localhost).");
    const s = await navigator.mediaDevices.getUserMedia({ audio: { echoCancellation: true, noiseSuppression: true } });
    stream.current = s; chunks.current = [];
    const mr = new MediaRecorder(s); rec.current = mr;
    mr.ondataavailable = (e) => e.data.size && chunks.current.push(e.data);
    mr.start(); setRecording(true); setSeconds(0);
    timer.current = setInterval(() => setSeconds((x) => x + 1), 1000);
    const Ctx = window.AudioContext || (window as any).webkitAudioContext; const ctx = new Ctx(); actx.current = ctx;
    const an = ctx.createAnalyser(); an.fftSize = 256; ctx.createMediaStreamSource(s).connect(an);
    const data = new Uint8Array(an.frequencyBinCount);
    const loop = () => { an.getByteTimeDomainData(data); let m = 0; data.forEach((v) => (m = Math.max(m, Math.abs(v - 128)))); setLevel(m / 128); raf.current = requestAnimationFrame(loop); };
    loop();
  }, []);

  const stop = useCallback((): Promise<Blob> => new Promise((resolve) => {
    const mr = rec.current!;
    mr.onstop = () => { const b = new Blob(chunks.current, { type: mr.mimeType || "audio/webm" }); cleanup(); setRecording(false); resolve(b); };
    mr.stop();
  }), []);

  return { recording, seconds, level, start, stop };
}
