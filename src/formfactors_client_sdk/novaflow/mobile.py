"""Pre-built NovaFlow Action nodes for MobileRobotService.

These inherit from novaflow_client_sdk.Action and pre-fill service/operation/data
so you don't need to use raw strings.

Requires: pip install formfactors-client-sdk[novaflow]
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from novaflow_client_sdk import Action, value

if TYPE_CHECKING:
    from formfactors_client_sdk.connector import ConnectorClient

SERVICE = "MobileRobotService"


def _robot_params(robot_model: str | None, robot_id: str | None) -> dict[str, Any]:
    """Build common robot params dict."""
    params: dict[str, Any] = {}
    if robot_model:
        params["robot_model"] = value(robot_model)
    if robot_id:
        params["robot_id"] = value(robot_id)
    return params


class Walk(Action):
    """Walk forward/backward at a given speed for a duration.

    Args:
        speed_mps: Speed in m/s (-3 to 3, default 1.0).
        duration_s: Duration in seconds (0 to 120, default 3.0).
        robot_model: Robot model (optional if using MobileRobot builder).
        robot_id: Robot ID (optional if using MobileRobot builder).
    """

    def __init__(
        self,
        speed_mps: float = 1.0,
        duration_s: float = 3.0,
        robot_model: str | None = None,
        robot_id: str | None = None,
        **kwargs: Any,
    ):
        data = {
            **_robot_params(robot_model, robot_id),
            "speed_mps": value(speed_mps),
            "duration_s": value(duration_s),
        }
        super().__init__(service=SERVICE, operation="Walk", data=data, **kwargs)


class Strafe(Action):
    """Strafe laterally at a given speed for a duration.

    Args:
        speed_mps: Lateral speed in m/s (-3 to 3, default 1.0).
        duration_s: Duration in seconds (0 to 120, default 3.0).
    """

    def __init__(
        self,
        speed_mps: float = 1.0,
        duration_s: float = 3.0,
        robot_model: str | None = None,
        robot_id: str | None = None,
        **kwargs: Any,
    ):
        data = {
            **_robot_params(robot_model, robot_id),
            "speed_mps": value(speed_mps),
            "duration_s": value(duration_s),
        }
        super().__init__(service=SERVICE, operation="Strafe", data=data, **kwargs)


class Turn(Action):
    """Turn in place at a given angular speed for a duration.

    Args:
        angular_speed_rad_s: Angular speed in rad/s (-6 to 6, default 1.0).
        duration_s: Duration in seconds (0 to 120, default 3.0).
    """

    def __init__(
        self,
        angular_speed_rad_s: float = 1.0,
        duration_s: float = 3.0,
        robot_model: str | None = None,
        robot_id: str | None = None,
        **kwargs: Any,
    ):
        data = {
            **_robot_params(robot_model, robot_id),
            "angular_speed_rad_s": value(angular_speed_rad_s),
            "duration_s": value(duration_s),
        }
        super().__init__(service=SERVICE, operation="Turn", data=data, **kwargs)


class WalkToWaypoint(Action):
    """Navigate to a GraphNav waypoint.

    Args:
        graphnav_asset_id: Asset ID of the GraphNav graph.
        waypoint_id: Target waypoint ID.
        speed_mps: Walking speed (0 to 3, default 1.0).
        goal_yaw_rad: Target yaw at waypoint (default 0).
    """

    def __init__(
        self,
        graphnav_asset_id: str,
        waypoint_id: str,
        speed_mps: float = 1.0,
        goal_yaw_rad: float = 0.0,
        robot_model: str | None = None,
        robot_id: str | None = None,
        **kwargs: Any,
    ):
        data = {
            **_robot_params(robot_model, robot_id),
            "graphnav_asset_id": value(graphnav_asset_id),
            "waypoint_id": value(waypoint_id),
            "speed_mps": value(speed_mps),
            "goal_yaw_rad": value(goal_yaw_rad),
            "map_asset_id": value(None),
        }
        super().__init__(service=SERVICE, operation="WalkToWaypoint", data=data, **kwargs)


class EStop(Action):
    """Emergency stop the robot."""

    def __init__(
        self,
        robot_model: str | None = None,
        robot_id: str | None = None,
        **kwargs: Any,
    ):
        data = _robot_params(robot_model, robot_id)
        super().__init__(service=SERVICE, operation="EStop", data=data, **kwargs)


class Stop(Action):
    """Graceful stop the robot."""

    def __init__(
        self,
        robot_model: str | None = None,
        robot_id: str | None = None,
        **kwargs: Any,
    ):
        data = _robot_params(robot_model, robot_id)
        super().__init__(service=SERVICE, operation="Stop", data=data, **kwargs)


class ExecuteStandardAction(Action):
    """Execute a named standard action (undock, dock, sit, stand, etc.).

    Args:
        action_name: The action to execute.
    """

    def __init__(
        self,
        action_name: str,
        robot_model: str | None = None,
        robot_id: str | None = None,
        **kwargs: Any,
    ):
        data = {
            **_robot_params(robot_model, robot_id),
            "action_name": value(action_name),
        }
        super().__init__(service=SERVICE, operation="ExecuteStandardAction", data=data, **kwargs)


class Undock(ExecuteStandardAction):
    """Undock the robot."""

    def __init__(self, robot_model: str | None = None, robot_id: str | None = None, **kwargs: Any):
        super().__init__(action_name="undock", robot_model=robot_model, robot_id=robot_id, **kwargs)


class Dock(ExecuteStandardAction):
    """Dock the robot."""

    def __init__(self, robot_model: str | None = None, robot_id: str | None = None, **kwargs: Any):
        super().__init__(action_name="dock", robot_model=robot_model, robot_id=robot_id, **kwargs)


class SetRobotMode(Action):
    """Set the robot's operating mode.

    Args:
        mode_name: Mode to set (e.g. "walk", "crawl").
    """

    def __init__(
        self,
        mode_name: str,
        robot_model: str | None = None,
        robot_id: str | None = None,
        **kwargs: Any,
    ):
        data = {
            **_robot_params(robot_model, robot_id),
            "mode_name": value(mode_name),
        }
        super().__init__(service=SERVICE, operation="SetRobotMode", data=data, **kwargs)


# ---------------------------------------------------------------------------
# MobileRobot builder — pre-fills robot_model, robot_id, graphnav_asset_id
# ---------------------------------------------------------------------------


class MobileRobot:
    """Builder for mobile robot action nodes with pre-filled robot context.

    Pre-fills robot_model, robot_id, and graphnav_asset_id into every action
    so you don't need to repeat them.

    Args:
        model: Robot model (e.g. "spot", "g1").
        robot_id: Robot ID (e.g. "greyhound").
        graphnav_asset_id: Default GraphNav asset ID for navigation actions.

    Example:
        spot = MobileRobot(model="spot", id="greyhound", graphnav_asset_id="a94...")
        flow.tree(Sequence(children=[
            spot.undock(),
            spot.walk_to_waypoint("kitchen-wp-id"),
            spot.dock(),
        ]))
    """

    def __init__(
        self,
        model: str,
        id: str,
        graphnav_asset_id: str | None = None,
    ):
        self.model = model
        self.id = id
        self.graphnav_asset_id = graphnav_asset_id

    @classmethod
    def from_registry(
        cls,
        connector: "ConnectorClient",
        robot_id: str,
        graphnav_asset_id: str | None = None,
    ) -> "MobileRobot":
        """Create a MobileRobot by discovering the robot from the connector.

        Auto-fills model from the registry. Optionally discovers the first
        available GraphNav graph if graphnav_asset_id is not provided.

        Args:
            connector: A ConnectorClient instance.
            robot_id: Robot ID to look up.
            graphnav_asset_id: Override GraphNav asset. If None, uses first graph found.
        """
        robots = connector.list_robots()
        robot = next((r for r in robots if r.id == robot_id), None)
        if robot is None:
            raise ValueError(f"Robot '{robot_id}' not found in connector registry")

        model = robot.robot_model or "unknown"

        if graphnav_asset_id is None:
            # Try to discover from the connector's graphnav endpoint
            scope = connector.robot(model, robot_id)
            graphs = scope.list_graphs()
            if graphs:
                graphnav_asset_id = graphs[0].id

        return cls(model=model, id=robot_id, graphnav_asset_id=graphnav_asset_id)

    def _rp(self) -> dict[str, str | None]:
        return {"robot_model": self.model, "robot_id": self.id}

    def walk(self, speed_mps: float = 1.0, duration_s: float = 3.0, **kwargs: Any) -> Walk:
        """Create a Walk action node."""
        return Walk(speed_mps=speed_mps, duration_s=duration_s, **self._rp(), **kwargs)

    def strafe(self, speed_mps: float = 1.0, duration_s: float = 3.0, **kwargs: Any) -> Strafe:
        """Create a Strafe action node."""
        return Strafe(speed_mps=speed_mps, duration_s=duration_s, **self._rp(), **kwargs)

    def turn(
        self, angular_speed_rad_s: float = 1.0, duration_s: float = 3.0, **kwargs: Any
    ) -> Turn:
        """Create a Turn action node."""
        return Turn(
            angular_speed_rad_s=angular_speed_rad_s, duration_s=duration_s, **self._rp(), **kwargs
        )

    def walk_to_waypoint(
        self,
        waypoint_id: str,
        speed_mps: float = 1.0,
        goal_yaw_rad: float = 0.0,
        graphnav_asset_id: str | None = None,
        **kwargs: Any,
    ) -> WalkToWaypoint:
        """Create a WalkToWaypoint action node.

        Args:
            waypoint_id: Target waypoint ID.
            speed_mps: Walking speed.
            goal_yaw_rad: Target yaw at waypoint.
            graphnav_asset_id: Override default graph asset ID.
        """
        asset_id = graphnav_asset_id or self.graphnav_asset_id
        if not asset_id:
            raise ValueError("graphnav_asset_id required — set on MobileRobot or pass explicitly")
        return WalkToWaypoint(
            graphnav_asset_id=asset_id,
            waypoint_id=waypoint_id,
            speed_mps=speed_mps,
            goal_yaw_rad=goal_yaw_rad,
            **self._rp(),
            **kwargs,
        )

    def estop(self, **kwargs: Any) -> EStop:
        """Create an EStop action node."""
        return EStop(**self._rp(), **kwargs)

    def stop(self, **kwargs: Any) -> Stop:
        """Create a Stop action node."""
        return Stop(**self._rp(), **kwargs)

    def undock(self, **kwargs: Any) -> Undock:
        """Create an Undock action node."""
        return Undock(**self._rp(), **kwargs)

    def dock(self, **kwargs: Any) -> Dock:
        """Create a Dock action node."""
        return Dock(**self._rp(), **kwargs)

    def execute_action(self, action_name: str, **kwargs: Any) -> ExecuteStandardAction:
        """Create an ExecuteStandardAction node."""
        return ExecuteStandardAction(action_name=action_name, **self._rp(), **kwargs)

    def set_mode(self, mode_name: str, **kwargs: Any) -> SetRobotMode:
        """Create a SetRobotMode action node."""
        return SetRobotMode(mode_name=mode_name, **self._rp(), **kwargs)
