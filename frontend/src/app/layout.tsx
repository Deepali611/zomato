import type { Metadata } from "next";
import "./globals.css";


export const metadata: Metadata = {
  title: "Zomato AI - Concierge Search",
  description: "AI-powered restaurant discovery and smart recommendations concierge.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="h-full dark antialiased">
      <body className="min-h-full flex flex-col bg-[#0f131d] text-[#dfe2f1] font-sans">{children}</body>
    </html>
  );
}
