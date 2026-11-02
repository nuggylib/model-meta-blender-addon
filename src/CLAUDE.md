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
