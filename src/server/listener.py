import socket
from typing import ClassVar

import bpy

from ..scene import armatures, blend_file, changes
from . import protocol

HOST = "127.0.0.1"
PORT = 7417
TICK_SECONDS = 0.1


class _Client:
    def __init__(self, sock):
        self.sock = sock
        self.inbox = b""
        self.outbox = b""
        self.subscribed = False
        self.subscribed_filepath = None
        self.pending = False
        self.busy_sent = False
        self.last_sent = None


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
        kind, problem = protocol.parse_request(line)
        if problem is not None:
            client.outbox += protocol.error(problem)
        elif kind == "get_filepath":
            client.outbox += protocol.filepath(blend_file.blend_filepath())
        else:
            client.subscribed = client.pending = True
            client.subscribed_filepath = blend_file.blend_filepath()
            client.last_sent = None


def _file_changed():
    path = blend_file.blend_filepath()
    for client in _State.clients:
        if not client.subscribed:
            continue
        if path == client.subscribed_filepath:
            client.pending = True
        else:
            client.outbox += protocol.filepath(path)
            client.subscribed = client.pending = client.busy_sent = False


def _answer_pending():
    waiting = [client for client in _State.clients if client.pending]
    if not waiting:
        return
    if bpy.context.window_manager.is_interface_locked:
        for client in waiting:
            if not client.busy_sent:
                client.outbox += protocol.error("busy")
                client.busy_sent = True
        return
    try:
        names = armatures.armature_names()
    except Exception as exc:  # noqa: BLE001 - sent to the client as "query failed"
        for client in waiting:
            client.outbox += protocol.error(f"query failed: {exc}")
            client.pending = client.busy_sent = False
        return
    for client in waiting:
        if names != client.last_sent or client.busy_sent:
            client.outbox += protocol.success(names)
            client.last_sent = names
        client.pending = client.busy_sent = False


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
