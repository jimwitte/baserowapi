import inspect
import json
from pathlib import Path

import pytest

import baserowapi


pytestmark = pytest.mark.offline

SNAPSHOT_PATH = Path(__file__).parent / "fixtures" / "public_api.json"


def load_snapshot():
    with SNAPSHOT_PATH.open(encoding="utf-8") as stream:
        return json.load(stream)


def resolve_qualified_attribute(qualified_name):
    owner_name, attribute_name = qualified_name.split(".", maxsplit=1)
    return getattr(getattr(baserowapi, owner_name), attribute_name)


def test_intended_root_exports_are_recorded():
    expected = set(load_snapshot()["root_names"])
    actual = set(baserowapi.__all__)

    assert actual == expected
    assert all(hasattr(baserowapi, name) for name in expected)


@pytest.mark.parametrize(
    "qualified_name,expected_parameters",
    load_snapshot()["parameters"].items(),
)
def test_intended_public_signatures_are_recorded(
    qualified_name, expected_parameters
):
    callable_object = resolve_qualified_attribute(qualified_name)

    assert list(inspect.signature(callable_object).parameters) == expected_parameters
