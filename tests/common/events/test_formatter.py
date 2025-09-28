"""
Unit tests for common.events.formatter module.

Tests J-X calculations, formatting functions, emoji template generation, and price formatting.
"""

from datetime import datetime, timedelta

import pytest

from common.events.formatter import EventFormatter
from common.events.models import Event


class TestEventFormatter:
    """Tests for EventFormatter utility."""

    @pytest.fixture
    def sample_event_data(self):
        """Sample event data for testing."""
        return {
            "id": "9517226",
            "capacity": 30,
            "shortCode": "ABC123",
            "entryFee": {"amount": 1500, "currency": "CHF"},
            "description": "Membres 12 CHF Non Membre 15 CHF\nLots pour les 8 premiers.\n",
            "distance": 538.66338732,
            "emailAddress": "info@xenomorphe.ch",
            "hasTop8": False,
            "isAdHoc": False,
            "isOnline": False,
            "latitude": 46.20118,
            "longitude": 6.13793,
            "title": "Duel Commander Monthly",
            "eventTemplateId": "",
            "pairingType": "SWISS",
            "phoneNumber": "+41(0) 223297052",
            "requiredTeamSize": 1,
            "rulesEnforcementLevel": "COMPETITIVE",
            "scheduledStartTime": "2025-09-12T19:00:00.0000000Z",
            "startingTableNumber": 1,
            "status": "SCHEDULED",
            "tags": ["magic:_the_gathering", "commander"],
            "timeZone": "Europe/Paris",
            "cardSet": None,
            "organization": {"id": "10933", "name": "Xenomorphe"},
            "eventFormat": {"id": "5iHivnNhxMmSTOhGjL7cyo", "name": "Duel Commander"},
            "numberOfPlayers": 8,
        }

    def test_calculate_j_minus_today(self):
        """Test J-minus calculation for today."""
        today = datetime.now()
        result = EventFormatter.calculate_j_minus(today)
        assert result == "J"

    def test_calculate_j_minus_tomorrow(self):
        """Test J-minus calculation for tomorrow."""
        tomorrow = datetime.now() + timedelta(days=1)
        result = EventFormatter.calculate_j_minus(tomorrow)
        assert result == "J-1"

    def test_calculate_j_minus_future_days(self):
        """Test J-minus calculation for future days."""
        future_date = datetime.now() + timedelta(days=5)
        result = EventFormatter.calculate_j_minus(future_date)
        assert result == "J-5"

    def test_calculate_j_minus_past_days(self):
        """Test J-minus calculation for past days."""
        past_date = datetime.now() - timedelta(days=3)
        result = EventFormatter.calculate_j_minus(past_date)
        assert result == "J+3"

    def test_format_date_french(self):
        """Test French date formatting."""
        test_date = datetime(2025, 9, 12, 19, 0, 0)
        result = EventFormatter.format_date_french(test_date)
        assert result == "12/09/2025"

    def test_format_time_french(self):
        """Test French time formatting."""
        from zoneinfo import ZoneInfo

        # Test with UTC timezone (will be converted to Zurich time)
        test_date = datetime(
            2025, 9, 12, 17, 30, 0, tzinfo=ZoneInfo("UTC")
        )  # UTC 17:30 = Zurich 19:30
        result = EventFormatter.format_time_french(test_date)
        assert result == "19:30"

        test_date_morning = datetime(
            2025, 9, 12, 7, 5, 0, tzinfo=ZoneInfo("UTC")
        )  # UTC 07:05 = Zurich 09:05
        result_morning = EventFormatter.format_time_french(test_date_morning)
        assert result_morning == "09:05"

    def test_format_day_date_french(self):
        """Test French day and date formatting."""
        # Test different weekdays
        monday = datetime(2025, 9, 8)  # This is a Monday
        result_monday = EventFormatter.format_day_date_french(monday)
        assert result_monday == "lundi 8 septembre"

        friday = datetime(2025, 9, 12)  # This is a Friday
        result_friday = EventFormatter.format_day_date_french(friday)
        assert result_friday == "vendredi 12 septembre"

    def test_format_pricing_display_with_member_price(self):
        """Test pricing display with member price."""
        result = EventFormatter.format_pricing_display("12 CHF", "15 CHF")
        expected = "Tarif Membre : 12 CHF / Tarif Non Membre : 15 CHF"
        assert result == expected

    def test_format_pricing_display_without_member_price(self):
        """Test pricing display without member price."""
        result = EventFormatter.format_pricing_display(None, "15 CHF")
        expected = "Tarif Non Membre : 15 CHF"
        assert result == expected

    def test_format_pricing_display_non_member_only_with_member_price(self):
        """Test non-member only pricing display with member price."""
        result = EventFormatter.format_pricing_display_non_member_only(
            "12 CHF", "15 CHF"
        )
        expected = "Tarif : 15 CHF"
        assert result == expected

    def test_format_pricing_display_non_member_only_without_member_price(self):
        """Test non-member only pricing display without member price."""
        result = EventFormatter.format_pricing_display_non_member_only(None, "15 CHF")
        expected = "Tarif : 15 CHF"
        assert result == expected

    def test_format_availability(self, sample_event_data):
        """Test availability formatting."""
        event = Event(**sample_event_data)
        result = EventFormatter.format_availability(event)
        expected = "Places disponibles : 30 / ✅ Inscrits actuellement : 8 / 30"
        assert result == expected

    def test_format_availability_no_players(self, sample_event_data):
        """Test availability formatting with no players."""
        sample_event_data["numberOfPlayers"] = None
        event = Event(**sample_event_data)
        result = EventFormatter.format_availability(event)
        expected = "Places disponibles : 30 / ✅ Inscrits actuellement : 0 / 30"
        assert result == expected

    def test_format_compact_event(self, sample_event_data):
        """Test compact event formatting."""
        # Use a specific date in the future for predictable J+X calculation
        future_date = datetime.now() + timedelta(days=3)
        sample_event_data["scheduledStartTime"] = future_date.isoformat() + "Z"

        event = Event(**sample_event_data)
        result = EventFormatter.format_compact_event(event)

        # Should contain J-3, title, price, registration count, and shortCode
        assert "J-3" in result
        assert "Duel Commander Monthly" in result
        assert "15 CHF" in result
        assert "(8/30)" in result  # Registration count
        assert "(ABC123)" in result

    def test_format_compact_event_no_short_code(self, sample_event_data):
        """Test compact event formatting without short code."""
        sample_event_data["shortCode"] = None
        event = Event(**sample_event_data)
        result = EventFormatter.format_compact_event(event)

        # Should use truncated event ID and include registration count
        assert "(8/30)" in result  # Registration count
        assert "(9517226)" in result

    def test_format_compact_event_no_capacity(self, sample_event_data):
        """Test compact event formatting with no capacity."""
        sample_event_data["capacity"] = None
        event = Event(**sample_event_data)
        result = EventFormatter.format_compact_event(event)

        # Should show only registered players when no capacity
        assert "(8)" in result  # Registration count without capacity
        assert "ABC123" in result

    def test_format_detailed_event(self, sample_event_data):
        """Test detailed event formatting with emojis."""
        event = Event(**sample_event_data)
        result = EventFormatter.format_detailed_event(event)

        # Check for all expected emojis and content
        assert (
            "Vendredi: Duel Commander Monthly" in result
        )  # Day and title as first line
        assert "📅 Date : 12/09/2025 🕒 Horaire : 21:00" in result
        assert "📍 Lieu : Clos Voltaire 49 rue de Lyon" in result
        assert "📝 Format : Duel Commander" in result  # Now uses eventFormat.name
        assert "💰 Tarif : 15 CHF" in result  # Now shows only non-member pricing
        assert "📜 Niveau d'application des règles : Compétitif" in result
        assert (
            "👥 Places disponibles : 30 / ✅ Inscrits actuellement : 8 / 30" in result
        )
        assert "📱 Code Companion : ABC123" in result
        assert (
            "📄 Description :\nMembres 12 CHF Non Membre 15 CHF" in result
        )  # Now includes description with line break

    def test_format_detailed_event_no_short_code(self, sample_event_data):
        """Test detailed event formatting without short code."""
        sample_event_data["shortCode"] = None
        event = Event(**sample_event_data)
        result = EventFormatter.format_detailed_event(event)

        # Should use full event ID and include day and title
        assert "Vendredi: Duel Commander Monthly" in result
        assert "📱 Code Companion : 9517226" in result

    def test_format_detailed_event_no_event_format_name(self, sample_event_data):
        """Test detailed event formatting when eventFormat has no name."""
        sample_event_data["eventFormat"]["name"] = None
        event = Event(**sample_event_data)
        result = EventFormatter.format_detailed_event(event)

        # Should fall back to event title
        assert "📝 Format : Duel Commander Monthly" in result

    def test_format_detailed_event_no_description(self, sample_event_data):
        """Test detailed event formatting without description."""
        sample_event_data["description"] = None
        event = Event(**sample_event_data)
        result = EventFormatter.format_detailed_event(event)

        # Should not include description line
        assert "📄 Description :" not in result

    def test_format_event_list_compact_empty(self):
        """Test compact event list formatting with empty list."""
        result = EventFormatter.format_event_list_compact([])
        assert result == "Aucun événement trouvé."

    def test_format_event_list_compact_no_events_in_range(self, sample_event_data):
        """Test compact event list with no events in range."""
        # Set event far in the future (beyond the days_ahead range)
        far_future_date = datetime.now() + timedelta(days=30)
        sample_event_data["scheduledStartTime"] = far_future_date.isoformat() + "Z"
        event = Event(**sample_event_data)

        result = EventFormatter.format_event_list_compact([event], days_ahead=15)
        assert result == "Aucun événement dans les prochains jours."

    def test_format_event_list_compact_with_events(self, sample_event_data):
        """Test compact event list formatting with events."""
        # Set event in near future
        future_date = datetime.now() + timedelta(days=5)
        sample_event_data["scheduledStartTime"] = future_date.isoformat() + "Z"
        event = Event(**sample_event_data)

        result = EventFormatter.format_event_list_compact([event], days_ahead=15)

        assert "Prochains événements:" in result
        assert "Duel Commander Monthly" in result

    def test_format_event_list_detailed_empty(self):
        """Test detailed event list formatting with empty list."""
        result = EventFormatter.format_event_list_detailed([])
        assert result == "Aucun événement trouvé."

    def test_format_event_list_detailed_no_events_in_range(self, sample_event_data):
        """Test detailed event list with no events in range."""
        # Set event far in the future (beyond the days_ahead range)
        far_future_date = datetime.now() + timedelta(days=30)
        sample_event_data["scheduledStartTime"] = far_future_date.isoformat() + "Z"
        event = Event(**sample_event_data)

        result = EventFormatter.format_event_list_detailed([event], days_ahead=7)
        assert result == "Aucun événement dans les 7 prochains jours."

    def test_format_event_list_detailed_with_events(self, sample_event_data):
        """Test detailed event list formatting with events."""
        # Set event in near future
        future_date = datetime.now() + timedelta(days=3)
        sample_event_data["scheduledStartTime"] = future_date.isoformat() + "Z"
        event = Event(**sample_event_data)

        result = EventFormatter.format_event_list_detailed([event], days_ahead=7)

        assert "Événements des 7 prochains jours:" in result
        assert ":" in result  # Day: Title format should be present
        assert "📅 Date :" in result
        assert "📍 Lieu :" in result

    def test_format_event_list_detailed_multiple_events(self, sample_event_data):
        """Test detailed event list with multiple events."""
        # Create two events
        future_date_1 = datetime.now() + timedelta(days=2)
        future_date_2 = datetime.now() + timedelta(days=4)

        sample_event_data["scheduledStartTime"] = future_date_1.isoformat() + "Z"
        event1 = Event(**sample_event_data)

        sample_event_data_2 = sample_event_data.copy()
        sample_event_data_2["id"] = "event2"
        sample_event_data_2["title"] = "Another Event"
        sample_event_data_2["scheduledStartTime"] = future_date_2.isoformat() + "Z"
        # Make a deep copy of eventFormat and remove the name to test fallback
        sample_event_data_2["eventFormat"] = {
            "id": "5iHivnNhxMmSTOhGjL7cyo",
            "name": None,
        }
        event2 = Event(**sample_event_data_2)

        result = EventFormatter.format_event_list_detailed(
            [event1, event2], days_ahead=7
        )

        # Should have both events separated by empty line
        assert "Duel Commander" in result  # Now uses eventFormat.name
        assert (
            "Another Event" in result
        )  # This event has no eventFormat.name, so uses title
        # Should have empty lines between events
        lines = result.split("\n")
        assert "" in lines  # Empty line separator

    def test_format_complete_message_empty(self):
        """Test complete message formatting with empty list."""
        result = EventFormatter.format_complete_message([])
        assert result == "Aucun événement trouvé."

    def test_format_complete_message_with_events(self, sample_event_data):
        """Test complete message formatting with events."""
        # Set event in near future
        future_date = datetime.now() + timedelta(days=5)
        sample_event_data["scheduledStartTime"] = future_date.isoformat() + "Z"
        event = Event(**sample_event_data)

        result = EventFormatter.format_complete_message([event])

        # Should contain both sections
        assert "Prochains événements:" in result
        assert "Événements des 7 prochains jours:" in result

        # Should have both compact and detailed formatting
        assert "15 CHF" in result  # Compact format
        assert "📅 Date :" in result  # Detailed format

    def test_french_days_mapping(self):
        """Test French days mapping."""
        assert EventFormatter.FRENCH_DAYS[0] == "lundi"
        assert EventFormatter.FRENCH_DAYS[1] == "mardi"
        assert EventFormatter.FRENCH_DAYS[4] == "vendredi"
        assert EventFormatter.FRENCH_DAYS[6] == "dimanche"

    def test_french_months_mapping(self):
        """Test French months mapping."""
        assert EventFormatter.FRENCH_MONTHS[1] == "janvier"
        assert EventFormatter.FRENCH_MONTHS[9] == "septembre"
        assert EventFormatter.FRENCH_MONTHS[12] == "décembre"
