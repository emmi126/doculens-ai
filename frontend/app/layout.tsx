import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";
import { Metadata } from "next";
import Auth0Provider from "@/components/providers/Auth0Provider";
import { Toaster } from "react-hot-toast";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "DocuLens AI - AI-Powered Note Processing",
  description: "Transform handwritten notes, blackboard photos, and presentation screenshots into beautifully formatted study materials with AI-powered OCR.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body
        className={`${geistSans.variable} ${geistMono.variable} antialiased`}
      >
        <Auth0Provider>
          {children}
          <Toaster position="top-right" />
        </Auth0Provider>
      </body>
    </html>
  );
}
