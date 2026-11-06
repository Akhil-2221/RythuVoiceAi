import type { Metadata, Viewport } from "next";
import "./globals.css";
export const metadata: Metadata = { title: "RythuVoice AI – Voice assistant for Indian farmers", description: "Ask farming questions by voice in Telugu, Hindi or English and hear the answer." };
export const viewport: Viewport = { width: "device-width", initialScale: 1, themeColor: "#275c21" };
export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (<html lang="en"><body className="font-sans">{children}</body></html>);
}
