"""MCP resources for MTG card data retrieval.

This module provides MCP resources for accessing Magic: The Gathering card
information by ID. Resources are read-only data entities accessed via URI
patterns that communicate with the FastAPI backend via HTTP.
"""

from mcp_server.client import get_client
from mcp_server.server import mcp


@mcp.resource("mtg://cards/scryfall/{scryfall_id}")
async def get_card_by_scryfall_id(scryfall_id: str) -> dict:
    """Get specific MTG card printing by Scryfall ID.

    This resource retrieves a single card printing identified by its unique
    Scryfall ID. Each Scryfall ID represents a specific printing of a card
    in a particular set.

    Args:
        scryfall_id: UUID Scryfall ID (unique per printing)

    Returns:
        Card data dictionary including:
            - id: Scryfall ID
            - oracle_id: Oracle ID (shared across printings)
            - name: Card name
            - image_uris: Image URLs (thumbnail, small, normal, large, png, art_crop, border_crop)
            - All other card metadata from Scryfall

    Raises:
        httpx.HTTPStatusError: If card not found (404) or API error (500)
        httpx.RequestError: If request fails (network error, timeout, etc.)

    Example:
        >>> # Resource URI: mtg://cards/scryfall/bd8fa327-dd41-4737-8f19-2cf5eb1f7cdd
        >>> # Returns Lightning Bolt from Alpha set
    """
    client = get_client()
    response = await client.get(f"/cards/id/{scryfall_id}")
    return response.json()


@mcp.resource("mtg://cards/oracle/{oracle_id}")
async def get_cards_by_oracle_id(oracle_id: str) -> list[dict]:
    """Get all printings of a card by Oracle ID.

    This resource retrieves all printings of a card that share the same Oracle ID.
    Oracle IDs represent the card concept/rules and are shared across all printings
    of functionally identical cards.

    Args:
        oracle_id: UUID Oracle ID (represents card concept, non-unique)

    Returns:
        List of card data dictionaries, sorted by release date (newest first).
        Each card includes:
            - id: Scryfall ID (unique per printing)
            - oracle_id: Oracle ID (same for all results)
            - name: Card name
            - set: Set code
            - image_uris: Image URLs for this specific printing
            - All other card metadata from Scryfall

    Raises:
        httpx.HTTPStatusError: If no cards found (404) or API error (500)
        httpx.RequestError: If request fails (network error, timeout, etc.)

    Example:
        >>> # Resource URI: mtg://cards/oracle/e3285e6b-3e79-4d7c-bf96-d920f973b122
        >>> # Returns all Lightning Bolt printings from all sets
    """
    client = get_client()
    response = await client.get(f"/cards/oracle/{oracle_id}")
    return response.json()
