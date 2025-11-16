"""Tests for custom MongoDB mock classes.

This module tests MockMongoCursor and MockMongoCollection to ensure they
correctly simulate MongoDB operations for integration testing.
"""

import pytest

from tests.mocks.mongodb import MockMongoCollection, MockMongoCursor

# Sample test data
SAMPLE_CARDS = [
    {
        "id": "1",
        "name": "Lightning Bolt",
        "colors": ["R"],
        "cmc": 1.0,
        "rarity": "common",
        "set_name": "Alpha",
    },
    {
        "id": "2",
        "name": "Counterspell",
        "colors": ["U"],
        "cmc": 2.0,
        "rarity": "uncommon",
        "set_name": "Alpha",
    },
    {
        "id": "3",
        "name": "Black Lotus",
        "colors": [],
        "cmc": 0.0,
        "rarity": "rare",
        "set_name": "Alpha",
    },
    {
        "id": "4",
        "name": "Progenitus",
        "colors": ["W", "U", "B", "R", "G"],
        "cmc": 10.0,
        "rarity": "mythic",
        "set_name": "Conflux",
    },
]


@pytest.mark.unit
def test_cursor_iteration():
    """Test that MockMongoCursor can be iterated."""
    cursor = MockMongoCursor(SAMPLE_CARDS)
    cards = list(cursor)

    assert len(cards) == 4
    assert cards[0]["name"] == "Lightning Bolt"
    assert cards[3]["name"] == "Progenitus"


@pytest.mark.unit
def test_cursor_sort_ascending():
    """Test that MockMongoCursor.sort() works in ascending order."""
    cursor = MockMongoCursor(SAMPLE_CARDS)
    cursor.sort("cmc", 1)
    cards = list(cursor)

    assert cards[0]["cmc"] == 0.0
    assert cards[1]["cmc"] == 1.0
    assert cards[2]["cmc"] == 2.0
    assert cards[3]["cmc"] == 10.0


@pytest.mark.unit
def test_cursor_sort_descending():
    """Test that MockMongoCursor.sort() works in descending order."""
    cursor = MockMongoCursor(SAMPLE_CARDS)
    cursor.sort("cmc", -1)
    cards = list(cursor)

    assert cards[0]["cmc"] == 10.0
    assert cards[3]["cmc"] == 0.0


@pytest.mark.unit
def test_cursor_limit():
    """Test that MockMongoCursor.limit() restricts results."""
    cursor = MockMongoCursor(SAMPLE_CARDS)
    cursor.limit(2)
    cards = list(cursor)

    assert len(cards) == 2


@pytest.mark.unit
def test_cursor_sort_and_limit_chaining():
    """Test that sort and limit can be chained together."""
    cursor = MockMongoCursor(SAMPLE_CARDS)
    cursor.sort("cmc", -1).limit(2)
    cards = list(cursor)

    assert len(cards) == 2
    assert cards[0]["name"] == "Progenitus"
    assert cards[1]["name"] == "Counterspell"


@pytest.mark.unit
def test_find_one_exact_match():
    """Test find_one with exact field match."""
    collection = MockMongoCollection(SAMPLE_CARDS)
    result = collection.find_one({"name": "Lightning Bolt"})

    assert result is not None
    assert result["name"] == "Lightning Bolt"
    assert result["cmc"] == 1.0


@pytest.mark.unit
def test_find_one_returns_none():
    """Test find_one returns None when no match found."""
    collection = MockMongoCollection(SAMPLE_CARDS)
    result = collection.find_one({"name": "Nonexistent Card"})

    assert result is None


@pytest.mark.unit
def test_find_one_with_projection():
    """Test find_one with field projection."""
    collection = MockMongoCollection(SAMPLE_CARDS)
    result = collection.find_one(
        {"name": "Lightning Bolt"}, projection={"name": 1, "cmc": 1, "_id": 0}
    )

    assert result is not None
    assert "name" in result
    assert "cmc" in result
    assert "_id" not in result
    assert "colors" not in result


@pytest.mark.unit
def test_find_with_regex():
    """Test find with $regex operator."""
    collection = MockMongoCollection(SAMPLE_CARDS)
    cursor = collection.find({"name": {"$regex": "bolt"}})
    results = list(cursor)

    assert len(results) == 1
    assert results[0]["name"] == "Lightning Bolt"


@pytest.mark.unit
def test_find_with_in_operator():
    """Test find with $in operator."""
    collection = MockMongoCollection(SAMPLE_CARDS)
    cursor = collection.find({"rarity": {"$in": ["rare", "mythic"]}})
    results = list(cursor)

    assert len(results) == 2
    rarities = [r["rarity"] for r in results]
    assert "rare" in rarities
    assert "mythic" in rarities


@pytest.mark.unit
def test_find_with_all_operator():
    """Test find with $all operator."""
    collection = MockMongoCollection(SAMPLE_CARDS)
    cursor = collection.find({"colors": {"$all": ["W", "U"]}})
    results = list(cursor)

    assert len(results) == 1
    assert results[0]["name"] == "Progenitus"


@pytest.mark.unit
def test_find_with_gte_lte_operators():
    """Test find with $gte and $lte comparison operators."""
    collection = MockMongoCollection(SAMPLE_CARDS)
    cursor = collection.find({"cmc": {"$gte": 1.0, "$lte": 2.0}})
    results = list(cursor)

    assert len(results) == 2
    names = [r["name"] for r in results]
    assert "Lightning Bolt" in names
    assert "Counterspell" in names


@pytest.mark.unit
def test_aggregate_match_stage():
    """Test aggregate with $match stage."""
    collection = MockMongoCollection(SAMPLE_CARDS)
    pipeline = [{"$match": {"cmc": {"$gte": 2.0}}}]
    cursor = collection.aggregate(pipeline)
    results = list(cursor)

    assert len(results) == 2
    assert all(r["cmc"] >= 2.0 for r in results)


@pytest.mark.unit
def test_aggregate_project_stage():
    """Test aggregate with $project stage."""
    collection = MockMongoCollection(SAMPLE_CARDS)
    pipeline = [{"$project": {"name": 1, "cmc": 1, "_id": 0}}]
    cursor = collection.aggregate(pipeline)
    results = list(cursor)

    assert len(results) == 4
    assert all("name" in r for r in results)
    assert all("cmc" in r for r in results)
    assert all("colors" not in r for r in results)


@pytest.mark.unit
def test_aggregate_group_stage():
    """Test aggregate with $group stage."""
    collection = MockMongoCollection(SAMPLE_CARDS)
    pipeline = [
        {
            "$group": {
                "_id": "$set_name",
                "count": {"$sum": 1},
                "max_cmc": {"$max": "$cmc"},
            }
        }
    ]
    cursor = collection.aggregate(pipeline)
    results = list(cursor)

    assert len(results) == 2  # Alpha and Conflux
    alpha_group = next((r for r in results if r["_id"] == "Alpha"), None)
    assert alpha_group is not None
    assert alpha_group["count"] == 3
    assert alpha_group["max_cmc"] == 2.0


@pytest.mark.unit
def test_aggregate_sort_stage():
    """Test aggregate with $sort stage."""
    collection = MockMongoCollection(SAMPLE_CARDS)
    pipeline = [{"$sort": {"cmc": -1}}]
    cursor = collection.aggregate(pipeline)
    results = list(cursor)

    assert len(results) == 4
    assert results[0]["cmc"] == 10.0
    assert results[-1]["cmc"] == 0.0


@pytest.mark.unit
def test_aggregate_limit_stage():
    """Test aggregate with $limit stage."""
    collection = MockMongoCollection(SAMPLE_CARDS)
    pipeline = [{"$sort": {"cmc": -1}}, {"$limit": 2}]
    cursor = collection.aggregate(pipeline)
    results = list(cursor)

    assert len(results) == 2
    assert results[0]["name"] == "Progenitus"


@pytest.mark.unit
def test_aggregate_complex_pipeline():
    """Test aggregate with multiple stages combined."""
    collection = MockMongoCollection(SAMPLE_CARDS)
    pipeline = [
        {"$match": {"set_name": "Alpha"}},
        {"$project": {"name": 1, "cmc": 1, "_id": 0}},
        {"$sort": {"cmc": 1}},
        {"$limit": 2},
    ]
    cursor = collection.aggregate(pipeline)
    results = list(cursor)

    assert len(results) == 2
    assert results[0]["name"] == "Black Lotus"
    assert results[0]["cmc"] == 0.0
    assert results[1]["name"] == "Lightning Bolt"
    assert results[1]["cmc"] == 1.0
    assert "colors" not in results[0]


@pytest.mark.unit
def test_text_search():
    """Test find with $text and $search operators."""
    collection = MockMongoCollection(SAMPLE_CARDS)
    cursor = collection.find({"$text": {"$search": "bolt"}})
    results = list(cursor)

    assert len(results) == 1
    assert results[0]["name"] == "Lightning Bolt"


@pytest.mark.unit
def test_exists_operator():
    """Test find with $exists operator."""
    # Add a card without colors field for this test
    cards_with_missing = SAMPLE_CARDS + [{"id": "5", "name": "Test Card", "cmc": 1.0}]
    collection = MockMongoCollection(cards_with_missing)

    # Find cards where colors exists
    cursor = collection.find({"colors": {"$exists": True}})
    results = list(cursor)
    assert len(results) == 4

    # Find cards where colors doesn't exist
    cursor = collection.find({"colors": {"$exists": False}})
    results = list(cursor)
    assert len(results) == 1
    assert results[0]["name"] == "Test Card"


@pytest.mark.unit
def test_or_operator():
    """Test find with $or operator."""
    collection = MockMongoCollection(SAMPLE_CARDS)
    cursor = collection.find({"$or": [{"cmc": 0.0}, {"rarity": "mythic"}]})
    results = list(cursor)

    assert len(results) == 2
    names = [r["name"] for r in results]
    assert "Black Lotus" in names
    assert "Progenitus" in names


@pytest.mark.unit
def test_and_operator():
    """Test find with $and operator."""
    collection = MockMongoCollection(SAMPLE_CARDS)
    cursor = collection.find({"$and": [{"cmc": {"$gte": 1.0}}, {"cmc": {"$lte": 2.0}}]})
    results = list(cursor)

    assert len(results) == 2
    assert all(1.0 <= r["cmc"] <= 2.0 for r in results)
