"""
MTG Events module for fetching and formatting Magic: The Gathering events.

This module provides functionality to fetch events from Wizards' GraphQL API,
filter them by organization, and format them in French for display.
"""

from .fetcher import EventFetcher
from .formatter import EventFormatter
from .models import Event, EventFilter, EventFormat, Organization, VenueMapping

__all__ = [
    "Event",
    "Organization",
    "EventFormat",
    "VenueMapping",
    "EventFilter",
    "EventFetcher",
    "EventFormatter",
]
