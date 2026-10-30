import type { Metadata } from "next";
import "leaflet/dist/leaflet.css";
import "./globals.css";
import { QueryProvider } from "@/lib/queries/providers";
import { Header } from "@/components/layout/header";
import { Footer } from "@/components/layout/footer";

export const metadata: Metadata = {
  title: "KathaYantra — An Atlas of World Folklore & Urban Legends",
  description:
    "An illustrated cultural publication and geographic atlas exploring 300 documented legends, mythical traditions, and oral narratives across 15 sovereign nations.",
  keywords: [
    "folklore archive",
    "world mythology",
    "urban legends",
    "historical atlas",
    "cultural stories",
    "cartography",
  ],
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="scroll-smooth">
      <body className="antialiased bg-parchment text-ink selection:bg-lunar-yellow/50 selection:text-ink min-h-screen flex flex-col font-serif">
        <QueryProvider>
          <Header />
          <main className="flex-1 relative z-10">{children}</main>
          <Footer />
        </QueryProvider>
      </body>
    </html>
  );
}
