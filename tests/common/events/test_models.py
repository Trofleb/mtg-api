"""
Unit tests for common.events.models module.

Tests Pydantic models, validation logic, coordinate mapping, and pricing extraction.
"""

from datetime import datetime

import pytest

from common.events.models import (
    Event,
    EventFilter,
    EventFormat,
    Money,
    Organization,
    VenueMapping,
)


class TestMoney:
    """Tests for Money model."""

    def test_money_creation(self):
        """Test Money model creation."""
        money = Money(amount=1500, currency="CHF")
        assert money.amount == 1500
        assert money.currency == "CHF"


class TestOrganization:
    """Tests for Organization model."""

    def test_organization_creation(self):
        """Test Organization model creation."""
        org = Organization(id="10933", name="Xenomorphe")
        assert org.id == "10933"
        assert org.name == "Xenomorphe"


class TestEventFormat:
    """Tests for EventFormat model."""

    def test_event_format_creation(self):
        """Test EventFormat model creation."""
        format_obj = EventFormat(id="test-format-id")
        assert format_obj.id == "test-format-id"


class TestEvent:
    """Tests for Event model."""

    @pytest.fixture
    def sample_event_data(self):
        """Sample event data for testing."""
        return {
            "id": "9517226",
            "capacity": 30,
            "shortCode": "ABC123",
            "entryFee": {"amount": 1500, "currency": "CHF"},
            "description": "Membres 12 CHF Non Membre 15 CHF\nLots pour les 8 premiers.\n",
            "latitude": 46.20118,
            "longitude": 6.13793,
            "title": "Duel Commander Monthly",
            "rulesEnforcementLevel": "COMPETITIVE",
            "scheduledStartTime": "2025-09-12T19:00:00.0000000Z",
            "organization": {"id": "10933", "name": "Xenomorphe"},
            "eventFormat": {"id": "5iHivnNhxMmSTOhGjL7cyo"},
            "numberOfPlayers": 8,
        }

    def test_event_creation(self, sample_event_data):
        """Test Event model creation."""
        event = Event(**sample_event_data)
        assert event.id == "9517226"
        assert event.title == "Duel Commander Monthly"
        assert event.capacity == 30
        assert event.numberOfPlayers == 8

    def test_is_xenomorphe_property(self, sample_event_data):
        """Test is_xenomorphe property."""
        event = Event(**sample_event_data)
        assert event.is_xenomorphe is True

        # Test non-Xenomorphe organization
        sample_event_data["organization"]["id"] = "6081"
        event_non_xeno = Event(**sample_event_data)
        assert event_non_xeno.is_xenomorphe is False

    def test_start_datetime_property(self, sample_event_data):
        """Test start_datetime property parsing."""
        event = Event(**sample_event_data)
        expected_date = datetime(2025, 9, 12, 19, 0, 0).replace(tzinfo=None)
        actual_date = event.start_datetime.replace(tzinfo=None)
        assert actual_date == expected_date

    def test_venue_name_mapping(self, sample_event_data):
        """Test venue name mapping from coordinates."""
        event = Event(**sample_event_data)
        assert event.venue_name == "Clos Voltaire 49 rue de Lyon"

        # Test unknown coordinates
        sample_event_data["latitude"] = 45.0
        sample_event_data["longitude"] = 5.0
        event_unknown = Event(**sample_event_data)
        assert "Latitude: 45.0, Longitude: 5.0" in event_unknown.venue_name

    def test_entry_fee_formatted(self, sample_event_data):
        """Test entry fee formatting."""
        event = Event(**sample_event_data)
        assert event.entry_fee_formatted == "15.00 CHF"

        # Test zero amount
        sample_event_data["entryFee"]["amount"] = 0
        event_free = Event(**sample_event_data)
        assert event_free.entry_fee_formatted == "0.00 CHF"

    def test_pricing_info_with_member_pricing(self, sample_event_data):
        """Test pricing extraction with member pricing."""
        event = Event(**sample_event_data)
        member_price, non_member_price = event.pricing_info
        assert member_price == "12 CHF"
        assert non_member_price == "15 CHF"

    def test_pricing_info_without_member_pricing(self, sample_event_data):
        """Test pricing extraction without member pricing."""
        sample_event_data["description"] = "Just a regular event description"
        event = Event(**sample_event_data)
        member_price, non_member_price = event.pricing_info
        assert member_price is None
        assert non_member_price == "15.00 CHF"

    def test_pricing_info_no_description(self, sample_event_data):
        """Test pricing extraction with no description."""
        sample_event_data["description"] = None
        event = Event(**sample_event_data)
        member_price, non_member_price = event.pricing_info
        assert member_price is None
        assert non_member_price == "15.00 CHF"

    def test_pricing_info_alternative_patterns(self, sample_event_data):
        """Test pricing extraction with different patterns."""
        # Test alternative pattern
        sample_event_data["description"] = "10 CHF membres 13 CHF non membres"
        event = Event(**sample_event_data)
        member_price, non_member_price = event.pricing_info
        assert member_price == "10 CHF"
        assert non_member_price == "13 CHF"

        # Test another pattern
        sample_event_data["description"] = "Membre: 8 CHF Non-Membre: 12 CHF"
        event2 = Event(**sample_event_data)
        member_price2, non_member_price2 = event2.pricing_info
        assert member_price2 == "8 CHF"
        assert non_member_price2 == "12 CHF"

    def test_rules_level_french(self, sample_event_data):
        """Test rules enforcement level translation to French."""
        event = Event(**sample_event_data)
        assert event.rules_level_french == "Compétitif"

        # Test other levels
        sample_event_data["rulesEnforcementLevel"] = "CASUAL"
        event_casual = Event(**sample_event_data)
        assert event_casual.rules_level_french == "Casual"

        sample_event_data["rulesEnforcementLevel"] = "REGULAR"
        event_regular = Event(**sample_event_data)
        assert event_regular.rules_level_french == "Régulier"

        # Test unknown level
        sample_event_data["rulesEnforcementLevel"] = "UNKNOWN"
        event_unknown = Event(**sample_event_data)
        assert event_unknown.rules_level_french == "UNKNOWN"


class TestVenueMapping:
    """Tests for VenueMapping utility."""

    def test_get_venue_coordinates(self):
        """Test venue coordinate mapping."""
        venues = VenueMapping.get_venue_coordinates()

        assert len(venues) == 2
        assert (46.2114995, 6.1206073) in venues
        assert (46.20118, 6.13793) in venues

        expected_venue_1 = "Espace Santé Esclarmonde, Avenue Soret 39, 1203 Genève"
        expected_venue_2 = "Clos Voltaire 49 rue de Lyon"

        assert venues[(46.2114995, 6.1206073)] == expected_venue_1
        assert venues[(46.20118, 6.13793)] == expected_venue_2


class TestEventFilter:
    """Tests for EventFilter utility."""

    @pytest.fixture
    def sample_events(self):
        """Sample events for filtering tests."""
        from datetime import datetime, timedelta
        from zoneinfo import ZoneInfo

        # Create events relative to current time to make tests predictable
        now = datetime.now(ZoneInfo("UTC"))
        future_event_time = (now + timedelta(days=5)).isoformat().replace("+00:00", "Z")

        event_data_base = {
            "id": "test-event",
            "capacity": 20,
            "entryFee": {"amount": 1000, "currency": "CHF"},
            "title": "Test Event",
            "rulesEnforcementLevel": "CASUAL",
            "scheduledStartTime": future_event_time,
            "eventFormat": {"id": "test-format"},
        }

        # Create events with different organizations
        events = []
        for i, org_id in enumerate(["10933", "6081", "10933"]):
            event_data = event_data_base.copy()
            event_data["id"] = f"event-{i}"
            event_data["organization"] = {"id": org_id, "name": "Test Org"}
            events.append(Event(**event_data))

        return events

    def test_filter_by_organization(self, sample_events):
        """Test organization filtering."""
        filtered = EventFilter.filter_by_organization(sample_events, "10933")
        assert len(filtered) == 2
        assert all(event.organization.id == "10933" for event in filtered)

        filtered_other = EventFilter.filter_by_organization(sample_events, "6081")
        assert len(filtered_other) == 1
        assert filtered_other[0].organization.id == "6081"

    def test_filter_by_date_range(self, sample_events):
        """Test date range filtering."""
        # All events are in the future for this test
        filtered = EventFilter.filter_by_date_range(sample_events, days_ahead=365)
        assert len(filtered) == 3

        # Test with very short range (should filter out events)
        filtered_short = EventFilter.filter_by_date_range(sample_events, days_ahead=0)
        # Since test events are 5 days in the future, they should be filtered out with 0 days ahead
        assert len(filtered_short) == 0

        # Test with longer range (should include events)
        filtered_long = EventFilter.filter_by_date_range(sample_events, days_ahead=10)
        # Since test events are 5 days in the future, they should be included with 10 days ahead
        assert len(filtered_long) == 3
