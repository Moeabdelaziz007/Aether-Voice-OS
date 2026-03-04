import type { Metadata } from "next";
import AetherBrain from "@/components/AetherBrain";
import { TelemetryProvider } from "@/hooks/useTelemetry";
import "./globals.css";

export const metadata: Metadata = {
    title: "Aether OS | Live Voice Interface",
    description: "Next-generation multimodal voice agent — AetherOS Live Voice Portal",
};

export default function RootLayout({
    children,
}: Readonly<{
    children: React.ReactNode;
}>) {
    return (
        <html lang="en">
            <body>
                <TelemetryProvider>
                    <AetherBrain />
                    {children}
                </TelemetryProvider>
            </body>
        </html>
    );
}
