import type { Metadata } from "next";
import { connection } from "next/server";
import "./globals.css";
import "./editorial.css";
import "./motion.css";

export const metadata: Metadata = {
  title: { default: "SUNOVATE", template: "%s | SUNOVATE" },
  description: "Ruang pengelolaan pengetahuan dan koordinasi kerja Direktorat Surat Utang Negara",
  robots: {
    index: false,
    follow: false,
    noarchive: true,
    nosnippet: true,
    noimageindex: true,
  },
};

export default async function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  // Every page is rendered per request so the script nonce from proxy.ts can be applied;
  // a prerendered page would carry no nonce and its scripts would be blocked.
  await connection();
  return (
    <html lang="id" data-scroll-behavior="smooth">
      <body>
        <a className="skip-link" href="#main-content">
          Langsung ke konten utama
        </a>
        {children}
      </body>
    </html>
  );
}
