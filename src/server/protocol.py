import json

VERSION = 1


def success(names):
    return _encode({"status": "success", "result": {"armatures": names}})


def error(message):
    return _encode({"status": "error", "message": message})


def _encode(body):
    line = json.dumps({"protocol": VERSION, **body}, separators=(",", ":"))
    return (line + "\n").encode()


def parse_request(line):
    """Return None for a valid subscribe, else the error message to send."""
    try:
        request = json.loads(line)
    except ValueError:
        return "invalid JSON"
    if not isinstance(request, dict):
        return "invalid JSON"
    version = request.get("protocol")
    if isinstance(version, bool) or version != VERSION:  # bool is an int
        return f"unsupported protocol: {json.dumps(version)}"
    kind = request.get("type")
    if kind != "subscribe_armatures":
        return f"unknown type: {json.dumps(kind)}"
    return None
