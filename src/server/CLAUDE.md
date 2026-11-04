# `server/`

Serves the protocol in `src/CLAUDE.md` over TCP, without threads.

- `protocol.py`: builds outgoing lines (`success(result)`, `error(message)`) and checks incoming
  ones (`parse_request(line, known_types)`, which returns the whole request dict so handlers can read
  its parameters). Pure JSON; no `bpy`, no sockets.
- `listener.py`: `start()` opens a non-blocking listening socket and registers `_tick` as a
  persistent `bpy.app.timers` callback every 0.1 s; `stop()` unregisters it and closes every socket.
  `_HANDLERS` maps each request type to its handler and is the list `parse_request` accepts.
  `_SUBSCRIPTIONS` maps each subscribe type to the query that builds its `result`. A new
  subscription is one entry there; it gets a handler automatically.

## How a tick works

Accept new clients, read complete lines, handle a save/load if `scene.changes` saw one, answer
pending clients, write what each socket will take, drop closed ones.

- `get_filepath` is answered as soon as its line is read, so it never waits behind a subscription.
- Each client holds one `_Subscription` per subscribe type: the file it subscribed on, `pending`,
  `busy_sent` and `last_sent`. Subscribing again replaces it, so the next answer is always sent.
- On a save/load, a subscription still on the file it subscribed on is marked pending. Ones on a
  different file are removed, and the client gets the new path once, never their results.
- Each query runs at most once per tick, shared by every client waiting on it. A result is sent only
  if it differs from that subscription's `last_sent`.
- While `is_interface_locked`, pending subscriptions stay pending and a client gets one `busy` error
  however many are waiting. When it unlocks they get their results, even if unchanged.
- Never block: every socket call is non-blocking and `BlockingIOError` means "try next tick".
