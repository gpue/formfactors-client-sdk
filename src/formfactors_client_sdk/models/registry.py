"""Registry data models."""

from __future__ import annotations

from pydantic import BaseModel, Field


class RobotCapabilities(BaseModel):
    """Capabilities advertised by a robot connector."""

    walk_control: bool = False
    lidar: bool = False
    gps: bool = False
    cameras: bool = False
    graphnav: bool = False
    arm: bool = False
    gripper: bool = False


class RobotEndpoint(BaseModel):
    """A service endpoint for a robot."""

    url: str = ""
    type: str = ""


class RegistryRobot(BaseModel):
    """A robot entry from the NATS KV registry or connector API."""

    id: str
    robot_model: str = Field("", alias="robot_type")
    online: bool = True
    source: str = ""
    capabilities: list[str] = Field(default_factory=list)
    endpoints: list[RobotEndpoint] = Field(default_factory=list)

    model_config = {"populate_by_name": True}


class RegistryCamera(BaseModel):
    """A camera feed entry from the NATS KV registry or connector API."""

    robot_id: str
    robot_type: str = ""
    feed: str
    stream_url: str = ""
    source: str = ""
