import type { Metadata } from "next"
import { Inter } from "next/font/google"
import "./globals.css"
import { AuthProvider } from "@/contexts/AuthContext"
import DevModeInit from "@/components/DevModeInit"

const inter = Inter({ subsets: ["latin"] })

export const metadata: Metadata = {
  title: "GWorkspace Analyzer",
  description: "Analyze your Google Workspace",
}

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode
}>) {
  return (
    <html lang="en">
      <body className={inter.className}>
        <DevModeInit />
        <AuthProvider>
          {children}
        </AuthProvider>
      </body>
    </html>
  )
}
