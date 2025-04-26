import os, json
from http.server import BaseHTTPRequestHandler, HTTPServer
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()
db = MongoClient(os.getenv("MONGODB_URI")).askademia

class Handler(BaseHTTPRequestHandler):
    def _respond(self, code=200, data=None):
        self.send_response(code)
        self.send_header('Content-Type','application/json')
        self.end_headers()
        if data:
            self.wfile.write(json.dumps(data).encode())

    def do_GET(self):
        if self.path == "/escalations":
            pending = list(db.escalations.find({"status":"pending"}, {"_id":0}))
            self._respond(200, pending)

    def do_POST(self):
        if self.path.startswith("/escalations/") and self.path.endswith("/reply"):
            esc_id = self.path.split("/")[2]
            length = int(self.headers['Content-Length'])
            data   = json.loads(self.rfile.read(length))
            db.escalations.update_one(
                {"_id": esc_id},
                {"$set": {"answer": data["answer"], "status": "answered"}}
            )
            self._respond(204)

if __name__=="__main__":
    HTTPServer(('',8000), Handler).serve_forever()