"""Telemetry data models."""

from __future__ import annotations

from pydantic import BaseModel, Field


class Pose(BaseModel):
    """3D pose."""

    x: float = 0.0
    y: float = 0.0
    z: float = 0.0
    yaw: float = 0.0
    pitch: float = 0.0
    roll: float = 0.0


class TelemetryState(BaseModel):
    """Robot state telemetry message."""

    robot_model: str = ""
    robot_id: str = ""
    mode: str = ""
    battery: float = 0.0
    pose: Pose = Field(default_factory=Pose)
    has_lease: bool = False
    faults: list[str] = Field(default_factory=list)


class TelemetryGps(BaseModel):
    """GPS telemetry message."""

    lat: float = 0.0
    lon: float = 0.0
    heading_deg: float = 0.0
    yaw_rad: float = 0.0
    stale: bool = False


class TelemetryMotion(BaseModel):
    """Motion telemetry message."""

    vx: float = 0.0
    vy: float = 0.0
    vyaw: float = 0.0
