"""Tests for REST client construction and model parsing."""

from formfactors_client_sdk import AssetsClient, ConnectorClient, VlmClient
from formfactors_client_sdk.models.graphnav import Graph, Waypoint
from formfactors_client_sdk.models.registry import RegistryCamera, RegistryRobot


def test_connector_client_init():
    client = ConnectorClient("http://localhost:8000")
    assert client.base_url == "http://localhost:8000"
    client.close()


def test_assets_client_init():
    client = AssetsClient("http://localhost:3050")
    assert client.base_url == "http://localhost:3050"
    client.close()


def test_vlm_client_init():
    client = VlmClient("http://localhost:8010")
    assert client.base_url == "http://localhost:8010"
    client.close()


def test_robot_scope():
    client = ConnectorClient("http://localhost:8000")
    robot = client.robot("spot", "greyhound")
    assert robot.model == "spot"
    assert robot.id == "greyhound"
    assert robot._prefix == "/api/spot/greyhound"
    client.close()


def test_registry_robot_model():
    r = RegistryRobot(id="spot-01", robot_type="spot", capabilities=["walk_control", "cameras"])
    assert r.id == "spot-01"
    assert r.robot_model == "spot"
    assert "cameras" in r.capabilities


def test_registry_camera_model():
    c = RegistryCamera(robot_id="greyhound", robot_type="spot", feed="front", stream_url="http://x")
    assert c.feed == "front"


def test_graph_model():
    g = Graph(id="abc-123", name="All shopfloor")
    assert g.id == "abc-123"


def test_waypoint_model():
    wp = Waypoint(id="wp-1", name="Kitchen", x=1.0, y=2.0)
    assert wp.name == "Kitchen"
    assert wp.x == 1.0
