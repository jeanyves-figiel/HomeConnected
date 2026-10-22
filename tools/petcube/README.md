# Petcube capture (B1 phase 1)

Goal: learn Petcube app API (auth, devices, commands, stream setup) to build `custom_components/petcube`.

1. On laptop: `pipx install mitmproxy` (or `brew install mitmproxy`).
2. `mitmdump -s tools/petcube/capture_addon.py --set petcube_out=petcube_capture.jsonl`
3. iPhone: Wi-Fi → proxy → manual → laptop IP, port 8080. Open `http://mitm.it`, install profile, then Settings → General → About → Certificate Trust Settings → enable.
4. Petcube app (secondary account): log in, open live view, toggle night vision, laser, treat, browse events. ~5 min.
5. Stop mitmdump, remove iPhone proxy + profile.
6. Share redacted `petcube_capture.jsonl` (default mode redacts tokens/passwords).

If app shows no traffic or fails to connect: certificate pinning → fallback Android emulator + Frida (separate procedure).
