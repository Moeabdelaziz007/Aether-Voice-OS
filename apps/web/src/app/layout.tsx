import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
    title: "Aether OS | Live Voice Interface",
    description: "Advanced Multimodal Voice Agent Shell",
};

export default function RootLayout({
    children,
}: Readonly<{
    children: React.ReactNode;
}>) {
    return (
        <html lang="en">
            <body className="antialiased">
                <main className="min-h-screen bg-black text-white">
                    {children}
                </main>
            </body>
        </html>
    );
}
