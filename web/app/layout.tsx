import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  metadataBase: new URL('http://localhost:3000'),
  title: 'Smart Video Search',
  description:
    'Search video metadata by keyword with PostgreSQL and pgvector.',
  openGraph: {
    title: 'Smart Video Search',
    description: 'Keyword ranking, clearly scored.',
    images: ['/og.png'],
  },
  twitter: {
    card: 'summary_large_image',
    title: 'Smart Video Search',
    description: 'Keyword ranking, clearly scored.',
    images: ['/og.png'],
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
