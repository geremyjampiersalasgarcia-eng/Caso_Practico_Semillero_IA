import type { Metadata } from "next";
import { Outfit } from "next/font/google";
import "./globals.css";
import { cn } from "@/lib/utils";

const font = Outfit({ subsets: ["latin"] });


export const metadata: Metadata = {
  title: "Patito IA — Mesa de Ayuda Ventas",
  description: "Mesa de Ayuda IA con agentes especializados para el Departamento de Ventas de Patito S.A.",
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
