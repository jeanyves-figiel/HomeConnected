# Proposal: all devices in Apple Home

Date: 2026-10-20. Status: draft for review.

## TL;DR

- 3 of 7 device families native today: **Hue**, **HomePod**, **Dreame X50** (Matter via OTA).
- **Sonos**: AirPlay 2 speakers in Home. Audio only, no HomeKit/Matter control.
- **Xiaomi purifier**: Home Assistant (HA) → HomeKit Bridge. Reliable.
- **Neakasa litter**: no native/official path. HA community integration (cloud) → HomeKit Bridge, sensors + clean button. Best effort.
- **Petcube**: no API, no HomeKit, no RTSP. Cannot be bridged. Keep app, or replace camera.
- Architecture: Apple home hub (HomePod/HomeView) + **Home Assistant** on small always-on host as single bridge for non-native devices.

## HomeView: what it is, what it changes

Facts (announced 2026-10-13):
- Apple smart display, 7" screen, A18, Siri AI, face recognition, video calls. From $299. Tabletop + wall-mount. Ships 2026-11-13. ([CNBC](https://www.cnbc.com/2026/10/13/apple-homeview-smart-home-siri-ai.html), [MacRumors](https://www.macrumors.com/2026/10/11/apple-homeview-smart-home-hub-ship-next-month/), [9to5Mac](https://9to5mac.com/2026/10/13/apple-homeview-announced-features-price-release-date/))
- Acts as Apple Home hub; same launch: new Apple TV 4K remains hub + Matter controller + Thread border router. ([Forbes](https://www.forbes.com/sites/paullamkin/2026/10/13/apples-smart-home-comeback-now-official-with-new-homeview-apple-tv-and-more/))

What it changes for this setup:
- Wall/counter dashboard + Siri control for everything **already in Home**.
- Does **not** add support for non-HomeKit/non-Matter devices. Bridging still required.
- Camera tiles only for HomeKit/HKSV/Matter cameras → Petcube won't show.
- Inferred (not confirmed in sources): Thread border router like HomePod mini. Existing HomePod already covers hub + Thread role, so HomeView is optional for this plan.

Prerequisite: Apple ended legacy Home architecture 2026-02-10. Home must be on new architecture (Home app → Home Settings → Software Update).

## Per-device status

| Device | Native HomeKit/Matter (Oct 2026) | Path into Home | Confidence |
|---|---|---|---|
| Philips Hue lamps + plugs | Yes. Hue Bridge = HomeKit + Matter bridge | Add Hue Bridge in Home (HomeKit code or Matter) | High |
| HomePod (music, temp/humidity) | Yes. Built-in sensors | Already in Home | High |
| Sonos | No HomeKit/Matter. AirPlay 2 only | Add as AirPlay speakers in Home (play/volume, scenes w/ audio). Groups/EQ stay in Sonos app | High |
| Dreame X50 | Matter via OTA (X50 line) → Home "robot vacuum" (iOS 18.4+) | Native Matter pairing | Medium: verify OTA on unit |
| Xiaomi air purifier | No Matter (no source found) | HA `xiaomi_home` (official) or `xiaomi_miot` (HACS) → HomeKit Bridge | High |
| Neakasa litter (M1) | No | HA community integration (cloud, HACS) → HomeKit Bridge | Low |
| Petcube camera | No. No public API/RTSP | None viable. Replace or keep app | High (that it's blocked) |

### Details and caveats

**Hue**
- Hue Bridge v2+ exposes all lights + Hue smart plugs to HomeKit.
- Prefer Matter pairing of Hue Bridge only if needed for multi-admin; HomeKit pairing is mature and exposes more.

**HomePod**
- Temp/humidity sensors usable in automations (e.g. purifier on when humidity/air bad, via HA-bridged purifier).
- Keep one HomePod/Apple TV/HomeView as hub. Wired Apple TV preferred for stability.

**Sonos**
- Home app → Add accessory → each AirPlay 2 Sonos appears; assign rooms.
- Limits: no Sonos grouping, inputs, EQ from Home. Siri "play X in kitchen" works via AirPlay.
- Optional: HA `sonos` integration for automations (doorbell chime, TTS); HA can't expose Sonos as HomeKit speaker with full control (HomeKit TV/speaker tiles limited). Not recommended.
- Sonos joined CSA (Matter) but no Matter product support announced.

**Dreame X50**
- Update firmware in Dreamehome app → Matter option appears → Home app → Add accessory.
- Reported issue: QR scan fails; enter Matter PIN manually ([labomaison](https://labomaison.com/entretien/aspirateur-robot/dreame-matter-apple-maison-aspirateur-robot/)).
- Apple Home RVC features: start/stop/dock, modes, room selection (if exported). Maps, mop settings → Dreamehome app.
- Fallback if OTA missing: HA `dreame_vacuum` (Tasshack, HACS) → Matterbridge (separate instance, vacuum alone; Apple requires standalone RVC node). Verify X50 model ID in integration list first.

**Xiaomi purifier**
- HA `xiaomi_home` (official Xiaomi integration, cloud login) or `xiaomi_miot` (HACS, local token option).
- HomeKit Bridge exposes as air purifier: on/off, speed, auto mode, PM2.5/air quality, filter life (model-dependent).
- Caveat: HA + purifier on same subnet/VLAN for local mode.

**Neakasa**
- No official API, no Matter. Device is ESP32-based; community HA work exists ([forum](https://community.home-assistant.io/t/neakasa-m1-integration/738783)). Check HACS for a current `neakasa` integration before relying on it.
- If available: expose waste-bin full, last use, cat weight as sensors; "clean now" as switch. Home has no litter-box category → appears as sensors/switches.
- Cloud-dependent; can break on vendor app changes.

**Petcube**
- No HomeKit, Matter, RTSP or public API. Alexa skill only.
- Options:
  1. Keep Petcube app (treats/laser stay there anyway).
  2. Add HKSV camera for cat area (Eve Cam, Aqara G-series, Logitech Circle View) → shows on HomeView + iPhone, iCloud+ storage.
- No bridge recommended; Alexa-based hacks are fragile.

## Recommended architecture

```
                 ┌─────────── Apple Home (iPhone, HomeView, Siri) ───────────┐
                 │  Hub: HomePod / Apple TV 4K / HomeView (Thread BR)        │
                 └───┬─────────────┬──────────────┬──────────────┬──────────┘
                HomeKit         Matter          AirPlay 2     HomeKit Bridge
                    │              │                │              │
               Hue Bridge      Dreame X50        Sonos      Home Assistant
              (lamps, plugs)                                (HA Green / Pi 5 / NUC)
                                                              ├─ Xiaomi purifier
                                                              └─ Neakasa (best effort)
   HomePod sensors: native            Petcube: own app (or replace with HKSV cam)
```

Principle: native first, HA only for gaps. One bridge, one place for credentials.

Host options for HA:
- **HA Green** (~€100, plug-and-play). Default.
- Raspberry Pi 5 + SSD, or mini PC (N100) if more add-ons planned.
- Wired Ethernet, same subnet as Apple hub (mDNS required for HomeKit Bridge).

## Setup steps

1. **Apple Home baseline**
   - Confirm new Home architecture.
   - Set hub: Home Settings → Home Hubs & Bridges. Prefer wired Apple TV or HomePod; add HomeView after 2026-11-13.
2. **Native devices**
   - Hue: Home → Add accessory → scan Hue Bridge code. Assign rooms.
   - Sonos: Home → Add accessory → each speaker (AirPlay). Assign rooms.
   - Dreame: update firmware → enable Matter in Dreamehome → Home → Add accessory → manual code if QR fails.
3. **Home Assistant**
   - Install HA OS on host. Onboard. Set static IP / DHCP reservation.
   - Install HACS (only if using community integrations).
   - Add Xiaomi: Settings → Devices → Add → `Xiaomi Home` (or HACS `xiaomi_miot`).
   - Add Neakasa: HACS community integration, if one exists and works for your model.
4. **Bridge to Apple Home**
   - Settings → Devices → Add → `HomeKit Bridge`. Mode: bridge. Include only: purifier `fan`/`sensor` entities, Neakasa sensors/switch. Exclude everything already native (avoid duplicates).
   - Scan pairing QR from HA notification in Home app.
   - Optional fallback for vacuum: Matterbridge add-on, dedicated instance for Dreame only.
5. **Automations (in Apple Home)**
   - HomePod humidity/temp → purifier mode.
   - "Leaving" scene → lights off, vacuum start.
   - Neakasa bin full → notification (via HA sensor in Home).
6. **Validate**
   - Each device controllable from Home + Siri + HomeView.
   - Reboot HA → accessories return without re-pairing.
   - Remote access works (hub online).

## Risks

- Dreame Matter OTA rollout per region/model: unverified for exact unit.
- Neakasa/Petcube: vendor-locked clouds. Partial or no integration.
- HomeKit Bridge pairing breaks if HA IP changes or mDNS blocked (VLAN, mesh Wi-Fi isolation).
- Duplicates if a device is both native and bridged → strict HA include filter.

## Decisions needed

- Accept Petcube staying outside Home, or buy HKSV camera.
- Buy HA host (HA Green default).
- Neakasa: accept best-effort integration or keep app-only.

## Sources

- [CNBC: HomeView](https://www.cnbc.com/2026/10/13/apple-homeview-smart-home-siri-ai.html)
- [MacRumors: HomeView ships mid-Nov](https://www.macrumors.com/2026/10/11/apple-homeview-smart-home-hub-ship-next-month/)
- [Forbes: Apple smart home launches](https://www.forbes.com/sites/paullamkin/2026/10/13/apples-smart-home-comeback-now-official-with-new-homeview-apple-tv-and-more/)
- [Apple: Matter accessories](https://support.apple.com/en-us/102135), [Apple: home hub](https://support.apple.com/en-us/102557)
- [Dreame: Matter robot vacuums](https://www.dreametech.com/blogs/blog/matter-robot-vacuum)
- [Smart Home Compared: X50 Ultra](https://smarthomecompared.com/robot-vacuums/dreame-d30-ultra-ce-vs-dreame-x50-ultra)
- [Tasshack/dreame-vacuum](https://github.com/Tasshack/dreame-vacuum)
- [Matterbridge RVC note (Apple standalone node)](https://unpkg.com/matterbridge-roborock-vacuum-plugin@1.1.7/README.md)
- [homebridge-miot](https://cdn.jsdelivr.net/npm/homebridge-miot@1.8.7/README.md)
- [HA forum: Neakasa M1](https://community.home-assistant.io/t/neakasa-m1-integration/738783)
- [HA forum: Petcube](https://community.home-assistant.io/t/pet-cube-component/51326)
- [What Hi-Fi: Sonos joins CSA](https://www.whathifi.com/news/sonos-is-now-part-of-the-matter-smart-home-alliance-joining-amazon-apple-and-google)
