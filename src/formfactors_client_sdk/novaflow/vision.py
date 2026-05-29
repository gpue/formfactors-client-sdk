"""Pre-built NovaFlow Action nodes for VisionService.

Requires: pip install formfactors-client-sdk[novaflow]
"""

from __future__ import annotations

from typing import Any

from novaflow_client_sdk import Action, value

SERVICE = "VisionService"


class CaptureImage(Action):
    """Capture an image from a camera stream.

    Args:
        stream: Camera stream URI (e.g. "camera://greyhound.frontleft_fisheye_image").
        rotation: Image rotation in degrees (0, 90, 180, 270).
    """

    def __init__(
        self,
        stream: str,
        rotation: int = 0,
        **kwargs: Any,
    ):
        data = {
            "stream": value(stream),
            "rotation": value(rotation),
        }
        super().__init__(service=SERVICE, operation="CaptureImage", data=data, **kwargs)


class AskVlm(Action):
    """Ask the VLM a question about a camera image.

    Args:
        stream: Camera stream URI.
        prompt: Question to ask the VLM.
        rotation: Image rotation in degrees.
    """

    def __init__(
        self,
        stream: str,
        prompt: str,
        rotation: int = 0,
        **kwargs: Any,
    ):
        data = {
            "stream": value(stream),
            "prompt": value(prompt),
            "rotation": value(rotation),
        }
        super().__init__(service=SERVICE, operation="AskVlm", data=data, **kwargs)


class ClassifyImage(Action):
    """Classify an image using CLIP against a label.

    Args:
        stream: Camera stream URI.
        label: Label to classify against.
        threshold: Confidence threshold (0.0 to 1.0).
        rotation: Image rotation in degrees.
    """

    def __init__(
        self,
        stream: str,
        label: str,
        threshold: float = 0.5,
        rotation: int = 0,
        **kwargs: Any,
    ):
        data = {
            "stream": value(stream),
            "label": value(label),
            "threshold": value(threshold),
            "rotation": value(rotation),
        }
        super().__init__(service=SERVICE, operation="ClassifyImage", data=data, **kwargs)


class ImageLabelMatch(Action):
    """Check if an image matches a label (condition-style action).

    Args:
        stream: Camera stream URI.
        label: Label to match against (e.g. "Human", "Dog").
        threshold: Confidence threshold (0.0 to 1.0).
        rotation: Image rotation in degrees.
    """

    def __init__(
        self,
        stream: str,
        label: str,
        threshold: float = 0.5,
        rotation: int = 0,
        **kwargs: Any,
    ):
        data = {
            "stream": value(stream),
            "label": value(label),
            "threshold": value(threshold),
            "rotation": value(rotation),
        }
        super().__init__(service=SERVICE, operation="ImageLabelMatch", data=data, **kwargs)
