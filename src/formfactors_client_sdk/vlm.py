"""VlmClient — typed HTTP client for the nova-vlm vision service."""

from __future__ import annotations

from typing import Any

import httpx
from pydantic import BaseModel, Field

from .models.registry import RegistryCamera

# In-cluster default
DEFAULT_VLM_URL = "http://app-nova-vlm:8080/cell/nova-vlm"


class VlmAnalysisResult(BaseModel):
    """Result from VLM analysis."""

    answer: str = ""
    captured_image_base64: str = ""
    inference_time_seconds: float = 0.0
    prompt_tokens: int = 0
    completion_tokens: int = 0


class VlmDetectionResult(BaseModel):
    """Result from person detection."""

    detections: list[dict[str, Any]] = Field(default_factory=list)
    count: int = 0
    inference_time_seconds: float = 0.0


class VlmClient:
    """HTTP client for the nova-vlm vision-language model service.

    Args:
        base_url: Base URL of the nova-vlm service.
        timeout: HTTP request timeout in seconds.
    """

    def __init__(
        self,
        base_url: str = DEFAULT_VLM_URL,
        timeout: float = 60.0,
    ):
        self.base_url = base_url.rstrip("/")
        self._client = httpx.Client(base_url=self.base_url, timeout=timeout)

    def health(self) -> dict[str, Any]:
        """Check service health."""
        resp = self._client.get("/health")
        resp.raise_for_status()
        return resp.json()

    def status(self) -> dict[str, Any]:
        """Get model download/loading status."""
        resp = self._client.get("/api/status")
        resp.raise_for_status()
        return resp.json()

    def list_cameras(self) -> list[RegistryCamera]:
        """List discovered cameras from the KV registry."""
        resp = self._client.get("/api/cameras")
        resp.raise_for_status()
        data = resp.json()
        items = data.get("cameras", []) if isinstance(data, dict) else data
        return [RegistryCamera(**c) for c in items]

    def find_camera(
        self, feed: str | None = None, robot_id: str | None = None
    ) -> RegistryCamera | None:
        """Find a camera by feed name or robot_id (substring match)."""
        cameras = self.list_cameras()
        for cam in cameras:
            if feed and feed.lower() in cam.feed.lower():
                return cam
            if robot_id and robot_id.lower() in cam.robot_id.lower():
                return cam
        return None

    def analyze(
        self,
        prompt: str,
        robot_id: str | None = None,
        feed: str | None = None,
        stream: str | None = None,
    ) -> VlmAnalysisResult:
        """Run generative VLM analysis on a camera snapshot.

        Args:
            prompt: Question or instruction for the VLM.
            robot_id: Robot ID whose camera to use.
            feed: Specific camera feed name.
            stream: Direct stream URL (overrides robot_id/feed).

        Returns:
            VlmAnalysisResult with answer and metadata.
        """
        body: dict[str, Any] = {"prompt": prompt}
        if robot_id:
            body["robot_id"] = robot_id
        if feed:
            body["feed"] = feed
        if stream:
            body["stream"] = stream
        resp = self._client.post("/api/analyze", json=body)
        resp.raise_for_status()
        return VlmAnalysisResult(**resp.json())

    def detect(
        self,
        robot_id: str | None = None,
        feed: str | None = None,
        stream: str | None = None,
        confidence: float = 0.5,
    ) -> VlmDetectionResult:
        """Run person detection on a camera snapshot.

        Args:
            robot_id: Robot ID whose camera to use.
            feed: Specific camera feed name.
            stream: Direct stream URL.
            confidence: Detection confidence threshold.

        Returns:
            VlmDetectionResult with detections.
        """
        body: dict[str, Any] = {"conf": confidence}
        if robot_id:
            body["robot_id"] = robot_id
        if feed:
            body["feed"] = feed
        if stream:
            body["stream"] = stream
        resp = self._client.post("/api/detect", json=body)
        resp.raise_for_status()
        return VlmDetectionResult(**resp.json())

    def embed(
        self,
        robot_id: str | None = None,
        feed: str | None = None,
        stream: str | None = None,
    ) -> dict[str, Any]:
        """Get CLIP embedding for a camera snapshot.

        Returns:
            Dict with 'embedding' (512-D vector) and 'fingerprint'.
        """
        body: dict[str, Any] = {}
        if robot_id:
            body["robot_id"] = robot_id
        if feed:
            body["feed"] = feed
        if stream:
            body["stream"] = stream
        resp = self._client.post("/api/embed", json=body)
        resp.raise_for_status()
        return resp.json()

    def model_info(self) -> dict[str, Any]:
        """Get loaded model metadata."""
        resp = self._client.get("/api/model/info")
        resp.raise_for_status()
        return resp.json()

    # --- Lifecycle ---

    def close(self) -> None:
        self._client.close()

    def __enter__(self) -> VlmClient:
        return self

    def __exit__(self, *args: Any) -> None:
        self.close()
