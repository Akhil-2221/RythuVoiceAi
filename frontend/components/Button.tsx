import { cn } from "@/lib/utils";
import type { ButtonHTMLAttributes } from "react";
export function Button({ className, variant = "primary", ...p }: ButtonHTMLAttributes<HTMLButtonElement> & { variant?: "primary" | "ghost" | "outline" }) {
  return <button {...p} className={cn("inline-flex items-center justify-center gap-2 rounded-xl px-4 py-3 font-semibold transition disabled:opacity-50 min-h-12",
    variant === "primary" && "bg-leaf-700 text-white hover:bg-leaf-800",
    variant === "outline" && "border-2 border-leaf-700 text-leaf-800 hover:bg-leaf-50",
    variant === "ghost" && "text-leaf-800 hover:bg-leaf-100", className)} />;
}
