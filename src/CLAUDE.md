# `src/`

The Blender extension package. Blender loads this directory as the add-on; build it with
`blender --command extension build --source-dir src`.

- `blender_manifest.toml`: extension metadata. Its `[build]` table keeps every `CLAUDE.md` out of
  the built zip.
- `__init__.py`: `register()` / `unregister()`, called when the add-on is enabled / disabled.

## Conventions

- Relative imports only (`from . import x`); Blender extensions require it.
- Requires Blender 4.2.0 or later.
- Never modify the scene; only read it.
- No threads. All `bpy` access runs on the main thread (timers and handlers).

## Protocol

- TCP `127.0.0.1:7417`. Not listening in background mode or if the port is taken.
- One UTF-8 JSON object per line, `\n`-terminated. Every message has `"protocol": 1`.
- Request: `{"protocol":1,"type":"subscribe_armatures"}`.
- Success: `{"protocol":1,"status":"success","result":{"armatures":[...]}}`, sent on subscribe and
  after a save/load that changes the list from the last one sent on that connection.
- Error: `{"protocol":1,"status":"error","message":"..."}`. Connection stays open. Messages: `busy`
  (interface locked; sent once, names follow when it unlocks), `invalid JSON`,
  `unsupported protocol: <v>`, `unknown type: <t>`, `query failed: <detail>`.
