"""GraphNav data models."""

from __future__ import annotations

from pydantic import BaseModel, Field


class Waypoint(BaseModel):
    """A waypoint in a GraphNav graph."""

    id: str
    name: str = ""
    x: float = 0.0
    y: float = 0.0
    z: float = 0.0
    yaw: float = 0.0


class Graph(BaseModel):
    """A GraphNav graph."""

    id: str
    name: str = ""
    waypoints: list[Waypoint] = Field(default_factory=list)
    activated: bool = False
