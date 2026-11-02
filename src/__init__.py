import bpy

from .scene import changes
from .server import listener


def register():
    changes.register()
    if not bpy.app.background:
        listener.start()


def unregister():
    listener.stop()
    changes.unregister()
