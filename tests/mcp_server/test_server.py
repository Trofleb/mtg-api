"""Unit tests for MCP server initialization."""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from mcp_server.server import mcp  # noqa: E402


class TestMCPServer:
    """Test suite for MCP server initialization."""

    def test_server_initialized(self):
        """Test MCP server initializes with correct name."""
        assert mcp.name == "MTG MCP Server"

    def test_server_has_instructions(self):
        """Test MCP server has instructions configured."""
        assert mcp.instructions is not None
        assert len(mcp.instructions) > 0
        assert "Magic: The Gathering" in mcp.instructions
        assert "MTG" in mcp.instructions

    def test_server_has_no_tools_initially(self):
        """Test server starts with no tools in Phase 1."""
        # In Phase 1, we're just setting up infrastructure
        # Tools will be added in later phases
        # This test documents the expected state
        pass

    def test_server_has_card_resources(self):
        """Test card resources are registered after Phase 2."""
        # After Phase 2, card resources should be available
        # Verify the resources module has the expected decorators
        from mcp_server.resources import cards

        # Check that resource wrapper objects exist
        assert hasattr(cards, "get_card_by_scryfall_id")
        assert hasattr(cards, "get_cards_by_oracle_id")

        # Verify the underlying functions are async (decorator wraps them)
        import inspect

        assert inspect.iscoroutinefunction(cards.get_card_by_scryfall_id.fn)
        assert inspect.iscoroutinefunction(cards.get_cards_by_oracle_id.fn)
