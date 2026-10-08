import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: { default: "SUNOVATE", template: "%s | SUNOVATE" },
  description: "SUN Organizational Values and Transformation through Experience (prototipe pengembangan)",
  robots: { index: false, follow: false },
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
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
