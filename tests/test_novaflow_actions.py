"""Tests for novaflow action builders."""

from formfactors_client_sdk.novaflow.mobile import (
    Dock,
    EStop,
    MobileRobot,
    Walk,
    WalkToWaypoint,
)
from formfactors_client_sdk.novaflow.vision import AskVlm, ImageLabelMatch


def test_walk_action():
    action = Walk(speed_mps=1.5, duration_s=5.0, robot_model="spot", robot_id="greyhound")
    assert action.service == "MobileRobotService"
    assert action.operation == "Walk"
    assert action.data["speed_mps"]["data"] == 1.5
    assert action.data["duration_s"]["data"] == 5.0
    assert action.data["robot_model"]["data"] == "spot"


def test_walk_to_waypoint_action():
    action = WalkToWaypoint(
        graphnav_asset_id="graph-1",
        waypoint_id="wp-1",
        speed_mps=0.8,
        robot_model="spot",
        robot_id="greyhound",
    )
    assert action.operation == "WalkToWaypoint"
    assert action.data["graphnav_asset_id"]["data"] == "graph-1"
    assert action.data["waypoint_id"]["data"] == "wp-1"


def test_estop_action():
    action = EStop(robot_model="g1", robot_id="default")
    assert action.operation == "EStop"
    assert action.data["robot_model"]["data"] == "g1"


def test_dock_action():
    action = Dock(robot_model="spot", robot_id="greyhound")
    assert action.operation == "ExecuteStandardAction"
    assert action.data["action_name"]["data"] == "dock"


def test_mobile_robot_builder():
    spot = MobileRobot(model="spot", id="greyhound", graphnav_asset_id="graph-1")
    walk = spot.walk(speed_mps=2.0)
    assert walk.data["robot_model"]["data"] == "spot"
    assert walk.data["robot_id"]["data"] == "greyhound"
    assert walk.data["speed_mps"]["data"] == 2.0

    wp = spot.walk_to_waypoint("wp-kitchen")
    assert wp.data["graphnav_asset_id"]["data"] == "graph-1"
    assert wp.data["waypoint_id"]["data"] == "wp-kitchen"

    dock = spot.dock()
    assert dock.data["action_name"]["data"] == "dock"
    assert dock.data["robot_model"]["data"] == "spot"


def test_image_label_match():
    action = ImageLabelMatch(stream="camera://greyhound.front", label="Human", threshold=0.7)
    assert action.service == "VisionService"
    assert action.operation == "ImageLabelMatch"
    assert action.data["label"]["data"] == "Human"
    assert action.data["threshold"]["data"] == 0.7


def test_ask_vlm():
    action = AskVlm(stream="camera://greyhound.front", prompt="What do you see?")
    assert action.operation == "AskVlm"
    assert action.data["prompt"]["data"] == "What do you see?"
