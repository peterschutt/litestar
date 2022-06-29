from typing import Optional

import pytest

from starlite import Controller, HttpMethod, Response, Router, Starlite, get
from starlite.handlers import BaseRouteHandler

router_response = type("router_response", (Response,), {})
controller_response = type("controller_response", (Response,), {})
app_response = type("app_response", (Response,), {})
local_response = type("local_response", (Response,), {})

test_path = "/test"


class MyController(Controller):
    path = test_path

    @get(
        path="/{path_param:str}",
    )
    def test_method(self) -> None:
        pass


@pytest.mark.parametrize(
    "layer, expected",
    [[0, local_response], [1, controller_response], [2, router_response], [3, app_response], [None, Response]],
)
def test_response_class(layer: Optional[int], expected: Response) -> None:
    MyController.test_method.resolved_response_class = BaseRouteHandler.empty if layer != 0 else expected  # type: ignore
    MyController.response_class = None if layer != 1 else expected  # type: ignore
    router = Router(path="/users", route_handlers=[MyController], response_class=None if layer != 2 else expected)  # type: ignore
    app = Starlite(route_handlers=[router], response_class=None if layer != 3 else expected)  # type: ignore
    route_handler, _ = app.routes[0].route_handler_map[HttpMethod.GET]  # type: ignore
    layer_map = {
        0: route_handler,
        1: MyController,
        2: router,
        3: app,
    }
    component = layer_map.get(layer)  # type: ignore
    if component:
        component.response_class = expected
        assert component.response_class is expected
    response_class = route_handler.resolve_response_class()
    assert response_class is expected
    if component:
        component.response_class = None
        assert component.response_class is None
