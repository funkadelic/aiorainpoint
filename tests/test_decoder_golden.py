"""Pin each hand-written model's full decode of its committed frames.

The model-to-decoder table below mirrors ha-rainpoint's DECODER_REGISTRY plus the
display hub special case. Regenerate with UPDATE_GOLDEN=1 after an intended change.
"""

import json
import os
from pathlib import Path

import pytest

from aiorainpoint import (
    decode_co2,
    decode_flowmeter,
    decode_hcs005frf,
    decode_hcs015arf,
    decode_hcs024frf_v1,
    decode_hcs044frf,
    decode_hcs0528arf,
    decode_hic801w,
    decode_htv145frf,
    decode_htv210b,
    decode_htv213frf_valve,
    decode_hws019wrf_v2,
    decode_moisture_full,
    decode_moisture_simple,
    decode_pool_plus,
    decode_rain,
    decode_temphum,
    decode_valve_hub,
    models as m,
)

from . import payload_samples as s

GOLDEN = Path(__file__).with_name("decoder_golden.json")

# model -> (decoder, sample constant names). Models with no frame of their own
# reuse the frame of the decoder they pass through to.
CASES = {
    m.MODEL_MOISTURE_SIMPLE: (decode_moisture_simple, ["MOISTURE_SIMPLE_HEX_PAYLOAD", "MOISTURE_SIMPLE_SECOND_CAPTURE_PAYLOAD"]),
    m.MODEL_MOISTURE_FULL: (decode_moisture_full, ["MOISTURE_FULL_HEX_PAYLOAD", "MOISTURE_FULL_ASCII_PAYLOAD"]),
    m.MODEL_RAIN: (decode_rain, ["RAIN_HEX_PAYLOAD"]),
    m.MODEL_HCS044FRF: (decode_hcs044frf, ["RAIN_DETECTOR_DRY_PAYLOAD", "RAIN_DETECTOR_WET_PAYLOAD"]),
    m.MODEL_TEMPHUM: (decode_temphum, ["SAMPLE_HCS014ARF_HEX", "SAMPLE_HCS014ARF_ASCII"]),
    m.MODEL_FLOWMETER: (decode_flowmeter, ["FLOWMETER_IDLE_HEX", "FLOWMETER_FLOWING_HEX"]),
    m.MODEL_CO2: (decode_co2, ["SAMPLE_HCS0530THO_HEX", "SAMPLE_HCS0530THO_HEX_2", "SAMPLE_HCS0530THO_ASCII"]),
    # Stub decoder, no capture exists: pins the passthrough shape only.
    m.MODEL_POOL_PLUS: (decode_pool_plus, ["BASIC_HEX_PAYLOAD"]),
    m.MODEL_VALVE_HUB: (decode_valve_hub, ["VALVE_HUB_TLV_PAYLOAD"]),
    m.MODEL_VALVE_113: (decode_htv145frf, ["SAMPLE_HTV113_IDLE_PAYLOAD"]),
    m.MODEL_VALVE_145: (
        decode_htv145frf,
        ["SAMPLE_HTV145_CLOSED_PAYLOAD", "SAMPLE_HTV145_OPEN_PAYLOAD", "SAMPLE_HTV145_AFTER_RUN_PAYLOAD"],
    ),
    m.MODEL_HTV157B: (decode_htv145frf, ["SAMPLE_HTV157B_IDLE_PAYLOAD", "SAMPLE_HTV157B_IDLE_PAYLOAD_LOW_BATTERY_FLAG"]),
    m.MODEL_HTP160FRF: (decode_htv145frf, ["SAMPLE_HTP160_IDLE_PAYLOAD"]),
    m.MODEL_HTP115FRF: (decode_htv145frf, ["SAMPLE_HTP115_IDLE_PAYLOAD"]),
    m.MODEL_VALVE_213: (decode_htv213frf_valve, ["SAMPLE_HTV213_01_PREFIX_PAYLOAD"]),
    m.MODEL_VALVE_245: (
        decode_htv213frf_valve,
        [
            "SAMPLE_HTV245_TLV_PAYLOAD",
            "SAMPLE_HTV245_FULL_IDLE_PAYLOAD",
            "SAMPLE_HTV245_FULL_ZONE2_ACTIVE_PAYLOAD",
            "SAMPLE_HTV245_ASCII_PAYLOAD",
        ],
    ),
    m.MODEL_VALVE_345: (decode_htv213frf_valve, ["SAMPLE_HTV345_TLV_PAYLOAD"]),
    m.MODEL_VALVE_405: (decode_htv213frf_valve, ["SAMPLE_HTV405_TLV_PAYLOAD"]),
    m.MODEL_VALVE_445: (decode_htv213frf_valve, ["SAMPLE_HTV445_TLV_PAYLOAD"]),
    m.MODEL_HTV210B: (decode_htv210b, ["SAMPLE_HTV210B_TLV_PAYLOAD"]),
    m.MODEL_HIC801W: (decode_hic801w, ["SAMPLE_HIC801W_IDLE_PAYLOAD", "SAMPLE_HIC801W_STATION3_PAYLOAD"]),
    m.MODEL_HCS005FRF: (decode_hcs005frf, ["MOISTURE_SIMPLE_HEX_PAYLOAD"]),
    m.MODEL_HCS024FRF_V1: (decode_hcs024frf_v1, ["MOISTURE_FULL_HEX_PAYLOAD"]),
    m.MODEL_HCS015ARF: (decode_hcs015arf, ["POOL_HCS0528ARF_HEX_PAYLOAD"]),
    m.MODEL_HCS0528ARF: (decode_hcs0528arf, ["POOL_HCS0528ARF_HEX_PAYLOAD"]),
    m.MODEL_DISPLAY_HUB: (decode_hws019wrf_v2, ["HWS019WRF_V2_PAYLOAD"]),
}


def _decode_all() -> dict:
    # JSON round trip so int zone keys compare as stored; bytes become hex.
    out = {f"{model} {name}": decoder(getattr(s, name)) for model, (decoder, names) in CASES.items() for name in names}
    return json.loads(json.dumps(out, sort_keys=True, default=bytes.hex))


def test_every_hand_written_model_has_a_case():
    assert set(CASES) == set(m.HAND_WRITTEN_MODELS)


def test_decoder_outputs_match_golden():
    actual = _decode_all()
    if os.environ.get("UPDATE_GOLDEN"):
        GOLDEN.write_text(json.dumps(actual, indent=2, sort_keys=True) + "\n")
        pytest.skip("golden file regenerated")
    expected = json.loads(GOLDEN.read_text())
    assert actual.keys() == expected.keys()
    for key in expected:
        assert actual[key] == expected[key], key
