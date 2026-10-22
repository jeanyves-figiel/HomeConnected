# Changelog

## [Unreleased]

### Added
- Petlibro feeder (Granary): proposal entry, `homeassistant/packages/petlibro_homekit.yaml` (feed now, food low, blocked), bridge filter (B7).
- `docs/apple-home-proposal.md`: proposal to bring Hue, HomePod, Sonos, Dreame X50, Xiaomi purifier, Petcube, Neakasa into Apple Home (HomeView context, per-device status, Home Assistant bridge architecture, setup steps).
- Build plan (no device left out): Petcube custom integration (B1), Dreame room/mode control (B5), purifier fan speed (B6).
- `homeassistant/packages/`: HomeKit Bridge filter, Sonos volume/group/favorites accessories, Neakasa M1 sensor/switch mapping.

### Changed
- HA host: existing always-on Mac (HA OS in UTM VM, bridged; Scrypted native on macOS) instead of dedicated box.
- Proposal updated for exact models: Dreame X50 Ultra Complete (native Matter, basic), Xiaomi Smart Air Purifier 4 Compact (`xiaomi_miot`), Neakasa M1.
