"""mitmproxy addon: log Petcube app traffic for B1 (API reverse engineering).

Usage:
    mitmdump -s tools/petcube/capture_addon.py --set petcube_out=petcube_capture.jsonl

Writes one JSON line per request/response to Petcube hosts.
Secrets (auth headers, passwords, tokens) are redacted unless --set petcube_raw=true.
Never commit raw captures.
"""

import json
import re
from pathlib import Path

from mitmproxy import ctx, http

HOST_RE = re.compile(r"(^|\.)petcube\.(com|io|net)$")
SECRET_HEADERS = {"authorization", "cookie", "set-cookie", "x-auth-token"}
SECRET_KEYS = re.compile(r"pass(word)?|token|secret|session", re.I)


def _redact(obj):
    if isinstance(obj, dict):
        return {k: "<redacted>" if SECRET_KEYS.search(k) else _redact(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_redact(v) for v in obj]
    return obj


def _body(message, raw):
    if not message or not message.content:
        return None
    try:
        data = json.loads(message.get_text(strict=False))
    except (ValueError, TypeError):
        return f"<{len(message.content)} bytes {message.headers.get('content-type', '')}>"
    return data if raw else _redact(data)


def _ws_text(text, raw):
    if raw:
        return text
    try:
        return _redact(json.loads(text))
    except ValueError:
        return f"<{len(text)} chars non-JSON>"


def _headers(headers, raw):
    return {k: v if raw or k.lower() not in SECRET_HEADERS else "<redacted>" for k, v in headers.items()}


class PetcubeCapture:
    def load(self, loader):
        loader.add_option("petcube_out", str, "petcube_capture.jsonl", "Output JSONL path")
        loader.add_option("petcube_raw", bool, False, "Keep secrets (local use only)")

    def _write(self, entry):
        with Path(ctx.options.petcube_out).open("a") as f:
            f.write(json.dumps(entry) + "\n")

    def tls_failed_client(self, data):
        # App rejected the mitm certificate: sign of certificate pinning.
        self._write({"tls_failed": data.context.server.sni or str(data.context.server.address)})

    def response(self, flow: http.HTTPFlow):
        if not HOST_RE.search(flow.request.pretty_host):
            # Other hosts (stream relays, CDNs, analytics): host + path only, no bodies.
            self._write({"ts": flow.request.timestamp_start, "other": flow.request.pretty_host,
                         "method": flow.request.method, "path": flow.request.path.split("?")[0],
                         "status": flow.response.status_code if flow.response else None})
            return
        raw = ctx.options.petcube_raw
        entry = {
            "ts": flow.request.timestamp_start,
            "method": flow.request.method,
            "url": flow.request.pretty_url,
            "req_headers": _headers(flow.request.headers, raw),
            "req_body": _body(flow.request, raw),
            "status": flow.response.status_code if flow.response else None,
            "resp_body": _body(flow.response, raw),
        }
        with Path(ctx.options.petcube_out).open("a") as f:
            f.write(json.dumps(entry) + "\n")

    def websocket_message(self, flow: http.HTTPFlow):
        if not HOST_RE.search(flow.request.pretty_host):
            return
        msg = flow.websocket.messages[-1]
        with Path(ctx.options.petcube_out).open("a") as f:
            f.write(json.dumps({
                "ts": msg.timestamp,
                "ws": flow.request.pretty_url,
                "from_client": msg.from_client,
                "data": _ws_text(msg.text, ctx.options.petcube_raw) if msg.is_text else f"<{len(msg.content)} bytes>",
            }) + "\n")


addons = [PetcubeCapture()]
