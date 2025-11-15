"use client";

import Image from "next/image";
import { Badge } from "@/components/ui/badge";
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { ScrollArea } from "@/components/ui/scroll-area";
import type { OracleCard } from "@/lib/api";

interface CardDetailsDialogProps {
  card: OracleCard;
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

export function CardDetailsDialog({ card, open, onOpenChange }: CardDetailsDialogProps) {
  const thumbnail = card.thumbnail || card.faces_thumbnails?.[0];

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-4xl max-h-[90vh]">
        <DialogHeader>
          <DialogTitle>{card.name}</DialogTitle>
        </DialogHeader>

        <ScrollArea className="max-h-[calc(90vh-8rem)]">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Left Column - Image(s) */}
            <div className="space-y-4">
              {thumbnail ? (
                <div className="relative aspect-[5/7] w-full">
                  <Image
                    src={thumbnail}
                    alt={card.name || "Magic card"}
                    fill
                    className="object-contain rounded-lg"
                    sizes="(max-width: 768px) 100vw, 50vw"
                    priority
                  />
                </div>
              ) : card.faces_thumbnails && card.faces_thumbnails.length > 0 ? (
                <div className="space-y-4">
                  {card.faces_thumbnails.map((img, i) => (
                    <div key={i} className="relative aspect-[5/7] w-full">
                      <Image
                        src={img}
                        alt={`${card.name} face ${i + 1}`}
                        fill
                        className="object-contain rounded-lg"
                        sizes="(max-width: 768px) 100vw, 50vw"
                        priority={i === 0}
                      />
                    </div>
                  ))}
                </div>
              ) : (
                <div className="aspect-[5/7] bg-muted rounded-lg flex items-center justify-center">
                  <p className="text-muted-foreground">No image available</p>
                </div>
              )}
            </div>

            {/* Right Column - Details */}
            <div className="space-y-4">
              {/* Type Line */}
              {card.type_line && (
                <div>
                  <h3 className="font-semibold text-sm text-muted-foreground mb-1">Type</h3>
                  <p>{card.type_line}</p>
                </div>
              )}

              {/* Mana Cost & CMC */}
              <div className="grid grid-cols-2 gap-4">
                {card.mana_cost && (
                  <div>
                    <h3 className="font-semibold text-sm text-muted-foreground mb-1">Mana Cost</h3>
                    <p className="font-mono">{card.mana_cost}</p>
                  </div>
                )}
                {card.cmc !== undefined && (
                  <div>
                    <h3 className="font-semibold text-sm text-muted-foreground mb-1">CMC</h3>
                    <p>{card.cmc}</p>
                  </div>
                )}
              </div>

              {/* Colors */}
              {card.colors && card.colors.length > 0 && (
                <div>
                  <h3 className="font-semibold text-sm text-muted-foreground mb-1">Colors</h3>
                  <div className="flex gap-1">
                    {card.colors.map((color) => (
                      <Badge key={color} variant="secondary">
                        {color}
                      </Badge>
                    ))}
                  </div>
                </div>
              )}

              {/* Rarity */}
              {card.rarity && (
                <div>
                  <h3 className="font-semibold text-sm text-muted-foreground mb-1">Rarity</h3>
                  <Badge className="capitalize">{card.rarity}</Badge>
                </div>
              )}

              {/* Oracle Text */}
              {card.card_text && (
                <div>
                  <h3 className="font-semibold text-sm text-muted-foreground mb-1">Oracle Text</h3>
                  <p className="whitespace-pre-wrap text-sm">{card.card_text}</p>
                </div>
              )}

              {/* Printings */}
              {card.card_count !== undefined && (
                <div>
                  <h3 className="font-semibold text-sm text-muted-foreground mb-1">Printings</h3>
                  <p>{card.card_count}</p>
                </div>
              )}

              {/* Rankings */}
              <div className="grid grid-cols-2 gap-4">
                {card.edhrec_rank !== undefined && (
                  <div>
                    <h3 className="font-semibold text-sm text-muted-foreground mb-1">
                      EDHREC Rank
                    </h3>
                    <p>#{card.edhrec_rank}</p>
                  </div>
                )}
                {card.penny_rank !== undefined && (
                  <div>
                    <h3 className="font-semibold text-sm text-muted-foreground mb-1">Penny Rank</h3>
                    <p>#{card.penny_rank}</p>
                  </div>
                )}
              </div>

              {/* All Printings */}
              {card.cards && card.cards.length > 0 && (
                <div>
                  <h3 className="font-semibold text-sm text-muted-foreground mb-2">
                    All Printings ({card.cards.length})
                  </h3>
                  <ScrollArea className="h-48 rounded border p-4">
                    <div className="space-y-3">
                      {card.cards.map((printing, i) => (
                        <div
                          key={`${printing.id}-${i}`}
                          className="flex items-start gap-3 pb-3 border-b last:border-0"
                        >
                          {printing.image_uris?.small && (
                            <div className="relative w-16 h-22 flex-shrink-0">
                              <Image
                                src={printing.image_uris.small}
                                alt={printing.set_name}
                                fill
                                className="object-contain rounded"
                                sizes="64px"
                              />
                            </div>
                          )}
                          <div className="flex-1 min-w-0">
                            <p className="font-semibold text-sm">{printing.set_name}</p>
                            <p className="text-xs text-muted-foreground">
                              Set: {printing.set.toUpperCase()}
                            </p>
                            <p className="text-xs text-muted-foreground">
                              Released: {printing.released_at}
                            </p>
                          </div>
                        </div>
                      ))}
                    </div>
                  </ScrollArea>
                </div>
              )}
            </div>
          </div>
        </ScrollArea>
      </DialogContent>
    </Dialog>
  );
}
