"""
GraphQL client for fetching MTG events from Wizards' API.

This module handles HTTP requests to the Wizards GraphQL endpoint,
organization filtering, and error handling.
"""

import asyncio
import logging
from typing import Any, Dict, List, Optional

import httpx
from pydantic import ValidationError

from .models import Event, EventFilter

logger = logging.getLogger(__name__)


class EventFetcher:
    """Client for fetching MTG events from Wizards' GraphQL API."""

    BASE_URL = "https://api.tabletop.wizards.com/silverbeak-griffin-service/graphql"

    # Default geographic coordinates for Geneva area (broad search)
    DEFAULT_LATITUDE = 46.2043907
    DEFAULT_LONGITUDE = 6.1431577
    DEFAULT_MAX_METERS = 50000  # 50km radius for broad search

    def __init__(
        self, timeout: int = 30, max_retries: int = 3, retry_delay: float = 1.0
    ):
        """
        Initialize the event fetcher.

        Args:
            timeout: Request timeout in seconds
            max_retries: Maximum number of retry attempts
            retry_delay: Delay between retries in seconds
        """
        self.timeout = timeout
        self.max_retries = max_retries
        self.retry_delay = retry_delay

    def _build_graphql_query(self) -> str:
        """
        Build the GraphQL query string for event search.

        Returns:
            GraphQL query string with all required fields
        """
        return """
        query queryEvents($latitude: Float!, $longitude: Float!, $maxMeters: Int!,
                         $tags: [String!]!, $sort: EventSearchSortField,
                         $sortDirection: EventSearchSortDirection, $orgs: [ID!],
                         $startDate: DateTime, $endDate: DateTime, $page: Int, $pageSize: Int) {
            searchEvents(query: {
                latitude: $latitude,
                longitude: $longitude,
                maxMeters: $maxMeters,
                tags: $tags,
                sort: $sort,
                sortDirection: $sortDirection,
                orgs: $orgs,
                startDate: $startDate,
                endDate: $endDate,
                page: $page,
                pageSize: $pageSize
            }) {
                events {
                    id
                    capacity
                    shortCode
                    entryFee {
                        amount
                        currency
                    }
                    description
                    latitude
                    longitude
                    title
                    rulesEnforcementLevel
                    scheduledStartTime
                    organization {
                        id
                        name
                    }
                    eventFormat {
                        id
                        name
                    }
                    numberOfPlayers
                }
                pageInfo {
                    page
                    pageSize
                    totalResults
                }
            }
        }
        """

    def _build_query_variables(
        self,
        page: int = 0,
        page_size: int = 50,
        organization_ids: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Build query variables for the GraphQL request.

        Args:
            page: Page number for pagination
            page_size: Number of events per page
            organization_ids: List of organization IDs to filter by

        Returns:
            Dictionary of query variables
        """
        return {
            "latitude": self.DEFAULT_LATITUDE,
            "longitude": self.DEFAULT_LONGITUDE,
            "maxMeters": self.DEFAULT_MAX_METERS,
            "tags": ["magic:_the_gathering"],
            "sort": "date",
            "sortDirection": "Asc",
            "orgs": organization_ids or [],  # Filter by specific orgs at query level
            "page": page,
            "pageSize": page_size,
        }

    async def _make_request(self, variables: Dict[str, Any]) -> Dict[str, Any]:
        """
        Make HTTP request to GraphQL endpoint with retry logic.

        Args:
            variables: Query variables

        Returns:
            GraphQL response data

        Raises:
            httpx.HTTPError: If all retry attempts fail
        """
        query = self._build_graphql_query()
        payload = {
            "operationName": "queryEvents",
            "variables": variables,
            "query": query,
        }

        for attempt in range(self.max_retries + 1):
            try:
                async with httpx.AsyncClient(timeout=self.timeout) as client:
                    response = await client.post(
                        self.BASE_URL,
                        json=payload,
                        headers={"Content-Type": "application/json"},
                    )
                    response.raise_for_status()

                    data = response.json()

                    # Check for GraphQL errors
                    if "errors" in data:
                        error_msg = "; ".join(
                            [
                                error.get("message", "Unknown error")
                                for error in data["errors"]
                            ]
                        )
                        raise httpx.HTTPError(f"GraphQL errors: {error_msg}")

                    return data

            except httpx.HTTPError as e:
                logger.warning(f"Request attempt {attempt + 1} failed: {e}")
                if attempt < self.max_retries:
                    await asyncio.sleep(self.retry_delay * (attempt + 1))
                else:
                    raise

    def _parse_response(
        self, response_data: Dict[str, Any], show_raw_events: bool = False
    ) -> List[Event]:
        """
        Parse GraphQL response into Event objects.

        Args:
            response_data: Raw GraphQL response
            show_raw_events: If True, log raw event data for debugging

        Returns:
            List of parsed Event objects

        Raises:
            ValidationError: If response format is invalid
        """
        try:
            search_events = response_data["data"]["searchEvents"]
            events_data = search_events["events"]

            events = []
            for event_data in events_data:
                if show_raw_events:
                    import json

                    logger.info(
                        f"Raw event data: {json.dumps(event_data, indent=2, default=str)}"
                    )

                try:
                    event = Event(**event_data)
                    events.append(event)
                except ValidationError as e:
                    logger.warning(
                        f"Failed to parse event {event_data.get('id', 'unknown')}: {e}"
                    )
                    continue

            return events

        except KeyError as e:
            raise ValidationError(f"Invalid response format: missing key {e}")

    async def fetch_events(
        self,
        organization_id: str = "10933",
        days_ahead: int = 15,
        page_size: int = 50,
        show_raw_events: bool = False,
    ) -> List[Event]:
        """
        Fetch events for the specified organization.

        Args:
            organization_id: Organization ID to filter by (default: "10933" for Xenomorphe)
            days_ahead: Number of days ahead to search
            page_size: Number of events per page
            show_raw_events: If True, log raw event data for debugging

        Returns:
            List of events filtered by organization
        """
        all_events = []
        page = 0

        logger.info(
            f"Fetching events for organization {organization_id}, {days_ahead} days ahead"
        )

        # Fetch all pages until we have enough events or no more results
        while True:
            variables = self._build_query_variables(
                page=page, page_size=page_size, organization_ids=[organization_id]
            )

            try:
                response_data = await self._make_request(variables)
                events = self._parse_response(response_data, show_raw_events)

                if not events:
                    break

                all_events.extend(events)

                # Check if we have more pages
                page_info = response_data["data"]["searchEvents"]["pageInfo"]
                total_results = page_info["totalResults"]
                current_page = page_info["page"]

                if (current_page + 1) * page_size >= total_results:
                    break

                page += 1

                # Add small delay between requests to be conservative
                await asyncio.sleep(0.5)

            except Exception as e:
                logger.error(f"Failed to fetch events page {page}: {e}")
                break

        # Post-processing filter as safety measure (in case API filtering is incomplete)
        filtered_events = [
            event for event in all_events if event.organization.id == organization_id
        ]

        logger.info(
            f"Fetched {len(all_events)} events, filtered to {len(filtered_events)} for organization {organization_id}"
        )

        # Sort by start time
        filtered_events.sort(key=lambda e: e.start_datetime)

        return filtered_events

    async def fetch_events_by_date_range(
        self, organization_id: str = "10933", days_ahead: int = 15
    ) -> List[Event]:
        """
        Fetch events filtered by organization and date range.

        Args:
            organization_id: Organization ID to filter by
            days_ahead: Maximum days ahead to include

        Returns:
            List of events within the specified date range
        """
        events = await self.fetch_events(
            organization_id=organization_id, days_ahead=days_ahead
        )
        return EventFilter.filter_by_date_range(events, days_ahead)
