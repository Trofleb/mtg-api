import react from "@vitejs/plugin-react";
import tsconfigPaths from "vite-tsconfig-paths";
import { defineConfig } from "vitest/config";

export default defineConfig({
  plugins: [
    tsconfigPaths(), // Resolves path aliases from tsconfig.json
    react(), // Enables React support
  ],
  test: {
    environment: "jsdom", // Use jsdom for DOM testing
    globals: true,
    setupFiles: ["./vitest.setup.ts"],
    css: true,
    exclude: [
      "**/node_modules/**",
      "**/dist/**",
      "**/e2e/**", // Exclude Playwright e2e tests
      "**/.next/**",
    ],
    coverage: {
      provider: "v8",
      reporter: ["text", "json", "html"],
      exclude: [
        "node_modules/**",
        "**/*.config.{ts,js}",
        "**/*.d.ts",
        "**/types/**",
        "**/__tests__/**",
        "**/test/**",
        "**/e2e/**",
      ],
    },
  },
});
