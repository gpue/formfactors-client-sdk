"""@nova_script decorator — captures Python functions as RunScript Action nodes.

Requires: pip install formfactors-client-sdk[novaflow]

Usage:
    from formfactors_client_sdk.novaflow.arm import nova_script

    @nova_script
    async def move_z(mg, tcp, params):
        from nova.actions import linear as lin
        state = await mg.get_state()
        pose = state.pose
        down = pose.model_copy(deep=True)
        down.position.z += params.get("delta_mm", -100)
        traj = await mg.plan([lin(down)], tcp=tcp)
        await mg.execute(traj, tcp=tcp)
        return {"status": "done"}

    # Use in a flow:
    node = move_z(delta_mm=-100)  # returns an Action node with serialized code
"""

from __future__ import annotations

import inspect
import json
import textwrap
from typing import Any

from novaflow_client_sdk import Action, value

SERVICE = "MotionService"


class NovaScript(Action):
    """Action node that runs user code via MotionService.RunScript."""

    def __init__(
        self,
        code: str,
        function_name: str = "main",
        motion_group: str | None = None,
        tcp: str | None = None,
        params: dict[str, Any] | None = None,
        **kwargs: Any,
    ):
        data = {
            "code": value(code),
            "function_name": value(function_name),
            "motion_group": value(motion_group or ""),
            "tcp": value(tcp or ""),
            "params_json": value(json.dumps(params) if params else "{}"),
        }
        metadata = kwargs.pop("metadata", {})
        metadata.setdefault("name", kwargs.pop("name", function_name))
        super().__init__(
            service=SERVICE,
            operation="RunScript",
            data=data,
            metadata=metadata,
            **kwargs,
        )


def nova_script(func):
    """Decorator that turns an async function into a NovaScript node factory.

    The decorated function can be called with keyword arguments to produce
    an Action node containing the serialized source code.

    The function signature must be: async def name(mg, tcp, params)
    """
    source = textwrap.dedent(inspect.getsource(func))
    # Strip the decorator line(s) from the source
    lines = source.split("\n")
    func_start = next(
        i for i, line in enumerate(lines) if line.lstrip().startswith("async def ")
    )
    clean_source = "\n".join(lines[func_start:])

    def factory(
        motion_group: str | None = None,
        tcp: str | None = None,
        name: str | None = None,
        **params: Any,
    ) -> NovaScript:
        return NovaScript(
            code=clean_source,
            function_name=func.__name__,
            motion_group=motion_group,
            tcp=tcp,
            params=params,
            name=name or func.__name__,
        )

    factory.__name__ = func.__name__
    factory.__doc__ = func.__doc__
    factory._nova_script = True
    factory._source = clean_source
    return factory
