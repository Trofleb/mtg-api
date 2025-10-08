"""
Message formatting utilities for MTG events.

This module provides French formatting functions for events,
including compact and detailed emoji templates.
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional
from zoneinfo import ZoneInfo

from .models import Event


class EventFormatter:
    """Utility class for formatting MTG events in French."""

    @staticmethod
    def _format_bold(text: str) -> str:
        """Format text in WhatsApp bold syntax."""
        return f"*{text}*"

    @staticmethod
    def _format_italic(text: str) -> str:
        """Format text in WhatsApp italic syntax (Note: doesn't work well with spaces/multi-line)."""
        return f"_{text}_"

    @staticmethod
    def _format_mono(text: str) -> str:
        """Format text in WhatsApp monospace syntax."""
        return f"`{text}`"

    @staticmethod
    def _is_competitive(event: "Event") -> bool:
        """Check if event is competitive (COMPETITIVE rules level)."""
        return event.rulesEnforcementLevel == "COMPETITIVE"

    @staticmethod
    def group_events_by_date_then_venue(
        events: List["Event"],
    ) -> Dict[str, Dict[str, List["Event"]]]:
        """Group events by date first, then by venue within each date.

        Args:
            events: List of events to group

        Returns:
            Dictionary mapping date strings to venue dictionaries
        """
        from collections import defaultdict

        # Group by date first
        date_groups = defaultdict(lambda: defaultdict(list))

        for event in events:
            # Create date key for grouping (format_day_date_french handles timezone conversion)
            date_key = EventFormatter.format_day_date_french(event.start_datetime)
            venue_name = event.venue_name

            date_groups[date_key][venue_name].append(event)

        # Sort events within each venue by time
        for date_key in date_groups:
            for venue_name in date_groups[date_key]:
                date_groups[date_key][venue_name].sort(key=lambda e: e.start_datetime)

        # Convert defaultdict to regular dict and sort by date
        result = {}
        sorted_dates = sorted(
            date_groups.keys(),
            key=lambda date_str:
            # Parse the date string back to datetime for sorting
            next(
                event.start_datetime
                for events_by_venue in date_groups[date_str].values()
                for event in events_by_venue
            ),
        )

        for date_key in sorted_dates:
            result[date_key] = dict(date_groups[date_key])

        return result

    @staticmethod
    def group_events_by_venue(events: List["Event"]) -> Dict[str, List["Event"]]:
        """Group events by venue address (legacy method for backward compatibility).

        Args:
            events: List of events to group

        Returns:
            Dictionary mapping venue names to lists of events
        """
        from collections import defaultdict

        venue_groups = defaultdict(list)
        for event in events:
            venue_name = event.venue_name
            venue_groups[venue_name].append(event)

        # Sort events within each venue by date
        for venue_name in venue_groups:
            venue_groups[venue_name].sort(key=lambda e: e.start_datetime)

        return dict(venue_groups)

    @staticmethod
    def format_detailed_event_whatsapp(event: "Event") -> str:
        """
        Format event in detailed WhatsApp format for venue-grouped listing.

        Format:
        *Event Name* 🏆 🕒 *Day DD month - HH:MM*
        📝 Format : [Format]
        💰 Tarif : XX.XX CHF
        👥 Inscrits : X/Y
        📱 Code : `ABC123`
        📄 _Description text_

        Args:
            event: Event object

        Returns:
            Formatted detailed event string with WhatsApp syntax
        """
        # Format event title with competitive indicator
        title = EventFormatter._format_bold(event.title)
        if EventFormatter._is_competitive(event):
            title += " 🏆"

        # Format time only (date is already shown in the date header above)
        time_str = EventFormatter.format_time_french(event.start_datetime)

        # Format pricing (non-member only)
        _, non_member_price = event.pricing_info

        # Format attendance (simplified)
        registered = event.numberOfPlayers or 0
        total = event.capacity or 0
        attendance_str = f"{registered}/{total}" if total > 0 else str(registered)

        # Use short code if available
        code = event.shortCode or event.id[:7]
        code_formatted = EventFormatter._format_bold(code)

        # Use eventFormat name if available
        format_name = event.eventFormat.name if event.eventFormat.name else event.title

        lines = [
            f"{title} 🕒 {time_str}",
            f"📝 Format : {format_name}",
            f"💰 Tarif : {non_member_price}",
            f"👥 Inscrits : {attendance_str}",
            f"📱 Code : {code_formatted}",
        ]

        # Add description if available
        if event.description and event.description.strip():
            # Apply italic formatting to each line separately for WhatsApp compatibility
            description_lines = event.description.strip().split("\n")
            formatted_description_lines = []
            for desc_line in description_lines:
                if desc_line.strip():  # Only format non-empty lines
                    formatted_line = EventFormatter._format_italic(desc_line.strip())
                    formatted_description_lines.append(formatted_line)

            if formatted_description_lines:
                lines.append(f"📄 {formatted_description_lines[0]}")
                # Add additional lines if present
                for additional_line in formatted_description_lines[1:]:
                    lines.append(additional_line)

        return "\n".join(lines)

    @staticmethod
    def format_compact_event_whatsapp(event: "Event") -> str:
        """
        Format event in compact WhatsApp format for venue-grouped listing.

        Format: J-X *Event Name* 🏆 - XX.XX CHF (X/Y) `CODE`

        Args:
            event: Event object

        Returns:
            Formatted compact event string with WhatsApp syntax
        """
        j_minus = EventFormatter.calculate_j_minus(event.start_datetime)

        # Format event name in bold
        event_name = EventFormatter._format_bold(event.title)

        # Add competitive indicator if applicable
        competitive_indicator = " 🏆" if EventFormatter._is_competitive(event) else ""

        # Get pricing (non-member only)
        _, non_member_price = event.pricing_info

        # Format attendance
        registered = event.numberOfPlayers or 0
        total = event.capacity or 0
        registration_info = (
            f"({registered}/{total})" if total > 0 else f"({registered})"
        )

        # Use short code if available
        code = event.shortCode or event.id[:7]
        code_formatted = EventFormatter._format_bold(code)

        return f"{j_minus} {event_name}{competitive_indicator} - {non_member_price} {registration_info} {code_formatted}"

    @staticmethod
    def format_events_grouped_by_venue_detailed(
        events: List["Event"], days_ahead: int = 7
    ) -> str:
        """
        Format events grouped by venue for detailed section (7 days).

        Args:
            events: List of events to format
            days_ahead: Number of days to include (default: 7)

        Returns:
            Formatted string with events grouped by venue in detailed format
        """
        if not events:
            return "Aucun événement trouvé."

        # Filter events within the date range
        from .models import EventFilter

        filtered_events = EventFilter.filter_by_date_range(events, days_ahead)

        if not filtered_events:
            return f"Aucun événement dans les {days_ahead} prochains jours."

        # Group events by date first, then by venue
        date_venue_groups = EventFormatter.group_events_by_date_then_venue(
            filtered_events
        )

        lines = [EventFormatter._format_bold("📅 ÉVÉNEMENTS - 7 PROCHAINS JOURS"), ""]

        first_date = True
        for date_key, venue_groups in date_venue_groups.items():
            if not first_date:
                lines.append("")  # Empty line between dates

            # Date header
            date_header = EventFormatter._format_bold(f"📅 {date_key.upper()}")
            lines.append(date_header)
            lines.append("")  # Empty line after date header

            first_venue_in_date = True
            for venue_name, venue_events in venue_groups.items():
                if not first_venue_in_date:
                    lines.append("")  # Empty line between venues within same date

                # Venue header (within the date, no bold)
                venue_header = f"📍 {venue_name}"
                lines.append(venue_header)
                lines.append("")  # Empty line after venue header

                # Format each event in the venue
                for i, event in enumerate(venue_events):
                    if i > 0:
                        lines.append("")  # Empty line between events
                    lines.append(EventFormatter.format_detailed_event_whatsapp(event))

                first_venue_in_date = False

            first_date = False

        return "\n".join(lines)

    @staticmethod
    def format_events_grouped_by_venue_compact(
        events: List["Event"], start_day: int = 8, end_day: int = 15
    ) -> str:
        """
        Format events grouped by venue for compact section (days 8-15).

        Args:
            events: List of events to format
            start_day: Start day for filtering (default: 8)
            end_day: End day for filtering (default: 15)

        Returns:
            Formatted string with events grouped by venue in compact format
        """
        if not events:
            return "Aucun événement trouvé."

        # Filter events within the date range (days 8-15)
        zurich_tz = ZoneInfo("Europe/Zurich")
        now = datetime.now(zurich_tz)
        start_date = now + timedelta(days=start_day - 1)
        end_date = now + timedelta(days=end_day)

        filtered_events = []
        for event in events:
            event_dt = event.start_datetime
            if event_dt.tzinfo is None:
                event_dt = event_dt.replace(tzinfo=ZoneInfo("UTC"))
            event_dt_zurich = event_dt.astimezone(zurich_tz)

            if start_date < event_dt_zurich <= end_date:
                filtered_events.append(event)

        if not filtered_events:
            return f"Aucun événement entre J-{start_day} et J-{end_day}."

        # Group events by date first, then by venue
        date_venue_groups = EventFormatter.group_events_by_date_then_venue(
            filtered_events
        )

        lines = [
            "---",
            "",
            EventFormatter._format_bold("📆 APERÇU - PROCHAINES SEMAINES"),
            "",
        ]

        for date_key, venue_groups in date_venue_groups.items():
            # Date header
            date_header = EventFormatter._format_bold(f"📅 {date_key.upper()}")
            lines.append(date_header)

            for venue_name, venue_events in venue_groups.items():
                # Venue header (indented under date, no bold)
                venue_header = f"📍 {venue_name}"
                lines.append(venue_header)

                # Format each event in compact format
                for event in venue_events:
                    lines.append(EventFormatter.format_compact_event_whatsapp(event))

            lines.append("")  # Empty line after each date group

        return "\n".join(lines)

    @staticmethod
    def format_complete_message_whatsapp(events: List["Event"]) -> str:
        """
        Format complete WhatsApp message with venue-grouped detailed and compact sections.

        Args:
            events: List of events to format

        Returns:
            Complete formatted message with WhatsApp syntax and venue grouping
        """
        if not events:
            return "Aucun événement trouvé."

        # Section 1: Detailed venue-grouped format (7 days)
        detailed_section = EventFormatter.format_events_grouped_by_venue_detailed(
            events, days_ahead=7
        )

        # Section 2: Compact venue-grouped format (8-15 days)
        compact_section = EventFormatter.format_events_grouped_by_venue_compact(
            events, start_day=8, end_day=15
        )

        # Combine sections
        return f"{detailed_section}\n\n{compact_section}"

    # French day names
    FRENCH_DAYS = {
        0: "lundi",
        1: "mardi",
        2: "mercredi",
        3: "jeudi",
        4: "vendredi",
        5: "samedi",
        6: "dimanche",
    }

    # French month names
    FRENCH_MONTHS = {
        1: "janvier",
        2: "février",
        3: "mars",
        4: "avril",
        5: "mai",
        6: "juin",
        7: "juillet",
        8: "août",
        9: "septembre",
        10: "octobre",
        11: "novembre",
        12: "décembre",
    }

    @staticmethod
    def calculate_j_minus(event_date: datetime) -> str:
        """
        Calculate J-X day notation for an event.

        Args:
            event_date: Event datetime

        Returns:
            String like "J-1", "J-3", etc.
        """
        # Use Zurich timezone for consistent date calculations
        zurich_tz = ZoneInfo("Europe/Zurich")
        now = datetime.now(zurich_tz)

        # Convert event datetime to Zurich timezone for comparison
        if event_date.tzinfo is None:
            event_date = event_date.replace(tzinfo=ZoneInfo("UTC"))
        event_date_zurich = event_date.astimezone(zurich_tz)

        days_diff = (event_date_zurich.date() - now.date()).days

        if days_diff == 0:
            return "J"
        elif days_diff == 1:
            return "J-1"
        elif days_diff > 0:
            return f"J-{days_diff}"
        else:
            return f"J+{abs(days_diff)}"

    @staticmethod
    def format_date_french(event_date: datetime) -> str:
        """
        Format date in French format (DD/MM/YYYY).

        Args:
            event_date: Event datetime

        Returns:
            Formatted date string
        """
        # Convert to Zurich timezone for display
        zurich_tz = ZoneInfo("Europe/Zurich")
        if event_date.tzinfo is None:
            event_date = event_date.replace(tzinfo=ZoneInfo("UTC"))
        event_date_zurich = event_date.astimezone(zurich_tz)
        return event_date_zurich.strftime("%d/%m/%Y")

    @staticmethod
    def format_time_french(event_date: datetime) -> str:
        """
        Format time in French format (HH:MM).

        Args:
            event_date: Event datetime

        Returns:
            Formatted time string
        """
        # Convert to Zurich timezone for display
        zurich_tz = ZoneInfo("Europe/Zurich")
        if event_date.tzinfo is None:
            event_date = event_date.replace(tzinfo=ZoneInfo("UTC"))
        event_date_zurich = event_date.astimezone(zurich_tz)
        return event_date_zurich.strftime("%H:%M")

    @staticmethod
    def format_day_date_french(event_date: datetime) -> str:
        """
        Format day and date in French (e.g., "vendredi 5 septembre").

        Args:
            event_date: Event datetime

        Returns:
            Formatted day and date string
        """
        # Convert to Zurich timezone for display
        zurich_tz = ZoneInfo("Europe/Zurich")
        if event_date.tzinfo is None:
            event_date = event_date.replace(tzinfo=ZoneInfo("UTC"))
        event_date_zurich = event_date.astimezone(zurich_tz)

        weekday = EventFormatter.FRENCH_DAYS[event_date_zurich.weekday()]
        day = event_date_zurich.day
        month = EventFormatter.FRENCH_MONTHS[event_date_zurich.month]

        return f"{weekday} {day} {month}"

    @staticmethod
    def format_pricing_display(
        member_price: Optional[str], non_member_price: str
    ) -> str:
        """
        Format pricing for display.

        Args:
            member_price: Member price string or None
            non_member_price: Non-member price string

        Returns:
            Formatted pricing string
        """
        if member_price:
            return (
                f"Tarif Membre : {member_price} / Tarif Non Membre : {non_member_price}"
            )
        else:
            return f"Tarif Non Membre : {non_member_price}"

    @staticmethod
    def format_pricing_display_non_member_only(
        _: Optional[str], non_member_price: str
    ) -> str:
        """
        Format pricing for display showing only non-member price.

        Args:
            _: Member price string or None (ignored)
            non_member_price: Non-member price string

        Returns:
            Formatted pricing string with only non-member price
        """
        return f"Tarif : {non_member_price}"

    @staticmethod
    def format_availability(event: Event) -> str:
        """
        Format availability information.

        Args:
            event: Event object

        Returns:
            Formatted availability string
        """
        registered = event.numberOfPlayers or 0
        total = event.capacity or 0
        return f"Places disponibles : {total} / ✅ Inscrits actuellement : {registered} / {total}"

    @staticmethod
    def format_compact_event(event: Event) -> str:
        """
        Format event in compact format for 15-day listing.

        Format: "J-X DD/MM Event Name - XX CHF NM (x/total) (CODE)"

        Args:
            event: Event object

        Returns:
            Formatted compact event string
        """
        j_minus = EventFormatter.calculate_j_minus(event.start_datetime)

        # Add DD/MM date format after J-X
        zurich_tz = ZoneInfo("Europe/Zurich")
        event_dt = event.start_datetime
        if event_dt.tzinfo is None:
            event_dt = event_dt.replace(tzinfo=ZoneInfo("UTC"))
        event_dt_zurich = event_dt.astimezone(zurich_tz)
        date_short = event_dt_zurich.strftime("%d/%m")

        _, non_member_price = event.pricing_info

        # Use short code if available, otherwise truncate event ID
        code = event.shortCode or event.id[:7]

        # Add registration count
        registered = event.numberOfPlayers or 0
        total = event.capacity or 0
        registration_info = (
            f"({registered}/{total})" if total > 0 else f"({registered})"
        )

        return f"{j_minus} {date_short} {event.title} - {non_member_price} {registration_info} ({code})"

    @staticmethod
    def format_detailed_event(event: Event) -> str:
        """
        Format event in detailed emoji format for 7-day listing.

        Uses the emoji template from the plan:
        📅 Date : DD/MM/YYYY 🕒 Horaire : HH:MM
        📍 Lieu : [Venue Name]
        📝 Format : [Event Title]
        💰 [Pricing info]
        📜 Niveau d'application des règles : [Rules Level]
        👥 [Availability info]
        📱 Code Companion : [Code]

        Args:
            event: Event object

        Returns:
            Formatted detailed event string with emojis
        """
        date_str = EventFormatter.format_date_french(event.start_datetime)
        time_str = EventFormatter.format_time_french(event.start_datetime)

        member_price, non_member_price = event.pricing_info
        pricing_str = EventFormatter.format_pricing_display_non_member_only(
            member_price, non_member_price
        )

        availability_str = EventFormatter.format_availability(event)

        # Use short code if available, otherwise use event ID
        code = event.shortCode or event.id

        # Use eventFormat name if available, otherwise fall back to title
        format_name = event.eventFormat.name if event.eventFormat.name else event.title

        # Get the French day name using Zurich timezone
        zurich_tz = ZoneInfo("Europe/Zurich")
        event_dt = event.start_datetime
        if event_dt.tzinfo is None:
            event_dt = event_dt.replace(tzinfo=ZoneInfo("UTC"))
        event_dt_zurich = event_dt.astimezone(zurich_tz)

        day_name = EventFormatter.FRENCH_DAYS[event_dt_zurich.weekday()]
        day_name_capitalized = day_name.capitalize()

        lines = [
            f"{day_name_capitalized}: {event.title}",
            f"📅 Date : {date_str} 🕒 Horaire : {time_str}",
            f"📍 Lieu : {event.venue_name}",
            f"📝 Format : {format_name}",
            f"💰 {pricing_str}",
            f"📜 Niveau d'application des règles : {event.rules_level_french}",
            f"👥 {availability_str}",
            f"📱 Code Companion : {code}",
        ]

        # Add description if available
        if event.description and event.description.strip():
            lines.append(f"📄 Description :\n{event.description.strip()}")

        return "\n".join(lines)

    @staticmethod
    def format_event_list_compact(events: List[Event], days_ahead: int = 15) -> str:
        """
        Format list of events in compact format.

        Args:
            events: List of events to format
            days_ahead: Number of days to filter (default: 15)

        Returns:
            Formatted compact event list
        """
        if not events:
            return "Aucun événement trouvé."

        # Filter events within the date range using Zurich timezone
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

        if not filtered_events:
            return "Aucun événement dans les prochains jours."

        lines = ["Prochains événements:"]
        for event in filtered_events:
            lines.append(EventFormatter.format_compact_event(event))

        return "\n".join(lines)

    @staticmethod
    def format_event_list_detailed(events: List[Event], days_ahead: int = 7) -> str:
        """
        Format list of events in detailed emoji format.

        Args:
            events: List of events to format
            days_ahead: Number of days to filter (default: 7)

        Returns:
            Formatted detailed event list with emojis
        """
        if not events:
            return "Aucun événement trouvé."

        # Filter events within the date range using Zurich timezone
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

        if not filtered_events:
            return "Aucun événement dans les 7 prochains jours."

        lines = [f"Événements des {days_ahead} prochains jours:", ""]

        for i, event in enumerate(filtered_events):
            if i > 0:
                lines.append("")  # Empty line between events
            lines.append(EventFormatter.format_detailed_event(event))

        return "\n".join(lines)

    @staticmethod
    def format_complete_message(events: List[Event]) -> str:
        """
        Format complete message with both compact and detailed sections.

        Args:
            events: List of events to format

        Returns:
            Complete formatted message with both sections
        """
        if not events:
            return "Aucun événement trouvé."

        # Section 1: Compact 15-day format
        compact_section = EventFormatter.format_event_list_compact(
            events, days_ahead=15
        )

        # Section 2: Detailed 7-day format
        detailed_section = EventFormatter.format_event_list_detailed(
            events, days_ahead=7
        )

        # Combine sections
        return f"{compact_section}\n\n{detailed_section}"
