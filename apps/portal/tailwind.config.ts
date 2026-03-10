/** @type {import('tailwindcss').Config} */
module.exports = {
    content: [
        "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
        "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
        "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
    ],
    theme: {
        extend: {
            colors: {
                background: "var(--background)",
                foreground: "var(--foreground)",
                neon: {
                    cyan: "#00F3FF",
                    purple: "#BC13FE",
                    emerald: "#10B981",
                    pink: "#FF1CE7",
                },
                carbon: {
                    950: "#050505",
                    900: "#0a0a0f",
                    800: "#14141a",
                },
                glass: "rgba(255, 255, 255, 0.05)",
            },
            backgroundImage: {
                "gradient-conic": "conic-gradient(from 180deg at 50% 50%, var(--tw-gradient-stops))",
                "neon-glow": "radial-gradient(circle at center, var(--neon-cyan) 0%, transparent 70%)",
            },
            animation: {
                "orb-pulse": "pulse 4s cubic-bezier(0.4, 0, 0.6, 1) infinite",
                "hud-glitch": "glitch 0.3s ease-in-out infinite",
            },
        },
    },
    plugins: [],
};
