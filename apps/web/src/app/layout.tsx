import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: { default: "SUNOVATE", template: "%s | SUNOVATE" },
  description: "SUN Integrated Management and Knowledge Platform (prototype pengembangan)",
  robots: { index: false, follow: false },
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="id">
      <body>
        <a className="skip-link" href="#main-content">
          Langsung ke konten utama
        </a>
        {children}
      </body>
    </html>
  );
}
