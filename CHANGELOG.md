# Changelog

## [0.2.0](https://github.com/funkadelic/aiorainpoint/compare/v0.1.2...v0.2.0) (2026-11-07)


### ⚠ BREAKING CHANGES

* remove the unused RainPointClient.set_device_state ([#22](https://github.com/funkadelic/aiorainpoint/issues/22))
* decode_soil, decode_temp_hum, decode_temp_hum_full and decode_display can no longer be imported from aiorainpoint.
* these names can no longer be imported from aiorainpoint: _RecordSummary, _base_decoder_dict, _extract_battery_flag, _extract_report_time, _extract_rssi, _is_dp_id_framed, _le16, _parse_rainpoint_payload, _parse_tlv_payload, _redact_identifier, _redact_secret, _safe_key, _validate_payload, _validate_tag. They stay private in their own modules. generic_decoder._STATUS_FIELDS is now generic_decoder.STATUS_FIELDS and is read-only; use dict(STATUS_FIELDS) for a plain dict.

### Added

* remove four decoders no model uses ([ee69eed](https://github.com/funkadelic/aiorainpoint/commit/ee69eedd7065424a0034e588b6795820f2b988e5))
* remove the unused RainPointClient.set_device_state ([#22](https://github.com/funkadelic/aiorainpoint/issues/22)) ([e946daa](https://github.com/funkadelic/aiorainpoint/commit/e946daa9e0366de1ae9da197831f86f0a3d9f179))
* trim the public API to documented names ([7d89aba](https://github.com/funkadelic/aiorainpoint/commit/7d89aba053bf8fccf0c4045eac1fe0472e70ebff))


### Fixed

* keep cloud values out of logs and reject malformed responses ([#17](https://github.com/funkadelic/aiorainpoint/issues/17)) ([a1531d0](https://github.com/funkadelic/aiorainpoint/commit/a1531d041ac2839b12fe282b8324a31c0d50f382))
* keep raw payloads out of decoder logs and errors ([#20](https://github.com/funkadelic/aiorainpoint/issues/20)) ([3766c85](https://github.com/funkadelic/aiorainpoint/commit/3766c85f9eb90dea8f2748d3b62c255170ed3b58))
* restore CO2, temperature and humidity readings ([1147481](https://github.com/funkadelic/aiorainpoint/commit/11474817a31d3de05885b059491b2a4df2f896c6))
* stop reporting a false signal strength for CO2 and temperature sensors ([1147481](https://github.com/funkadelic/aiorainpoint/commit/11474817a31d3de05885b059491b2a4df2f896c6))


### Other Changes

* add a contributing guide ([#19](https://github.com/funkadelic/aiorainpoint/issues/19)) ([d863e81](https://github.com/funkadelic/aiorainpoint/commit/d863e811721babeb5dc68a6bda379a153e1fcbe3))
* add mutation testing and run tests before each commit ([#15](https://github.com/funkadelic/aiorainpoint/issues/15)) ([330cdf5](https://github.com/funkadelic/aiorainpoint/commit/330cdf5071e91e910f0e4ecf4f5172879ecb60a1))
* bump mypy from 2.4.0 to 2.4.1 in the pip group ([#24](https://github.com/funkadelic/aiorainpoint/issues/24)) ([933f189](https://github.com/funkadelic/aiorainpoint/commit/933f189c4265d5d1592694e9efd136daa5c1f1fc))
* bump the actions group with 2 updates ([#23](https://github.com/funkadelic/aiorainpoint/issues/23)) ([de74fdd](https://github.com/funkadelic/aiorainpoint/commit/de74fdd4e1d3b47f4b5806a196c618e463f087ab))
* drop the stale cron comment ([#16](https://github.com/funkadelic/aiorainpoint/issues/16)) ([df14476](https://github.com/funkadelic/aiorainpoint/commit/df14476aec70ba2bf51f6e5d556fb7da84088734))
* fail the pin bump on a pin it cannot compare ([#14](https://github.com/funkadelic/aiorainpoint/issues/14)) ([75b7142](https://github.com/funkadelic/aiorainpoint/commit/75b714262a1c2fb66e934a22adbd4f9268773e5d))
* update pytest requirement from &gt;=9.1.1 to &gt;=9.2.0 ([#25](https://github.com/funkadelic/aiorainpoint/issues/25)) ([34e64c2](https://github.com/funkadelic/aiorainpoint/commit/34e64c2231704b7b8c23fe63277a117d8bb3130d))
* update pytest-asyncio requirement from &gt;=1.4.1 to &gt;=1.4.1.post1 ([#26](https://github.com/funkadelic/aiorainpoint/issues/26)) ([eff0c0e](https://github.com/funkadelic/aiorainpoint/commit/eff0c0ea1055f01b63b4c935c5fbbb3df356ad8b))
* wait for the package index before opening the pin bump ([#12](https://github.com/funkadelic/aiorainpoint/issues/12)) ([eea8cc7](https://github.com/funkadelic/aiorainpoint/commit/eea8cc7d8c2ad75fc96925a1ebfa6b9cbe5b95b1))

## [0.1.2](https://github.com/funkadelic/aiorainpoint/compare/v0.1.1...v0.1.2) (2026-11-05)


### Other Changes

* describe the client from the library's side ([#11](https://github.com/funkadelic/aiorainpoint/issues/11)) ([7a29db4](https://github.com/funkadelic/aiorainpoint/commit/7a29db43ebbfdbbbcb0d11e0c6abccbdc729f05c))
* open a pin bump pull request on the integration after each release ([#10](https://github.com/funkadelic/aiorainpoint/issues/10)) ([60d0383](https://github.com/funkadelic/aiorainpoint/commit/60d038371f5bdfee20e567cbc27cd9f458f30d18))
* update pytest-cov requirement from &gt;=7.0.0 to &gt;=7.1.0 ([#2](https://github.com/funkadelic/aiorainpoint/issues/2)) ([e9b4bb4](https://github.com/funkadelic/aiorainpoint/commit/e9b4bb4298d958e90683040a65cddcda60de9c91))

## [0.1.1](https://github.com/funkadelic/aiorainpoint/compare/v0.1.0...v0.1.1) (2026-11-04)


### Fixed

* **catalog:** refresh the product catalog snapshot ([#7](https://github.com/funkadelic/aiorainpoint/issues/7)) ([407ea78](https://github.com/funkadelic/aiorainpoint/commit/407ea7856665b1dd8643480c19cc00fabab78d24))


### Other Changes

* update pytest requirement from &gt;=8.2 to &gt;=9.1.1 ([#3](https://github.com/funkadelic/aiorainpoint/issues/3)) ([b3459ba](https://github.com/funkadelic/aiorainpoint/commit/b3459ba22e5ae3aaeb71d4e38255db6a868cd3c2))
* update pytest-asyncio requirement from &gt;=1.3.0 to &gt;=1.4.1 ([#4](https://github.com/funkadelic/aiorainpoint/issues/4)) ([30ce583](https://github.com/funkadelic/aiorainpoint/commit/30ce58352890404114d39526562e15f07f9cb3fa))

## 0.1.0 (2026-11-04)


### Other Changes

* package the client as aiorainpoint ([#1](https://github.com/funkadelic/aiorainpoint/issues/1)) ([5b3afc1](https://github.com/funkadelic/aiorainpoint/commit/5b3afc1974ffc725d91672da2d4d2c89dbc15a5a))
* publish releases to PyPI through trusted publishing ([#5](https://github.com/funkadelic/aiorainpoint/issues/5)) ([737ce70](https://github.com/funkadelic/aiorainpoint/commit/737ce701be6038b5afb58a3d84e39b92eeb167e5))
* run tests and checks on every change ([#1](https://github.com/funkadelic/aiorainpoint/issues/1)) ([1de3b06](https://github.com/funkadelic/aiorainpoint/commit/1de3b06b2f708c71df820d068843999f9050fdf5))
