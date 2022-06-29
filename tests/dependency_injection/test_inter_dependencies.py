from starlite import Controller, MediaType, Provide, get
from starlite.testing import create_test_client


def test_inter_dependencies() -> None:
    def top_dependency(query_param: int) -> int:
        return query_param

    def mid_level_dependency() -> int:
        return 5

    def local_dependency(path_param: int, mid_level: int, top_level: int) -> int:
        return path_param + mid_level + top_level

    class MyController(Controller):
        path = "/test"
        dependencies = {"mid_level": Provide(mid_level_dependency)}

        @get(
            path="/{path_param:int}",
            dependencies={
                "summed": Provide(local_dependency),
            },
            media_type=MediaType.TEXT,
        )
        def test_function(self, summed: int) -> str:
            return str(summed)

    with create_test_client(MyController, dependencies={"top_level": Provide(top_dependency)}) as client:
        response = client.get("/test/5?query_param=5")
        assert response.text == "15"
