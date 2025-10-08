"""Unit tests for card resource API endpoints."""

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from fastapi import HTTPException

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))


@pytest.fixture
def mock_collection():
    """Mock MongoDB collection for testing."""
    return MagicMock()


class TestGetCardByScryfallID:
    """Test suite for GET /cards/id/{scryfall_id} endpoint."""

    def test_get_card_by_scryfall_id_success(self, mock_collection):
        """Test successful card retrieval by Scryfall ID."""
        # Mock data
        mock_card = {
            "id": "bd8fa327-dd41-4737-8f19-2cf5eb1f7cdd",
            "oracle_id": "e3285e6b-3e79-4d7c-bf96-d920f973b122",
            "name": "Lightning Bolt",
            "image_uris": {
                "small": "https://cards.scryfall.io/small/front/b/d/bd8fa327.jpg",
                "normal": "https://cards.scryfall.io/normal/front/b/d/bd8fa327.jpg",
                "large": "https://cards.scryfall.io/large/front/b/d/bd8fa327.jpg",
                "png": "https://cards.scryfall.io/png/front/b/d/bd8fa327.png",
                "art_crop": "https://cards.scryfall.io/art_crop/front/b/d/bd8fa327.jpg",
                "border_crop": "https://cards.scryfall.io/border_crop/front/b/d/bd8fa327.jpg",
            },
        }
        mock_collection.find_one.return_value = mock_card

        # Import after mocking to avoid module-level side effects
        with patch("api.router.cards.collection", mock_collection):
            from api.router.cards import get_card_by_scryfall_id

            result = get_card_by_scryfall_id("bd8fa327-dd41-4737-8f19-2cf5eb1f7cdd")

        # Assert correct query was made
        mock_collection.find_one.assert_called_once()
        call_args = mock_collection.find_one.call_args
        assert call_args[0][0] == {"id": "bd8fa327-dd41-4737-8f19-2cf5eb1f7cdd"}

        # Assert response includes all required fields
        assert result["id"] == "bd8fa327-dd41-4737-8f19-2cf5eb1f7cdd"
        assert result["oracle_id"] == "e3285e6b-3e79-4d7c-bf96-d920f973b122"
        assert result["name"] == "Lightning Bolt"
        assert "image_uris" in result

    def test_get_card_by_scryfall_id_not_found(self, mock_collection):
        """Test 404 when Scryfall ID doesn't exist."""
        mock_collection.find_one.return_value = None

        with patch("api.router.cards.collection", mock_collection):
            from api.router.cards import get_card_by_scryfall_id

            with pytest.raises(HTTPException) as exc_info:
                get_card_by_scryfall_id("nonexistent-id")

        assert exc_info.value.status_code == 404
        assert "not found" in exc_info.value.detail.lower()

    def test_get_card_by_scryfall_id_includes_images(self, mock_collection):
        """Test response includes all image_uris fields."""
        mock_card = {
            "id": "test-id",
            "oracle_id": "test-oracle",
            "name": "Test Card",
            "image_uris": {
                "small": "https://example.com/small.jpg",
                "normal": "https://example.com/normal.jpg",
                "large": "https://example.com/large.jpg",
                "png": "https://example.com/card.png",
                "art_crop": "https://example.com/art.jpg",
                "border_crop": "https://example.com/border.jpg",
            },
        }
        mock_collection.find_one.return_value = mock_card

        with patch("api.router.cards.collection", mock_collection):
            from api.router.cards import get_card_by_scryfall_id

            result = get_card_by_scryfall_id("test-id")

        # Assert all image variants present
        assert "image_uris" in result
        image_uris = result["image_uris"]
        assert "small" in image_uris
        assert "normal" in image_uris
        assert "large" in image_uris
        assert "png" in image_uris
        assert "art_crop" in image_uris
        assert "border_crop" in image_uris


class TestGetCardsByOracleID:
    """Test suite for GET /cards/oracle/{oracle_id} endpoint."""

    def test_get_cards_by_oracle_id_success(self, mock_collection):
        """Test successful retrieval of all printings."""
        # Mock multiple card printings
        mock_cards = [
            {
                "id": f"scryfall-{i}",
                "oracle_id": "shared-oracle-id",
                "name": "Test Card",
                "set": f"set{i}",
                "image_uris": {"normal": f"https://example.com/{i}.jpg"},
            }
            for i in range(5)
        ]

        # Mock MongoDB cursor
        mock_cursor = MagicMock()
        mock_cursor.sort.return_value = mock_cards
        mock_collection.find.return_value = mock_cursor

        with patch("api.router.cards.collection", mock_collection):
            from api.router.cards import get_cards_by_oracle_id

            result = get_cards_by_oracle_id("shared-oracle-id")

        # Assert correct query was made
        mock_collection.find.assert_called_once()
        call_args = mock_collection.find.call_args
        assert call_args[0][0] == {"oracle_id": "shared-oracle-id"}

        # Assert multiple printings returned
        assert len(result) == 5
        for card in result:
            assert card["oracle_id"] == "shared-oracle-id"
            assert "image_uris" in card

    def test_get_cards_by_oracle_id_empty(self, mock_collection):
        """Test 404 when Oracle ID has no printings."""
        mock_cursor = MagicMock()
        mock_cursor.sort.return_value = []
        mock_collection.find.return_value = mock_cursor

        with patch("api.router.cards.collection", mock_collection):
            from api.router.cards import get_cards_by_oracle_id

            with pytest.raises(HTTPException) as exc_info:
                get_cards_by_oracle_id("nonexistent-oracle-id")

        assert exc_info.value.status_code == 404
        assert "no cards found" in exc_info.value.detail.lower()

    def test_get_cards_by_oracle_id_single_printing(self, mock_collection):
        """Test Oracle ID with only one printing."""
        mock_card = {
            "id": "single-scryfall-id",
            "oracle_id": "single-oracle-id",
            "name": "Unique Card",
            "image_uris": {"normal": "https://example.com/unique.jpg"},
        }

        mock_cursor = MagicMock()
        mock_cursor.sort.return_value = [mock_card]
        mock_collection.find.return_value = mock_cursor

        with patch("api.router.cards.collection", mock_collection):
            from api.router.cards import get_cards_by_oracle_id

            result = get_cards_by_oracle_id("single-oracle-id")

        assert len(result) == 1
        assert result[0]["id"] == "single-scryfall-id"
        assert result[0]["oracle_id"] == "single-oracle-id"

    def test_get_cards_by_oracle_id_image_consistency(self, mock_collection):
        """Test all returned cards include image_uris."""
        mock_cards = [
            {
                "id": f"id-{i}",
                "oracle_id": "oracle",
                "image_uris": {
                    "normal": f"https://example.com/{i}.jpg",
                    "large": f"https://example.com/{i}_large.jpg",
                },
            }
            for i in range(3)
        ]

        mock_cursor = MagicMock()
        mock_cursor.sort.return_value = mock_cards
        mock_collection.find.return_value = mock_cursor

        with patch("api.router.cards.collection", mock_collection):
            from api.router.cards import get_cards_by_oracle_id

            result = get_cards_by_oracle_id("oracle")

        # Assert every card has image_uris
        for card in result:
            assert "image_uris" in card
            assert "normal" in card["image_uris"]
