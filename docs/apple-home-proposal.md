# Proposal: all devices in Apple Home

Date: 2026-10-20. Status: draft for review.

## TL;DR

- 3 of 8 device families native today: **Hue**, **HomePod**, **Dreame X50** (Matter via OTA).
- **Sonos**: AirPlay 2 in Home + **built** HA package: volume, grouping, favorites as Home accessories.
- **Xiaomi purifier**: Home Assistant (HA) → HomeKit Bridge. Reliable.
- **Neakasa litter**: existing community HA integration (cloud MQTT push) + **built** mapping → Home sensors + "Clean now" switch.
- **Petlibro feeder**: community HA integration + **built** mapping → "Feed now" switch + alert sensors.
- **Petcube**: **build** custom HA integration (reverse-engineer app API + stream) → go2rtc → Scrypted → Home camera with HKSV.
- Architecture: Apple home hub (HomePod/HomeView) + **Home Assistant** on small always-on host as single bridge for non-native devices.
- Policy: no device left out. Where no integration exists, we build it. See [Build plan](#build-plan).

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
| Sonos (1× Sonos One, Bathroom) | No HomeKit/Matter. AirPlay 2 only | AirPlay 2 in Home + HA `sonos` → template accessories (volume/favorites) → HomeKit Bridge | High |
| Sony BRAVIA 4K VH2 TV | AirPlay 2 + HomeKit (supported BRAVIA models) | Add in Home app directly (Home → Add accessory, or TV settings → AirPlay & HomeKit). Not bridged via HA | High |
| Dreame X50 Ultra Complete | Yes, Matter via firmware ≥ 4.3.9_3276 (basic: start/stop/pause/dock) | Native Matter + HA `dreame_vacuum` room/mode switches via HomeKit Bridge | High (native), Medium (rooms) |
| Xiaomi Smart Air Purifier 4 Compact (`xiaomi.airp.cpa4`) | No Matter | HA `xiaomi_miot` (HACS) → HomeKit Bridge | High (fan speed needs workaround) |
| Neakasa litter (M1) | No | HACS `ha-neakasa-litterbox` → template mapping → HomeKit Bridge | Medium |
| Petlibro Granary (no camera, PLAF103) | No (Homebridge plugin exists, no Matter) | HACS `jjjonesjr33/petlibro` → template mapping → HomeKit Bridge | Medium |
| Petcube camera | No. No public API/RTSP | Custom HA integration (to build) → go2rtc → Scrypted (HKSV) | Low until API capture done |

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
- Apple Home has no speaker category for 3rd-party controls; HomeKit Bridge TV/receiver mode only gives power button. Built workaround ([`sonos_homekit.yaml`](../homeassistant/packages/sonos_homekit.yaml)):
  - Volume → dimmable "light" (brightness = volume). Works in Home, scenes, Siri ("set Bathroom Volume to 30%").
  - Sonos favorites (radio, playlists) → scripts shown as switches.
- Sonos joined CSA (Matter) but no Matter product support announced.

**Dreame X50 Ultra Complete**
- Native Matter confirmed for this model ([Apfeltalk](https://www.apfeltalk.de/magazin/news/endlich-matter-bei-dreame-so-bringst-du-den-x50-ultra-complete-ins-apple-home/)). Firmware ≥ 4.3.9_3276 (user report). Rolled out in waves.
- Update firmware in Dreamehome app → Matter option appears → Home app → Add accessory.
- Reported issue: QR scan fails; enter Matter PIN manually ([labomaison](https://labomaison.com/entretien/aspirateur-robot/dreame-matter-apple-maison-aspirateur-robot/)).
- Matter exposes only start/stop/pause/dock (~4 entities vs ~200 via cloud).
- Gap filler (B5): HA `dreame_vacuum` (Tasshack, HACS, cloud mode) → per-room clean, suction, mop mode as scripts/switches via HomeKit Bridge. Native vacuum tile stays Matter.
- Fallback if OTA missing: HA `dreame_vacuum` (Tasshack, HACS) → Matterbridge (separate instance, vacuum alone; Apple requires standalone RVC node). Verify X50 model ID in integration list first.

**Xiaomi Smart Air Purifier 4 Compact**
- Model `xiaomi.airp.cpa4`. Use `xiaomi_miot` (HACS); `xiaomi_home` (official) as alternative.
- Known gap: no fan speed entity. Fix: `xiaomi_miot.set_miot_property` (siid 9 / piid 11 reported, [forum](https://community.home-assistant.io/t/mi-air-purifier-4-compact/487880?page=2)); verify on unit, then wrap in template fan (B6).
- HomeKit Bridge exposes as air purifier: on/off, speed, auto mode, PM2.5/air quality, filter life (model-dependent).
- Caveat: HA + purifier on same subnet/VLAN for local mode.

**Neakasa**
- No official API, no Matter. Community integrations exist ([forum](https://community.home-assistant.io/t/neakasa-m1-integration/738783)):
  - [`roquerodrigo/ha-neakasa-litterbox`](https://github.com/roquerodrigo/ha-neakasa-litterbox): cloud MQTT push, sand level, visits, "Clean now". **Preferred.**
  - [`tabascoz/hass-neakasa`](https://github.com/tabascoz/hass-neakasa): maintained fork of original `timniklas`; switches (child lock, auto-level, silent mode).
- Built mapping ([`neakasa_homekit.yaml`](../homeassistant/packages/neakasa_homekit.yaml)): bin full → problem sensor (Home notification), cat present → occupancy, visits → sensor, clean → switch.
- Caveat: one login per Neakasa account → create second Neakasa account, share device to it, use that in HA.
- Cloud-dependent. Hardening build: local ESP32 firmware (ESPHome) only if cloud breaks; voids warranty.

**Petlibro Granary**
- No native HomeKit/Matter. Options: HACS [`jjjonesjr33/petlibro`](https://github.com/jjjonesjr33/petlibro) (cloud, preferred: same HA bridge) or [`homebridge-petlibro-2`](https://cdn.jsdelivr.net/npm/homebridge-petlibro-2@1.5.2/README.md).
- Built mapping ([`petlibro_homekit.yaml`](../homeassistant/packages/petlibro_homekit.yaml)): "Feed now" switch, food low + dispenser blocked → problem sensors (Home notifications). Schedules stay in Petlibro app.
- Use secondary Petlibro account (shared device) for HA.

**Petcube**
- No HomeKit, Matter, RTSP or public API. Cloud host `api.petcube.com`. Only HA code found: [`lyntoo/petcube-ha`](https://github.com/lyntoo/petcube-ha) (Bites treat dispenser, no video).
- Build: see [Build plan](#build-plan) B1. Phased; stream extraction is the hard part.
- Interim: Petcube app for live view; Home gets nothing until B1 phase 2.

## Dashboard & remote access

Goal: one dashboard on iPad controlling everything, reachable remotely from every approved device.

**Primary: Apple Home app** (iPad, iPhone, Mac, HomeView).
- Every device lands in Home: native (Hue, HomePod, Dreame Matter, BRAVIA TV, Sonos AirPlay) + HA HomeKit Bridge (purifier, Neakasa, Petlibro, Sonos volume/favorites, Dreame rooms).
- Remote access: automatic through the home hub (HomePod; HomeView/Apple TV later). No port forwarding.
- Approved people: Home → Home Settings → People → Invite (Apple Account). Per-person remote access + edit rights.
- iPad as wall/counter panel: Home app full screen, lock with Guided Access (Settings → Accessibility → Guided Access), Auto-Lock off, keep charging.

**Secondary: Home Assistant dashboard** for what Home can't show (Dreame map, Petcube extras, history).
- HA Companion app on iPad/iPhone, or browser.
- Remote: Tailscale add-on (WireGuard mesh, no open ports), devices joined to the user's tailnet. Not installed yet.

## Recommended architecture

```
                 ┌─────────── Apple Home (iPhone, HomeView, Siri) ───────────┐
                 │  Hub: HomePod / Apple TV 4K / HomeView (Thread BR)        │
                 └───┬─────────────┬──────────────┬──────────────┬──────────┘
                HomeKit         Matter          AirPlay 2     HomeKit Bridge
                    │              │                │              │
               Hue Bridge      Dreame X50        Sonos      Home Assistant
              (lamps, plugs)                                (VM on home laptop)
                                                              ├─ Xiaomi purifier
                                                              ├─ Neakasa
                                                              └─ Petlibro feeder
   HomePod sensors: native            Petcube: own app (or replace with HKSV cam)
```

Principle: native first, HA only for gaps. One bridge, one place for credentials.

Host: **user's laptop, always on at home** (decided 2026-10-22, replaces Mac).
- macOS: Home Assistant OS in **UTM** VM, bridged network. Windows: HA OS in Hyper-V/VirtualBox VM, bridged. Linux: HA OS in KVM, bridged. Never Docker Desktop (no host networking → HomeKit discovery fails).
- Scrypted native on host OS (Petcube video → HKSV).
- Laptop-as-server: power connected, sleep disabled (incl. lid closed), Ethernet preferred, VM auto-start at login, auto-login after power loss. Bridge goes offline whenever laptop leaves home.
- Same subnet as HomePod.

## Setup steps

1. **Apple Home baseline**
   - Confirm new Home architecture.
   - Set hub: Home Settings → Home Hubs & Bridges. Prefer wired Apple TV or HomePod; add HomeView after 2026-11-13.
2. **Native devices**
   - Hue: Home → Add accessory → scan Hue Bridge code. Assign rooms.
   - Sonos: Home → Add accessory → each speaker (AirPlay). Assign rooms.
   - Dreame: update firmware → enable Matter in Dreamehome → Home → Add accessory → manual code if QR fails.
3. **Home Assistant**
   - Install hypervisor on laptop (UTM on macOS) → create VM from HA OS image (bridged network, 2 vCPU, 4 GB RAM, 32 GB disk) → onboard at `http://homeassistant.local:8123`. DHCP reservation for VM MAC.
   - Install Scrypted on laptop OS (for B1 phase 4).
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

## Build plan

Rule: no device left out. Order = value × feasibility.

| # | Build | What | Status | Needs from you |
|---|---|---|---|---|
| B1 | **Petcube HA integration** | Custom component `petcube`: login, devices, status, night vision, treat/laser. Then camera entity with stream | To build | Petcube account (2nd account w/ shared device), one traffic capture session |
| B2 | Sonos Home accessories | Template volume/group/favorites | Done ([yaml](../homeassistant/packages/sonos_homekit.yaml)) | Entity IDs, favorite names |
| B3 | Neakasa Home mapping | Template sensors/switch on community integration | Done ([yaml](../homeassistant/packages/neakasa_homekit.yaml)) | 2nd Neakasa account |
| B4 | HomeKit Bridge config | Single bridge, strict include filter | Done ([yaml](../homeassistant/packages/homekit_bridge.yaml)) | None |
| B5 | Dreame rooms/modes | `dreame_vacuum` → room-clean + suction/mop scripts → HomeKit Bridge (Matter covers basics only) | Done + deployed ([yaml](../homeassistant/packages/dreame_homekit.yaml)), 6 rooms, CleanGenius modes | Dreame account, room names |
| B7 | Petlibro feeder | Template mapping on community integration | Done + deployed ([yaml](../homeassistant/packages/petlibro_homekit.yaml)) | Model, 2nd Petlibro account |
| B6 | Purifier fan speed | Template fan wrapping `set_miot_property` | Done ([yaml](../homeassistant/packages/xiaomi_purifier_homekit.yaml)), siid/piid + max level TBC on unit | Confirm siid/piid on unit |

### B1 Petcube: phases

1. **API capture** ([tool](../tools/petcube/README.md)): mitmproxy on iPhone (or Android emulator if cert pinning) while using Petcube app. Record auth, device list, commands, stream negotiation.
2. **Control integration**: Python `custom_components/petcube` (config flow, coordinator polling `api.petcube.com`). Entities: online, night vision switch, laser/treat buttons, motion/sound events. → HomeKit Bridge.
3. **Video**: identify stream transport (likely WebRTC/proprietary relay). Implement in go2rtc source (`exec:` wrapper or native WebRTC client) → HA `camera` entity.
4. **HomeKit camera**: Scrypted (HA add-on) imports go2rtc stream → HomeKit Secure Video (motion, recordings in iCloud+). Visible on HomeView, iPhone, Apple TV.
5. **Publish**: HACS repo, tests, ChangeLog.

Risks: cert pinning (→ Frida/emulator), proprietary video codec relay (→ largest effort), ToS. Fallback if phase 3 blocked after time-box: control-only integration + HKSV camera aimed at same area.

## Risks

- Dreame Matter OTA rollout per region/model: unverified for exact unit.
- Neakasa/Petcube: vendor clouds, unofficial APIs. Can break on app updates → pin versions, monitor.
- HomeKit Bridge pairing breaks if HA IP changes or mDNS blocked (VLAN, mesh Wi-Fi isolation).
- Duplicates if a device is both native and bridged → strict HA include filter.

## Decisions needed

- Laptop OS + CPU (Apple Silicon/Intel/AMD).
- Create secondary Petcube + Neakasa + Petlibro accounts (share devices) for HA.
- Schedule Petcube capture session (B1 phase 1).

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
