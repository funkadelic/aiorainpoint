"""Model identifiers and the table of models with a hand-written decoder.

``MODELS`` maps each hand-written model to its decoder, its device family and,
for controllable models, the run-duration unit and write endpoint. Every field
is stated per row rather than derived from the product catalog, so a catalog
that fails to load cannot change how a supported device decodes or is driven.
"""

from collections.abc import Callable, Mapping
from dataclasses import dataclass
from enum import StrEnum
from types import MappingProxyType

from . import _decoders as _d

__all__ = [
    "HAND_WRITTEN_MODELS",
    "HCS005FRF",
    "HCS008FRF",
    "HCS012ARF",
    "HCS014ARF",
    "HCS015ARF",
    "HCS015ARF_PLUS",
    "HCS021FRF",
    "HCS024FRF_V1",
    "HCS026FRF",
    "HCS044FRF",
    "HCS0528ARF",
    "HCS0530THO",
    "HIC801W",
    "HTP115FRF",
    "HTP160FRF",
    "HTV0540FRF",
    "HTV113FRF",
    "HTV145FRF",
    "HTV157B",
    "HTV210B",
    "HTV213FRF",
    "HTV245FRF",
    "HTV345FRF",
    "HTV405FRF",
    "HTV445FRF",
    "HWS019WRF_V2",
    "MODELS",
    "VALVE_FAMILIES",
    "ControlEndpoint",
    "DurationUnit",
    "Family",
    "ModelSpec",
]

# Sensors
HCS005FRF = "HCS005FRF"  # Moisture only
HCS008FRF = "HCS008FRF"  # Flowmeter
HCS012ARF = "HCS012ARF"  # Rain gauge
HCS014ARF = "HCS014ARF"  # Temperature/humidity
HCS015ARF = "HCS015ARF"  # Pool temperature
HCS015ARF_PLUS = "HCS015ARF+"  # Pool plus ambient temperature/humidity
HCS021FRF = "HCS021FRF"  # Moisture, temperature and lux
HCS024FRF_V1 = "HCS024FRF-V1"  # Moisture, temperature and lux
HCS026FRF = "HCS026FRF"  # Moisture only
HCS044FRF = "HCS044FRF"  # Rain detector, wet/dry only
HCS0528ARF = "HCS0528ARF"  # Pool temperature
HCS0530THO = "HCS0530THO"  # CO2, temperature and humidity

# Valves and controllers
HTV113FRF = "HTV113FRF"  # Single-outlet timer, HTV145FRF frame
HTV145FRF = "HTV145FRF"  # Single-outlet timer, 10# compact frame
HTV157B = "HTV157B"  # Single-outlet timer, HTV145FRF frame with a 4-byte duration
HTP160FRF = "HTP160FRF"  # Single-outlet timer, HTV145FRF frame without STA_LASTUSAGE
HTP115FRF = "HTP115FRF"  # Solar houseplant timer, HTP160FRF frame plus STA_LASTUSAGE
HTV213FRF = "HTV213FRF"  # Single-zone RF timer
HTV245FRF = "HTV245FRF"  # Irrigation valve
HTV345FRF = "HTV345FRF"  # Irrigation valve
HTV405FRF = "HTV405FRF"  # 4-zone irrigation valve
HTV445FRF = "HTV445FRF"  # 4-zone irrigation valve
HTV0540FRF = "HTV0540FRF"  # Multi-zone valve hub
HTV210B = "HTV210B"  # Bluetooth valve, reports over RF once hub-paired
HIC801W = "HIC801W"  # 8-station controller; catalog variant 279 carries the stations

# Hubs
HWS019WRF_V2 = "HWS019WRF-V2"  # Irrigation display hub


class Family(StrEnum):
    """Entity shape a model gets; the decoder is chosen per row, not per family."""

    SINGLE_OUTLET_TIMER = "single_outlet_timer"
    ZONE_VALVE = "zone_valve"
    VALVE_HUB = "valve_hub"
    BT_VALVE = "bt_valve"
    STATION_CONTROLLER = "station_controller"
    DISPLAY_HUB = "display_hub"
    SENSOR = "sensor"


class DurationUnit(StrEnum):
    """Unit the device's run-duration command field reads."""

    SECONDS = "seconds"
    MINUTES = "minutes"


class ControlEndpoint(StrEnum):
    """Cloud endpoint a model's valve commands go through."""

    WORK_MODE = "controlWorkMode"
    WORK_MODE_DP = "controlWorkModeDP"


# Families whose decode carries a zones dict. The HIC801W reports one running
# station instead, so STATION_CONTROLLER is not one of them.
VALVE_FAMILIES = frozenset({Family.SINGLE_OUTLET_TIMER, Family.ZONE_VALVE, Family.VALVE_HUB, Family.BT_VALVE})
_CONTROLLED_FAMILIES = VALVE_FAMILIES | {Family.STATION_CONTROLLER}


@dataclass(frozen=True, slots=True)
class ModelSpec:
    """One hand-written model: its decoder, family and, if controllable, its control fields."""

    decoder: Callable[[str], dict]
    family: Family
    duration_unit: DurationUnit | None = None
    control_endpoint: ControlEndpoint | None = None

    def __post_init__(self) -> None:
        """Require both control fields on a controllable family and neither elsewhere."""
        controlled = self.family in _CONTROLLED_FAMILIES
        stated = (self.duration_unit is not None, self.control_endpoint is not None)
        if stated != (controlled, controlled):
            raise ValueError(f"{self.family} needs duration_unit and control_endpoint {'set' if controlled else 'unset'}")


def _sensor(decoder: Callable[[str], dict]) -> ModelSpec:
    return ModelSpec(decoder, Family.SENSOR)


def _valve(decoder: Callable[[str], dict], family: Family, endpoint: ControlEndpoint = ControlEndpoint.WORK_MODE) -> ModelSpec:
    return ModelSpec(decoder, family, DurationUnit.SECONDS, endpoint)


MODELS: Mapping[str, ModelSpec] = MappingProxyType(
    {
        HCS005FRF: _sensor(_d.decode_hcs005frf),
        HCS008FRF: _sensor(_d.decode_flowmeter),
        HCS012ARF: _sensor(_d.decode_rain),
        HCS014ARF: _sensor(_d.decode_temphum),
        HCS015ARF: _sensor(_d.decode_hcs015arf),
        # decode_pool_plus is a stub: no capture of this model exists yet.
        HCS015ARF_PLUS: _sensor(_d.decode_pool_plus),
        HCS021FRF: _sensor(_d.decode_moisture_full),
        HCS024FRF_V1: _sensor(_d.decode_hcs024frf_v1),
        HCS026FRF: _sensor(_d.decode_moisture_simple),
        HCS044FRF: _sensor(_d.decode_hcs044frf),
        HCS0528ARF: _sensor(_d.decode_hcs0528arf),
        HCS0530THO: _sensor(_d.decode_co2),
        HTV113FRF: _valve(_d.decode_htv145frf, Family.SINGLE_OUTLET_TIMER),
        HTV145FRF: _valve(_d.decode_htv145frf, Family.SINGLE_OUTLET_TIMER),
        # Upstream routes HTV157B to the DP endpoint; unverified on hardware, so it stays on controlWorkMode.
        HTV157B: _valve(_d.decode_htv145frf, Family.SINGLE_OUTLET_TIMER),
        HTP160FRF: _valve(_d.decode_htv145frf, Family.SINGLE_OUTLET_TIMER),
        HTP115FRF: _valve(_d.decode_htv145frf, Family.SINGLE_OUTLET_TIMER),
        HTV213FRF: _valve(_d.decode_htv213frf_valve, Family.ZONE_VALVE),
        HTV245FRF: _valve(_d.decode_htv213frf_valve, Family.ZONE_VALVE),
        HTV345FRF: _valve(_d.decode_htv213frf_valve, Family.ZONE_VALVE),
        HTV405FRF: _valve(_d.decode_htv213frf_valve, Family.ZONE_VALVE),
        HTV445FRF: _valve(_d.decode_htv213frf_valve, Family.ZONE_VALVE),
        HTV0540FRF: _valve(_d.decode_valve_hub, Family.VALVE_HUB),
        HTV210B: _valve(_d.decode_htv210b, Family.BT_VALVE, ControlEndpoint.WORK_MODE_DP),
        HIC801W: ModelSpec(_d.decode_hic801w, Family.STATION_CONTROLLER, DurationUnit.MINUTES, ControlEndpoint.WORK_MODE),
        HWS019WRF_V2: ModelSpec(_d.decode_hws019wrf_v2, Family.DISPLAY_HUB),
    }
)

# Every model here is kept off the model-agnostic generic decode path.
HAND_WRITTEN_MODELS: frozenset[str] = frozenset(MODELS)
