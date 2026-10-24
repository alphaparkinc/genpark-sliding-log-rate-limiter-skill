"""MCP Stdio Server for Sliding Log Rate Limiter.
100% Python Standard Library.
"""
import sys
import json
from client import SlidingLogRateLimiter

limiter = SlidingLogRateLimiter()

def handle_rpc(line):
    try:
        req = json.loads(line)
    except Exception:
        return
    req_id = req.get("id")
    method = req.get("method")
    params = req.get("params", {})

    if method == "initialize":
        res = {
            "protocolVersion": "2024-11-05",
            "serverInfo": {"name": "genpark-sliding-log-rate-limiter-skill", "version": "1.0.1"},
            "capabilities": {"tools": {}}
        }
        send_response(req_id, res)
    elif method == "tools/list":
        tools = [
            {
                "name": "allow_request",
                "description": "Evaluate if request is permitted under sliding window log constraints",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "client_id": {"type": "string"},
                        "max_requests": {"type": "integer", "default": 60},
                        "window_seconds": {"type": "number", "default": 60.0}
                    },
                    "required": ["client_id"]
                }
            },
            {
                "name": "get_rate_status",
                "description": "Query client rate limit utilization and remaining quota without incrementing count",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "client_id": {"type": "string"},
                        "max_requests": {"type": "integer", "default": 60},
                        "window_seconds": {"type": "number", "default": 60.0}
                    },
                    "required": ["client_id"]
                }
            },
            {
                "name": "reset_rate_log",
                "description": "Clear all logged request timestamps for a client",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "client_id": {"type": "string"}
                    },
                    "required": ["client_id"]
                }
            }
        ]
        send_response(req_id, {"tools": tools})
    elif method == "tools/call":
        name = params.get("name")
        args = params.get("arguments", {})
        if name == "allow_request":
            out = limiter.allow_request(args.get("client_id", ""), int(args.get("max_requests", 60)), float(args.get("window_seconds", 60.0)))
        elif name == "get_rate_status":
            out = limiter.get_rate_status(args.get("client_id", ""), int(args.get("max_requests", 60)), float(args.get("window_seconds", 60.0)))
        elif name == "reset_rate_log":
            out = limiter.reset_rate_log(args.get("client_id", ""))
        else:
            send_error(req_id, -32601, f"Unknown tool: {name}")
            return
        send_response(req_id, {"content": [{"type": "text", "text": json.dumps(out, indent=2)}]})

def send_response(req_id, result):
    sys.stdout.write(json.dumps({"jsonrpc": "2.0", "id": req_id, "result": result}) + "\n")
    sys.stdout.flush()

def send_error(req_id, code, message):
    sys.stdout.write(json.dumps({"jsonrpc": "2.0", "id": req_id, "error": {"code": code, "message": message}}) + "\n")
    sys.stdout.flush()

def main():
    for line in sys.stdin:
        if line.strip():
            handle_rpc(line.strip())

if __name__ == "__main__":
    main()
