"""JSON API server for Next.js recommendations query."""

import sys
from http.server import HTTPServer, BaseHTTPRequestHandler
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.services.recommendation_service import create_default_service

# Load the service once on startup
service = create_default_service()


class APIHandler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        # Respond to CORS preflight options request
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS, GET")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self):
        if self.path == "/api/locations":
            try:
                unique_locations = sorted(list({r.location for r in service.repository.get_all() if r.location}))
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                self.wfile.write(json.dumps(unique_locations).encode("utf-8"))
            except Exception as e:
                self.send_response(500)
                self.send_header("Content-Type", "application/json")
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                self.wfile.write(json.dumps({"error": f"Failed to load locations: {e}"}).encode("utf-8"))
        else:
            self.send_response(404)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(json.dumps({"error": "Endpoint not found"}).encode("utf-8"))

    def do_POST(self):
        if self.path == "/api/recommend":
            content_length = int(self.headers["Content-Length"])
            body = self.rfile.read(content_length)
            try:
                raw_input = json.loads(body.decode("utf-8"))
            except Exception as e:
                self.send_response(400)
                self.send_header("Content-Type", "application/json")
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                self.wfile.write(json.dumps({"error": f"Invalid JSON body: {e}"}).encode("utf-8"))
                return

            try:
                result = service.recommend(raw_input)
                rec = result.recommendation
                
                # Format recommendations list to match data contract
                recommendations_list = []
                for item in rec.recommendations:
                    # Retrieve the location from repository if it is not present on the item (e.g. RecommendationItem)
                    loc = getattr(item, "location", None)
                    if not loc:
                        matches = service.repository.get_by_ids([item.restaurant_id])
                        loc = matches[0].location if matches else "Unknown"

                    recommendations_list.append({
                        "restaurant_id": item.restaurant_id,
                        "rank": item.rank,
                        "name": item.name,
                        "cuisines": item.cuisines,
                        "rating": item.rating,
                        "cost_for_two": item.cost_for_two,
                        "explanation": item.explanation,
                        "location": loc
                    })

                response_payload = {
                    "summary": rec.summary,
                    "recommendations": recommendations_list,
                    "degraded": rec.degraded,
                    "warnings": rec.warnings + result.messages
                }

                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                self.wfile.write(json.dumps(response_payload).encode("utf-8"))
            except Exception as e:
                self.send_response(500)
                self.send_header("Content-Type", "application/json")
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                self.wfile.write(json.dumps({"error": f"Recommendation failed: {e}"}).encode("utf-8"))
        else:
            self.send_response(404)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(json.dumps({"error": "Endpoint not found"}).encode("utf-8"))


def run(port=8000):
    server = HTTPServer(("localhost", port), APIHandler)
    print(f"API server running on http://localhost:{port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    # Standard port is 8000
    run()
