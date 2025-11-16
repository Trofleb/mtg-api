// API client for MTG card search

export interface CardFilter {
  sets?: string[]; // API expects "sets" not "selected_sets"
  colors?: string[];
  color_operator?: "or" | "and" | "exactly";
  cmc_min?: number;
  cmc_max?: number;
  types?: string[];
  rarities?: string[];
}

export interface OracleCard {
  id: string;
  name: string;
  card_text?: string;
  type_line?: string;
  mana_cost?: string;
  cmc?: number;
  colors?: string[];
  rarity?: string;
  set_count?: number;
  thumbnail?: string;
  faces_thumbnails?: string[];
  card_count?: number;
  edhrec_rank?: number;
  penny_rank?: number;
  cards?: PrintedCard[];
}

export interface PrintedCard {
  id: string;
  name: string;
  set: string;
  set_name: string;
  released_at: string;
  image_uris?: {
    small: string;
    normal: string;
    large: string;
  };
}

export interface SearchResponse {
  cards: OracleCard[];
  cursor: string | null;
  has_more: boolean;
}

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export async function searchCards(
  text: string,
  cursor?: string | null,
  filters?: CardFilter
): Promise<SearchResponse> {
  const params = new URLSearchParams({
    lang: "en",
    page_count: "20",
  });

  if (cursor) {
    params.append("cursor", cursor);
  }

  // Add filter parameters as query params
  if (filters) {
    // Add sets (can be multiple)
    if (filters.sets && filters.sets.length > 0) {
      for (const set of filters.sets) {
        params.append("sets", set);
      }
    }

    // Add colors (can be multiple)
    if (filters.colors && filters.colors.length > 0) {
      for (const color of filters.colors) {
        params.append("colors", color);
      }
    }

    // Add color operator
    if (filters.color_operator) {
      params.append("color_operator", filters.color_operator);
    }

    // Add CMC filters
    if (filters.cmc_min !== undefined) {
      params.append("cmc_min", filters.cmc_min.toString());
    }
    if (filters.cmc_max !== undefined) {
      params.append("cmc_max", filters.cmc_max.toString());
    }

    // Add types (can be multiple)
    if (filters.types && filters.types.length > 0) {
      for (const type of filters.types) {
        params.append("types", type);
      }
    }

    // Add rarities (can be multiple)
    if (filters.rarities && filters.rarities.length > 0) {
      for (const rarity of filters.rarities) {
        params.append("rarities", rarity);
      }
    }
  }

  const response = await fetch(
    `${API_BASE_URL}/cards/search/${encodeURIComponent(text)}?${params.toString()}`,
    {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
      },
    }
  );

  if (!response.ok) {
    throw new Error(`Failed to search cards: ${response.statusText}`);
  }

  return response.json();
}

export async function getAllSets(): Promise<string[]> {
  const response = await fetch(`${API_BASE_URL}/sets`, {
    method: "GET",
    headers: {
      "Content-Type": "application/json",
    },
  });

  if (!response.ok) {
    throw new Error(`Failed to fetch sets: ${response.statusText}`);
  }

  const data = await response.json();
  return data.sets;
}
