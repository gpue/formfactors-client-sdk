# formfactors-client-sdk

Python client SDK for the Nova Formfactors platform.

## Install

```bash
pip install "git+https://github.com/gpue/formfactors-client-sdk.git"

# With NovaFlow action builders:
pip install "git+https://github.com/gpue/formfactors-client-sdk.git#egg=formfactors-client-sdk[novaflow]"
```

## Usage

```python
from formfactors_client_sdk import ConnectorClient, AssetsClient, VlmClient

# Discover robots
connector = ConnectorClient()
robots = connector.list_robots()
robot = connector.robot("spot", "greyhound")

# Find waypoints by name
assets = AssetsClient()
wp = assets.find_waypoint("Kitchen", asset_name="All shopfloor")

# Vision analysis
vlm = VlmClient()
result = vlm.analyze("What do you see?", robot_id="greyhound", feed="frontleft")
```

### With NovaFlow (`[novaflow]` extra)

```python
from formfactors_client_sdk.novaflow.mobile import MobileRobot
from formfactors_client_sdk.novaflow.vision import ImageLabelMatch
from novaflow_client_sdk import Flow, Sequence

spot = MobileRobot.from_registry(connector, robot_id="greyhound")

flow = Flow("patrol")
flow.tree(Sequence(children=[
    spot.undock(),
    spot.walk_to_waypoint(wp.id),
    ImageLabelMatch(stream="camera://greyhound.front", label="Human"),
    spot.dock(),
]))
```
