import json

VERSION = 1


def success(result):
    return _encode({"status": "success", "result": result})


def error(message):
    return _encode({"status": "error", "message": message})


def _encode(body):
    line = json.dumps({"protocol": VERSION, **body}, separators=(",", ":"))
    return (line + "\n").encode()


def parse_request(line, known_types):
    """Return (the request dict, None) if valid, else (None, the error message to send)."""
    try:
        request = json.loads(line)
    except ValueError:
        return None, "invalid JSON"
    if not isinstance(request, dict):
        return None, "invalid JSON"
    version = request.get("protocol")
    if isinstance(version, bool) or version != VERSION:  # bool is an int
        return None, f"unsupported protocol: {json.dumps(version)}"
    kind = request.get("type")
    if not isinstance(kind, str) or kind not in known_types:
        return None, f"unknown type: {json.dumps(kind)}"
    return request, None
