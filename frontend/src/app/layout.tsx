import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "Tri Médical — Secrétariat Radiologie",
  description:
    "Système de tri automatisé des demandes de secrétariat médical en radiologie",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html
      lang="fr"
      className={`${geistSans.variable} ${geistMono.variable} h-full antialiased`}
    >
      <body className="min-h-full flex flex-col bg-gray-50 text-gray-900">
        <header className="bg-[#1e293b] px-6 py-4">
          <div className="max-w-7xl mx-auto flex items-center justify-between">
            <div className="flex items-center gap-2">
              <h1 className="text-lg font-bold text-white">
                Secrétariat Radiologie
              </h1>
              <span className="text-sm text-gray-400">
                / Gestion des demandes d&apos;examens
              </span>
            </div>
            <div className="flex items-center gap-4">
              <span className="text-sm text-gray-400">
                POC &middot; Données synthétiques
              </span>
            </div>
          </div>
        </header>
        <main className="flex-1 max-w-7xl mx-auto w-full px-6 py-8">
          {children}
        </main>
      </body>
    </html>
  );
}
