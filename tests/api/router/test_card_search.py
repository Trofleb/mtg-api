"""Unit tests for enhanced card search endpoint with filters."""

from unittest.mock import MagicMock, patch

import pytest

from api.router.cards import CardFilter


@pytest.fixture
def mock_collection():
    """Mock MongoDB collection for testing."""
    return MagicMock()


class TestCardFilterModel:
    """Test suite for CardFilter Pydantic model."""

    def test_card_filter_empty(self):
        filter_obj = CardFilter()
        assert filter_obj.sets is None
        assert filter_obj.colors is None
        assert filter_obj.color_operator == "or"
        assert filter_obj.cmc_min is None
        assert filter_obj.cmc_max is None
        assert filter_obj.types is None
        assert filter_obj.rarities is None

    def test_card_filter_sets_only(self):
        """Test CardFilter with only set filter."""

        filter_obj = CardFilter(sets=["Dominaria", "Kamigawa: Neon Dynasty"])
        assert filter_obj.sets == ["Dominaria", "Kamigawa: Neon Dynasty"]
        assert filter_obj.colors is None

    def test_card_filter_colors_or(self):
        filter_obj = CardFilter(colors=["R", "G"], color_operator="or")
        assert filter_obj.colors == ["R", "G"]
        assert filter_obj.color_operator == "or"

    def test_card_filter_colors_and(self):
        """Test CardFilter with color 'and' operator."""

        filter_obj = CardFilter(colors=["U", "B"], color_operator="and")
        assert filter_obj.colors == ["U", "B"]
        assert filter_obj.color_operator == "and"

    def test_card_filter_colors_exactly(self):
        filter_obj = CardFilter(colors=["W"], color_operator="exactly")
        assert filter_obj.colors == ["W"]
        assert filter_obj.color_operator == "exactly"

    def test_card_filter_cmc_range(self):
        """Test CardFilter with CMC min and max."""

        filter_obj = CardFilter(cmc_min=2, cmc_max=4)
        assert filter_obj.cmc_min == 2
        assert filter_obj.cmc_max == 4

    def test_card_filter_cmc_min_only(self):
        filter_obj = CardFilter(cmc_min=5)
        assert filter_obj.cmc_min == 5
        assert filter_obj.cmc_max is None

    def test_card_filter_cmc_max_only(self):
        """Test CardFilter with only CMC max."""

        filter_obj = CardFilter(cmc_max=3)
        assert filter_obj.cmc_min is None
        assert filter_obj.cmc_max == 3

    def test_card_filter_types(self):
        filter_obj = CardFilter(types=["Creature", "Instant"])
        assert filter_obj.types == ["Creature", "Instant"]

    def test_card_filter_rarities(self):
        """Test CardFilter with rarities."""

        filter_obj = CardFilter(rarities=["rare", "mythic"])
        assert filter_obj.rarities == ["rare", "mythic"]

    def test_card_filter_all_filters(self):
        filter_obj = CardFilter(
            sets=["Modern Horizons 2"],
            colors=["W", "U"],
            color_operator="and",
            cmc_min=1,
            cmc_max=5,
            types=["Creature"],
            rarities=["uncommon", "rare"],
        )
        assert filter_obj.sets == ["Modern Horizons 2"]
        assert filter_obj.colors == ["W", "U"]
        assert filter_obj.color_operator == "and"
        assert filter_obj.cmc_min == 1
        assert filter_obj.cmc_max == 5
        assert filter_obj.types == ["Creature"]
        assert filter_obj.rarities == ["uncommon", "rare"]


class TestSearchCardByTextFilters:
    """Test suite for search_card_by_text endpoint with filters."""

    def test_search_no_filters(self, mock_collection):
        """Test search with no filters applied."""
        # Mock aggregation results
        mock_results = [
            {
                "_id": "oracle-1",
                "name": "Lightning Bolt",
                "score": 10.5,
                "card_text": "Deal 3 damage",
                "thumbnail": "https://example.com/bolt.jpg",
            }
        ]
        mock_collection.aggregate.return_value = mock_results

        with patch("api.router.cards.collection", mock_collection):
            from api.router.cards import search_card_by_text

            result = search_card_by_text("Lightning Bolt")

        # Verify aggregation was called
        mock_collection.aggregate.assert_called_once()
        pipeline = mock_collection.aggregate.call_args[0][0]

        # Check match stage
        match_stage = pipeline[0]["$match"]
        assert "$text" in match_stage
        assert match_stage["$text"]["$search"] == "Lightning Bolt"
        assert match_stage["lang"] == {"$eq": "en"}

        # Verify result structure
        assert "cards" in result
        assert "cursor" in result
        assert "has_more" in result
        assert len(result["cards"]) == 1

    def test_search_with_set_filter(self, mock_collection):
        mock_results = [
            {"_id": "oracle-1", "name": "Test Card", "score": 8.0, "set_name": "Alpha"}
        ]
        mock_collection.aggregate.return_value = mock_results

        with patch("api.router.cards.collection", mock_collection):
            from api.router.cards import search_card_by_text

            card_filter = CardFilter(sets=["Alpha", "Beta"])
            search_card_by_text("Test", card_filter=card_filter)

        pipeline = mock_collection.aggregate.call_args[0][0]
        match_stage = pipeline[0]["$match"]

        # Verify set filter in match conditions
        assert "set_name" in match_stage
        assert match_stage["set_name"] == {"$in": ["Alpha", "Beta"]}

    def test_search_with_color_filter_or(self, mock_collection):
        """Test search with color 'or' operator."""

        mock_results = []
        mock_collection.aggregate.return_value = mock_results

        with patch("api.router.cards.collection", mock_collection):
            from api.router.cards import search_card_by_text

            card_filter = CardFilter(colors=["R", "G"], color_operator="or")
            search_card_by_text("card", card_filter=card_filter)

        pipeline = mock_collection.aggregate.call_args[0][0]
        match_stage = pipeline[0]["$match"]

        # Verify color filter with 'or' operator
        assert "colors" in match_stage
        assert match_stage["colors"] == {"$in": ["R", "G"]}

    def test_search_with_color_filter_and(self, mock_collection):
        mock_results = []
        mock_collection.aggregate.return_value = mock_results

        with patch("api.router.cards.collection", mock_collection):
            from api.router.cards import search_card_by_text

            card_filter = CardFilter(colors=["U", "B"], color_operator="and")
            search_card_by_text("card", card_filter=card_filter)

        pipeline = mock_collection.aggregate.call_args[0][0]
        match_stage = pipeline[0]["$match"]

        # Verify color filter with 'and' operator
        assert "colors" in match_stage
        assert match_stage["colors"] == {"$all": ["U", "B"]}

    def test_search_with_color_filter_exactly(self, mock_collection):
        """Test search with color 'exactly' operator."""

        mock_results = []
        mock_collection.aggregate.return_value = mock_results

        with patch("api.router.cards.collection", mock_collection):
            from api.router.cards import search_card_by_text

            card_filter = CardFilter(colors=["W"], color_operator="exactly")
            search_card_by_text("card", card_filter=card_filter)

        pipeline = mock_collection.aggregate.call_args[0][0]
        match_stage = pipeline[0]["$match"]

        # Verify color filter with 'exactly' operator
        assert "colors" in match_stage
        # Should have both $size and $all checks
        assert match_stage["colors"] == {"$all": ["W"]}

    def test_search_with_cmc_min(self, mock_collection):
        mock_results = []
        mock_collection.aggregate.return_value = mock_results

        with patch("api.router.cards.collection", mock_collection):
            from api.router.cards import search_card_by_text

            card_filter = CardFilter(cmc_min=3)
            search_card_by_text("card", card_filter=card_filter)

        pipeline = mock_collection.aggregate.call_args[0][0]
        match_stage = pipeline[0]["$match"]

        # Verify CMC min filter
        assert "cmc" in match_stage
        assert "$gte" in match_stage["cmc"]
        assert match_stage["cmc"]["$gte"] == 3

    def test_search_with_cmc_max(self, mock_collection):
        """Test search with CMC maximum filter."""

        mock_results = []
        mock_collection.aggregate.return_value = mock_results

        with patch("api.router.cards.collection", mock_collection):
            from api.router.cards import search_card_by_text

            card_filter = CardFilter(cmc_max=5)
            search_card_by_text("card", card_filter=card_filter)

        pipeline = mock_collection.aggregate.call_args[0][0]
        match_stage = pipeline[0]["$match"]

        # Verify CMC max filter
        assert "cmc" in match_stage
        assert "$lte" in match_stage["cmc"]
        assert match_stage["cmc"]["$lte"] == 5

    def test_search_with_cmc_range(self, mock_collection):
        mock_results = []
        mock_collection.aggregate.return_value = mock_results

        with patch("api.router.cards.collection", mock_collection):
            from api.router.cards import search_card_by_text

            card_filter = CardFilter(cmc_min=2, cmc_max=4)
            search_card_by_text("card", card_filter=card_filter)

        pipeline = mock_collection.aggregate.call_args[0][0]
        match_stage = pipeline[0]["$match"]

        # Verify CMC range filter
        assert "cmc" in match_stage
        assert "$gte" in match_stage["cmc"]
        assert "$lte" in match_stage["cmc"]
        assert match_stage["cmc"]["$gte"] == 2
        assert match_stage["cmc"]["$lte"] == 4

    def test_search_with_type_filter(self, mock_collection):
        """Test search with card type filter."""

        mock_results = []
        mock_collection.aggregate.return_value = mock_results

        with patch("api.router.cards.collection", mock_collection):
            from api.router.cards import search_card_by_text

            card_filter = CardFilter(types=["Creature", "Instant"])
            search_card_by_text("card", card_filter=card_filter)

        pipeline = mock_collection.aggregate.call_args[0][0]
        match_stage = pipeline[0]["$match"]

        # Verify type filter with regex
        assert "$or" in match_stage
        type_patterns = match_stage["$or"]
        assert len(type_patterns) == 2
        assert type_patterns[0]["type_line"]["$regex"] == "Creature"
        assert type_patterns[0]["type_line"]["$options"] == "i"
        assert type_patterns[1]["type_line"]["$regex"] == "Instant"

    def test_search_with_rarity_filter(self, mock_collection):
        mock_results = []
        mock_collection.aggregate.return_value = mock_results

        with patch("api.router.cards.collection", mock_collection):
            from api.router.cards import search_card_by_text

            card_filter = CardFilter(rarities=["rare", "mythic"])
            search_card_by_text("card", card_filter=card_filter)

        pipeline = mock_collection.aggregate.call_args[0][0]
        match_stage = pipeline[0]["$match"]

        # Verify rarity filter
        assert "rarity" in match_stage
        assert match_stage["rarity"] == {"$in": ["rare", "mythic"]}

    def test_search_with_all_filters_combined(self, mock_collection):
        """Test search with all filters applied simultaneously."""

        mock_results = []
        mock_collection.aggregate.return_value = mock_results

        with patch("api.router.cards.collection", mock_collection):
            from api.router.cards import search_card_by_text

            card_filter = CardFilter(
                sets=["Dominaria"],
                colors=["W", "U"],
                color_operator="and",
                cmc_min=2,
                cmc_max=4,
                types=["Creature"],
                rarities=["uncommon"],
            )
            search_card_by_text("angel", card_filter=card_filter)

        pipeline = mock_collection.aggregate.call_args[0][0]
        match_stage = pipeline[0]["$match"]

        # Verify all filters are present
        assert "$text" in match_stage
        assert "set_name" in match_stage
        assert "colors" in match_stage
        assert "cmc" in match_stage
        assert "$or" in match_stage
        assert "rarity" in match_stage

        # Verify specific filter values
        assert match_stage["set_name"] == {"$in": ["Dominaria"]}
        assert match_stage["colors"] == {"$all": ["W", "U"]}
        assert match_stage["cmc"]["$gte"] == 2
        assert match_stage["cmc"]["$lte"] == 4
        assert match_stage["rarity"] == {"$in": ["uncommon"]}

    def test_search_pagination_with_cursor(self, mock_collection):
        """Test search pagination using cursor."""
        mock_results = [
            {"_id": f"oracle-{i}", "name": f"Card {i}", "score": 10.0 - i}
            for i in range(11)
        ]
        mock_collection.aggregate.return_value = mock_results

        with patch("api.router.cards.collection", mock_collection):
            from api.router.cards import search_card_by_text

            search_card_by_text("test", cursor="9.5")

        pipeline = mock_collection.aggregate.call_args[0][0]

        # Find the cursor match stage
        cursor_match = None
        for stage in pipeline:
            if "$match" in stage and "score" in stage["$match"]:
                cursor_match = stage["$match"]
                break

        # Verify cursor filter
        assert cursor_match is not None
        assert "score" in cursor_match
        assert "$lt" in cursor_match["score"]
        assert cursor_match["score"]["$lt"] == 9.5

    def test_search_pagination_result_structure(self, mock_collection):
        """Test pagination result includes correct fields."""
        # Return 11 results (page_count + 1)
        mock_results = [
            {"_id": f"oracle-{i}", "name": f"Card {i}", "score": 10.0 - i}
            for i in range(11)
        ]
        mock_collection.aggregate.return_value = mock_results

        with patch("api.router.cards.collection", mock_collection):
            from api.router.cards import search_card_by_text

            result = search_card_by_text("test", page_count=10)

        # Verify result structure
        assert "cards" in result
        assert "cursor" in result
        assert "has_more" in result

        # Should return 10 cards (not 11)
        assert len(result["cards"]) == 10

        # Should indicate more results available
        assert result["has_more"] is True

        # Cursor should be score of 2nd-to-last result in the 11 results (index 9)
        assert result["cursor"] == str(mock_results[9]["score"])

    def test_search_pagination_no_more_results(self, mock_collection):
        """Test pagination when no more results available."""
        # Return exactly page_count results
        mock_results = [
            {"_id": f"oracle-{i}", "name": f"Card {i}", "score": 10.0 - i}
            for i in range(5)
        ]
        mock_collection.aggregate.return_value = mock_results

        with patch("api.router.cards.collection", mock_collection):
            from api.router.cards import search_card_by_text

            result = search_card_by_text("test", page_count=10)

        # Verify no more results
        assert result["has_more"] is False
        assert result["cursor"] is None
        assert len(result["cards"]) == 5


class TestSearchCardProjection:
    """Test suite for search result projection fields."""

    def test_search_includes_required_fields(self, mock_collection):
        """Test search results include all required fields for UI."""
        mock_results = [
            {
                "_id": "oracle-1",
                "name": "Test Card",
                "score": 10.0,
                "card_text": "Test text",
                "type_line": "Creature — Human",
                "mana_cost": "{2}{U}",
                "cmc": 3,
                "colors": ["U"],
                "rarity": "common",
                "thumbnail": "https://example.com/thumb.jpg",
            }
        ]
        mock_collection.aggregate.return_value = mock_results

        with patch("api.router.cards.collection", mock_collection):
            from api.router.cards import search_card_by_text

            result = search_card_by_text("test")

        card = result["cards"][0]

        # Verify all new fields are present
        assert "name" in card
        assert "type_line" in card
        assert "mana_cost" in card
        assert "cmc" in card
        assert "colors" in card
        assert "rarity" in card
        assert "thumbnail" in card


class TestColorFilterEdgeCases:
    """Test edge cases for color filtering."""

    def test_colorless_cards(self, mock_collection):
        mock_results = []
        mock_collection.aggregate.return_value = mock_results

        with patch("api.router.cards.collection", mock_collection):
            from api.router.cards import search_card_by_text

            # Empty colors list should work
            card_filter = CardFilter(colors=[], color_operator="exactly")
            search_card_by_text("card", card_filter=card_filter)

        # Should not crash with empty colors list
        mock_collection.aggregate.assert_called_once()

    def test_monocolor_exactly(self, mock_collection):
        """Test exactly one color filter."""

        mock_results = []
        mock_collection.aggregate.return_value = mock_results

        with patch("api.router.cards.collection", mock_collection):
            from api.router.cards import search_card_by_text

            card_filter = CardFilter(colors=["R"], color_operator="exactly")
            search_card_by_text("card", card_filter=card_filter)

        pipeline = mock_collection.aggregate.call_args[0][0]
        match_stage = pipeline[0]["$match"]

        # Should match cards with exactly red
        assert match_stage["colors"] == {"$all": ["R"]}

    def test_five_color_exactly(self, mock_collection):
        mock_results = []
        mock_collection.aggregate.return_value = mock_results

        with patch("api.router.cards.collection", mock_collection):
            from api.router.cards import search_card_by_text

            card_filter = CardFilter(
                colors=["W", "U", "B", "R", "G"], color_operator="exactly"
            )
            search_card_by_text("card", card_filter=card_filter)

        pipeline = mock_collection.aggregate.call_args[0][0]
        match_stage = pipeline[0]["$match"]

        # Should match only five-color cards
        assert match_stage["colors"] == {"$all": ["W", "U", "B", "R", "G"]}


class TestCMCFilterEdgeCases:
    """Test edge cases for CMC filtering."""

    def test_cmc_zero(self, mock_collection):
        mock_results = []
        mock_collection.aggregate.return_value = mock_results

        with patch("api.router.cards.collection", mock_collection):
            from api.router.cards import search_card_by_text

            card_filter = CardFilter(cmc_min=0, cmc_max=0)
            search_card_by_text("card", card_filter=card_filter)

        pipeline = mock_collection.aggregate.call_args[0][0]
        match_stage = pipeline[0]["$match"]

        # Should allow CMC of zero
        assert match_stage["cmc"]["$gte"] == 0
        assert match_stage["cmc"]["$lte"] == 0

    def test_cmc_high_value(self, mock_collection):
        """Test filtering for very high CMC."""

        mock_results = []
        mock_collection.aggregate.return_value = mock_results

        with patch("api.router.cards.collection", mock_collection):
            from api.router.cards import search_card_by_text

            card_filter = CardFilter(cmc_min=15)
            search_card_by_text("card", card_filter=card_filter)

        pipeline = mock_collection.aggregate.call_args[0][0]
        match_stage = pipeline[0]["$match"]

        # Should allow high CMC values
        assert match_stage["cmc"]["$gte"] == 15
