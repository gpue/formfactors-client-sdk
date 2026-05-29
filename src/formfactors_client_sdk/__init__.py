"""Formfactors Client SDK — Python client for the Nova Formfactors platform.

Provides typed REST API clients for platform services, data models,
and optional NovaFlow action builders for mobile robots.

Basic usage:
    from formfactors_client_sdk import ConnectorClient, AssetsClient, VlmClient

    connector = ConnectorClient()
    robots = connector.list_robots()

With NovaFlow (pip install formfactors-client-sdk[novaflow]):
    from formfactors_client_sdk.novaflow.mobile import MobileRobot
"""

from .assets import AssetsClient
from .connector import ConnectorClient, RobotScope
from .vlm import VlmClient

__all__ = [
    "AssetsClient",
    "ConnectorClient",
    "RobotScope",
    "VlmClient",
]
