# `server/`

Serves the protocol in `src/CLAUDE.md` over TCP, without threads.

- `protocol.py`: builds outgoing lines (`success`, `error`) and checks incoming ones
  (`parse_request`). Pure JSON; no `bpy`, no sockets.
- `listener.py`: `start()` opens a non-blocking listening socket and registers `_tick` as a
  persistent `bpy.app.timers` callback every 0.1 s; `stop()` unregisters it and closes every socket.

## How a tick works

Accept new clients, read complete lines, mark subscribers pending if `scene.changes` saw a
save/load, answer pending clients, write what each socket will take, drop closed ones.

- Each client keeps its own `last_sent`; a change is sent only if it differs from that.
- While `is_interface_locked`, pending clients get one `busy` error and stay pending. When it unlocks
  they get the names, even if unchanged.
- Never block: every socket call is non-blocking and `BlockingIOError` means "try next tick".
