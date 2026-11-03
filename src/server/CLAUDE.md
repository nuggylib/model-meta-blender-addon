# `server/`

Serves the protocol in `src/CLAUDE.md` over TCP, without threads.

- `protocol.py`: builds outgoing lines (`filepath`, `success`, `error`) and checks incoming ones
  (`parse_request`, which returns the request type). Pure JSON; no `bpy`, no sockets.
- `listener.py`: `start()` opens a non-blocking listening socket and registers `_tick` as a
  persistent `bpy.app.timers` callback every 0.1 s; `stop()` unregisters it and closes every socket.

## How a tick works

Accept new clients, read complete lines, handle a save/load if `scene.changes` saw one, answer
pending clients, write what each socket will take, drop closed ones.

- `get_filepath` is answered as soon as its line is read, so it never waits behind armatures.
- On a save/load, a subscriber still on the file it subscribed on (`subscribed_filepath`) is marked
  pending. One on a different file gets the new path and is unsubscribed, never names.
- Each client keeps its own `last_sent`; a change is sent only if it differs from that.
- While `is_interface_locked`, pending clients get one `busy` error and stay pending. When it unlocks
  they get the names, even if unchanged.
- Never block: every socket call is non-blocking and `BlockingIOError` means "try next tick".
