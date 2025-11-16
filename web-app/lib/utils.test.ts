import { describe, expect, it } from "vitest";
import { cn } from "./utils";

describe("cn utility function", () => {
  it("should merge class names correctly", () => {
    const result = cn("text-red-500", "bg-blue-500");
    expect(result).toBe("text-red-500 bg-blue-500");
  });

  it("should handle conditional classes", () => {
    const result = cn("base-class", false && "hidden", true && "visible");
    expect(result).toBe("base-class visible");
  });

  it("should merge Tailwind conflicting classes correctly", () => {
    // twMerge should handle conflicts - later class wins
    const result = cn("p-4", "p-8");
    expect(result).toBe("p-8");
  });

  it("should handle arrays of classes", () => {
    const result = cn(["text-sm", "font-bold"], "text-center");
    expect(result).toBe("text-sm font-bold text-center");
  });

  it("should handle undefined and null values", () => {
    const result = cn("base", undefined, null, "active");
    expect(result).toBe("base active");
  });

  it("should handle empty input", () => {
    const result = cn();
    expect(result).toBe("");
  });

  it("should handle objects with boolean values", () => {
    const result = cn({
      "text-red-500": true,
      "bg-blue-500": false,
      "p-4": true,
    });
    expect(result).toBe("text-red-500 p-4");
  });
});
