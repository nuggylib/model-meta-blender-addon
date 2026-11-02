import bpy
from bpy.app.handlers import persistent

_dirty = False


@persistent
def _mark_dirty(_filepath):
    global _dirty
    _dirty = True


def take_dirty():
    global _dirty
    was_dirty, _dirty = _dirty, False
    return was_dirty


def register():
    for handlers in (bpy.app.handlers.save_post, bpy.app.handlers.load_post):
        if _mark_dirty not in handlers:
            handlers.append(_mark_dirty)


def unregister():
    for handlers in (bpy.app.handlers.save_post, bpy.app.handlers.load_post):
        if _mark_dirty in handlers:
            handlers.remove(_mark_dirty)
