import bpy
from bpy.app.handlers import persistent


class _State:
    dirty = False
    revision = 0


@persistent
def _mark_dirty(_filepath):
    _State.dirty = True
    _State.revision += 1


def take_dirty():
    was_dirty, _State.dirty = _State.dirty, False
    return was_dirty


def revision():
    return _State.revision


def register():
    for handlers in (bpy.app.handlers.save_post, bpy.app.handlers.load_post):
        if _mark_dirty not in handlers:
            handlers.append(_mark_dirty)


def unregister():
    for handlers in (bpy.app.handlers.save_post, bpy.app.handlers.load_post):
        if _mark_dirty in handlers:
            handlers.remove(_mark_dirty)
