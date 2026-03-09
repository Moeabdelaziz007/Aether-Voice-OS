const withBundleAnalyzer = require('@next/bundle-analyzer')({
  enabled: process.env.ANALYZE === 'true',
})

/** @type {import('next').NextConfig} */
const nextConfig = {
  transpilePackages: ['three'],
  productionBrowserSourceMaps: false,
  output: 'export',
  images: {
    unoptimized: true,
  },
}

module.exports = withBundleAnalyzer(nextConfig)
