#!/usr/bin/env python3
"""
MTG Events CLI Script

A command-line tool to fetch and display Magic: The Gathering events
from Wizards' GraphQL API, filtered for organization 10933 (Xenomorphe).
"""

import asyncio
import logging
import sys
from pathlib import Path

import typer
from rich.console import Console
from rich.logging import RichHandler

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from common.events import EventFetcher, EventFormatter  # noqa: E402

app = typer.Typer(
    name="mtg-events",
    help="Fetch and display MTG events for Xenomorphe organization",
    no_args_is_help=True,
)

console = Console()


def setup_logging(debug: bool = False) -> None:
    """Set up logging configuration."""
    level = logging.DEBUG if debug else logging.INFO

    logging.basicConfig(
        level=level,
        format="%(message)s",
        handlers=[RichHandler(console=console, rich_tracebacks=True)],
    )


@app.command()
def list_events(
    organization_id: str = typer.Option(
        "10933",
        "--org-id",
        "-o",
        help="Organization ID to filter events (default: 10933 for Xenomorphe)",
    ),
    days_ahead: int = typer.Option(
        15, "--days", "-d", help="Number of days ahead to search for events"
    ),
    compact_days: int = typer.Option(
        15, "--compact-days", help="Number of days for compact format section"
    ),
    detailed_days: int = typer.Option(
        7, "--detailed-days", help="Number of days for detailed format section"
    ),
    format_type: str = typer.Option(
        "complete",
        "--format",
        "-f",
        help="Output format: 'complete', 'compact', 'detailed', 'whatsapp', or 'whatsapp-detailed'",
    ),
    debug: bool = typer.Option(False, "--debug", help="Enable debug logging"),
    verbose: bool = typer.Option(
        False, "--verbose", "-v", help="Enable verbose output"
    ),
    show_raw_events: bool = typer.Option(
        False,
        "--show-raw-events",
        help="Show raw GraphQL response JSON for each event (enables debug logging automatically)",
    ),
) -> None:
    """
    Fetch and display MTG events for the specified organization.

    By default, displays a complete message with:
    - Compact format for next 15 days
    - Detailed emoji format for next 7 days

    WhatsApp format options:
    - 'whatsapp': Complete venue-grouped message with WhatsApp formatting
    - 'whatsapp-detailed': Only detailed venue-grouped section
    """
    setup_logging(debug or verbose or show_raw_events)

    logger = logging.getLogger(__name__)

    if debug:
        logger.debug(f"Fetching events for organization {organization_id}")
        logger.debug(f"Search range: {days_ahead} days ahead")
        logger.debug(f"Format: {format_type}")

    async def fetch_and_format():
        try:
            # Initialize fetcher
            fetcher = EventFetcher()

            # Fetch events
            logger.info(f"Fetching events for organization {organization_id}...")
            events = await fetcher.fetch_events(
                organization_id=organization_id,
                days_ahead=days_ahead,
                show_raw_events=show_raw_events,
            )

            if not events:
                console.print(
                    f"[yellow]Aucun événement trouvé pour l'organisation {organization_id}[/yellow]"
                )
                return

            logger.info(f"Found {len(events)} events")

            # Format output based on requested format
            if format_type == "compact":
                output = EventFormatter.format_event_list_compact(events, compact_days)
            elif format_type == "detailed":
                output = EventFormatter.format_event_list_detailed(
                    events, detailed_days
                )
            elif format_type == "whatsapp":
                output = EventFormatter.format_complete_message_whatsapp(events)
            elif format_type == "whatsapp-detailed":
                output = EventFormatter.format_events_grouped_by_venue_detailed(
                    events, detailed_days
                )
            else:  # complete (default)
                output = EventFormatter.format_complete_message(events)

            # Display results
            console.print(output)

        except Exception as e:
            logger.error(f"Error fetching events: {e}")
            if debug:
                logger.exception("Full traceback:")
            sys.exit(1)

    # Run async function
    asyncio.run(fetch_and_format())


@app.command()
def test_connection(
    debug: bool = typer.Option(False, "--debug", help="Enable debug logging"),
) -> None:
    """Test connection to Wizards' GraphQL API."""
    setup_logging(debug)
    logger = logging.getLogger(__name__)

    async def test():
        try:
            fetcher = EventFetcher()
            logger.info("Testing connection to Wizards' GraphQL API...")

            # Try to fetch just one page of events
            events = await fetcher.fetch_events(days_ahead=1)
            console.print("[green]✅ Connection successful![/green]")
            console.print(f"Found {len(events)} events for organization 10933")

        except Exception as e:
            console.print(f"[red]❌ Connection failed: {e}[/red]")
            if debug:
                logger.exception("Full traceback:")
            sys.exit(1)

    asyncio.run(test())


@app.command()
def version() -> None:
    """Show version information."""
    console.print("MTG Events CLI v1.0.0")
    console.print("Fetches Magic: The Gathering events for Xenomorphe organization")


if __name__ == "__main__":
    app()
