"use client";

import Image from "next/image";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import type { OracleCard } from "@/lib/api";

interface CardGridProps {
  cards: OracleCard[];
  onCardClick: (card: OracleCard) => void;
}

const RARITY_EMOJI = {
  common: "⚪",
  uncommon: "🔵",
  rare: "🟡",
  mythic: "🔴",
} as const;

export function CardGrid({ cards, onCardClick }: CardGridProps) {
  return (
    <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-4">
      {cards.map((card, index) => {
        const thumbnail = card.thumbnail || card.faces_thumbnails?.[0];
        const rarityEmoji = card.rarity
          ? RARITY_EMOJI[card.rarity as keyof typeof RARITY_EMOJI]
          : "⚪";

        return (
          <Card
            key={`${card.id}-${index}`}
            className="overflow-hidden hover:shadow-lg transition-shadow cursor-pointer group"
            onClick={() => onCardClick(card)}
            data-testid="card-item"
          >
            <CardContent className="p-0">
              {/* Card Image */}
              <div className="relative aspect-[5/7] bg-muted">
                {thumbnail ? (
                  <Image
                    src={thumbnail}
                    alt={card.name || "Magic card"}
                    fill
                    className="object-cover group-hover:scale-105 transition-transform"
                    sizes="(max-width: 768px) 50vw, (max-width: 1024px) 33vw, (max-width: 1280px) 25vw, 20vw"
                  />
                ) : (
                  <div className="flex items-center justify-center h-full text-muted-foreground text-sm">
                    No image available
                  </div>
                )}
              </div>

              {/* Card Info */}
              <div className="p-3 space-y-2">
                <h3 className="font-semibold text-sm line-clamp-2 min-h-[2.5rem]">{card.name}</h3>

                <div className="flex items-center justify-between text-xs">
                  {card.mana_cost && (
                    <span className="text-muted-foreground truncate flex-1">{card.mana_cost}</span>
                  )}
                  {card.rarity && (
                    <span className="ml-2" title={card.rarity}>
                      {rarityEmoji}
                    </span>
                  )}
                </div>

                <Button
                  variant="secondary"
                  size="sm"
                  className="w-full"
                  onClick={(e) => {
                    e.stopPropagation();
                    onCardClick(card);
                  }}
                >
                  View Details
                </Button>
              </div>
            </CardContent>
          </Card>
        );
      })}
    </div>
  );
}
