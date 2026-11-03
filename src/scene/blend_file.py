import bpy


def blend_filepath():
    """None when the file has never been saved."""
    return bpy.data.filepath or None
