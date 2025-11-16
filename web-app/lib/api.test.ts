import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { type CardFilter, getAllSets, searchCards } from "./api";

// Mock fetch globally
const mockFetch = vi.fn();
global.fetch = mockFetch;

describe("api", () => {
  beforeEach(() => {
    mockFetch.mockClear();
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  describe("searchCards", () => {
    it("should fetch cards with basic search text", async () => {
      const mockResponse = {
        cards: [
          {
            id: "1",
            name: "Black Lotus",
            mana_cost: "{0}",
            type_line: "Artifact",
          },
        ],
        cursor: null,
        has_more: false,
      };

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse,
      });

      const result = await searchCards("Black Lotus");

      expect(mockFetch).toHaveBeenCalledOnce();
      expect(mockFetch).toHaveBeenCalledWith(
        expect.stringContaining("/cards/search/Black%20Lotus"),
        expect.objectContaining({
          method: "GET",
          headers: {
            "Content-Type": "application/json",
          },
        })
      );
      expect(result).toEqual(mockResponse);
    });

    it("should include cursor parameter when provided", async () => {
      const mockResponse = {
        cards: [],
        cursor: "0.9:abc123",
        has_more: true,
      };

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse,
      });

      await searchCards("test", "0.9:abc123");

      expect(mockFetch).toHaveBeenCalledWith(
        expect.stringContaining("cursor=0.9%3Aabc123"),
        expect.any(Object)
      );
    });

    it("should include filter parameters as query params when provided", async () => {
      const mockResponse = {
        cards: [],
        cursor: null,
        has_more: false,
      };

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse,
      });

      const filters: CardFilter = {
        sets: ["LEA", "LEB"],
        colors: ["W", "U"],
        color_operator: "and",
        cmc_min: 2,
        cmc_max: 5,
        types: ["Creature"],
        rarities: ["rare", "mythic"],
      };

      await searchCards("test", null, filters);

      // Check URL contains filter query params
      const callUrl = mockFetch.mock.calls[0][0];
      expect(callUrl).toContain("sets=LEA");
      expect(callUrl).toContain("sets=LEB");
      expect(callUrl).toContain("colors=W");
      expect(callUrl).toContain("colors=U");
      expect(callUrl).toContain("color_operator=and");
      expect(callUrl).toContain("cmc_min=2");
      expect(callUrl).toContain("cmc_max=5");
      expect(callUrl).toContain("types=Creature");
      expect(callUrl).toContain("rarities=rare");
      expect(callUrl).toContain("rarities=mythic");

      // Check request has no body
      const callOptions = mockFetch.mock.calls[0][1];
      expect(callOptions.body).toBeUndefined();
    });

    it("should not include undefined filter values in query params", async () => {
      const mockResponse = {
        cards: [],
        cursor: null,
        has_more: false,
      };

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse,
      });

      const filters: CardFilter = {
        colors: ["W"],
      };

      await searchCards("test", null, filters);

      // Check URL only contains provided filter values
      const callUrl = mockFetch.mock.calls[0][0];
      expect(callUrl).toContain("colors=W");
      expect(callUrl).not.toContain("sets=");
      expect(callUrl).not.toContain("cmc_min=");
      expect(callUrl).not.toContain("rarities=");
    });

    it("should throw error when fetch fails", async () => {
      mockFetch.mockResolvedValueOnce({
        ok: false,
        statusText: "Not Found",
      });

      await expect(searchCards("test")).rejects.toThrow("Failed to search cards: Not Found");
    });

    it("should use default API base URL", async () => {
      const mockResponse = {
        cards: [],
        cursor: null,
        has_more: false,
      };

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse,
      });

      await searchCards("test");

      expect(mockFetch).toHaveBeenCalledWith(
        expect.stringContaining("http://localhost:8000/cards/search"),
        expect.any(Object)
      );
    });
  });

  describe("getAllSets", () => {
    it("should fetch all sets successfully", async () => {
      const mockResponse = {
        sets: ["LEA", "LEB", "ARN", "ATQ"],
      };

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse,
      });

      const result = await getAllSets();

      expect(mockFetch).toHaveBeenCalledOnce();
      expect(mockFetch).toHaveBeenCalledWith(
        "http://localhost:8000/sets",
        expect.objectContaining({
          method: "GET",
          headers: {
            "Content-Type": "application/json",
          },
        })
      );
      expect(result).toEqual(["LEA", "LEB", "ARN", "ATQ"]);
    });

    it("should throw error when fetch fails", async () => {
      mockFetch.mockResolvedValueOnce({
        ok: false,
        statusText: "Internal Server Error",
      });

      await expect(getAllSets()).rejects.toThrow("Failed to fetch sets: Internal Server Error");
    });
  });
});
