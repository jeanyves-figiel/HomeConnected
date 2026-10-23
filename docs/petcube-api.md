# Petcube API findings (B1 phase 1)

Capture: 2026-10-22, iPhone Petcube app via mitmproxy (redacted mode). Raw capture kept off-repo.
Scope (user): **live view only, plus pan/tilt**. Night vision, laser, treats, events out of scope.

## Device

| Field | Value |
|---|---|
| Model | Petcube Cam 360 (`device_type` / `device_subtype` = `Petcube Cam PTZ`) |
| Firmware | `soft_ver` 6.3.9.2277, board `prod_rev` 6.10.7 |
| `streaming_mode` | `["ptcb"]` (proprietary Petcube transport) |
| `capabilities` | `ptt` (push-to-talk), `camera_rotation` (pan/tilt) |
| Plan | "Live Video Streaming" (active), no video history |

## REST API (`https://api.petcube.com/api/v1`)

- No certificate pinning: app traffic decrypts with a user-trusted CA.
- Auth: bearer access token + `POST /token/refresh` (refresh token). Tokens redacted.
- Useful endpoints:
  - `GET /users/{user_id}/petcubes`: device list (id, type, capabilities, `streaming_mode`, firmware).
  - `GET /care/petcubes`: subscription + device status (`status.version`).
  - `GET /config/common`: streaming parameters (below).
  - `GET /user/profile`, `/user/settings`, `/user/app4/settings`, `/subscriptions`.
- Other Petcube hosts: `mmetrics.petcube.com` (metrics), `logs.petcube.com` (app logs), `trckr.petcube.com` (device auth/tracking), `petcube.com/home/...` (web views).

## Live stream: how it is negotiated

- While live view ran (~30 s), and while the camera was moved, the app made **no HTTP(S) calls** except metrics.
  Stream setup, media, and pan/tilt commands use a non-HTTP channel (raw TCP/UDP sockets), which an HTTP proxy cannot see.
- `GET /config/common` → `data.calls` describes a call-style session with three paths:
  `bandwidthEstimations.p2p`, `.nat`, `.relay` (direct, NAT-traversed, relayed), adaptive bitrate (min 100 kbit/s, initial 1.2 Mbit/s).
- `data.videobitrates.h264["Petcube Cam"]`: H.264, 1920×1080 @ 30 fps (≥ 1.3 Mbit/s) or 1280×720 @ 30 fps.
- Inference: ICE-like peer-to-peer session with relay fallback, signalled over Petcube's own protocol (`ptcb`). Not standard RTSP/HLS.

## Local network

- LAN scan (2026-10-22): no host exposes RTSP (554/8554), RTMP (1935) or ONVIF (8000/8899). The camera offers no local stream.

## Feasibility of live view in Apple Home (phase 3)

| Option | Effort | Risk |
|---|---|---|
| A. Reverse `ptcb` (decompile Android APK with jadx, then Frida if obfuscated): signalling host, auth, ICE/relay, media framing, PTZ messages. Then go2rtc source → Scrypted → HomeKit camera; PTZ presets as bridge switches | High (weeks) | Breaks on app/firmware updates; ToS |
| B. Replace with a HomeKit Secure Video PTZ camera (e.g. Aqara Camera Hub G3/G5 Pro, Eve Cam (fixed)) | Low | Hardware cost |
| C. Keep Petcube app for live view, add a Home shortcut/tile that opens the app | None | Not inside Home |

Next step if A: static analysis of the Android APK (no device traffic needed) to locate the `ptcb` client and its signalling endpoint.
