import type { Metadata } from "next";
import "leaflet/dist/leaflet.css";
import "./globals.css";
import { QueryProvider } from "@/lib/queries/providers";
import { Header } from "@/components/layout/header";
import { Footer } from "@/components/layout/footer";

export const metadata: Metadata = {
  title: "KathaYantra — An Atlas of World Folklore & Urban Legends",
  description:
    "An interactive cultural archive and digital museum exploring 300 documented legends, mythical traditions, and oral narratives across 15 nations.",
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
    <html lang="en" className="dark scroll-smooth">
      <body className="antialiased bg-ink text-linen selection:bg-brass/25 selection:text-linen min-h-screen flex flex-col font-serif">
        <QueryProvider>
          <Header />
          <main className="flex-1 relative z-10">{children}</main>
          <Footer />
        </QueryProvider>
      </body>
    </html>
  );
}
