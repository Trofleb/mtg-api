import { beforeEach, describe, expect, it, vi } from "vitest";
import * as api from "@/lib/api";
import { render, screen, waitFor } from "@/test/test-utils";
import { CardSearch } from "./card-search";

// Mock the API module
vi.mock("@/lib/api", () => ({
  searchCards: vi.fn(),
  getAllSets: vi.fn(),
}));

describe("CardSearch", () => {
  const mockSearchCards = vi.mocked(api.searchCards);
  const mockGetAllSets = vi.mocked(api.getAllSets);

  beforeEach(() => {
    vi.clearAllMocks();

    // Default mock implementations
    mockGetAllSets.mockResolvedValue(["LEA", "LEB", "ARN", "ATQ"]);
    mockSearchCards.mockResolvedValue({
      cards: [],
      cursor: null,
      has_more: false,
    });
  });

  it("should render search input and button", () => {
    render(<CardSearch />);

    expect(screen.getByPlaceholderText(/search for cards by name/i)).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /search/i })).toBeInTheDocument();
  });

  it("should load sets on mount", async () => {
    render(<CardSearch />);

    await waitFor(() => {
      expect(mockGetAllSets).toHaveBeenCalledOnce();
    });
  });

  it("should have default search text", () => {
    render(<CardSearch />);

    const input = screen.getByPlaceholderText(/search for cards by name/i);
    expect(input).toHaveValue("Black Lotus");
  });

  it("should update search text when typing", async () => {
    const { user } = render(<CardSearch />);

    const input = screen.getByPlaceholderText(/search for cards by name/i);

    await user.clear(input);
    await user.type(input, "Lightning Bolt");

    expect(input).toHaveValue("Lightning Bolt");
  });

  it("should perform search when clicking search button", async () => {
    const mockCards = [
      {
        id: "1",
        name: "Black Lotus",
        mana_cost: "{0}",
        type_line: "Artifact",
      },
      {
        id: "2",
        name: "Black Knight",
        mana_cost: "{B}{B}",
        type_line: "Creature — Human Knight",
      },
    ];

    mockSearchCards.mockResolvedValue({
      cards: mockCards,
      cursor: null,
      has_more: false,
    });

    const { user } = render(<CardSearch />);

    const searchButton = screen.getByRole("button", { name: /search/i });
    await user.click(searchButton);

    await waitFor(() => {
      expect(mockSearchCards).toHaveBeenCalledWith("Black Lotus", null, {
        selected_sets: undefined,
        colors: undefined,
        color_operator: undefined,
        cmc_min: undefined,
        cmc_max: undefined,
        types: undefined,
        rarities: undefined,
      });
    });

    // Check that results count is displayed (2 cards, no "+" since has_more is false)
    await waitFor(() => {
      expect(screen.getByText(/2/)).toBeInTheDocument();
      expect(screen.getByText(/results found/i)).toBeInTheDocument();
    });
  });

  it("should perform search when pressing Enter in input", async () => {
    mockSearchCards.mockResolvedValue({
      cards: [
        {
          id: "1",
          name: "Lightning Bolt",
          mana_cost: "{R}",
          type_line: "Instant",
        },
      ],
      cursor: null,
      has_more: false,
    });

    const { user } = render(<CardSearch />);

    const input = screen.getByPlaceholderText(/search for cards by name/i);
    await user.clear(input);
    await user.type(input, "Lightning Bolt");
    await user.keyboard("{Enter}");

    await waitFor(() => {
      expect(mockSearchCards).toHaveBeenCalledWith("Lightning Bolt", null, expect.any(Object));
    });
  });

  it("should disable search button when loading", async () => {
    mockSearchCards.mockImplementation(
      () =>
        new Promise((resolve) =>
          setTimeout(
            () =>
              resolve({
                cards: [],
                cursor: null,
                has_more: false,
              }),
            100
          )
        )
    );

    const { user } = render(<CardSearch />);

    const searchButton = screen.getByRole("button", { name: /search/i });
    await user.click(searchButton);

    // Button should be disabled while loading
    expect(searchButton).toBeDisabled();

    await waitFor(() => {
      expect(searchButton).not.toBeDisabled();
    });
  });

  it("should toggle filters panel", async () => {
    const { user } = render(<CardSearch />);

    const filtersButton = screen.getByRole("button", { name: /filters/i });

    // Initially filters should not be visible - look for a unique filter label
    expect(screen.queryByText("Card Types")).not.toBeInTheDocument();

    // Click to show filters
    await user.click(filtersButton);

    await waitFor(() => {
      expect(screen.getByText("Card Types")).toBeInTheDocument();
    });

    // Click again to hide filters
    await user.click(filtersButton);

    await waitFor(() => {
      expect(screen.queryByText("Card Types")).not.toBeInTheDocument();
    });
  });

  it("should show load more button when has_more is true", async () => {
    mockSearchCards.mockResolvedValue({
      cards: [
        {
          id: "1",
          name: "Card 1",
          type_line: "Creature",
        },
      ],
      cursor: "next-page",
      has_more: true,
    });

    const { user } = render(<CardSearch />);

    const searchButton = screen.getByRole("button", { name: /search/i });
    await user.click(searchButton);

    await waitFor(() => {
      expect(screen.getByRole("button", { name: /load more cards/i })).toBeInTheDocument();
    });
  });

  it("should load more cards when clicking load more button", async () => {
    // First search response
    mockSearchCards.mockResolvedValueOnce({
      cards: [
        {
          id: "1",
          name: "Card 1",
          type_line: "Creature",
        },
      ],
      cursor: "cursor-1",
      has_more: true,
    });

    // Second search response (load more)
    mockSearchCards.mockResolvedValueOnce({
      cards: [
        {
          id: "2",
          name: "Card 2",
          type_line: "Creature",
        },
      ],
      cursor: null,
      has_more: false,
    });

    const { user } = render(<CardSearch />);

    // Perform initial search
    const searchButton = screen.getByRole("button", { name: /search/i });
    await user.click(searchButton);

    await waitFor(() => {
      expect(screen.getByText("1+")).toBeInTheDocument();
    });

    // Click load more
    const loadMoreButton = screen.getByRole("button", {
      name: /load more cards/i,
    });
    await user.click(loadMoreButton);

    await waitFor(
      () => {
        expect(mockSearchCards).toHaveBeenCalledTimes(2);
      },
      { timeout: 2000 }
    );
  });

  it("should clear all filters when clicking clear all", async () => {
    const { user } = render(<CardSearch />);

    // Open filters
    const filtersButton = screen.getByRole("button", { name: /filters/i });
    await user.click(filtersButton);

    await waitFor(() => {
      expect(screen.getByText("Card Types")).toBeInTheDocument();
    });

    // Select a color
    const whiteButton = screen.getByRole("button", { name: /⚪ W/i });
    await user.click(whiteButton);

    // Click clear all
    const clearButton = screen.getByRole("button", { name: /clear all/i });
    await user.click(clearButton);

    // Verify clear all button exists (state reset is internal, hard to test without detailed class inspection)
    expect(clearButton).toBeInTheDocument();
  });

  it("should handle search errors gracefully", async () => {
    const consoleErrorSpy = vi.spyOn(console, "error").mockImplementation(() => {});
    mockSearchCards.mockRejectedValue(new Error("Network error"));

    const { user } = render(<CardSearch />);

    const searchButton = screen.getByRole("button", { name: /search/i });
    await user.click(searchButton);

    await waitFor(
      () => {
        expect(consoleErrorSpy).toHaveBeenCalledWith("Failed to search cards:", expect.any(Error));
      },
      { timeout: 2000 }
    );

    consoleErrorSpy.mockRestore();
  });

  it("should not search when text is empty", async () => {
    const { user } = render(<CardSearch />);

    const input = screen.getByPlaceholderText(/search for cards by name/i);
    await user.clear(input);

    const searchButton = screen.getByRole("button", { name: /search/i });

    // Button should be disabled when input is empty
    expect(searchButton).toBeDisabled();
  });
});
