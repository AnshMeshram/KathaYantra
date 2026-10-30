import type { Metadata } from "next";
import "./globals.css";
import { QueryProvider } from "@/lib/queries/providers";
import { Header } from "@/components/layout/header";
import { Footer } from "@/components/layout/footer";

export const metadata: Metadata = {
  title: "KathaYantra — A Haunted Atlas of World Folklore & Urban Legends",
  description:
    "An interactive supernatural folklore archive and digital museum exploring 300 documented legends, spectral myths, and oral narratives across 15 nations.",
  keywords: [
    "folklore",
    "urban legends",
    "mythology",
    "ghost stories",
    "supernatural atlas",
    "cultural heritage",
  ],
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="dark">
      <body className="antialiased bg-obsidian text-ivory selection:bg-gold/30 selection:text-ivory min-h-screen flex flex-col font-serif">
        <QueryProvider>
          <Header />
          <main className="flex-1 relative z-10">{children}</main>
          <Footer />
        </QueryProvider>
      </body>
    </html>
  );
}
