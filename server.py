import json
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path
from urllib.parse import urlparse, parse_qs
from search import search

BASE_DIR = Path(__file__).resolve().parent

SWAGGER_UI_HTML = """<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="utf-8">
<title>Поиск по PDF — API</title>
<link rel="stylesheet" href="https://unpkg.com/swagger-ui-dist@5/swagger-ui.css">
</head>
<body>
<div id="swagger-ui"></div>
<script src="https://unpkg.com/swagger-ui-dist@5/swagger-ui-bundle.js"></script>
<script>
window.ui = SwaggerUIBundle({ url: "/openapi.yaml", dom_id: "#swagger-ui" });
</script>
</body>
</html>
"""


class Handler(BaseHTTPRequestHandler):
    def _set_headers(self, status_code=200, content_type="application/json; charset=utf-8"):
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

    def _send_html(self, html, status_code=200):
        """Отправляет HTML-страницу"""
        self._set_headers(status_code, "text/html; charset=utf-8")
        self.wfile.write(html.encode("utf-8"))

    def _send_openapi(self, status_code=200):
        """Отправляет OpenAPI-спецификацию"""
        self._set_headers(status_code, "text/yaml; charset=utf-8")
        spec_path = BASE_DIR / "openapi.yaml"
        with open(spec_path, "r", encoding="utf-8") as f:
            self.wfile.write(f.read().encode("utf-8"))

    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path == "/search":
            self._handle_search(parsed)
        elif parsed.path == "/docs":
            self._send_html(SWAGGER_UI_HTML)
        elif parsed.path == "/openapi.yaml":
            self._send_openapi()
        else:
            self._send_error(status_code=404, message="not found")
            return

    def _handle_search(self, parsed):
        """Обрабатывает GET /search"""
        params = parse_qs(parsed.query)
        query = params.get("q", [""])[0].strip()
        if not query:
            self._send_error(status_code=400, message="empty query")
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
    print(f"  GET  http://{host}:{port}/docs          - Swagger UI")
    print(f"  GET  http://{host}:{port}/openapi.yaml  - OpenAPI specification")
    print("Press Ctrl+C to stop the server")

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped")
        httpd.server_close()