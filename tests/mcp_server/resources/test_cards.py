"""Unit tests for MCP card resources."""

import sys
from pathlib import Path
from unittest.mock import AsyncMock, Mock, patch

import httpx
import pytest

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))


@pytest.fixture
def mock_api_client():
    """Mock APIClient for testing."""
    client = Mock()
    client.get = AsyncMock()
    return client


class TestScryfallIDResource:
    """Test suite for mtg://cards/scryfall/{scryfall_id} resource."""

    @pytest.mark.asyncio
    async def test_resource_success(self, mock_api_client):
        """Test successful card retrieval via resource."""
        # Mock card data with all required fields
        mock_card_data = {
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

        # Mock response
        mock_response = Mock()
        mock_response.json.return_value = mock_card_data
        mock_api_client.get.return_value = mock_response

        # Import and test
        with patch(
            "mcp_server.resources.cards.get_client", return_value=mock_api_client
        ):
            from mcp_server.resources.cards import get_card_by_scryfall_id

            # Call the underlying function (decorator wraps it)
            result = await get_card_by_scryfall_id.fn(
                "bd8fa327-dd41-4737-8f19-2cf5eb1f7cdd"
            )

        # Assert correct API endpoint was called
        mock_api_client.get.assert_called_once_with(
            "/cards/id/bd8fa327-dd41-4737-8f19-2cf5eb1f7cdd"
        )

        # Assert response includes all required fields
        assert result["id"] == "bd8fa327-dd41-4737-8f19-2cf5eb1f7cdd"
        assert result["oracle_id"] == "e3285e6b-3e79-4d7c-bf96-d920f973b122"
        assert result["name"] == "Lightning Bolt"
        assert "image_uris" in result
        assert "normal" in result["image_uris"]

    @pytest.mark.asyncio
    async def test_resource_404_error(self, mock_api_client):
        """Test 404 error handling."""
        # Mock 404 HTTPStatusError
        mock_response = Mock()
        mock_response.status_code = 404
        mock_api_client.get.side_effect = httpx.HTTPStatusError(
            "Not found", request=Mock(), response=mock_response
        )

        with patch(
            "mcp_server.resources.cards.get_client", return_value=mock_api_client
        ):
            from mcp_server.resources.cards import get_card_by_scryfall_id

            # Error should propagate (FastMCP will handle conversion to MCP error)
            with pytest.raises(httpx.HTTPStatusError) as exc_info:
                await get_card_by_scryfall_id.fn("nonexistent-id")

        assert exc_info.value.response.status_code == 404

    @pytest.mark.asyncio
    async def test_resource_500_error(self, mock_api_client):
        """Test 500 error handling."""
        # Mock 500 HTTPStatusError
        mock_response = Mock()
        mock_response.status_code = 500
        mock_api_client.get.side_effect = httpx.HTTPStatusError(
            "Internal server error", request=Mock(), response=mock_response
        )

        with patch(
            "mcp_server.resources.cards.get_client", return_value=mock_api_client
        ):
            from mcp_server.resources.cards import get_card_by_scryfall_id

            with pytest.raises(httpx.HTTPStatusError) as exc_info:
                await get_card_by_scryfall_id.fn("test-id")

        assert exc_info.value.response.status_code == 500

    @pytest.mark.asyncio
    async def test_resource_timeout(self, mock_api_client):
        """Test timeout handling."""
        # Mock timeout exception
        mock_api_client.get.side_effect = httpx.TimeoutException("Request timeout")

        with patch(
            "mcp_server.resources.cards.get_client", return_value=mock_api_client
        ):
            from mcp_server.resources.cards import get_card_by_scryfall_id

            with pytest.raises(httpx.TimeoutException):
                await get_card_by_scryfall_id.fn("test-id")

    @pytest.mark.asyncio
    async def test_resource_includes_all_image_fields(self, mock_api_client):
        """Test response includes all image_uris variants."""
        mock_card_data = {
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

        mock_response = Mock()
        mock_response.json.return_value = mock_card_data
        mock_api_client.get.return_value = mock_response

        with patch(
            "mcp_server.resources.cards.get_client", return_value=mock_api_client
        ):
            from mcp_server.resources.cards import get_card_by_scryfall_id

            result = await get_card_by_scryfall_id.fn("test-id")

        # Verify all image variants are present
        image_uris = result["image_uris"]
        assert "small" in image_uris
        assert "normal" in image_uris
        assert "large" in image_uris
        assert "png" in image_uris
        assert "art_crop" in image_uris
        assert "border_crop" in image_uris


class TestOracleIDResource:
    """Test suite for mtg://cards/oracle/{oracle_id} resource."""

    @pytest.mark.asyncio
    async def test_resource_multiple_printings(self, mock_api_client):
        """Test retrieving multiple printings."""
        # Mock 5 card printings with same oracle_id
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

        mock_response = Mock()
        mock_response.json.return_value = mock_cards
        mock_api_client.get.return_value = mock_response

        with patch(
            "mcp_server.resources.cards.get_client", return_value=mock_api_client
        ):
            from mcp_server.resources.cards import get_cards_by_oracle_id

            result = await get_cards_by_oracle_id.fn("shared-oracle-id")

        # Assert correct API endpoint was called
        mock_api_client.get.assert_called_once_with("/cards/oracle/shared-oracle-id")

        # Assert all printings returned
        assert len(result) == 5
        for i, card in enumerate(result):
            assert card["oracle_id"] == "shared-oracle-id"
            assert "image_uris" in card
            assert card["id"] == f"scryfall-{i}"

    @pytest.mark.asyncio
    async def test_resource_single_printing(self, mock_api_client):
        """Test Oracle ID with only one printing."""
        mock_card = {
            "id": "single-scryfall-id",
            "oracle_id": "single-oracle-id",
            "name": "Unique Card",
            "image_uris": {"normal": "https://example.com/unique.jpg"},
        }

        mock_response = Mock()
        mock_response.json.return_value = [mock_card]
        mock_api_client.get.return_value = mock_response

        with patch(
            "mcp_server.resources.cards.get_client", return_value=mock_api_client
        ):
            from mcp_server.resources.cards import get_cards_by_oracle_id

            result = await get_cards_by_oracle_id.fn("single-oracle-id")

        assert len(result) == 1
        assert result[0]["id"] == "single-scryfall-id"
        assert result[0]["oracle_id"] == "single-oracle-id"

    @pytest.mark.asyncio
    async def test_resource_404_error(self, mock_api_client):
        """Test 404 when Oracle ID has no printings."""
        mock_response = Mock()
        mock_response.status_code = 404
        mock_api_client.get.side_effect = httpx.HTTPStatusError(
            "Not found", request=Mock(), response=mock_response
        )

        with patch(
            "mcp_server.resources.cards.get_client", return_value=mock_api_client
        ):
            from mcp_server.resources.cards import get_cards_by_oracle_id

            with pytest.raises(httpx.HTTPStatusError) as exc_info:
                await get_cards_by_oracle_id.fn("nonexistent-oracle-id")

        assert exc_info.value.response.status_code == 404

    @pytest.mark.asyncio
    async def test_resource_image_consistency(self, mock_api_client):
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

        mock_response = Mock()
        mock_response.json.return_value = mock_cards
        mock_api_client.get.return_value = mock_response

        with patch(
            "mcp_server.resources.cards.get_client", return_value=mock_api_client
        ):
            from mcp_server.resources.cards import get_cards_by_oracle_id

            result = await get_cards_by_oracle_id.fn("oracle")

        # Verify every card has image_uris
        for card in result:
            assert "image_uris" in card
            assert "normal" in card["image_uris"]

    @pytest.mark.asyncio
    async def test_resource_network_error(self, mock_api_client):
        """Test network error handling."""
        mock_api_client.get.side_effect = httpx.RequestError("Network error")

        with patch(
            "mcp_server.resources.cards.get_client", return_value=mock_api_client
        ):
            from mcp_server.resources.cards import get_cards_by_oracle_id

            with pytest.raises(httpx.RequestError):
                await get_cards_by_oracle_id.fn("test-oracle-id")
