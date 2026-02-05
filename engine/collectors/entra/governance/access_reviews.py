"""Access reviews collector.

CIS Microsoft 365 Foundations Benchmark Controls:
    v6.0.0: 5.3.2

Connection Method: Microsoft Graph API
Required Scopes: AccessReview.Read.All
Graph Endpoint: /identityGovernance/accessReviews/definitions
"""

from typing import Any

from collectors.base import BaseDataCollector
from collectors.graph_client import GraphClient


class AccessReviewsDataCollector(BaseDataCollector):
    """Collects access review definitions for CIS compliance evaluation.

    This collector retrieves access review configurations to verify
    guest user access reviews are properly configured.
    """

    async def collect(self, client: GraphClient) -> dict[str, Any]:
        """Collect access reviews data.

        Returns:
            Dict containing:
            - access_review_definitions: List of access review definitions
            - total_reviews: Number of access review definitions
            - guest_reviews: Access reviews for guest users
            - guest_reviews_count: Number of guest user reviews
        """
        # Get access review definitions
        definitions = await client.get_all_pages(
            "/identityGovernance/accessReviews/definitions",
            beta=True,
        )

        # Filter for guest user reviews
        guest_reviews = []
        for definition in definitions:
            scope = definition.get("scope", {})
            # Check if review targets guest users
            query = scope.get("query", "")
            if "guest" in query.lower() or "userType eq 'Guest'" in query:
                guest_reviews.append(definition)

        return {
            "access_review_definitions": definitions,
            "total_reviews": len(definitions),
            "guest_reviews": guest_reviews,
            "guest_reviews_count": len(guest_reviews),
            "has_guest_reviews": len(guest_reviews) > 0,
        }
