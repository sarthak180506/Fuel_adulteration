import type { Metadata } from 'next'

export const metadata: Metadata = {
  title: 'FuelGuard Dashboard',
  description: 'Real-time fuel adulteration detection',
}

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  )
}
