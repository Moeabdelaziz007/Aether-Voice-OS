import type { NextConfig } from "next";
import withPWAInit from "@ducanh2912/next-pwa";

const withPWA = withPWAInit({
    dest: "public",
    disable: process.env.NODE_ENV === "development",
    register: true,
});

const nextConfig: NextConfig = {
    turbopack: {},
    
    // Image optimization for external URLs
    images: {
        unoptimized: true, // Required for static export
    },
    
    // Bundle Optimization
    experimental: {
        // Tree-shaking for heavy 3D libraries
        optimizePackageImports: [
            'three',
            '@react-three/drei',
            '@react-three/fiber',
            '@react-three/postprocessing',
            'postprocessing',
            'framer-motion',
        ],
    },
    
    // Webpack configuration for additional optimizations
    webpack: (config, { isServer }) => {
        // Optimize Three.js imports
        config.resolve.alias = {
            ...config.resolve.alias,
            'three/examples/jsm': 'three/examples/jsm',
        };
        
        // Tree-shake Three.js properly
        if (!isServer) {
            config.resolve.fallback = {
                ...config.resolve.fallback,
                fs: false,
                path: false,
            };
        }
        
        // Minimize chunk splitting for better caching
        if (!isServer && config.optimization) {
            config.optimization.splitChunks = {
                ...config.optimization.splitChunks,
                cacheGroups: {
                    ...config.optimization.splitChunks?.cacheGroups,
                    three: {
                        test: /[\\/]node_modules[\\/](three|@react-three)[\\/]/,
                        name: 'three-vendor',
                        chunks: 'all',
                        priority: 20,
                    },
                    postprocessing: {
                        test: /[\\/]node_modules[\\/](postprocessing)[\\/]/,
                        name: 'postprocessing-vendor',
                        chunks: 'all',
                        priority: 15,
                    },
                },
            };
        }
        
        return config;
    },
};

export default withPWA(nextConfig);
