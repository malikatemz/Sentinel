export const metadata = {
  title: "Sentinel",
  description: "Uptime monitoring and alerts",
}

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  )
}
