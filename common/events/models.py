"""
Pydantic models for MTG Events from Wizards' GraphQL API.

This module defines data models for events, organizations, and related entities
with validation and coordinate mapping functionality.
"""

import re
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from zoneinfo import ZoneInfo

from pydantic import BaseModel


class Money(BaseModel):
    """Entry fee information."""

    amount: int
    currency: str


class Organization(BaseModel):
    """Organization hosting the event."""

    id: str
    name: str


class EventFormat(BaseModel):
    """Format of the Magic event."""

    id: str
    name: Optional[str] = None


class Event(BaseModel):
    """Magic: The Gathering event data from Wizards API."""

    id: str
    capacity: Optional[int] = None
    shortCode: Optional[str] = None
    entryFee: Money
    description: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    title: str
    rulesEnforcementLevel: str
    scheduledStartTime: str
    organization: Organization
    eventFormat: EventFormat
    numberOfPlayers: Optional[int] = None

    @property
    def is_xenomorphe(self) -> bool:
        """Check if event belongs to organization 10933 (Xenomorphe)."""
        return self.organization.id == "10933"

    @property
    def start_datetime(self) -> datetime:
        """Parse scheduledStartTime to datetime object."""
        return datetime.fromisoformat(self.scheduledStartTime.replace("Z", "+00:00"))

    @property
    def venue_name(self) -> str:
        """Map coordinates to venue name using known mappings."""
        if self.latitude is None or self.longitude is None:
            return "Lieu non spécifié"

        venue_map = VenueMapping.get_venue_coordinates()
        coordinate_key = (self.latitude, self.longitude)

        return venue_map.get(
            coordinate_key, f"Latitude: {self.latitude}, Longitude: {self.longitude}"
        )

    @property
    def entry_fee_formatted(self) -> str:
        """Format entry fee as CHF amount (1700 -> 17.00 CHF)."""
        amount_chf = self.entryFee.amount / 100
        return f"{amount_chf:.2f} {self.entryFee.currency}"

    @property
    def pricing_info(self) -> Tuple[Optional[str], str]:
        """
        Extract member and non-member pricing from description.

        Returns:
            Tuple of (member_price, non_member_price)
            member_price is None if not found in description
        """
        if not self.description:
            return None, self.entry_fee_formatted

        # Look for patterns like "Membres XX CHF Non Membre YY CHF"
        patterns = [
            r"Membres?\s+(\d+)\s*CHF\s+Non[- ]?Membres?\s+(\d+)\s*CHF",
            r"(\d+)\s*CHF\s+membres?\s+(\d+)\s*CHF\s+non[- ]?membres?",
            r"Membre[s]?[:\s]*(\d+)\s*CHF[,\s]*Non[- ]?Membre[s]?[:\s]*(\d+)\s*CHF",
        ]

        for pattern in patterns:
            match = re.search(pattern, self.description, re.IGNORECASE)
            if match:
                member_price = f"{match.group(1)} CHF"
                non_member_price = f"{match.group(2)} CHF"
                return member_price, non_member_price

        # If no member pricing found, return only non-member price
        return None, self.entry_fee_formatted

    @property
    def rules_level_french(self) -> str:
        """Convert rules enforcement level to French."""
        level_map = {
            "CASUAL": "Casual",
            "COMPETITIVE": "Compétitif",
            "REGULAR": "Régulier",
        }
        return level_map.get(self.rulesEnforcementLevel, self.rulesEnforcementLevel)


class EventSearchResponse(BaseModel):
    """Response from the GraphQL events search."""

    events: List[Event]
    pageInfo: Dict


class VenueMapping:
    """Venue coordinate to address mapping utility."""

    @staticmethod
    def get_venue_coordinates() -> Dict[Tuple[float, float], str]:
        """
        Known venue coordinate mappings.

        Returns:
            Dictionary mapping (latitude, longitude) tuples to venue names
        """
        return {
            (
                46.2114995,
                6.1206073,
            ): "Espace Santé Esclarmonde, Avenue Soret 39, 1203 Genève",
            (46.20118, 6.13793): "Clos Voltaire 49 rue de Lyon",
            # (46.20118, 6.13793):
        }


class EventFilter:
    """Utility class for filtering events."""

    @staticmethod
    def filter_by_organization(
        events: List[Event], org_id: str = "10933"
    ) -> List[Event]:
        """
        Filter events to only include those from specified organization.

        Args:
            events: List of events to filter
            org_id: Organization ID to filter by (default: "10933" for Xenomorphe)

        Returns:
            Filtered list of events
        """
        return [event for event in events if event.organization.id == org_id]

    @staticmethod
    def filter_by_date_range(events: List[Event], days_ahead: int) -> List[Event]:
        """
        Filter events to only include those within specified days from now.

        Args:
            events: List of events to filter
            days_ahead: Number of days ahead to include

        Returns:
            Filtered list of events within date range
        """
        from datetime import timedelta

        # Use Zurich timezone for consistent date filtering
        zurich_tz = ZoneInfo("Europe/Zurich")
        now = datetime.now(zurich_tz)
        cutoff_date = now + timedelta(days=days_ahead)

        filtered_events = []
        for event in events:
            event_dt = event.start_datetime
            if event_dt.tzinfo is None:
                event_dt = event_dt.replace(tzinfo=ZoneInfo("UTC"))
            event_dt_zurich = event_dt.astimezone(zurich_tz)

            if event_dt_zurich <= cutoff_date:
                filtered_events.append(event)

        return filtered_events
