"""
Unit tests for common.events.fetcher module.

Tests integration with mocked API responses, error handling, and organization filtering.
"""

from unittest.mock import AsyncMock, Mock, patch

import httpx
import pytest

from common.events.fetcher import EventFetcher
from common.events.models import Event


class TestEventFetcher:
    """Tests for EventFetcher class."""

    @pytest.fixture
    def fetcher(self):
        """Create EventFetcher instance for testing."""
        return EventFetcher(timeout=10, max_retries=2, retry_delay=0.1)

    @pytest.fixture
    def mock_graphql_response(self):
        """Mock GraphQL response data."""
        return {
            "data": {
                "searchEvents": {
                    "events": [
                        {
                            "id": "9517226",
                            "capacity": 30,
                            "shortCode": "ABC123",
                            "entryFee": {
                                "amount": 1500,
                                "currency": "CHF",
                                "__typename": "Money",
                            },
                            "description": "Membres 12 CHF Non Membre 15 CHF",
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
                            "organization": {
                                "id": "10933",
                                "isPremium": False,
                                "name": "Xenomorphe",
                                "__typename": "Organization",
                            },
                            "eventFormat": {
                                "id": "5iHivnNhxMmSTOhGjL7cyo",
                                "__typename": "EventFormat",
                            },
                            "numberOfPlayers": 8,
                            "__typename": "Event",
                        },
                        {
                            "id": "9501806",
                            "capacity": 10,
                            "shortCode": "XYZ789",
                            "entryFee": {
                                "amount": 0,
                                "currency": "CHF",
                                "__typename": "Money",
                            },
                            "description": "Test event",
                            "distance": 296.24341541,
                            "emailAddress": "info@other.ch",
                            "hasTop8": False,
                            "isAdHoc": False,
                            "isOnline": False,
                            "latitude": 46.20676,
                            "longitude": 6.1414,
                            "title": "Other Event",
                            "eventTemplateId": "",
                            "pairingType": "SWISS",
                            "phoneNumber": "+42(0) 225577622",
                            "requiredTeamSize": 1,
                            "rulesEnforcementLevel": "REGULAR",
                            "scheduledStartTime": "2025-09-13T10:00:00.0000000Z",
                            "startingTableNumber": 1,
                            "status": "SCHEDULED",
                            "tags": ["magic:_the_gathering"],
                            "timeZone": "Europe/Zurich",
                            "cardSet": {"id": "test-set-id", "__typename": "CardSet"},
                            "organization": {
                                "id": "6081",
                                "isPremium": False,
                                "name": "Other Org",
                                "__typename": "Organization",
                            },
                            "eventFormat": {
                                "id": "other-format-id",
                                "__typename": "EventFormat",
                            },
                            "numberOfPlayers": 0,
                            "__typename": "Event",
                        },
                    ],
                    "pageInfo": {
                        "page": 0,
                        "pageSize": 50,
                        "totalResults": 2,
                        "__typename": "PageInfo",
                    },
                    "__typename": "EventPage",
                }
            }
        }

    def test_build_graphql_query(self, fetcher):
        """Test GraphQL query building."""
        query = fetcher._build_graphql_query()

        # Check for required fields in query
        assert "searchEvents" in query
        assert "events" in query
        assert "organization" in query
        assert "entryFee" in query
        assert "description" in query  # Important for pricing extraction

    def test_build_query_variables(self, fetcher):
        """Test query variables building."""
        variables = fetcher._build_query_variables(page=0, page_size=25)

        assert variables["latitude"] == EventFetcher.DEFAULT_LATITUDE
        assert variables["longitude"] == EventFetcher.DEFAULT_LONGITUDE
        assert variables["maxMeters"] == EventFetcher.DEFAULT_MAX_METERS
        assert variables["tags"] == ["magic:_the_gathering"]
        assert variables["sort"] == "date"
        assert variables["sortDirection"] == "Asc"
        assert variables["orgs"] == []  # Empty for post-processing filter
        assert variables["page"] == 0
        assert variables["pageSize"] == 25

    @pytest.mark.asyncio
    async def test_make_request_success(self, fetcher, mock_graphql_response):
        """Test successful HTTP request."""
        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client

            mock_response = Mock()
            mock_response.json.return_value = mock_graphql_response
            mock_response.raise_for_status.return_value = None
            mock_client.post.return_value = mock_response

            variables = {"test": "data"}
            result = await fetcher._make_request(variables)

            assert result == mock_graphql_response
            mock_client.post.assert_called_once()

    @pytest.mark.asyncio
    async def test_make_request_graphql_errors(self, fetcher):
        """Test HTTP request with GraphQL errors."""
        error_response = {
            "errors": [{"message": "Field error"}, {"message": "Another error"}]
        }

        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client

            mock_response = Mock()
            mock_response.json.return_value = error_response
            mock_response.raise_for_status.return_value = None
            mock_client.post.return_value = mock_response

            with pytest.raises(httpx.HTTPError) as exc_info:
                await fetcher._make_request({"test": "data"})

            assert "GraphQL errors" in str(exc_info.value)
            assert "Field error" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_make_request_retry_logic(self, fetcher):
        """Test retry logic on HTTP errors."""
        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client

            # First two calls fail, third succeeds
            mock_client.post.side_effect = [
                httpx.ConnectTimeout("Connection timeout"),
                httpx.ConnectTimeout("Connection timeout"),
                Mock(json=lambda: {"data": "success"}, raise_for_status=lambda: None),
            ]

            with patch("asyncio.sleep"):  # Speed up test
                result = await fetcher._make_request({"test": "data"})

            assert result == {"data": "success"}
            assert mock_client.post.call_count == 3

    @pytest.mark.asyncio
    async def test_make_request_max_retries_exceeded(self, fetcher):
        """Test behavior when max retries are exceeded."""
        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client

            # All calls fail
            mock_client.post.side_effect = httpx.ConnectTimeout("Connection timeout")

            with patch("asyncio.sleep"):  # Speed up test
                with pytest.raises(httpx.ConnectTimeout):
                    await fetcher._make_request({"test": "data"})

            # Should try max_retries + 1 times
            assert mock_client.post.call_count == fetcher.max_retries + 1

    def test_parse_response_success(self, fetcher, mock_graphql_response):
        """Test successful response parsing."""
        events = fetcher._parse_response(mock_graphql_response)

        assert len(events) == 2
        assert all(isinstance(event, Event) for event in events)

        # Check specific event data
        xenomorphe_event = events[0]
        assert xenomorphe_event.id == "9517226"
        assert xenomorphe_event.organization.id == "10933"
        assert xenomorphe_event.title == "Duel Commander Monthly"

        other_event = events[1]
        assert other_event.id == "9501806"
        assert other_event.organization.id == "6081"

    def test_parse_response_invalid_format(self, fetcher):
        """Test response parsing with invalid format."""
        invalid_response = {"invalid": "format"}

        with pytest.raises(Exception):  # Should raise ValidationError or similar
            fetcher._parse_response(invalid_response)

    def test_parse_response_invalid_event_data(self, fetcher):
        """Test response parsing with invalid event data."""
        response_with_invalid_event = {
            "data": {
                "searchEvents": {
                    "events": [
                        {
                            "id": "valid-event",
                            "capacity": 20,
                            "entryFee": {"amount": 1000, "currency": "CHF"},
                            "hasTop8": False,
                            "isAdHoc": False,
                            "isOnline": False,
                            "title": "Valid Event",
                            "eventTemplateId": "",
                            "pairingType": "SWISS",
                            "requiredTeamSize": 1,
                            "rulesEnforcementLevel": "CASUAL",
                            "scheduledStartTime": "2025-09-12T19:00:00.0000000Z",
                            "startingTableNumber": 1,
                            "status": "SCHEDULED",
                            "tags": ["magic:_the_gathering"],
                            "timeZone": "Europe/Paris",
                            "organization": {
                                "id": "10933",
                                "isPremium": False,
                                "name": "Test",
                            },
                            "eventFormat": {"id": "test-format"},
                        },
                        {
                            "id": "invalid-event",
                            # Missing required fields
                        },
                    ],
                    "pageInfo": {"page": 0, "pageSize": 50, "totalResults": 2},
                }
            }
        }

        # Should parse valid event and skip invalid one
        events = fetcher._parse_response(response_with_invalid_event)
        assert len(events) == 1
        assert events[0].id == "valid-event"

    @pytest.mark.asyncio
    async def test_fetch_events_organization_filtering(
        self, fetcher, mock_graphql_response
    ):
        """Test event fetching with organization filtering."""
        with patch.object(fetcher, "_make_request", return_value=mock_graphql_response):
            events = await fetcher.fetch_events(organization_id="10933")

            # Should only return Xenomorphe events
            assert len(events) == 1
            assert events[0].organization.id == "10933"
            assert events[0].title == "Duel Commander Monthly"

    @pytest.mark.asyncio
    async def test_fetch_events_no_matching_organization(
        self, fetcher, mock_graphql_response
    ):
        """Test event fetching with no matching organization."""
        with patch.object(fetcher, "_make_request", return_value=mock_graphql_response):
            events = await fetcher.fetch_events(organization_id="99999")

            # Should return empty list
            assert len(events) == 0

    @pytest.mark.asyncio
    async def test_fetch_events_pagination(self, fetcher):
        """Test event fetching with pagination."""
        # Mock two pages of results
        page1_response = {
            "data": {
                "searchEvents": {
                    "events": [
                        {
                            "id": "event1",
                            "capacity": 20,
                            "entryFee": {"amount": 1000, "currency": "CHF"},
                            "hasTop8": False,
                            "isAdHoc": False,
                            "isOnline": False,
                            "title": "Event 1",
                            "eventTemplateId": "",
                            "pairingType": "SWISS",
                            "requiredTeamSize": 1,
                            "rulesEnforcementLevel": "CASUAL",
                            "scheduledStartTime": "2025-09-12T19:00:00.0000000Z",
                            "startingTableNumber": 1,
                            "status": "SCHEDULED",
                            "tags": ["magic:_the_gathering"],
                            "timeZone": "Europe/Paris",
                            "organization": {
                                "id": "10933",
                                "isPremium": False,
                                "name": "Xenomorphe",
                            },
                            "eventFormat": {"id": "test-format"},
                        }
                    ],
                    "pageInfo": {"page": 0, "pageSize": 1, "totalResults": 2},
                }
            }
        }

        page2_response = {
            "data": {
                "searchEvents": {
                    "events": [
                        {
                            "id": "event2",
                            "capacity": 20,
                            "entryFee": {"amount": 1200, "currency": "CHF"},
                            "hasTop8": False,
                            "isAdHoc": False,
                            "isOnline": False,
                            "title": "Event 2",
                            "eventTemplateId": "",
                            "pairingType": "SWISS",
                            "requiredTeamSize": 1,
                            "rulesEnforcementLevel": "CASUAL",
                            "scheduledStartTime": "2025-09-13T19:00:00.0000000Z",
                            "startingTableNumber": 1,
                            "status": "SCHEDULED",
                            "tags": ["magic:_the_gathering"],
                            "timeZone": "Europe/Paris",
                            "organization": {
                                "id": "10933",
                                "isPremium": False,
                                "name": "Xenomorphe",
                            },
                            "eventFormat": {"id": "test-format"},
                        }
                    ],
                    "pageInfo": {"page": 1, "pageSize": 1, "totalResults": 2},
                }
            }
        }

        with patch.object(
            fetcher, "_make_request", side_effect=[page1_response, page2_response]
        ):
            with patch("asyncio.sleep"):  # Speed up test
                events = await fetcher.fetch_events(
                    organization_id="10933", page_size=1
                )

        # Should get events from both pages
        assert len(events) == 2
        assert events[0].id == "event1"
        assert events[1].id == "event2"

    @pytest.mark.asyncio
    async def test_fetch_events_by_date_range(self, fetcher, mock_graphql_response):
        """Test event fetching with date range filtering."""
        with patch.object(fetcher, "_make_request", return_value=mock_graphql_response):
            events = await fetcher.fetch_events_by_date_range(
                organization_id="10933",
                days_ahead=365,  # Large range to include test events
            )

            # Should return filtered events
            assert len(events) == 1
            assert events[0].organization.id == "10933"
