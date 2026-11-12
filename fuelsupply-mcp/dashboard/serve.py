"""Loopback-only FuelSupply dashboard. EIA credentials remain server-side."""

import argparse
import asyncio
import json
import logging
import sys
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from socketserver import TCPServer

ROOT = Path(__file__).resolve().parents[1]
DASHBOARD = Path(__file__).resolve().parent
SNAPSHOT = DASHBOARD / "data/snapshot.json"
ALLOWED_HISTORY = {3, 12, 26, 52}


class LocalHTTPServer(ThreadingHTTPServer):
    def server_bind(self):
        # Binding loopback needs no reverse-DNS lookup or external name service.
        TCPServer.server_bind(self)
        self.server_name = "localhost"
        self.server_port = self.server_address[1]


def save_snapshot(path, data):
    """Persist sanitized application results, never request URLs or credentials."""
    content = json.dumps(data, indent=2) + "\n"
    temp = path.with_suffix(".tmp")
    temp.write_text(content)
    temp.replace(path)
    script = path.with_suffix(".js")
    script.write_text("window.FUELSUPPLY_DATA = " + content.rstrip() + ";\n")


def retrieve(query):
    from fuelsupply.models import Query
    from fuelsupply.service import SupplyService

    result = asyncio.run(SupplyService().run(Query.model_validate(query)))
    if result.status not in {"ok", "partial"} or not result.observation_periods:
        raise ValueError("No observations retrieved")
    if any(
        "upstream" in item or "missing_credentials" in item
        for item in result.data_quality_diagnostics
    ):
        raise ValueError("Incomplete upstream retrieval")
    return {"query": query, "response": result.model_dump(mode="json")}


def create_server(port=8765, snapshot_path=SNAPSHOT, refresh=retrieve):
    lock = threading.Lock()

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *_args):
            # Suppress request paths, bodies, headers and upstream exceptions.
            pass

        def trusted_request(self):
            port = self.server.server_address[1]
            hosts = {f"127.0.0.1:{port}", f"localhost:{port}"}
            origin = self.headers.get("Origin")
            return self.headers.get("Host") in hosts and (
                origin is None or origin in {f"http://{host}" for host in hosts}
            )

        def send(self, status, payload, content_type="application/json"):
            if not isinstance(payload, bytes):
                payload = json.dumps(payload).encode()
            self.send_response(status)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(payload)))
            self.send_header("Cache-Control", "no-store")
            self.send_header("X-Content-Type-Options", "nosniff")
            self.send_header("Referrer-Policy", "no-referrer")
            self.send_header(
                "Content-Security-Policy",
                "default-src 'self'; script-src 'self' 'unsafe-inline'; "
                "style-src 'self' 'unsafe-inline'; img-src 'self' data:; "
                "connect-src 'self'; object-src 'none'; "
                "frame-ancestors 'none'; base-uri 'none'",
            )
            self.end_headers()
            self.wfile.write(payload)

        def do_GET(self):
            if not self.trusted_request():
                self.send(403, {"error": "Local requests only"})
                return
            files = {
                "/": (DASHBOARD / "index.html", "text/html; charset=utf-8"),
                "/styles.css": (DASHBOARD / "styles.css", "text/css"),
                "/app.js": (DASHBOARD / "app.js", "text/javascript"),
                "/data/snapshot.js": (
                    snapshot_path.with_suffix(".js"),
                    "text/javascript",
                ),
                "/api/snapshot": (snapshot_path, "application/json"),
            }
            selected = files.get(self.path)
            if not selected:
                self.send(404, {"error": "Not found"})
                return
            try:
                self.send(200, selected[0].read_bytes(), selected[1])
            except OSError:
                self.send(503, {"error": "Saved snapshot unavailable"})

        def do_POST(self):
            if not self.trusted_request():
                self.send(403, {"error": "Local requests only"})
                return
            if self.path != "/api/refresh":
                self.send(404, {"error": "Not found"})
                return
            if self.headers.get("Content-Type", "").split(";")[0] != "application/json":
                self.send(415, {"error": "JSON required"})
                return
            try:
                length = int(self.headers.get("Content-Length", "0"))
                if not 0 < length <= 2048:
                    raise ValueError()
                query = json.loads(self.rfile.read(length))
                if not isinstance(query, dict) or set(query) != {
                    "fuel",
                    "geography",
                    "frequency",
                    "lookback_periods",
                }:
                    raise ValueError()
                history = query["lookback_periods"]
                if type(history) is not int or history not in ALLOWED_HISTORY:
                    raise ValueError()
                snapshot = json.loads(snapshot_path.read_text())
                allowed = {
                    (
                        c["query"]["fuel"],
                        c["query"]["geography"],
                        c["query"]["frequency"],
                    )
                    for c in snapshot["cases"]
                }
                combination = (query["fuel"], query["geography"], query["frequency"])
                if combination not in allowed:
                    raise ValueError()
            except (ValueError, TypeError, KeyError, OSError):
                self.send(
                    400, {"error": "Choose a verified combination and bounded history"}
                )
                return
            if not lock.acquire(blocking=False):
                self.send(429, {"error": "A refresh is already running; retry shortly"})
                return
            try:
                case = refresh(query)
                # Re-read after retrieval so another completed refresh is preserved.
                snapshot = json.loads(snapshot_path.read_text())
                for index, existing in enumerate(snapshot["cases"]):
                    q = existing["query"]
                    if (q["fuel"], q["geography"], q["frequency"]) == combination:
                        snapshot["cases"][index] = case
                        break
                save_snapshot(snapshot_path, snapshot)
                self.send(200, {"case": case})
            except Exception:
                self.send(
                    502,
                    {
                        "error": (
                            "EIA refresh unavailable; saved data retained. "
                            "Check the local key or retry later."
                        )
                    },
                )
            finally:
                lock.release()

    return LocalHTTPServer(("127.0.0.1", port), Handler)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--port", type=int, default=8765)
    args = parser.parse_args()
    sys.path.insert(0, str(ROOT / "src"))
    from dotenv import load_dotenv

    # Explicit opt-in local launcher; the MCP server's credential behavior is unchanged.
    load_dotenv(ROOT / ".env", override=False)
    logging.getLogger("httpx").setLevel(logging.CRITICAL)
    logging.getLogger("httpcore").setLevel(logging.CRITICAL)
    if not SNAPSHOT.is_file():
        raise SystemExit("Saved snapshot missing; restore dashboard/data/snapshot.json")
    save_snapshot(SNAPSHOT, json.loads(SNAPSHOT.read_text()))
    with create_server(args.port) as server:
        print(
            f"FuelSupply dashboard: http://127.0.0.1:{server.server_address[1]}",
            flush=True,
        )
        print("Local access only. Press Control-C to stop.", flush=True)
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            pass


if __name__ == "__main__":
    main()
