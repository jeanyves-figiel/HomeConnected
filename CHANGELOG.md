# Changelog

## [Unreleased]

### Added
- Remote access: HA Tailscale app (add-on) v0.30.3 installed, auto-start, signed in to the user's tailnet (2026-10-23).
- `homeassistant/dashboards/home.yaml`: iPad "Home" dashboard (lights, Dreame map + rooms, purifier, pets, media, Petcube app button), deployed as `/home-ipad`.
- `docs/petcube-api.md`: B1 phase 1 findings (Petcube Cam 360 PTZ, REST endpoints, no cert pinning, live stream + pan/tilt on proprietary `ptcb` non-HTTP channel, no local RTSP/ONVIF, phase 3 options).
- `tools/petcube/capture_addon.py`: logs other contacted hosts (host + path only) and TLS failures (pinning signal); redacts JSON websocket messages.
- Proposal: "Dashboard & remote access" section (Apple Home primary on iPad/iPhone/Mac/HomeView via home hub + People invites; iPad Guided Access; HA dashboard secondary via Tailscale).
- Proposal: Sony BRAVIA 4K VH2 TV row (native AirPlay 2/HomeKit, not bridged).
- `homeassistant/packages/dreame_homekit.yaml` (B5): room clean, suction, mop mode scripts.
- `homeassistant/packages/xiaomi_purifier_homekit.yaml` (B6): wrapper fan with speed + presets.
- `tools/petcube/`: mitmproxy capture addon (secret redaction) + procedure (B1 phase 1).
- Petlibro feeder (Granary): proposal entry, `homeassistant/packages/petlibro_homekit.yaml` (feed now, food low, blocked), bridge filter (B7).
- `docs/apple-home-proposal.md`: proposal to bring Hue, HomePod, Sonos, Dreame X50, Xiaomi purifier, Petcube, Neakasa into Apple Home (HomeView context, per-device status, Home Assistant bridge architecture, setup steps).
- Build plan (no device left out): Petcube custom integration (B1), Dreame room/mode control (B5), purifier fan speed (B6).
- `homeassistant/packages/`: HomeKit Bridge filter, Sonos volume/group/favorites accessories, Neakasa M1 sensor/switch mapping.

### Changed
- Petcube: app-only by user decision (2026-10-23). No HA integration; dashboard button opens the Petcube app.
- `neakasa_homekit.yaml`: real Neakasa M1 entities (`binary_sensor.neakasa_m1_waste_bucket_full`, `..._needs_cleaning`, `sensor.neakasa_m1_status`, `button.neakasa_m1_clean_now`); new "Litter Needs Cleaning" problem sensor; visits-today dropped from bridge (no HomeKit numeric sensor type).
- `homekit_bridge.yaml`: Neakasa entries live; all bridged devices deployed.
- `xiaomi_purifier_homekit.yaml`: real entities (`fan.xiaomi_cpa4_5e82_air_purifier`); speed via `number.xiaomi_cpa4_5e82_favorite_level` (0-14, verified on unit) instead of raw `set_miot_property` siid/piid; new `binary_sensor.air_purifier_filter_low` (< 10 %).
- `homekit_bridge.yaml`: purifier linked to real PM2.5 + filter life sensors and filter-low indicator; deployed and paired.
- `dreame_homekit.yaml`: real entity `vacuum.x50_ultra_complete`; 6 rooms from Map 1 (Hallway 1, Bathroom 2, Hallway 2 3, Room 4 4, Living Room 5, Dining Room 6); suction/mop-mode scripts replaced by CleanGenius scripts (routine, deep, vacuum+mop, mop after vacuum), since suction/mode selects are unavailable while CleanGenius is on.
- `petlibro_homekit.yaml`: real Granary entities (`button.granary_smart_feeder_manual_feed`, `binary_sensor.granary_smart_feeder_food_status`, `..._food_dispenser`).
- `homekit_bridge.yaml`: Dreame include list matches new scripts; purifier + Neakasa marked pending.

### Fixed
- `homekit_bridge.yaml`: `linked_filter_change_indicator_binary_sensor` → `linked_filter_change_indication_binary_sensor` (invalid key made HomeKit setup fail).
- `sonos_homekit.yaml`: real entity `media_player.bathroom_bathroom` (single Sonos One); "Bathroom Volume" light; group switch removed; favorites kept but not bridged until Sonos favorites exist.
- `homekit_bridge.yaml`: include `light.bathroom_volume`; drop group switch; BRAVIA listed as native.
- HA host: user's always-on laptop (replaces Mac).
- HA host: existing always-on Mac (HA OS in UTM VM, bridged; Scrypted native on macOS) instead of dedicated box.
- Proposal updated for exact models: Dreame X50 Ultra Complete (native Matter, basic), Xiaomi Smart Air Purifier 4 Compact (`xiaomi_miot`), Neakasa M1.
