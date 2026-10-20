# Home Assistant config

Drop-in config for the HA bridge described in [../docs/apple-home-proposal.md](../docs/apple-home-proposal.md).

- `configuration.yaml` snippet:
  ```yaml
  homeassistant:
    packages: !include_dir_named packages
  ```
- Copy `packages/*.yaml` to `/config/packages/`.
- Replace placeholder entity IDs (`media_player.sonos_living`, `sensor.neakasa_*`, ...) with real ones from Settings → Entities.
- Requires HA ≥ 2025.7 (modern `template:` light/switch syntax).

| File | Purpose |
|---|---|
| `packages/homekit_bridge.yaml` | Single HomeKit Bridge, strict include filter (native devices excluded) |
| `packages/sonos_homekit.yaml` | Sonos volume, grouping, favorites as Home-compatible accessories |
| `packages/neakasa_homekit.yaml` | Neakasa litter box mapped to Home sensors/switches |
