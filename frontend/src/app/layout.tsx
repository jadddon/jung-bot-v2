import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "JungBot",
  description: "A Carl Jung chatbot enhanced by Retrieval-Augmented Generation which includes Jung's full body of work. You can use this to mimic a formal Jungian session or use it to find and cite relevant sources from Jung's body of work.",
  icons: {
    icon: '/Carl-Jung.jpeg?v=2',
    shortcut: '/Carl-Jung.jpeg?v=2',
    apple: '/Carl-Jung.jpeg?v=2',
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <head>
        <link rel="icon" type="image/jpeg" href="/Carl-Jung.jpeg?v=2" />
        <link rel="shortcut icon" type="image/jpeg" href="/Carl-Jung.jpeg?v=2" />
        <link rel="apple-touch-icon" href="/Carl-Jung.jpeg?v=2" />
      </head>
      <body>
        {children}
      </body>
    </html>
  );
}
