"""Sample MTG card data for testing.

This module provides realistic MTG card data in MongoDB document format,
covering various edge cases (colorless, five-color, CMC 0, high CMC, double-faced).
"""

# Lightning Bolt - Red instant, CMC 1, common (basic testing)
LIGHTNING_BOLT = {
    "id": "550c74d4-a843-4208-a3c2-c71e84a21979",
    "oracle_id": "b29c8b8a-2c8f-4891-88bc-f35d07a68293",
    "name": "Lightning Bolt",
    "name_search": "lightning bolt",
    "lang": "en",
    "released_at": "1993-08-05",
    "layout": "normal",
    "cmc": 1.0,
    "type_line": "Instant",
    "oracle_text": "Lightning Bolt deals 3 damage to any target.",
    "mana_cost": "{R}",
    "colors": ["R"],
    "color_identity": ["R"],
    "rarity": "common",
    "set_name": "Limited Edition Alpha",
    "set": "lea",
    "artist": "Christopher Rush",
    "image_uris": {
        "small": "https://cards.scryfall.io/small/lightning-bolt.jpg",
        "normal": "https://cards.scryfall.io/normal/lightning-bolt.jpg",
        "large": "https://cards.scryfall.io/large/lightning-bolt.jpg",
        "png": "https://cards.scryfall.io/png/lightning-bolt.png",
        "art_crop": "https://cards.scryfall.io/art_crop/lightning-bolt.jpg",
        "border_crop": "https://cards.scryfall.io/border_crop/lightning-bolt.jpg",
    },
    "promo": False,
    "reprint": False,
}

# Lightning Bolt reprint - Same oracle_id, different set (for testing multiple printings)
LIGHTNING_BOLT_REPRINT = {
    "id": "a8c8c3c2-3f3d-4c7b-9c7a-1a2b3c4d5e6f",
    "oracle_id": "b29c8b8a-2c8f-4891-88bc-f35d07a68293",  # Same oracle_id as above
    "name": "Lightning Bolt",
    "name_search": "lightning bolt",
    "lang": "en",
    "released_at": "2020-08-07",
    "layout": "normal",
    "cmc": 1.0,
    "type_line": "Instant",
    "oracle_text": "Lightning Bolt deals 3 damage to any target.",
    "mana_cost": "{R}",
    "colors": ["R"],
    "color_identity": ["R"],
    "rarity": "uncommon",
    "set_name": "Double Masters",
    "set": "2xm",
    "artist": "Christopher Rush",
    "image_uris": {
        "small": "https://cards.scryfall.io/small/lightning-bolt-2xm.jpg",
        "normal": "https://cards.scryfall.io/normal/lightning-bolt-2xm.jpg",
        "large": "https://cards.scryfall.io/large/lightning-bolt-2xm.jpg",
        "png": "https://cards.scryfall.io/png/lightning-bolt-2xm.png",
        "art_crop": "https://cards.scryfall.io/art_crop/lightning-bolt-2xm.jpg",
        "border_crop": "https://cards.scryfall.io/border_crop/lightning-bolt-2xm.jpg",
    },
    "promo": False,
    "reprint": True,
}

# Counterspell - Blue instant, CMC 2, uncommon (different color/rarity)
COUNTERSPELL = {
    "id": "f56b3f35-e6c5-4a3f-b0f5-3c7e6a6b6c6d",
    "oracle_id": "a8d9e8f0-1c2d-3e4f-5a6b-7c8d9e0f1a2b",
    "name": "Counterspell",
    "name_search": "counterspell",
    "lang": "en",
    "released_at": "1993-08-05",
    "layout": "normal",
    "cmc": 2.0,
    "type_line": "Instant",
    "oracle_text": "Counter target spell.",
    "mana_cost": "{U}{U}",
    "colors": ["U"],
    "color_identity": ["U"],
    "rarity": "uncommon",
    "set_name": "Limited Edition Alpha",
    "set": "lea",
    "artist": "Mark Poole",
    "image_uris": {
        "small": "https://cards.scryfall.io/small/counterspell.jpg",
        "normal": "https://cards.scryfall.io/normal/counterspell.jpg",
        "large": "https://cards.scryfall.io/large/counterspell.jpg",
        "png": "https://cards.scryfall.io/png/counterspell.png",
        "art_crop": "https://cards.scryfall.io/art_crop/counterspell.jpg",
        "border_crop": "https://cards.scryfall.io/border_crop/counterspell.jpg",
    },
    "promo": False,
    "reprint": False,
}

# Black Lotus - Colorless artifact, CMC 0, rare (edge: colorless, CMC 0)
BLACK_LOTUS = {
    "id": "d2c7e3c9-8c7a-4c3a-9c7a-1a2b3c4d5e6f",
    "oracle_id": "c3c9e8f0-1c2d-3e4f-5a6b-7c8d9e0f1a2b",
    "name": "Black Lotus",
    "name_search": "black lotus",
    "lang": "en",
    "released_at": "1993-08-05",
    "layout": "normal",
    "cmc": 0.0,
    "type_line": "Artifact",
    "oracle_text": "{T}, Sacrifice Black Lotus: Add three mana of any one color.",
    "mana_cost": "{0}",
    "colors": [],
    "color_identity": [],
    "rarity": "rare",
    "set_name": "Limited Edition Alpha",
    "set": "lea",
    "artist": "Christopher Rush",
    "image_uris": {
        "small": "https://cards.scryfall.io/small/black-lotus.jpg",
        "normal": "https://cards.scryfall.io/normal/black-lotus.jpg",
        "large": "https://cards.scryfall.io/large/black-lotus.jpg",
        "png": "https://cards.scryfall.io/png/black-lotus.png",
        "art_crop": "https://cards.scryfall.io/art_crop/black-lotus.jpg",
        "border_crop": "https://cards.scryfall.io/border_crop/black-lotus.jpg",
    },
    "promo": False,
    "reprint": False,
}

# Progenitus - Five-color creature, CMC 10, mythic (edge: all colors, high CMC)
PROGENITUS = {
    "id": "a8b9c0d1-2e3f-4a5b-6c7d-8e9f0a1b2c3d",
    "oracle_id": "d1e2f3a4-5b6c-7d8e-9f0a-1b2c3d4e5f6a",
    "name": "Progenitus",
    "name_search": "progenitus",
    "lang": "en",
    "released_at": "2009-02-06",
    "layout": "normal",
    "cmc": 10.0,
    "type_line": "Legendary Creature — Hydra Avatar",
    "oracle_text": "Protection from everything\nIf Progenitus would be put into a graveyard from anywhere, reveal Progenitus and shuffle it into its owner's library instead.",
    "mana_cost": "{W}{W}{U}{U}{B}{B}{R}{R}{G}{G}",
    "colors": ["W", "U", "B", "R", "G"],
    "color_identity": ["W", "U", "B", "R", "G"],
    "power": "10",
    "toughness": "10",
    "rarity": "mythic",
    "set_name": "Conflux",
    "set": "con",
    "artist": "Jaime Jones",
    "image_uris": {
        "small": "https://cards.scryfall.io/small/progenitus.jpg",
        "normal": "https://cards.scryfall.io/normal/progenitus.jpg",
        "large": "https://cards.scryfall.io/large/progenitus.jpg",
        "png": "https://cards.scryfall.io/png/progenitus.png",
        "art_crop": "https://cards.scryfall.io/art_crop/progenitus.jpg",
        "border_crop": "https://cards.scryfall.io/border_crop/progenitus.jpg",
    },
    "promo": False,
    "reprint": False,
}

# Delver of Secrets - Double-faced card (edge: card_faces)
DELVER_OF_SECRETS = {
    "id": "f9c9d1e2-3a4b-5c6d-7e8f-9a0b1c2d3e4f",
    "oracle_id": "e2f3a4b5-6c7d-8e9f-0a1b-2c3d4e5f6a7b",
    "name": "Delver of Secrets // Insectile Aberration",
    "name_search": "delver of secrets // insectile aberration",
    "lang": "en",
    "released_at": "2011-09-30",
    "layout": "transform",
    "cmc": 1.0,
    "type_line": "Creature — Human Wizard // Creature — Human Insect",
    "colors": ["U"],
    "color_identity": ["U"],
    "rarity": "common",
    "set_name": "Innistrad",
    "set": "isd",
    "artist": "Nils Hamm",
    "card_faces": [
        {
            "name": "Delver of Secrets",
            "mana_cost": "{U}",
            "type_line": "Creature — Human Wizard",
            "oracle_text": "At the beginning of your upkeep, look at the top card of your library. You may reveal that card. If an instant or sorcery card is revealed this way, transform Delver of Secrets.",
            "power": "1",
            "toughness": "1",
            "image_uris": {
                "small": "https://cards.scryfall.io/small/delver-front.jpg",
                "normal": "https://cards.scryfall.io/normal/delver-front.jpg",
                "large": "https://cards.scryfall.io/large/delver-front.jpg",
                "png": "https://cards.scryfall.io/png/delver-front.png",
                "art_crop": "https://cards.scryfall.io/art_crop/delver-front.jpg",
                "border_crop": "https://cards.scryfall.io/border_crop/delver-front.jpg",
            },
        },
        {
            "name": "Insectile Aberration",
            "type_line": "Creature — Human Insect",
            "oracle_text": "Flying",
            "power": "3",
            "toughness": "2",
            "image_uris": {
                "small": "https://cards.scryfall.io/small/delver-back.jpg",
                "normal": "https://cards.scryfall.io/normal/delver-back.jpg",
                "large": "https://cards.scryfall.io/large/delver-back.jpg",
                "png": "https://cards.scryfall.io/png/delver-back.png",
                "art_crop": "https://cards.scryfall.io/art_crop/delver-back.jpg",
                "border_crop": "https://cards.scryfall.io/border_crop/delver-back.jpg",
            },
        },
    ],
    "promo": False,
    "reprint": False,
}

# Sol Ring - Colorless artifact, CMC 1, uncommon (popular colorless artifact)
SOL_RING = {
    "id": "a1b2c3d4-5e6f-7a8b-9c0d-1e2f3a4b5c6d",
    "oracle_id": "f6a7b8c9-0d1e-2f3a-4b5c-6d7e8f9a0b1c",
    "name": "Sol Ring",
    "name_search": "sol ring",
    "lang": "en",
    "released_at": "1993-08-05",
    "layout": "normal",
    "cmc": 1.0,
    "type_line": "Artifact",
    "oracle_text": "{T}: Add {C}{C}.",
    "mana_cost": "{1}",
    "colors": [],
    "color_identity": [],
    "rarity": "uncommon",
    "set_name": "Limited Edition Alpha",
    "set": "lea",
    "artist": "Mark Tedin",
    "image_uris": {
        "small": "https://cards.scryfall.io/small/sol-ring.jpg",
        "normal": "https://cards.scryfall.io/normal/sol-ring.jpg",
        "large": "https://cards.scryfall.io/large/sol-ring.jpg",
        "png": "https://cards.scryfall.io/png/sol-ring.png",
        "art_crop": "https://cards.scryfall.io/art_crop/sol-ring.jpg",
        "border_crop": "https://cards.scryfall.io/border_crop/sol-ring.jpg",
    },
    "promo": False,
    "reprint": False,
}

# Izzet Charm - Two-color (U/R) instant, CMC 2, uncommon
IZZET_CHARM = {
    "id": "b1c2d3e4-5f6a-7b8c-9d0e-1f2a3b4c5d6e",
    "oracle_id": "c2d3e4f5-6a7b-8c9d-0e1f-2a3b4c5d6e7f",
    "name": "Izzet Charm",
    "name_search": "izzet charm",
    "lang": "en",
    "released_at": "2012-10-05",
    "layout": "normal",
    "cmc": 2.0,
    "type_line": "Instant",
    "oracle_text": "Choose one — • Counter target noncreature spell unless its controller pays {2}. • Izzet Charm deals 2 damage to target creature. • Draw two cards, then discard two cards.",
    "mana_cost": "{U}{R}",
    "colors": ["U", "R"],
    "color_identity": ["U", "R"],
    "rarity": "uncommon",
    "set_name": "Return to Ravnica",
    "set": "rtr",
    "artist": "Zoltan Boros",
    "image_uris": {
        "small": "https://cards.scryfall.io/small/izzet-charm.jpg",
        "normal": "https://cards.scryfall.io/normal/izzet-charm.jpg",
        "large": "https://cards.scryfall.io/large/izzet-charm.jpg",
        "png": "https://cards.scryfall.io/png/izzet-charm.png",
        "art_crop": "https://cards.scryfall.io/art_crop/izzet-charm.jpg",
        "border_crop": "https://cards.scryfall.io/border_crop/izzet-charm.jpg",
    },
    "promo": False,
    "reprint": False,
}

# Giant Growth - Green instant, CMC 1, common
GIANT_GROWTH = {
    "id": "c3d4e5f6-7a8b-9c0d-1e2f-3a4b5c6d7e8f",
    "oracle_id": "d4e5f6a7-8b9c-0d1e-2f3a-4b5c6d7e8f9a",
    "name": "Giant Growth",
    "name_search": "giant growth",
    "lang": "en",
    "released_at": "1993-08-05",
    "layout": "normal",
    "cmc": 1.0,
    "type_line": "Instant",
    "oracle_text": "Target creature gets +3/+3 until end of turn.",
    "mana_cost": "{G}",
    "colors": ["G"],
    "color_identity": ["G"],
    "rarity": "common",
    "set_name": "Limited Edition Alpha",
    "set": "lea",
    "artist": "Sandra Everingham",
    "image_uris": {
        "small": "https://cards.scryfall.io/small/giant-growth.jpg",
        "normal": "https://cards.scryfall.io/normal/giant-growth.jpg",
        "large": "https://cards.scryfall.io/large/giant-growth.jpg",
        "png": "https://cards.scryfall.io/png/giant-growth.png",
        "art_crop": "https://cards.scryfall.io/art_crop/giant-growth.jpg",
        "border_crop": "https://cards.scryfall.io/border_crop/giant-growth.jpg",
    },
    "promo": False,
    "reprint": False,
}

# Serra Angel - White creature, CMC 5, uncommon
SERRA_ANGEL = {
    "id": "d5e6f7a8-9b0c-1d2e-3f4a-5b6c7d8e9f0a",
    "oracle_id": "e6f7a8b9-0c1d-2e3f-4a5b-6c7d8e9f0a1b",
    "name": "Serra Angel",
    "name_search": "serra angel",
    "lang": "en",
    "released_at": "1993-08-05",
    "layout": "normal",
    "cmc": 5.0,
    "type_line": "Creature — Angel",
    "oracle_text": "Flying, vigilance",
    "mana_cost": "{3}{W}{W}",
    "colors": ["W"],
    "color_identity": ["W"],
    "power": "4",
    "toughness": "4",
    "rarity": "uncommon",
    "set_name": "Limited Edition Alpha",
    "set": "lea",
    "artist": "Douglas Shuler",
    "image_uris": {
        "small": "https://cards.scryfall.io/small/serra-angel.jpg",
        "normal": "https://cards.scryfall.io/normal/serra-angel.jpg",
        "large": "https://cards.scryfall.io/large/serra-angel.jpg",
        "png": "https://cards.scryfall.io/png/serra-angel.png",
        "art_crop": "https://cards.scryfall.io/art_crop/serra-angel.jpg",
        "border_crop": "https://cards.scryfall.io/border_crop/serra-angel.jpg",
    },
    "promo": False,
    "reprint": False,
}

# Doom Blade - Black instant, CMC 2, common
DOOM_BLADE = {
    "id": "e7f8a9b0-1c2d-3e4f-5a6b-7c8d9e0f1a2b",
    "oracle_id": "f8a9b0c1-2d3e-4f5a-6b7c-8d9e0f1a2b3c",
    "name": "Doom Blade",
    "name_search": "doom blade",
    "lang": "en",
    "released_at": "2010-07-16",
    "layout": "normal",
    "cmc": 2.0,
    "type_line": "Instant",
    "oracle_text": "Destroy target nonblack creature.",
    "mana_cost": "{1}{B}",
    "colors": ["B"],
    "color_identity": ["B"],
    "rarity": "common",
    "set_name": "Magic 2011",
    "set": "m11",
    "artist": "Chippy",
    "image_uris": {
        "small": "https://cards.scryfall.io/small/doom-blade.jpg",
        "normal": "https://cards.scryfall.io/normal/doom-blade.jpg",
        "large": "https://cards.scryfall.io/large/doom-blade.jpg",
        "png": "https://cards.scryfall.io/png/doom-blade.png",
        "art_crop": "https://cards.scryfall.io/art_crop/doom-blade.jpg",
        "border_crop": "https://cards.scryfall.io/border_crop/doom-blade.jpg",
    },
    "promo": False,
    "reprint": False,
}

# Emrakul, the Aeons Torn - Colorless creature, CMC 15, mythic
EMRAKUL = {
    "id": "f9a0b1c2-3d4e-5f6a-7b8c-9d0e1f2a3b4c",
    "oracle_id": "a0b1c2d3-4e5f-6a7b-8c9d-0e1f2a3b4c5d",
    "name": "Emrakul, the Aeons Torn",
    "name_search": "emrakul, the aeons torn",
    "lang": "en",
    "released_at": "2010-04-23",
    "layout": "normal",
    "cmc": 15.0,
    "type_line": "Legendary Creature — Eldrazi",
    "oracle_text": "Emrakul, the Aeons Torn can't be countered.\nWhen you cast this spell, take an extra turn after this one.\nFlying, protection from colored spells, annihilator 6\nWhen Emrakul is put into a graveyard from anywhere, its owner shuffles their graveyard into their library.",
    "mana_cost": "{15}",
    "colors": [],  # Colorless
    "color_identity": [],
    "power": "15",
    "toughness": "15",
    "rarity": "mythic",
    "set_name": "Rise of the Eldrazi",
    "set": "roe",
    "artist": "Mark Tedin",
    "image_uris": {
        "small": "https://cards.scryfall.io/small/emrakul.jpg",
        "normal": "https://cards.scryfall.io/normal/emrakul.jpg",
        "large": "https://cards.scryfall.io/large/emrakul.jpg",
        "png": "https://cards.scryfall.io/png/emrakul.png",
        "art_crop": "https://cards.scryfall.io/art_crop/emrakul.jpg",
        "border_crop": "https://cards.scryfall.io/border_crop/emrakul.jpg",
    },
    "promo": False,
    "reprint": False,
}


def get_all_sample_cards() -> list[dict]:
    """Get all sample cards as a list.

    Returns:
        List of all sample card dictionaries.
    """
    return [
        LIGHTNING_BOLT,
        LIGHTNING_BOLT_REPRINT,
        COUNTERSPELL,
        BLACK_LOTUS,
        PROGENITUS,
        DELVER_OF_SECRETS,
        SOL_RING,
        IZZET_CHARM,
        GIANT_GROWTH,
        SERRA_ANGEL,
        DOOM_BLADE,
        EMRAKUL,
    ]


def get_card_by_name(name: str) -> dict | None:
    """Get a card by its name.

    Args:
        name: Card name to search for.

    Returns:
        Card dictionary if found, None otherwise.
    """
    for card in get_all_sample_cards():
        if card["name"] == name or card["name"].startswith(name):
            return card
    return None


def get_cards_by_oracle_id(oracle_id: str) -> list[dict]:
    """Get all cards with the same oracle_id (all printings).

    Args:
        oracle_id: Oracle ID to search for.

    Returns:
        List of cards with matching oracle_id.
    """
    return [card for card in get_all_sample_cards() if card["oracle_id"] == oracle_id]


def get_sample_cards_by_color(color: str) -> list[dict]:
    """Get all cards containing a specific color.

    Args:
        color: Color to search for (W, U, B, R, G).

    Returns:
        List of cards containing the color.
    """
    return [card for card in get_all_sample_cards() if color in card.get("colors", [])]
