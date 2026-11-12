import json
import threading
from http.server import HTTPServer

import pytest

import storage
import structures
from server import Handler


@pytest.fixture
def server_url():
    structures.documents.clear()
    structures.documents.update({1: "/docs/a.pdf", 2: "/docs/b.pdf"})
    structures.inverted_index.clear()
    structures.inverted_index.update({"python": {1: 2, 2: 1}})
    structures.doc_lengths.clear()
    structures.doc_lengths.update({1: 10, 2: 10})
    storage.STATUS.update(mode="file", fallback=False, reason=None)

    httpd = HTTPServer(("127.0.0.1", 0), Handler)
    thread = threading.Thread(target=httpd.serve_forever)
    thread.start()
    try:
        yield f"http://127.0.0.1:{httpd.server_port}"
    finally:
        httpd.shutdown()
        httpd.server_close()
        thread.join()


def get_json(url):
    import urllib.request

    with urllib.request.urlopen(url) as response:
        return response.status, json.loads(response.read())


def test_search_returns_results(server_url):
    status, data = get_json(f"{server_url}/search?q=python")

    assert status == 200
    assert data["query"] == "python"
    assert [item["id"] for item in data["results"]] == [1, 2]


def test_search_without_query_returns_400(server_url):
    import urllib.error

    with pytest.raises(urllib.error.HTTPError) as error:
        get_json(f"{server_url}/search?q=")

    assert error.value.code == 400


def test_unknown_path_returns_404(server_url):
    import urllib.error

    with pytest.raises(urllib.error.HTTPError) as error:
        get_json(f"{server_url}/unknown")

    assert error.value.code == 404


def test_health_reports_storage_and_counters(server_url):
    status, data = get_json(f"{server_url}/health")

    assert status == 200
    assert data["storage"] == "file"
    assert data["fallback"] is False
    assert data["documents"] == 2
    assert data["unique_words"] == 1


def test_docs_page_returns_html(server_url):
    import urllib.request

    with urllib.request.urlopen(f"{server_url}/docs") as response:
        body = response.read().decode("utf-8")

    assert response.status == 200
    assert "swagger-ui" in body


def test_openapi_spec_is_served(server_url):
    import urllib.request

    with urllib.request.urlopen(f"{server_url}/openapi.yaml") as response:
        body = response.read().decode("utf-8")

    assert response.status == 200
    assert "openapi: 3.0.3" in body


def test_run_server_stops_on_keyboard_interrupt(monkeypatch):
    import server

    class FakeHTTPServer:
        def __init__(self, address, handler):
            self.address = address
            self.closed = False

        def serve_forever(self):
            raise KeyboardInterrupt

        def server_close(self):
            self.closed = True

    monkeypatch.setattr(server, "HTTPServer", FakeHTTPServer)

    server.run_server()
