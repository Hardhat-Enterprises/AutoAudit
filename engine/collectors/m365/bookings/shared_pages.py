"""Bookings shared pages collector.

CIS Microsoft 365 Foundations Benchmark Control:
    v6.0.0: 1.3.9 (restrict shared bookings pages)

Connection Method: Microsoft Graph Bookings API
Required Scopes: Bookings.Read.All (app), Bookings.Manage.All if write needed
Graph Endpoint: /solutions/bookingBusinesses
"""

from typing import Any

from collectors.base import BaseDataCollector
from collectors.graph_client import GraphClient


class BookingsSharedPagesDataCollector(BaseDataCollector):
    """Collects Bookings businesses and publication status for shared pages."""

    async def collect(self, client: GraphClient) -> dict[str, Any]:
        """Collect Bookings businesses and basic sharing metadata.

        Returns:
            Dict containing:
            - businesses: list of business objects with publication metadata
            - total: count of businesses
        """
        businesses = await client.get_all_pages("/solutions/bookingBusinesses", beta=True)

        items: list[dict[str, Any]] = []
        for biz in businesses:
            items.append(
                {
                    "id": biz.get("id"),
                    "displayName": biz.get("displayName"),
                    "isPublished": biz.get("isPublished"),
                    "publicUrl": biz.get("publicUrl"),
                    # These fields indicate whether anonymous/self-service booking is allowed
                    "allowStaffSelection": (biz.get("schedulingPolicy") or {}).get(
                        "allowStaffSelection"
                    ),
                    "isAnonymousJoinEnabled": (biz.get("schedulingPolicy") or {}).get(
                        "isAnonymousJoinEnabled"
                    ),
                }
            )

        return {
            "businesses": items,
            "total": len(items),
        }
