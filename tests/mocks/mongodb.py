"""Custom MongoDB mock classes for testing.

This module provides in-memory mock implementations of MongoDB cursor and
collection classes, enabling fast integration tests without external dependencies.

Supports MongoDB query operators: $regex, $in, $nin, $all, $size, $gte, $lte, $text, $search, $or, $and, $exists, $eq
Supports aggregation stages: $match, $project, $group, $sort, $limit
"""

import re
from copy import deepcopy
from typing import Any, Optional


class MockMongoCursor:
    """Mock MongoDB cursor supporting sort, limit, and iteration."""

    def __init__(self, documents: list[dict]):
        """Initialize cursor with documents.

        Args:
            documents: List of document dictionaries.
        """
        self._documents = deepcopy(documents)
        self._position = 0

    def sort(self, field: str, direction: int) -> "MockMongoCursor":
        """Sort documents by field.

        Args:
            field: Field name to sort by.
            direction: 1 for ascending, -1 for descending.

        Returns:
            Self for method chaining.
        """
        reverse = direction == -1
        self._documents.sort(key=lambda doc: doc.get(field, ""), reverse=reverse)
        return self

    def limit(self, count: int) -> "MockMongoCursor":
        """Limit number of documents.

        Args:
            count: Maximum number of documents to return.

        Returns:
            Self for method chaining.
        """
        self._documents = self._documents[:count]
        return self

    def __iter__(self):
        """Make cursor iterable."""
        self._position = 0
        return self

    def __next__(self):
        """Get next document in iteration."""
        if self._position >= len(self._documents):
            raise StopIteration
        document = self._documents[self._position]
        self._position += 1
        return document


class MockMongoCollection:
    """Mock MongoDB collection supporting find, find_one, and aggregate."""

    def __init__(self, documents: list[dict]):
        """Initialize collection with documents.

        Args:
            documents: List of document dictionaries.
        """
        self._documents = deepcopy(documents)
        self._last_search_text = None  # Track last text search for scoring

    def find_one(
        self, query: dict, projection: Optional[dict] = None
    ) -> Optional[dict]:
        """Find single document matching query.

        Args:
            query: MongoDB query dictionary.
            projection: Fields to include/exclude.

        Returns:
            Matching document or None.
        """
        for doc in self._documents:
            if self._matches_query(doc, query):
                if projection:
                    return self._apply_projection(doc, projection)
                return deepcopy(doc)
        return None

    def find(self, query: dict, projection: Optional[dict] = None) -> MockMongoCursor:
        """Find all documents matching query.

        Args:
            query: MongoDB query dictionary.
            projection: Fields to include/exclude.

        Returns:
            MockMongoCursor with matching documents.
        """
        matching_docs = []
        for doc in self._documents:
            if self._matches_query(doc, query):
                if projection:
                    matching_docs.append(self._apply_projection(doc, projection))
                else:
                    matching_docs.append(deepcopy(doc))
        return MockMongoCursor(matching_docs)

    def aggregate(self, pipeline: list[dict]) -> MockMongoCursor:
        """Execute aggregation pipeline.

        Args:
            pipeline: List of aggregation stage dictionaries.

        Returns:
            MockMongoCursor with aggregation results.
        """
        documents = deepcopy(self._documents)

        for stage in pipeline:
            documents = self._execute_aggregation_stage(documents, stage)

        return MockMongoCursor(documents)

    def _matches_query(self, doc: dict, query: dict) -> bool:
        """Check if document matches query.

        Args:
            doc: Document to check.
            query: Query dictionary.

        Returns:
            True if document matches query.
        """
        if not query:
            return True

        for field, condition in query.items():
            # Handle special operators
            if field == "$or":
                if not any(
                    self._matches_query(doc, sub_query) for sub_query in condition
                ):
                    return False
            elif field == "$and":
                if not all(
                    self._matches_query(doc, sub_query) for sub_query in condition
                ):
                    return False
            elif field == "$text":
                # Text search - simple implementation
                search_text = condition.get("$search", "").lower()
                self._last_search_text = search_text  # Save for scoring
                doc_text = str(doc).lower()
                if search_text not in doc_text:
                    return False
            elif isinstance(condition, dict):
                # Field with operators
                field_value = doc.get(field)

                for operator, value in condition.items():
                    if operator == "$regex":
                        if field_value is None:
                            return False
                        if not re.search(value, str(field_value), re.IGNORECASE):
                            return False
                    elif operator == "$in":
                        # Handle list fields (e.g., colors): check if ANY element matches
                        if isinstance(field_value, list):
                            if not any(item in value for item in field_value):
                                return False
                        # Handle scalar fields: check if value itself is in list
                        else:
                            if field_value not in value:
                                return False
                    elif operator == "$nin":
                        if field_value in value:
                            return False
                    elif operator == "$all":
                        if not isinstance(field_value, list):
                            return False
                        if not all(item in field_value for item in value):
                            return False
                    elif operator == "$size":
                        if not isinstance(field_value, list):
                            return False
                        if len(field_value) != value:
                            return False
                    elif operator == "$gt":
                        if field_value is None or field_value <= value:
                            return False
                    elif operator == "$gte":
                        if field_value is None or field_value < value:
                            return False
                    elif operator == "$lt":
                        if field_value is None or field_value >= value:
                            return False
                    elif operator == "$lte":
                        if field_value is None or field_value > value:
                            return False
                    elif operator == "$exists":
                        exists = field in doc
                        if exists != value:
                            return False
                    elif operator == "$eq":
                        if field_value != value:
                            return False
            else:
                # Direct field match
                if doc.get(field) != condition:
                    return False

        return True

    def _apply_projection(self, doc: dict, projection: dict) -> dict:
        """Apply projection to document.

        Args:
            doc: Document to project.
            projection: Projection dictionary.

        Returns:
            Projected document.
        """
        result = {}

        # Check if it's inclusion or exclusion projection
        is_inclusion = any(v == 1 for k, v in projection.items() if k != "_id")

        for field, include in projection.items():
            if include == 1:
                if field in doc:
                    result[field] = deepcopy(doc[field])
            elif include == 0 and not is_inclusion:
                # Exclusion mode
                result = {k: deepcopy(v) for k, v in doc.items() if k != field}

        # If inclusion mode, add all included fields
        if is_inclusion:
            for field in projection:
                if projection[field] == 1 and field in doc:
                    result[field] = deepcopy(doc[field])

        # Handle _id special case (included by default unless explicitly excluded)
        if "_id" not in projection or projection.get("_id") != 0:
            if "_id" in doc and "_id" not in result:
                result["_id"] = deepcopy(doc["_id"])

        return result

    def _execute_aggregation_stage(
        self, documents: list[dict], stage: dict
    ) -> list[dict]:
        """Execute single aggregation stage.

        Args:
            documents: Current documents.
            stage: Aggregation stage dictionary.

        Returns:
            Documents after applying stage.
        """
        stage_type = list(stage.keys())[0]
        stage_spec = stage[stage_type]

        if stage_type == "$match":
            # Filter documents
            return [doc for doc in documents if self._matches_query(doc, stage_spec)]

        elif stage_type == "$project":
            # Project fields with optional score calculation
            projected = []
            for doc in documents:
                projected_doc = self._apply_projection(doc, stage_spec)

                # Add text search score if requested
                if stage_spec.get("score") == 1 and self._last_search_text:
                    projected_doc["score"] = self._calculate_text_score(
                        doc, self._last_search_text
                    )

                projected.append(projected_doc)
            return projected

        elif stage_type == "$group":
            # Group documents
            return self._execute_group_stage(documents, stage_spec)

        elif stage_type == "$sort":
            # Sort documents (supports multiple sort fields)
            sort_fields = list(stage_spec.items())

            def sort_key(doc):
                # Return tuple of values for multi-field sort
                return tuple(doc.get(field, "") for field, _ in sort_fields)

            # Sort in reverse if first field is descending
            # Multi-field sort with mixed directions needs custom comparison
            if len(sort_fields) == 1:
                field, direction = sort_fields[0]
                return sorted(
                    documents,
                    key=lambda doc: doc.get(field, ""),
                    reverse=(direction == -1),
                )
            else:
                # Multi-field sort: use tuple comparison
                def multi_sort_key(doc):
                    values = []
                    for field, direction in sort_fields:
                        val = doc.get(field, "")
                        # Negate numeric values for descending sort
                        if direction == -1 and isinstance(val, (int, float)):
                            val = -val
                        elif direction == -1:
                            # For strings, can't negate, so we'll handle in reverse
                            pass
                        values.append((direction, val))
                    return values

                # Custom comparator for mixed direction sorts
                from functools import cmp_to_key

                def compare(a, b):
                    a_vals = multi_sort_key(a)
                    b_vals = multi_sort_key(b)
                    for (dir_a, val_a), (dir_b, val_b) in zip(a_vals, b_vals):
                        if val_a < val_b:
                            result = -1
                        elif val_a > val_b:
                            result = 1
                        else:
                            continue
                        return result * dir_a  # Apply direction
                    return 0

                return sorted(documents, key=cmp_to_key(compare))

        elif stage_type == "$limit":
            # Limit documents
            return documents[:stage_spec]

        else:
            # Unsupported stage - return as is
            return documents

    def _execute_group_stage(
        self, documents: list[dict], group_spec: dict
    ) -> list[dict]:
        """Execute $group aggregation stage.

        Args:
            documents: Documents to group.
            group_spec: Group specification.

        Returns:
            Grouped documents.
        """
        # Simple grouping implementation
        groups: dict[Any, dict] = {}
        group_id = group_spec.get("_id")

        for doc in documents:
            # Determine group key
            if isinstance(group_id, str) and group_id.startswith("$"):
                key = doc.get(group_id[1:])
            else:
                key = group_id

            if key not in groups:
                groups[key] = {"_id": key}

            # Apply accumulators
            for field, accumulator in group_spec.items():
                if field == "_id":
                    continue

                if isinstance(accumulator, dict):
                    acc_type = list(accumulator.keys())[0]
                    acc_value = accumulator[acc_type]

                    if acc_type == "$first":
                        if field not in groups[key]:
                            field_name = (
                                acc_value[1:]
                                if acc_value.startswith("$")
                                else acc_value
                            )
                            groups[key][field] = doc.get(field_name)

                    elif acc_type == "$sum":
                        if field not in groups[key]:
                            groups[key][field] = 0
                        if acc_value == 1:
                            groups[key][field] += 1
                        else:
                            field_name = (
                                acc_value[1:]
                                if acc_value.startswith("$")
                                else acc_value
                            )
                            groups[key][field] += doc.get(field_name, 0)

                    elif acc_type == "$max":
                        field_name = (
                            acc_value[1:] if acc_value.startswith("$") else acc_value
                        )
                        current_value = doc.get(field_name)
                        if current_value is not None:
                            if (
                                field not in groups[key]
                                or current_value > groups[key][field]
                            ):
                                groups[key][field] = current_value

                    elif acc_type == "$addToSet":
                        if field not in groups[key]:
                            groups[key][field] = []
                        if acc_value == "$$ROOT":
                            if doc not in groups[key][field]:
                                groups[key][field].append(deepcopy(doc))
                        else:
                            field_name = (
                                acc_value[1:]
                                if acc_value.startswith("$")
                                else acc_value
                            )
                            value = doc.get(field_name)
                            if value not in groups[key][field]:
                                groups[key][field].append(value)

        return list(groups.values())

    def _calculate_text_score(self, doc: dict, search_text: str) -> float:
        """Calculate mock text search score for pagination testing.

        Simulates MongoDB $text search score based on text relevance.
        Higher scores indicate better matches. Uses deterministic scoring
        for reproducible tests.

        Args:
            doc: Document to score
            search_text: Search query text

        Returns:
            Score between 0.0 and 1.0
        """
        if not search_text:
            return 0.5  # Default score

        name = doc.get("name", "").lower()
        oracle_text = doc.get("oracle_text", "").lower()
        search = search_text.lower()

        # Scoring rules (deterministic for testing):
        if search == name:
            return 1.0  # Perfect match
        elif name.startswith(search):
            return 0.9  # Prefix match
        elif search in name:
            return 0.8  # Substring match in name
        elif search in oracle_text:
            return 0.6  # Match in card text
        else:
            return 0.3  # Weak/generic match
