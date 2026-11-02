# `scene/`

Reads Blender's scene and tracks when it may have changed. Read-only: nothing here modifies `bpy` data.

- `armatures.py`: `armature_names()` lists `ARMATURE` objects linked to the active scene
  (`bpy.context.scene.objects`, not `bpy.data.objects`, so objects outside the scene are left out).
- `changes.py`: `save_post` / `load_post` handlers that only set a dirty flag. `take_dirty()` returns
  and clears it. Handlers are `@persistent` so they survive file loads.
