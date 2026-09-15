import json
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
from search import search


class Handler(BaseHTTPRequestHandler):
    def _set_headers(self, status_code=200, content_type="application/json"):
        """Устанавливает заголовки ответа"""
        self.send_response(status_code)
        self.send_header("Content-Type", content_type)
        self.end_headers()

    def _send_json_response(self, data, status_code=200):
        """Отправляет JSON ответ"""
        self._set_headers(status_code)
        if data is not None:
            self.wfile.write(json.dumps(data, ensure_ascii=False, indent=2).encode("utf-8"))

    def _send_error(self, status_code, message):
        """Отправляет ошибку"""
        self._send_json_response({"error": message}, status_code)

    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path != "/search":
            self._send_error(status_code=404, message="not found\n")
            return

        params = parse_qs(parsed.query)
        query = params.get("q", [""])[0].strip()
        if not query:
            self._send_error(status_code=400, message="empty query\n")
            return

        results = search(query)
        self._send_json_response(data={"query": query, "results": results}, status_code=200)

    def log_message(self, format, *args):
        pass


def run_server(host="127.0.0.1", port=8000):
    """Запускает HTTP сервер"""
    server_address = (host, port)
    httpd = HTTPServer(server_address, Handler)

    print(f"Server started at http://{host}:{port}")
    print("Endpoints:")
    print("  GET  /search?q=query - search for query")
    print("Press Ctrl+C to stop the server")

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped")
        httpd.server_close()