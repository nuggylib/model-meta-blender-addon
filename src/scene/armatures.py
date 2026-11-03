import bpy


def armature_names():
    return [o.name for o in bpy.context.scene.objects if o.type == "ARMATURE"]
