"""The model table: row validation and agreement with the committed catalog."""

import pytest

from aiorainpoint import decode_rain, has_bluetooth_control_identity
from aiorainpoint.models import (
    MODELS,
    VALVE_FAMILIES,
    ControlEndpoint,
    DurationUnit,
    Family,
    ModelSpec,
)


class TestModelSpec:
    """Control fields are required on controllable families and refused elsewhere."""

    @pytest.mark.parametrize(
        ("family", "unit", "endpoint"),
        [
            (Family.ZONE_VALVE, None, ControlEndpoint.WORK_MODE),
            (Family.STATION_CONTROLLER, DurationUnit.MINUTES, None),
            (Family.SENSOR, DurationUnit.SECONDS, None),
            (Family.DISPLAY_HUB, None, ControlEndpoint.WORK_MODE),
        ],
    )
    def test_mismatched_control_fields_raise(self, family, unit, endpoint):
        with pytest.raises(ValueError, match=family.value):
            ModelSpec(decode_rain, family, unit, endpoint)

    def test_table_rejects_writes(self):
        with pytest.raises(TypeError):
            MODELS["NEW"] = ModelSpec(decode_rain, Family.SENSOR)  # type: ignore[index]


class TestRows:
    """Rows that the catalog or the hardware already settled."""

    def test_control_endpoint_agrees_with_the_catalog(self):
        """A row's DP endpoint matches the catalog's Bluetooth control identity, HTV157B included."""
        disagree = [
            model
            for model, spec in MODELS.items()
            if spec.control_endpoint is not None
            and (spec.control_endpoint is ControlEndpoint.WORK_MODE_DP) != has_bluetooth_control_identity(model)
        ]
        assert disagree == []

    def test_only_the_hic801w_runs_in_minutes(self):
        minutes = [model for model, spec in MODELS.items() if spec.duration_unit is DurationUnit.MINUTES]
        assert minutes == ["HIC801W"]

    def test_station_controller_is_not_zone_shaped(self):
        assert Family.STATION_CONTROLLER not in VALVE_FAMILIES
