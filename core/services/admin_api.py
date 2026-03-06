"""
Aether Voice OS — Local Admin API.

Exposes a simple REST API on localhost:18790 for the Next.js Admin Dashboard.
Runs in a background thread and serves data fetched asynchronously.
"""

import json
import logging
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

logger = logging.getLogger(__name__)

# Global state updated asynchronously by the main loop
SHARED_STATE = {
    "sessions": [],
    "synapse": None,
    "system_status": "online",
    "tools": [],
    "hive": {},
    "telemetry": {},
}


class AdminAPIHandler(BaseHTTPRequestHandler):
    def end_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, OPTIONS")
        self.send_header("Content-Type", "application/json")
        super().end_headers()

    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()

    def do_GET(self):
        if self.path == "/api/sessions":
            self.send_response(200)
            self.end_headers()
            self.wfile.write(json.dumps(SHARED_STATE["sessions"], default=str).encode())
        elif self.path == "/api/synapse":
            self.send_response(200)
            self.end_headers()
            self.wfile.write(json.dumps(SHARED_STATE["synapse"], default=str).encode())
        elif self.path == "/api/status":
            self.send_response(200)
            self.end_headers()
            self.wfile.write(
                json.dumps({"status": SHARED_STATE["system_status"]}).encode()
            )
        elif self.path == "/api/tools":
            self.send_response(200)
            self.end_headers()
            self.wfile.write(json.dumps(SHARED_STATE["tools"], default=str).encode())
        elif self.path == "/api/hive":
            self.send_response(200)
            self.end_headers()
            self.wfile.write(json.dumps(SHARED_STATE["hive"], default=str).encode())
        elif self.path == "/api/telemetry":
            self.send_response(200)
            self.end_headers()
            self.wfile.write(
                json.dumps(SHARED_STATE["telemetry"], default=str).encode()
            )
        elif self.path == "/health":
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b'{"status": "pass"}')
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b'{"error": "Not found"}')

    # Disable default HTTP logging to avoid spam
    def log_message(self, format, *args):
        pass

    def address_string(self):
        """Prevent reverse DNS lookups."""
        return self.client_address[0]


class ReusableHTTPServer(HTTPServer):
    allow_reuse_address = True


class AdminAPIServer:
    def __init__(self, port: int = 18790):
        self.port = port
        self.server = None
        self.thread = None

    def start(self):
        try:
            self.server = ReusableHTTPServer(("127.0.0.1", self.port), AdminAPIHandler)
        except OSError as e:
            if e.errno == 48:
                logger.warning(
                    f"Port {self.port} occupied. Falling back to dynamic allocation."
                )
                self.server = ReusableHTTPServer(("127.0.0.1", 0), AdminAPIHandler)
                self.port = self.server.server_address[1]
            else:
                raise e

        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        logger.info(f"Admin API started on http://127.0.0.1:{self.port}")

    def stop(self):
        if self.server:
            self.server.shutdown()
            self.server.server_close()
        if self.thread:
            self.thread.join()
