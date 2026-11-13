"""Pin each hand-written model's full decode of its committed frames.

Each model decodes through its models.MODELS row. Regenerate with UPDATE_GOLDEN=1
after an intended change.
"""

import json
import os
from pathlib import Path

import pytest

from aiorainpoint import models as m

from . import payload_samples as s

GOLDEN = Path(__file__).with_name("decoder_golden.json")

# model -> sample constant names. Models with no frame of their own
# reuse the frame of the decoder they pass through to.
CASES = {
    m.HCS026FRF: ["MOISTURE_SIMPLE_HEX_PAYLOAD", "MOISTURE_SIMPLE_SECOND_CAPTURE_PAYLOAD"],
    m.HCS021FRF: ["MOISTURE_FULL_HEX_PAYLOAD", "MOISTURE_FULL_ASCII_PAYLOAD"],
    m.HCS012ARF: ["RAIN_HEX_PAYLOAD", "SAMPLE_HCS012ARF_UPSTREAM_HEX"],
    m.HCS044FRF: ["RAIN_DETECTOR_DRY_PAYLOAD", "RAIN_DETECTOR_WET_PAYLOAD"],
    m.HCS014ARF: ["SAMPLE_HCS014ARF_HEX", "SAMPLE_HCS014ARF_ASCII"],
    m.HCS008FRF: ["FLOWMETER_IDLE_HEX", "FLOWMETER_FLOWING_HEX"],
    m.HCS0530THO: ["SAMPLE_HCS0530THO_HEX", "SAMPLE_HCS0530THO_HEX_2", "SAMPLE_HCS0530THO_ASCII"],
    # Stub decoder, no capture exists: pins the passthrough shape only.
    m.HCS015ARF_PLUS: ["BASIC_HEX_PAYLOAD"],
    m.HTV0540FRF: ["VALVE_HUB_TLV_PAYLOAD"],
    m.HTV113FRF: [
        "SAMPLE_HTV113_IDLE_PAYLOAD",
        "SAMPLE_HTV113FRF_UPSTREAM_NORMAL_RUN",
        "SAMPLE_HTV113FRF_UPSTREAM_CYCLE_SOAK_RUN",
        "SAMPLE_HTV113FRF_UPSTREAM_CYCLE_SOAK_PAUSE",
    ],
    m.HTV145FRF: ["SAMPLE_HTV145_CLOSED_PAYLOAD", "SAMPLE_HTV145_OPEN_PAYLOAD", "SAMPLE_HTV145_AFTER_RUN_PAYLOAD"],
    m.HTV157B: ["SAMPLE_HTV157B_IDLE_PAYLOAD", "SAMPLE_HTV157B_IDLE_PAYLOAD_LOW_BATTERY_FLAG"],
    m.HTP160FRF: ["SAMPLE_HTP160_IDLE_PAYLOAD"],
    m.HTP115FRF: ["SAMPLE_HTP115_IDLE_PAYLOAD"],
    m.HTV213FRF: [
        "SAMPLE_HTV213_01_PREFIX_PAYLOAD",
        "SAMPLE_HTV213FRF_UPSTREAM_USAGE_HEX",
        "SAMPLE_HTV213FRF_UPSTREAM_LOW_BATTERY_HEX",
    ],
    m.HTV245FRF: [
        "SAMPLE_HTV245_TLV_PAYLOAD",
        "SAMPLE_HTV245_FULL_IDLE_PAYLOAD",
        "SAMPLE_HTV245_FULL_ZONE2_ACTIVE_PAYLOAD",
        "SAMPLE_HTV245_ASCII_PAYLOAD",
    ],
    m.HTV345FRF: ["SAMPLE_HTV345_TLV_PAYLOAD"],
    m.HTV405FRF: ["SAMPLE_HTV405_TLV_PAYLOAD"],
    m.HTV445FRF: ["SAMPLE_HTV445_TLV_PAYLOAD"],
    m.HTV210B: ["SAMPLE_HTV210B_TLV_PAYLOAD"],
    m.HIC801W: ["SAMPLE_HIC801W_IDLE_PAYLOAD", "SAMPLE_HIC801W_STATION3_PAYLOAD"],
    m.HCS005FRF: ["MOISTURE_SIMPLE_HEX_PAYLOAD"],
    m.HCS024FRF_V1: ["MOISTURE_FULL_HEX_PAYLOAD"],
    m.HCS015ARF: ["POOL_HCS0528ARF_HEX_PAYLOAD"],
    m.HCS0528ARF: ["POOL_HCS0528ARF_HEX_PAYLOAD"],
    m.HWS019WRF_V2: ["HWS019WRF_V2_PAYLOAD"],
}


def _decode_all() -> dict:
    # JSON round trip so int zone keys compare as stored; bytes become hex.
    out = {f"{model} {name}": m.MODELS[model].decoder(getattr(s, name)) for model, names in CASES.items() for name in names}
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
