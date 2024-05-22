import os
from http.server import BaseHTTPRequestHandler, HTTPServer
import urllib.parse

from label import print_label

class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        # Parse the URL and the query parameters
        url_path = urllib.parse.urlparse(self.path)
        if url_path.path == "/label":
            query_params = dict(urllib.parse.parse_qsl(url_path.query))
            wifi = None
            text = None
            if "ssid" in query_params or "psk" in query_params:
                if "ssid" not in query_params or "psk" not in query_params:
                    self.send_error(400, "Missing parameter: ssid or psk")
                    return
                wifi = {
                    "ssid": query_params["ssid"],
                    "psk": query_params["psk"]
                }
            elif "text" not in query_params:
                self.send_error(400, "Missing parameter: text")
                return
            if "text" in query_params:
                text = query_params["text"]
            if "count" not in query_params:
                count = 1
            else:
                count = int(query_params["count"])
            try:
                print_label(text, wifi, count)
            except Exception as e:
                self.send_error(500, str(e))
                raise e
            self.send_response(200)
            self.end_headers()
        else:
            self.send_error(404, "File not found.")

if __name__ == "__main__":
    port = int(os.environ["PORT_LABEL"])
    webServer = HTTPServer(("0.0.0.0", port), SimpleHTTPRequestHandler)
    print("Server started http://localhost:" + str(port))

    try:
        webServer.serve_forever()
    except KeyboardInterrupt:
        pass

    webServer.server_close()
    print("Server stopped.")
