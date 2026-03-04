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
                    cyan: "hsla(var(--neon-cyan) / <alpha-value>)",
                    purple: "hsla(var(--neon-purple) / <alpha-value>)",
                },
                carbon: {
                    900: "hsla(var(--carbon-900) / <alpha-value>)",
                    800: "hsla(var(--carbon-800) / <alpha-value>)",
                },
            },
        },
    },
    plugins: [],
};
