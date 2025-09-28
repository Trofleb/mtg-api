"""
Unit tests for scripts.mtg_events CLI.

Tests CLI interface with different argument combinations and output validation.
"""

# Import the CLI app
import sys
from pathlib import Path
from unittest.mock import AsyncMock, Mock, patch

import pytest
from typer.testing import CliRunner

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from scripts.mtg_events import app  # noqa: E402


class TestMTGEventsCLI:
    """Tests for MTG Events CLI."""

    @pytest.fixture
    def runner(self):
        """Create CLI test runner."""
        return CliRunner()

    def test_version_command(self, runner):
        """Test version command."""
        result = runner.invoke(app, ["version"])

        assert result.exit_code == 0
        assert "MTG Events CLI v1.0.0" in result.stdout
        assert "Xenomorphe organization" in result.stdout

    def test_help_command(self, runner):
        """Test help command."""
        result = runner.invoke(app, ["--help"])

        assert result.exit_code == 0
        assert "Fetch and display MTG events" in result.stdout
        assert "list-events" in result.stdout
        assert "test-connection" in result.stdout
        assert "version" in result.stdout

    def test_list_events_help(self, runner):
        """Test list-events command help."""
        result = runner.invoke(app, ["list-events", "--help"])

        assert result.exit_code == 0
        assert "--org-id" in result.stdout
        assert "--days" in result.stdout
        assert "--format" in result.stdout
        assert "--debug" in result.stdout

    def test_list_events_success(self, runner):
        """Test successful list-events execution."""
        # Mock the EventFetcher
        mock_events = [
            Mock(
                id="test-event",
                title="Test Event",
                organization=Mock(id="10933", name="Xenomorphe"),
                start_datetime=Mock(),
                is_xenomorphe=True,
            )
        ]

        with patch("scripts.mtg_events.EventFetcher") as MockFetcher:
            mock_fetcher_instance = AsyncMock()
            mock_fetcher_instance.fetch_events.return_value = mock_events
            MockFetcher.return_value = mock_fetcher_instance

            with patch("scripts.mtg_events.EventFormatter") as MockFormatter:
                MockFormatter.format_complete_message.return_value = (
                    "Test formatted output"
                )

                result = runner.invoke(app, ["list-events"])

        assert result.exit_code == 0
        assert "Test formatted output" in result.stdout

    def test_list_events_with_options(self, runner):
        """Test list-events with various options."""
        mock_events = []

        with patch("scripts.mtg_events.EventFetcher") as MockFetcher:
            mock_fetcher_instance = AsyncMock()
            mock_fetcher_instance.fetch_events.return_value = mock_events
            MockFetcher.return_value = mock_fetcher_instance

            result = runner.invoke(
                app,
                [
                    "list-events",
                    "--org-id",
                    "6081",
                    "--days",
                    "30",
                    "--format",
                    "compact",
                    "--verbose",
                ],
            )

        assert result.exit_code == 0
        # Should handle empty events gracefully

    def test_test_connection_success(self, runner):
        """Test successful test-connection command."""
        mock_events = [Mock(id="test")]

        with patch("scripts.mtg_events.EventFetcher") as MockFetcher:
            mock_fetcher_instance = AsyncMock()
            mock_fetcher_instance.fetch_events.return_value = mock_events
            MockFetcher.return_value = mock_fetcher_instance

            result = runner.invoke(app, ["test-connection"])

        assert result.exit_code == 0
        assert "Connection successful" in result.stdout

    def test_test_connection_failure(self, runner):
        """Test test-connection command with failure."""
        with patch("scripts.mtg_events.EventFetcher") as MockFetcher:
            mock_fetcher_instance = AsyncMock()
            mock_fetcher_instance.fetch_events.side_effect = Exception(
                "Connection error"
            )
            MockFetcher.return_value = mock_fetcher_instance

            result = runner.invoke(app, ["test-connection"])

        assert result.exit_code == 1
        assert "Connection failed" in result.stdout

    def test_no_args_shows_help(self, runner):
        """Test that running with no arguments shows help."""
        result = runner.invoke(app, [])

        # Should show help - exit code may be 0 with Typer's no_args_is_help
        assert "Usage:" in result.stdout or "Commands:" in result.stdout
