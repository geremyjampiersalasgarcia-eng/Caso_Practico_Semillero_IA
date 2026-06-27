import type { Metadata } from "next";
import { Outfit } from "next/font/google";
import "./globals.css";
import { cn } from "@/lib/utils";

const font = Outfit({ subsets: ["latin"] });


export const metadata: Metadata = {
  title: "Nexus IA",
  description: "Asistente inteligente con RAG Multi-Agente",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="es">
      <body className={font.className}>{children}</body>
    </html>
  );
}
