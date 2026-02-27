import type { Metadata } from "next";
import { AetherBrain } from "../components/AetherBrain";
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
                <main className="min-h-screen bg-transparent text-white">
                    <AetherBrain />
                    {children}
                </main>
            </body>
        </html>
    );
}
