# `src/`

The Blender extension package. Blender loads this directory as the add-on; build it with
`./build.sh` from the repo root, which writes the zip to `build/`. It finds Blender via `$BLENDER`,
else Spotlight (newest copy), else `blender` on `PATH`, and checks `blender_version_min`.

- `blender_manifest.toml`: extension metadata. Its `[build]` table keeps every `CLAUDE.md` out of
  the built zip.
- `__init__.py`: `register()` / `unregister()`, called when the add-on is enabled / disabled.
- `scene/`: the read-only armature and file path queries, and the save/load dirty flag.
- `server/`: the TCP listener and protocol messages. Not started in background mode.

## Conventions

- Relative imports only (`from . import x`); Blender extensions require it.
- Requires Blender 4.2.0 or later.
- Never modify the scene; only read it.
- No threads. All `bpy` access runs on the main thread (timers and handlers).

## Protocol

- TCP `127.0.0.1:7417`. Not listening in background mode or if the port is taken.
- One UTF-8 JSON object per line, `\n`-terminated. Every message has `"protocol": 1`.
- `{"protocol":1,"type":"get_filepath"}`: answered once with
  `{"protocol":1,"status":"success","result":{"filepath":"..."}}`, the open `.blend` file's absolute
  path, or `null` if it was never saved. Send it before subscribing to confirm the right file is open.
- `{"protocol":1,"type":"subscribe_armatures"}`: answered with
  `{"protocol":1,"status":"success","result":{"armatures":[...]}}` on subscribe and after a save/load
  that changes the list from the last one sent on that connection.
- Error: `{"protocol":1,"status":"error","message":"..."}`. Connection stays open. Messages: `busy`
  (interface locked; sent once, names follow when it unlocks), `invalid JSON`,
  `unsupported protocol: <v>`, `unknown type: <t>`, `query failed: <detail>`.
