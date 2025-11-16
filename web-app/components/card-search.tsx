"use client";

import { ChevronDown, Loader2, Search, X } from "lucide-react";
import { useCallback, useEffect, useState } from "react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Slider } from "@/components/ui/slider";
import { type CardFilter, getAllSets, type OracleCard, searchCards } from "@/lib/api";
import { CardDetailsDialog } from "./card-details-dialog";
import { CardGrid } from "./card-grid";

const CARD_TYPES = [
  "Creature",
  "Instant",
  "Sorcery",
  "Enchantment",
  "Artifact",
  "Planeswalker",
  "Land",
  "Battle",
];

const RARITIES = ["common", "uncommon", "rare", "mythic"];

const COLOR_MAP = {
  W: { name: "White", emoji: "⚪" },
  U: { name: "Blue", emoji: "🔵" },
  B: { name: "Black", emoji: "⚫" },
  R: { name: "Red", emoji: "🔴" },
  G: { name: "Green", emoji: "🟢" },
} as const;

export function CardSearch() {
  const [searchText, setSearchText] = useState("Black Lotus");
  const [cards, setCards] = useState<OracleCard[]>([]);
  const [loading, setLoading] = useState(false);
  const [cursor, setCursor] = useState<string | null>(null);
  const [hasMore, setHasMore] = useState(false);
  const [showFilters, setShowFilters] = useState(false);
  const [selectedCard, setSelectedCard] = useState<OracleCard | null>(null);

  // Filters
  const [sets, setSets] = useState<string[]>([]);
  const [selectedSets, setSelectedSets] = useState<string[]>([]);
  const [selectedColors, setSelectedColors] = useState<string[]>([]);
  const [colorOperator, setColorOperator] = useState<"or" | "and" | "exactly">("or");
  const [selectedTypes, setSelectedTypes] = useState<string[]>([]);
  const [selectedRarities, setSelectedRarities] = useState<string[]>([]);
  const [cmcRange, setCmcRange] = useState<[number, number]>([0, 16]);

  // Load sets on mount
  useEffect(() => {
    getAllSets().then(setSets).catch(console.error);
  }, []);

  const performSearch = useCallback(
    async (newSearch: boolean = true) => {
      if (!searchText.trim()) return;

      setLoading(true);
      try {
        const filters: CardFilter = {
          sets: selectedSets.length > 0 ? selectedSets : undefined,
          colors: selectedColors.length > 0 ? selectedColors : undefined,
          color_operator: selectedColors.length > 0 ? colorOperator : undefined,
          cmc_min: cmcRange[0] > 0 ? cmcRange[0] : undefined,
          cmc_max: cmcRange[1] < 16 ? cmcRange[1] : undefined,
          types: selectedTypes.length > 0 ? selectedTypes : undefined,
          rarities: selectedRarities.length > 0 ? selectedRarities : undefined,
        };

        const response = await searchCards(searchText, newSearch ? null : cursor, filters);

        if (newSearch) {
          setCards(response.cards);
        } else {
          setCards((prev) => [...prev, ...response.cards]);
        }

        setCursor(response.cursor);
        setHasMore(response.has_more);
      } catch (error) {
        console.error("Failed to search cards:", error);
      } finally {
        setLoading(false);
      }
    },
    [
      searchText,
      cursor,
      selectedSets,
      selectedColors,
      colorOperator,
      selectedTypes,
      selectedRarities,
      cmcRange,
    ]
  );

  const handleSearch = () => {
    performSearch(true);
  };

  const handleLoadMore = () => {
    performSearch(false);
  };

  const clearFilters = () => {
    setSelectedSets([]);
    setSelectedColors([]);
    setColorOperator("or");
    setSelectedTypes([]);
    setSelectedRarities([]);
    setCmcRange([0, 16]);
  };

  const toggleColor = (color: string) => {
    setSelectedColors((prev) =>
      prev.includes(color) ? prev.filter((c) => c !== color) : [...prev, color]
    );
  };

  const toggleType = (type: string) => {
    setSelectedTypes((prev) =>
      prev.includes(type) ? prev.filter((t) => t !== type) : [...prev, type]
    );
  };

  const toggleRarity = (rarity: string) => {
    setSelectedRarities((prev) =>
      prev.includes(rarity) ? prev.filter((r) => r !== rarity) : [...prev, rarity]
    );
  };

  return (
    <div className="space-y-6">
      {/* Search Bar */}
      <div className="flex gap-2">
        <div className="flex-1">
          <Input
            type="text"
            placeholder="Search for cards by name, text, or ability..."
            value={searchText}
            onChange={(e) => setSearchText(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === "Enter") handleSearch();
            }}
            className="w-full"
          />
        </div>
        <Button onClick={handleSearch} disabled={loading || !searchText.trim()}>
          {loading ? <Loader2 className="h-4 w-4 animate-spin" /> : <Search className="h-4 w-4" />}
          <span className="ml-2">Search</span>
        </Button>
        <Button variant="outline" onClick={() => setShowFilters(!showFilters)}>
          Filters
          <ChevronDown
            className={`ml-2 h-4 w-4 transition-transform ${showFilters ? "rotate-180" : ""}`}
          />
        </Button>
      </div>

      {/* Advanced Filters */}
      {showFilters && (
        <Card>
          <CardContent className="pt-6 space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {/* Left Column */}
              <div className="space-y-4">
                {/* Sets Filter */}
                <div>
                  <label className="text-sm font-medium mb-2 block">Sets</label>
                  <Select
                    value={selectedSets[0] || ""}
                    onValueChange={(value) => {
                      if (value && !selectedSets.includes(value)) {
                        setSelectedSets([...selectedSets, value]);
                      }
                    }}
                  >
                    <SelectTrigger>
                      <SelectValue placeholder="Select sets..." />
                    </SelectTrigger>
                    <SelectContent>
                      {sets.map((set) => (
                        <SelectItem key={set} value={set}>
                          {set}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                  {selectedSets.length > 0 && (
                    <div className="flex flex-wrap gap-2 mt-2">
                      {selectedSets.map((set) => (
                        <Badge key={set} variant="secondary">
                          {set}
                          <button
                            type="button"
                            onClick={() => setSelectedSets(selectedSets.filter((s) => s !== set))}
                            className="ml-1 hover:text-destructive"
                          >
                            <X className="h-3 w-3" />
                          </button>
                        </Badge>
                      ))}
                    </div>
                  )}
                </div>

                {/* Colors Filter */}
                <div>
                  <label className="text-sm font-medium mb-2 block">Colors</label>
                  <div className="flex gap-2">
                    {Object.entries(COLOR_MAP).map(([code, { name, emoji }]) => (
                      <Button
                        key={code}
                        variant={selectedColors.includes(code) ? "default" : "outline"}
                        size="sm"
                        onClick={() => toggleColor(code)}
                        className="flex-1"
                      >
                        {emoji} {code}
                      </Button>
                    ))}
                  </div>
                  {selectedColors.length > 0 && (
                    <div className="mt-2">
                      <Select
                        value={colorOperator}
                        onValueChange={(v) => setColorOperator(v as any)}
                      >
                        <SelectTrigger>
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="or">Any of selected colors</SelectItem>
                          <SelectItem value="and">All selected colors</SelectItem>
                          <SelectItem value="exactly">Only selected colors</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>
                  )}
                </div>

                {/* Card Types */}
                <div>
                  <label className="text-sm font-medium mb-2 block">Card Types</label>
                  <div className="flex flex-wrap gap-2">
                    {CARD_TYPES.map((type) => (
                      <Button
                        key={type}
                        variant={selectedTypes.includes(type) ? "default" : "outline"}
                        size="sm"
                        onClick={() => toggleType(type)}
                      >
                        {type}
                      </Button>
                    ))}
                  </div>
                </div>
              </div>

              {/* Right Column */}
              <div className="space-y-4">
                {/* CMC Filter */}
                <div>
                  <label className="text-sm font-medium mb-2 block">
                    Mana Cost (CMC): {cmcRange[0]} - {cmcRange[1] === 16 ? "16+" : cmcRange[1]}
                  </label>
                  <Slider
                    min={0}
                    max={16}
                    step={1}
                    value={cmcRange}
                    onValueChange={(value) => setCmcRange(value as [number, number])}
                    className="mt-4"
                  />
                </div>

                {/* Rarity Filter */}
                <div>
                  <label className="text-sm font-medium mb-2 block">Rarity</label>
                  <div className="flex flex-wrap gap-2">
                    {RARITIES.map((rarity) => (
                      <Button
                        key={rarity}
                        variant={selectedRarities.includes(rarity) ? "default" : "outline"}
                        size="sm"
                        onClick={() => toggleRarity(rarity)}
                        className="capitalize"
                      >
                        {rarity}
                      </Button>
                    ))}
                  </div>
                </div>
              </div>
            </div>

            {/* Filter Actions */}
            <div className="flex gap-2 pt-4 border-t">
              <Button onClick={handleSearch} disabled={loading}>
                Apply Filters
              </Button>
              <Button variant="outline" onClick={clearFilters}>
                Clear All
              </Button>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Results */}
      {cards.length > 0 && (
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <p className="text-sm text-muted-foreground">
              <strong>
                {cards.length}
                {hasMore ? "+" : ""}
              </strong>{" "}
              results found
            </p>
          </div>

          <CardGrid cards={cards} onCardClick={setSelectedCard} />

          {hasMore && (
            <div className="flex justify-center">
              <Button onClick={handleLoadMore} disabled={loading} variant="outline">
                {loading ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Loading...
                  </>
                ) : (
                  "Load More Cards"
                )}
              </Button>
            </div>
          )}
        </div>
      )}

      {/* Card Details Dialog */}
      {selectedCard && (
        <CardDetailsDialog
          card={selectedCard}
          open={!!selectedCard}
          onOpenChange={(open) => !open && setSelectedCard(null)}
        />
      )}
    </div>
  );
}
