"""ConnectorClient — typed HTTP client for robot connector APIs.

Works with sim-connector, spot-nova, unitree-nova, pidog-nova.
"""

from __future__ import annotations

from typing import Any

import httpx

from .models.graphnav import Graph, Waypoint
from .models.registry import RegistryCamera, RegistryRobot

# In-cluster default (sim-connector)
DEFAULT_CONNECTOR_URL = "http://app-sim-connector:8080/cell/sim-connector"


class RobotScope:
    """Robot-scoped API operations.

    Created via ConnectorClient.robot(model, id).
    """

    def __init__(self, client: httpx.Client, model: str, robot_id: str):
        self._client = client
        self.model = model
        self.id = robot_id
        self._prefix = f"/api/{model}/{robot_id}"

    # --- Info ---

    def health(self) -> dict[str, Any]:
        """Get robot health status."""
        resp = self._client.get(f"{self._prefix}/health")
        resp.raise_for_status()
        return resp.json()

    # --- Camera ---

    def list_cameras(self) -> list[RegistryCamera]:
        """List camera feeds for this robot."""
        resp = self._client.get(f"/api/camera/{self.id}/sources")
        resp.raise_for_status()
        data = resp.json()
        sources = data if isinstance(data, list) else data.get("sources", [])
        return [
            RegistryCamera(
                robot_id=self.id, robot_type=self.model, feed=s.get("feed", s), source="connector"
            )
            if isinstance(s, dict)
            else RegistryCamera(robot_id=self.id, robot_type=self.model, feed=s, source="connector")
            for s in sources
        ]

    def camera_snapshot_url(self, feed: str, quality: int = 80) -> str:
        """Get JPEG snapshot URL for a camera feed."""
        base = str(self._client._base_url).rstrip("/")
        return f"{base}/api/camera/{self.id}/{feed}/snapshot?quality={quality}"

    def camera_stream_url(self, feed: str, quality: int = 50, fps: int = 5) -> str:
        """Get MJPEG stream URL for a camera feed."""
        base = str(self._client._base_url).rstrip("/")
        return f"{base}/api/camera/{self.id}/{feed}/video_feed?quality={quality}&fps={fps}"

    # --- Actions & Modes ---

    def list_actions(self) -> list[str]:
        """List available actions (e.g. undock, dock, sit, stand)."""
        resp = self._client.get(f"{self._prefix}/action/list")
        resp.raise_for_status()
        data = resp.json()
        return data if isinstance(data, list) else data.get("actions", [])

    def execute_action(self, action_name: str) -> dict[str, Any]:
        """Execute a named action."""
        resp = self._client.post(f"{self._prefix}/action/{action_name}")
        resp.raise_for_status()
        return resp.json()

    def list_modes(self) -> list[str]:
        """List available robot modes."""
        resp = self._client.get(f"{self._prefix}/mode/list")
        resp.raise_for_status()
        data = resp.json()
        return data if isinstance(data, list) else data.get("modes", [])

    def set_mode(self, mode: str) -> dict[str, Any]:
        """Set robot mode."""
        resp = self._client.post(f"{self._prefix}/mode", json={"mode": mode})
        resp.raise_for_status()
        return resp.json()

    # --- Control ---

    def stop(self) -> None:
        """Emergency stop."""
        resp = self._client.post(f"{self._prefix}/stop")
        resp.raise_for_status()

    def power_on(self) -> dict[str, Any]:
        """Power on the robot."""
        resp = self._client.post(f"{self._prefix}/power/on")
        resp.raise_for_status()
        return resp.json()

    def power_off(self) -> dict[str, Any]:
        """Power off the robot."""
        resp = self._client.post(f"{self._prefix}/power/off")
        resp.raise_for_status()
        return resp.json()

    # --- Lease (Spot) ---

    def acquire_lease(self) -> dict[str, Any]:
        """Acquire control lease."""
        resp = self._client.post(f"{self._prefix}/lease/acquire")
        resp.raise_for_status()
        return resp.json()

    def release_lease(self) -> dict[str, Any]:
        """Release control lease."""
        resp = self._client.post(f"{self._prefix}/lease/release")
        resp.raise_for_status()
        return resp.json()

    # --- GraphNav ---

    def list_graphs(self) -> list[Graph]:
        """List available GraphNav graphs."""
        resp = self._client.get(f"{self._prefix}/graphnav/graphs")
        resp.raise_for_status()
        data = resp.json()
        items = data if isinstance(data, list) else data.get("graphs", [])
        return [Graph(**g) if isinstance(g, dict) else Graph(id=g) for g in items]

    def get_graph_waypoints(self, graph_id: str) -> list[Waypoint]:
        """Get waypoints for a graph."""
        resp = self._client.get(f"{self._prefix}/graphnav/graphs/{graph_id}/waypoints")
        resp.raise_for_status()
        data = resp.json()
        items = data if isinstance(data, list) else data.get("waypoints", [])
        return [Waypoint(**wp) for wp in items]

    def find_waypoint(self, name: str, graph_id: str | None = None) -> Waypoint | None:
        """Find a waypoint by name (case-insensitive substring match).

        If graph_id is None, searches all graphs.
        """
        graphs = [Graph(id=graph_id)] if graph_id else self.list_graphs()
        for graph in graphs:
            waypoints = self.get_graph_waypoints(graph.id)
            for wp in waypoints:
                if name.lower() in wp.name.lower():
                    return wp
        return None

    def activate_graph(self, graph_id: str) -> dict[str, Any]:
        """Activate a GraphNav graph for navigation."""
        resp = self._client.post(f"{self._prefix}/graphnav/graphs/{graph_id}/activate")
        resp.raise_for_status()
        return resp.json()

    def navigate_to_waypoint(self, graph_id: str, waypoint_id: str) -> dict[str, Any]:
        """Navigate to a waypoint."""
        resp = self._client.post(
            f"{self._prefix}/graphnav/graphs/{graph_id}/navigate",
            json={"waypoint_id": waypoint_id},
        )
        resp.raise_for_status()
        return resp.json()


class ConnectorClient:
    """HTTP client for robot connector APIs.

    Args:
        base_url: Base URL of the connector service.
            Defaults to in-cluster sim-connector URL.
        timeout: HTTP request timeout in seconds.
    """

    def __init__(
        self,
        base_url: str = DEFAULT_CONNECTOR_URL,
        timeout: float = 30.0,
    ):
        self.base_url = base_url.rstrip("/")
        self._client = httpx.Client(base_url=self.base_url, timeout=timeout)

    def health(self) -> dict[str, Any]:
        """Get connector health."""
        resp = self._client.get("/health")
        resp.raise_for_status()
        return resp.json()

    def list_robots(self) -> list[RegistryRobot]:
        """List all connected robots."""
        resp = self._client.get("/api/robots")
        resp.raise_for_status()
        data = resp.json()
        items = data if isinstance(data, list) else data.get("robots", [])
        return [RegistryRobot(**r) for r in items]

    def list_cameras(self) -> list[RegistryCamera]:
        """List all camera feeds across all robots."""
        resp = self._client.get("/api/cameras")
        resp.raise_for_status()
        data = resp.json()
        items = data if isinstance(data, list) else data.get("cameras", [])
        return [RegistryCamera(**c) for c in items]

    def list_capabilities(self) -> list[str]:
        """List connector capabilities."""
        resp = self._client.get("/api/capabilities")
        resp.raise_for_status()
        data = resp.json()
        return data if isinstance(data, list) else data.get("capabilities", [])

    def robot(self, model: str, robot_id: str) -> RobotScope:
        """Get a robot-scoped client for a specific robot.

        Args:
            model: Robot model (e.g. "spot", "g1", "go2").
            robot_id: Robot ID (e.g. "greyhound").

        Returns:
            RobotScope with robot-specific API methods.
        """
        return RobotScope(self._client, model, robot_id)

    def find_robot(self, robot_id: str) -> RobotScope | None:
        """Find a robot by ID and return a scoped client.

        Searches the robot list to determine the model automatically.
        """
        robots = self.list_robots()
        for r in robots:
            if r.id == robot_id:
                model = r.robot_model or "unknown"
                return RobotScope(self._client, model, robot_id)
        return None

    def close(self) -> None:
        self._client.close()

    def __enter__(self) -> ConnectorClient:
        return self

    def __exit__(self, *args: Any) -> None:
        self.close()
