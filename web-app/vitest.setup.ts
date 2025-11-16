import { cleanup } from "@testing-library/react";
import { afterEach, vi } from "vitest";
import "@testing-library/jest-dom/vitest";
import React from "react";

// Mock ResizeObserver (required by Radix UI components)
class ResizeObserverMock {
  observe = vi.fn();
  unobserve = vi.fn();
  disconnect = vi.fn();
}
global.ResizeObserver = ResizeObserverMock as any;

// Cleanup after each test
afterEach(() => {
  cleanup();
});

// Mock Next.js navigation
vi.mock("next/navigation", () => ({
  useRouter: vi.fn(() => ({
    push: vi.fn(),
    replace: vi.fn(),
    prefetch: vi.fn(),
    back: vi.fn(),
    forward: vi.fn(),
    refresh: vi.fn(),
  })),
  usePathname: vi.fn(() => "/"),
  useSearchParams: vi.fn(() => new URLSearchParams()),
  useParams: vi.fn(() => ({})),
}));

// Mock Next.js Image component
vi.mock("next/image", () => ({
  default: (props: any) => {
    // eslint-disable-next-line @next/next/no-img-element
    return React.createElement("img", props);
  },
}));

// Mock Next.js Link component
vi.mock("next/link", () => ({
  default: ({ children, href, ...props }: any) => {
    return React.createElement("a", { href, ...props }, children);
  },
}));
