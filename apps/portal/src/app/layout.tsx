import type { Metadata } from "next";
import { Inter, JetBrains_Mono } from "next/font/google";
import AuthGuard from "@/components/auth/AuthGuard";
import AetherBrain from "@/components/AetherBrain";
import { TelemetryProvider } from "@/hooks/useTelemetry";
import "./globals.css";

const inter = Inter({
    subsets: ["latin"],
    variable: "--font-inter",
    weight: ["300", "400", "500"],
});

const jetbrainsMono = JetBrains_Mono({
    subsets: ["latin"],
    variable: "--font-mono",
    weight: ["400"],
});

export const metadata: Metadata = {
    title: "Aether OS | Neural Voice Interface",
    description:
        "The neural interface between thought and action. " +
        "A multimodal, proactive voice agent powered by Gemini Live API, " +
        "Firebase, and Google ADK for the Gemini Live Agent Challenge 2026.",
    icons: {
        icon: "/favicon.png",
        apple: "/favicon.png",
    },
    openGraph: {
        title: "Aether Voice OS",
        description: "The Neural Interface Between Thought and Action",
        type: "website",
        images: ["/og-banner.png"],
    },
    twitter: {
        card: "summary_large_image",
        title: "Aether Voice OS",
        description: "Multimodal Voice Agent — Gemini Live Agent Challenge 2026",
    },
};

export default function RootLayout({
    children,
}: Readonly<{
    children: React.ReactNode;
}>) {
    return (
        <html lang="en" className={`${inter.variable} ${jetbrainsMono.variable}`}>
            <body className="font-sans">
                <TelemetryProvider>
                    <AuthGuard>
                        <AetherBrain />
                        {children}
                    </AuthGuard>
                </TelemetryProvider>
            </body>
        </html>
    );
}
