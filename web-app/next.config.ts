import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  /* config options here */
  reactStrictMode: true,
  output: "standalone",
  images: {
    remotePatterns: [
      {
        protocol: "https",
        hostname: "cards.scryfall.io",
      },
    ],
  },
};

export default nextConfig;
