import socket
from typing import ClassVar

import bpy

from ..scene import armatures, blend_file, changes
from . import protocol

HOST = "127.0.0.1"
PORT = 7417
TICK_SECONDS = 0.1

_SUBSCRIPTIONS = {
    "subscribe_armatures": lambda: {"armatures": armatures.armature_names()},
}


class _Subscription:
    def __init__(self, filepath):
        self.filepath = filepath
        self.pending = True
        self.busy_sent = False
        self.last_sent = None


class _Client:
    def __init__(self, sock):
        self.sock = sock
        self.inbox = b""
        self.outbox = b""
        self.subscriptions: dict[str, _Subscription] = {}


class _State:
    server: ClassVar[socket.socket | None] = None
    clients: ClassVar[list[_Client]] = []


def start():
    if _State.server is not None:
        return
    try:
        server = socket.create_server((HOST, PORT))
    except OSError as exc:
        print(f"Model Meta Bridge: not listening on {HOST}:{PORT}: {exc}")
        return
    server.setblocking(False)
    _State.server = server
    bpy.app.timers.register(_tick, persistent=True)


def stop():
    if bpy.app.timers.is_registered(_tick):
        bpy.app.timers.unregister(_tick)
    for client in _State.clients:
        client.sock.close()
    _State.clients.clear()
    if _State.server is not None:
        _State.server.close()
        _State.server = None


def _tick():
    _accept()
    for client in list(_State.clients):
        _receive(client)
    if changes.take_dirty():
        _file_changed()
    _answer_pending()
    for client in list(_State.clients):
        _flush(client)
    return TICK_SECONDS


def _accept():
    while True:
        try:
            sock, _ = _State.server.accept()
        except BlockingIOError:
            return
        sock.setblocking(False)
        _State.clients.append(_Client(sock))


def _receive(client):
    try:
        data = client.sock.recv(4096)
    except BlockingIOError:
        return
    except OSError:
        _drop(client)
        return
    if not data:
        _drop(client)
        return
    *lines, client.inbox = (client.inbox + data).split(b"\n")
    for line in lines:
        request, problem = protocol.parse_request(line, _HANDLERS)
        if problem is not None:
            client.outbox += protocol.error(problem)
        else:
            _HANDLERS[request["type"]](client, request)


def _get_filepath(client, _request):
    client.outbox += protocol.success({"filepath": blend_file.blend_filepath()})


def _subscribe(client, request):
    client.subscriptions[request["type"]] = _Subscription(blend_file.blend_filepath())


_HANDLERS = {
    "get_filepath": _get_filepath,
    **{kind: _subscribe for kind in _SUBSCRIPTIONS},
}


def _file_changed():
    path = blend_file.blend_filepath()
    for client in _State.clients:
        ended = [
            kind for kind, sub in client.subscriptions.items() if sub.filepath != path
        ]
        for kind in ended:
            del client.subscriptions[kind]
        for sub in client.subscriptions.values():
            sub.pending = True
        if ended:
            client.outbox += protocol.success({"filepath": path})


def _answer_pending():
    waiting = [
        (client, kind, sub)
        for client in _State.clients
        for kind, sub in client.subscriptions.items()
        if sub.pending
    ]
    if not waiting:
        return
    if bpy.context.window_manager.is_interface_locked:
        _send_busy(waiting)
        return
    answers = {}
    for client, kind, sub in waiting:
        if kind not in answers:
            answers[kind] = _query(kind)
        result, problem = answers[kind]
        if problem is not None:
            client.outbox += protocol.error(problem)
        elif result != sub.last_sent or sub.busy_sent:
            client.outbox += protocol.success(result)
            sub.last_sent = result
        sub.pending = sub.busy_sent = False


def _send_busy(waiting):
    # "busy" names no subscription, so a client hears it once however many are waiting.
    told = set()
    for client, _kind, sub in waiting:
        if not sub.busy_sent and client not in told:
            client.outbox += protocol.error("busy")
            told.add(client)
        sub.busy_sent = True


def _query(kind):
    try:
        return _SUBSCRIPTIONS[kind](), None
    except Exception as exc:  # noqa: BLE001 - sent to the client as "query failed"
        return None, f"query failed: {exc}"


def _flush(client):
    if not client.outbox:
        return
    try:
        sent = client.sock.send(client.outbox)
    except BlockingIOError:
        return
    except OSError:
        _drop(client)
        return
    client.outbox = client.outbox[sent:]


def _drop(client):
    client.sock.close()
    _State.clients.remove(client)
