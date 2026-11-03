import json

VERSION = 1


REQUEST_TYPES = ("get_filepath", "subscribe_armatures")


def filepath(path):
    return _encode({"status": "success", "result": {"filepath": path}})


def success(names):
    return _encode({"status": "success", "result": {"armatures": names}})


def error(message):
    return _encode({"status": "error", "message": message})


def _encode(body):
    line = json.dumps({"protocol": VERSION, **body}, separators=(",", ":"))
    return (line + "\n").encode()


def parse_request(line):
    """Return (type, None) for a valid request, else (None, the error message to send)."""
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
    if kind not in REQUEST_TYPES:
        return None, f"unknown type: {json.dumps(kind)}"
    return kind, None
