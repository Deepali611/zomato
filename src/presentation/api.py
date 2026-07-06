"""JSON API server for Next.js recommendations query."""

import sys
import os
from http.server import HTTPServer, BaseHTTPRequestHandler
import json
from urllib.parse import urlparse
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
        parsed_path = urlparse(self.path).path
        if parsed_path == "/api/locations":
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
        elif self.path in ("/", "/api", "/health", "/api/health", "/api/v1/health"):
            # Determine database status
            try:
                restaurant_count = len(service.repository.get_all())
                db_status = "loaded" if restaurant_count > 0 else "empty"
                db_message = f"{restaurant_count} restaurants loaded successfully."
            except Exception as e:
                db_status = "error"
                db_message = f"Failed to check repository: {e}"
                restaurant_count = 0

            # Determine LLM status
            api_key = service.settings.groq_api_key
            if api_key:
                masked_key = f"{api_key[:6]}...{api_key[-4:]}" if len(api_key) > 10 else "configured"
            else:
                masked_key = "not_found"

            llm_configured = service._llm_client is not None
            llm_warning = service.llm_warning

            if llm_configured and not llm_warning:
                llm_status = "healthy"
                llm_message = f"Groq LLM is configured with model '{service.settings.llm_model}'."
            else:
                llm_status = "warning"
                llm_message = llm_warning or "Groq LLM client is not initialized."

            # Determine overall status
            if db_status == "loaded" and llm_status == "healthy":
                overall_status = "healthy"
            elif db_status == "loaded":
                overall_status = "degraded"
            else:
                overall_status = "unhealthy"

            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            
            health_report = {
                "status": overall_status,
                "service": "Zomato AI Recommendation Engine API",
                "database": {
                    "status": db_status,
                    "count": restaurant_count,
                    "message": db_message
                },
                "llm": {
                    "status": llm_status,
                    "provider": service.settings.llm_provider,
                    "model": service.settings.llm_model,
                    "key_configured": api_key is not None,
                    "key_masked": masked_key,
                    "message": llm_message
                },
                "endpoints": {
                    "locations": "/api/locations",
                    "recommend": "/api/recommend (POST)"
                }
            }
            self.wfile.write(json.dumps(health_report).encode("utf-8"))
        else:
            self.send_response(404)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(json.dumps({"error": "Endpoint not found"}).encode("utf-8"))

    def do_POST(self):
        parsed_path = urlparse(self.path).path
        if parsed_path == "/api/recommend":
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


def run(host="0.0.0.0", port=8000):
    server = HTTPServer((host, port), APIHandler)
    print(f"API server running on http://{host}:{port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    # Read port from environment variable (standard for platforms like Railway)
    port_env = os.getenv("PORT", "8000")
    try:
        port = int(port_env)
    except ValueError:
        port = 8000
    run(host="0.0.0.0", port=port)
