"""Pins the public surface: the exact export set and a docstring on everything in it."""

import inspect

import pytest

import aiorainpoint
import aiorainpoint._generic_decoder as generic_decoder_module
import aiorainpoint._utils as utils_module
import aiorainpoint._validators as validators_module
import aiorainpoint.models as models_module

EXPECTED_PUBLIC_NAMES = {
    "RainPointApiError",
    "RainPointClient",
    "RainPointError",
    "RainPointMqttClient",
    "RainPointThrottledError",
    "SINGLE_OUTLET_GALLONS_PER_COUNT",
    "UNCODED_VARIANT",
    "USAGE_GALLONS_PER_COUNT",
    "battery_flag_is_low",
    "battery_flag_to_percent",
    "decode_co2",
    "decode_flow_meter",
    "decode_flowmeter",
    "decode_generic",
    "decode_hcs005frf",
    "decode_hcs014arf",
    "decode_hcs015arf",
    "decode_hcs024frf_v1",
    "decode_hcs044frf",
    "decode_hcs0528arf",
    "decode_hic801w",
    "decode_htv145frf",
    "decode_htv210b",
    "decode_htv210b_dp_state",
    "decode_htv213frf_valve",
    "decode_hws019wrf_v2",
    "decode_moisture_full",
    "decode_moisture_simple",
    "decode_packed_report_time",
    "decode_packed_timestamp",
    "decode_pool",
    "decode_pool_plus",
    "decode_rain",
    "decode_temphum",
    "decode_unknown",
    "decode_valve_hub",
    "encode_dp_duration_param",
    "f10_to_c",
    "get_catalog_entry",
    "get_catalog_fingerprint",
    "get_catalog_port_number",
    "get_catalog_variant_codes",
    "has_bluetooth_control_identity",
    "is_ascii_declined",
    "is_ascii_payload",
    "is_hand_written_model",
    "parse_entries",
    "parse_hub_broadcast_flag",
    "parse_sub_power_mode",
    "splice_hub_broadcast_param",
    "splice_sub_power_mode",
    "split_prefix",
    "summarize_record",
    "valid_rssi_dbm",
}

TRIMMED_HELPERS = {
    "_RecordSummary": utils_module,
    "_base_decoder_dict": utils_module,
    "_extract_report_time": utils_module,
    "_is_dp_id_framed": utils_module,
    "_le16": utils_module,
    "_parse_rainpoint_payload": utils_module,
    "_parse_tlv_payload": utils_module,
    "_redact_identifier": utils_module,
    "_redact_secret": utils_module,
    "_safe_key": utils_module,
    "_extract_battery_flag": validators_module,
    "_extract_rssi": validators_module,
    "_validate_payload": validators_module,
    "_validate_tag": validators_module,
}


class TestPublicNames:
    """The package exports exactly the pinned names."""

    def test_all_matches_the_pinned_set(self):
        """The length check catches a duplicate entry, which set equality hides."""
        assert set(aiorainpoint.__all__) == EXPECTED_PUBLIC_NAMES
        assert len(aiorainpoint.__all__) == len(EXPECTED_PUBLIC_NAMES)

    def test_every_name_resolves(self):
        """Iterates the literal set, so an emptied __all__ cannot pass this vacuously."""
        for name in sorted(EXPECTED_PUBLIC_NAMES):
            assert getattr(aiorainpoint, name) is not None

    def test_no_underscore_name_exported(self):
        """No private name is exported."""
        assert [name for name in aiorainpoint.__all__ if name.startswith("_")] == []

    def test_no_public_name_leaks_outside_all(self):
        """Every non-dunder name in the namespace is listed, so a private re-export fails too; only real submodules are exempt."""
        leaked = [
            name
            for name, value in vars(aiorainpoint).items()
            if not (name.startswith("__") and name.endswith("__"))
            and not (inspect.ismodule(value) and value.__name__ == f"aiorainpoint.{name}")
            and name not in aiorainpoint.__all__
        ]
        assert leaked == []


# The models namespace is public alongside the package root.
MODELS_PUBLIC_NAMES = {
    "HAND_WRITTEN_MODELS",
    "MODELS",
    "VALVE_FAMILIES",
    "ControlEndpoint",
    "DurationUnit",
    "Family",
    "ModelSpec",
    *(name for name, value in vars(models_module).items() if isinstance(value, str) and name.isupper()),
}


class TestModelsNamespace:
    """The models namespace exports its constants and table, and nothing it merely imports."""

    def test_all_matches_the_pinned_set(self):
        """Every model constant is listed, so a new one cannot ship unexported."""
        assert set(models_module.__all__) == MODELS_PUBLIC_NAMES
        assert len(models_module.__all__) == len(MODELS_PUBLIC_NAMES)

    def test_no_public_name_leaks_outside_all(self):
        """Only the stdlib names models.py imports sit outside __all__, so a new definition cannot ship unlisted."""
        imported = {"Callable", "Mapping", "MappingProxyType", "StrEnum", "dataclass"}
        public = {name for name in vars(models_module) if not name.startswith("_")}
        assert public - set(models_module.__all__) == imported

    def test_every_model_constant_has_a_row(self):
        """A model constant without a MODELS row would be a model the integration cannot decode."""
        constants = {value for name, value in vars(models_module).items() if isinstance(value, str) and name.isupper()}
        assert constants == set(models_module.MODELS)

    def test_legacy_aliases_are_gone(self):
        """The MODEL_ prefix and the old alias names were dropped together."""
        assert [name for name in vars(models_module) if name.startswith("MODEL_")] == []


class TestRemovedNames:
    """Old names stay gone, which __all__ alone cannot show."""

    def test_status_fields_is_public_on_its_module_only(self):
        """STATUS_FIELDS lives on generic_decoder under its public name and stays off the package."""
        assert not hasattr(generic_decoder_module, "_STATUS_FIELDS")
        assert generic_decoder_module.STATUS_FIELDS
        assert not hasattr(aiorainpoint, "STATUS_FIELDS")

    def test_status_fields_rejects_writes(self):
        """The Mapping annotation only stops type checkers, so the object has to refuse too."""
        with pytest.raises(TypeError):
            generic_decoder_module.STATUS_FIELDS[0] = "changed"

    def test_trimmed_helpers_stay_private_in_their_modules(self):
        """A trimmed helper leaves the package but stays on its defining module."""
        for name, module in TRIMMED_HELPERS.items():
            assert not hasattr(aiorainpoint, name)
            assert hasattr(module, name)


class TestDocstrings:
    """Everything exported is documented."""

    def test_exported_functions_and_classes_have_docstrings(self):
        """Reads __doc__ directly, because the inspect helper walks the MRO and would pass a class on its parent's text."""
        undocumented = []
        for name in sorted(aiorainpoint.__all__):
            obj = getattr(aiorainpoint, name)
            if (inspect.isfunction(obj) or inspect.isclass(obj)) and not (obj.__doc__ or "").strip():
                undocumented.append(name)
        assert undocumented == []

    def test_public_methods_of_exported_classes_have_docstrings(self):
        """Walks vars(cls), not dir(cls), so inherited Exception methods stay out."""
        undocumented = []
        for name in sorted(aiorainpoint.__all__):
            cls = getattr(aiorainpoint, name)
            if not inspect.isclass(cls):
                continue
            for method_name, member in vars(cls).items():
                is_method = inspect.isfunction(member) or isinstance(member, (staticmethod, classmethod, property))
                if is_method and not method_name.startswith("_") and not (member.__doc__ or "").strip():
                    undocumented.append(f"{name}.{method_name}")
        assert undocumented == []
