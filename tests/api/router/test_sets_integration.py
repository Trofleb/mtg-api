"""Integration tests for Sets Router endpoints.

This module tests the /sets endpoint which returns a list of unique MTG set names
from the cards collection, validating MongoDB aggregation and sorting.
"""

import pytest


@pytest.mark.integration
def test_get_sets_returns_unique_set_names(test_client):
    """Test that /sets endpoint returns all unique set names.

    This test validates that:
    - The endpoint returns HTTP 200
    - Response has correct structure: {"sets": [...]}
    - All unique set names are returned
    - Duplicate set names are deduplicated (MongoDB $group)
    - Multiple cards from the same set result in single entry

    Expected: 4 unique sets from sample data:
    - Limited Edition Alpha (4 cards)
    - Double Masters (1 card)
    - Conflux (1 card)
    - Innistrad (1 card)
    """
    response = test_client.get("/sets")

    assert response.status_code == 200

    data = response.json()
    assert "sets" in data
    assert isinstance(data["sets"], list)

    # Should have exactly 4 unique sets from sample data
    assert len(data["sets"]) == 4

    # Verify all expected sets are present
    expected_sets = {"Limited Edition Alpha", "Double Masters", "Conflux", "Innistrad"}
    assert set(data["sets"]) == expected_sets


@pytest.mark.integration
def test_get_sets_empty_database_returns_empty_list(test_client_empty):
    """Test that /sets endpoint handles empty database gracefully.

    This test validates that:
    - Empty database doesn't cause errors
    - Returns HTTP 200 (not 404 or 500)
    - Returns empty list, not null or error message
    - Response structure is still correct
    """
    response = test_client_empty.get("/sets")

    assert response.status_code == 200

    data = response.json()
    assert "sets" in data
    assert data["sets"] == []


@pytest.mark.integration
def test_get_sets_returns_alphabetically_sorted_descending(test_client):
    """Test that /sets endpoint returns sets sorted Z→A alphabetically.

    This test validates that:
    - MongoDB $sort stage with _id: -1 works correctly
    - Sets are in descending alphabetical order
    - Order is consistent across calls

    Expected order (Z→A):
    1. Limited Edition Alpha (starts with 'L')
    2. Innistrad (starts with 'I')
    3. Double Masters (starts with 'D')
    4. Conflux (starts with 'C')
    """
    response = test_client.get("/sets")

    assert response.status_code == 200

    data = response.json()
    sets = data["sets"]

    # Verify we have all 4 sets
    assert len(sets) == 4

    # Verify descending alphabetical order
    assert sets[0] == "Limited Edition Alpha"
    assert sets[1] == "Innistrad"
    assert sets[2] == "Double Masters"
    assert sets[3] == "Conflux"

    # Alternative verification: ensure list is sorted in descending order
    assert sets == sorted(sets, reverse=True)
