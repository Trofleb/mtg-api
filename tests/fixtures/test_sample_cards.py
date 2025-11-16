"""Tests for sample card data fixtures.

This module validates that the sample card data has correct structure
and that helper functions work as expected.
"""

import pytest

from tests.fixtures.sample_cards import (
    LIGHTNING_BOLT,
    LIGHTNING_BOLT_REPRINT,
    get_all_sample_cards,
    get_card_by_name,
    get_cards_by_oracle_id,
    get_sample_cards_by_color,
)

# Required fields that all cards must have
REQUIRED_FIELDS = [
    "id",
    "oracle_id",
    "name",
    "lang",
    "released_at",
    "layout",
    "cmc",
    "type_line",
    "colors",
    "color_identity",
    "rarity",
    "set_name",
    "set",
    "artist",
]


@pytest.mark.unit
def test_all_sample_cards_have_required_fields():
    """Test that all sample cards have required fields."""
    cards = get_all_sample_cards()

    assert len(cards) >= 6, "Should have at least 6 sample cards"

    for card in cards:
        for field in REQUIRED_FIELDS:
            assert field in card, (
                f"Card '{card.get('name', 'unknown')}' missing field: {field}"
            )


@pytest.mark.unit
def test_lightning_bolt_has_correct_attributes():
    """Test that Lightning Bolt card has correct attributes."""
    card = LIGHTNING_BOLT

    assert card["name"] == "Lightning Bolt"
    assert card["cmc"] == 1.0
    assert card["colors"] == ["R"]
    assert card["rarity"] == "common"
    assert card["type_line"] == "Instant"
    assert card["mana_cost"] == "{R}"
    assert "image_uris" in card
    assert "oracle_text" in card


@pytest.mark.unit
def test_multiple_printings_share_oracle_id():
    """Test that Lightning Bolt printings share the same oracle_id."""
    assert LIGHTNING_BOLT["oracle_id"] == LIGHTNING_BOLT_REPRINT["oracle_id"]
    assert LIGHTNING_BOLT["id"] != LIGHTNING_BOLT_REPRINT["id"]
    assert LIGHTNING_BOLT["set"] != LIGHTNING_BOLT_REPRINT["set"]


@pytest.mark.unit
def test_get_card_by_name_returns_correct_card():
    """Test that get_card_by_name helper function works."""
    card = get_card_by_name("Lightning Bolt")

    assert card is not None
    assert card["name"] == "Lightning Bolt"

    # Test non-existent card
    card = get_card_by_name("Nonexistent Card")
    assert card is None


@pytest.mark.unit
def test_get_cards_by_oracle_id_returns_all_printings():
    """Test that get_cards_by_oracle_id returns all printings."""
    oracle_id = LIGHTNING_BOLT["oracle_id"]
    printings = get_cards_by_oracle_id(oracle_id)

    assert len(printings) == 2
    assert all(card["oracle_id"] == oracle_id for card in printings)
    assert all(card["name"] == "Lightning Bolt" for card in printings)

    # Verify they have different sets
    sets = {card["set"] for card in printings}
    assert len(sets) == 2


@pytest.mark.unit
def test_sample_cards_cover_edge_cases():
    """Test that sample cards cover important edge cases."""
    cards = get_all_sample_cards()

    # Test colorless cards exist
    colorless_cards = [card for card in cards if not card["colors"]]
    assert len(colorless_cards) >= 2, "Should have at least 2 colorless cards"

    # Test CMC 0 exists
    cmc_zero_cards = [card for card in cards if card["cmc"] == 0.0]
    assert len(cmc_zero_cards) >= 1, "Should have at least 1 CMC 0 card"

    # Test high CMC exists
    high_cmc_cards = [card for card in cards if card["cmc"] >= 10.0]
    assert len(high_cmc_cards) >= 1, "Should have at least 1 high CMC card"

    # Test five-color exists
    five_color_cards = [card for card in cards if len(card["colors"]) == 5]
    assert len(five_color_cards) >= 1, "Should have at least 1 five-color card"

    # Test double-faced card exists
    double_faced_cards = [card for card in cards if "card_faces" in card]
    assert len(double_faced_cards) >= 1, "Should have at least 1 double-faced card"


@pytest.mark.unit
def test_get_sample_cards_by_color_works():
    """Test that get_sample_cards_by_color returns correct cards."""
    red_cards = get_sample_cards_by_color("R")
    assert len(red_cards) >= 1
    assert all("R" in card["colors"] for card in red_cards)

    # Test five-color card appears in all color searches
    for color in ["W", "U", "B", "R", "G"]:
        colored_cards = get_sample_cards_by_color(color)
        progenitus_in_results = any(
            card["name"] == "Progenitus" for card in colored_cards
        )
        assert progenitus_in_results, f"Progenitus should appear in {color} search"


@pytest.mark.unit
def test_image_uris_structure():
    """Test that image_uris have correct structure."""
    card = LIGHTNING_BOLT

    assert "image_uris" in card
    image_uris = card["image_uris"]

    # Check all required image sizes exist
    required_image_keys = ["small", "normal", "large", "png", "art_crop", "border_crop"]
    for key in required_image_keys:
        assert key in image_uris, f"Missing image_uris key: {key}"
        assert isinstance(image_uris[key], str)
        assert image_uris[key].startswith("https://")
