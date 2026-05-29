"""AssetsClient — typed HTTP client for the nova-assets service."""

from __future__ import annotations

from typing import Any

import httpx

from .models.graphnav import Waypoint

# In-cluster default
DEFAULT_ASSETS_URL = "http://app-nova-assets:8080/cell/nova-assets"


class AssetsClient:
    """HTTP client for the nova-assets spatial asset management service.

    Args:
        base_url: Base URL of the nova-assets service.
        timeout: HTTP request timeout in seconds.
    """

    def __init__(
        self,
        base_url: str = DEFAULT_ASSETS_URL,
        timeout: float = 30.0,
    ):
        self.base_url = base_url.rstrip("/")
        self._client = httpx.Client(base_url=self.base_url, timeout=timeout)

    # --- Assets CRUD ---

    def list_assets(
        self, kind: str | None = None, robot_model: str | None = None
    ) -> list[dict[str, Any]]:
        """List assets, optionally filtered by kind or robot_model.

        Args:
            kind: Filter by asset kind (model3d, map2d, graphnav).
            robot_model: Filter by robot model.
        """
        params: dict[str, str] = {}
        if kind:
            params["kind"] = kind
        if robot_model:
            params["robot_model"] = robot_model
        resp = self._client.get("/api/assets", params=params)
        resp.raise_for_status()
        return resp.json()

    def get_asset(self, asset_id: str) -> dict[str, Any]:
        """Get asset metadata by ID."""
        resp = self._client.get(f"/api/assets/{asset_id}")
        resp.raise_for_status()
        return resp.json()

    def create_graphnav_asset(self, name: str) -> dict[str, Any]:
        """Create a new GraphNav asset (no file upload needed)."""
        resp = self._client.post("/api/assets", json={"name": name, "kind": "graphnav"})
        resp.raise_for_status()
        return resp.json()

    def delete_asset(self, asset_id: str) -> None:
        """Delete an asset."""
        resp = self._client.delete(f"/api/assets/{asset_id}")
        resp.raise_for_status()

    # --- GraphNav ---

    def list_graphnav_assets(self, robot_model: str | None = None) -> list[dict[str, Any]]:
        """List all GraphNav assets."""
        return self.list_assets(kind="graphnav", robot_model=robot_model)

    def get_graphnav(self, asset_id: str) -> dict[str, Any]:
        """Get GraphNav metadata for an asset."""
        resp = self._client.get(f"/api/assets/{asset_id}/graphnav")
        resp.raise_for_status()
        return resp.json()

    def get_waypoints(self, asset_id: str) -> list[Waypoint]:
        """Get waypoints from a GraphNav asset's metadata.

        Parses the graphnav metadata to extract waypoint information.
        """
        data = self.get_graphnav(asset_id)
        waypoints_data = data.get("waypoints", [])
        return [Waypoint(**wp) for wp in waypoints_data]

    def find_graphnav_asset(
        self, name: str, robot_model: str | None = None
    ) -> dict[str, Any] | None:
        """Find a GraphNav asset by name (case-insensitive substring match).

        Args:
            name: Name to search for.
            robot_model: Optional robot model filter.

        Returns:
            Asset dict or None if not found.
        """
        assets = self.list_graphnav_assets(robot_model=robot_model)
        for asset in assets:
            asset_name = asset.get("name", "")
            if name.lower() in asset_name.lower():
                return asset
        return None

    def find_waypoint(
        self, waypoint_name: str, asset_id: str | None = None, asset_name: str | None = None
    ) -> Waypoint | None:
        """Find a waypoint by name across GraphNav assets.

        Args:
            waypoint_name: Waypoint name to search (case-insensitive substring).
            asset_id: Specific asset to search in.
            asset_name: Asset name to find first, then search waypoints in it.

        Returns:
            Waypoint or None.
        """
        if asset_id:
            waypoints = self.get_waypoints(asset_id)
            for wp in waypoints:
                if waypoint_name.lower() in wp.name.lower():
                    return wp
            return None

        if asset_name:
            asset = self.find_graphnav_asset(asset_name)
            if asset:
                return self.find_waypoint(waypoint_name, asset_id=asset["id"])
            return None

        # Search all graphnav assets
        assets = self.list_graphnav_assets()
        for asset in assets:
            wp = self.find_waypoint(waypoint_name, asset_id=asset["id"])
            if wp:
                return wp
        return None

    # --- Semantic Markers ---

    def get_markers(self, asset_id: str) -> list[dict[str, Any]]:
        """Get semantic markers for an asset."""
        resp = self._client.get(f"/api/assets/{asset_id}/markers")
        resp.raise_for_status()
        return resp.json()

    # --- Lifecycle ---

    def close(self) -> None:
        self._client.close()

    def __enter__(self) -> AssetsClient:
        return self

    def __exit__(self, *args: Any) -> None:
        self.close()
