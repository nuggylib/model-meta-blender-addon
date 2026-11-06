import os
import struct
from array import array

import bpy


def mesh_objects():
    """Sorted by name, so a cursor names the same mesh on every page."""
    return sorted(
        (o for o in bpy.context.scene.objects if o.type == "MESH"),
        key=lambda o: o.name,
    )


def summary(obj):
    return {
        "name": obj.name,
        "vertex_groups": [group.name for group in obj.vertex_groups],
        "material_slots": [slot.name for slot in obj.material_slots],
    }


def weight_report(target):
    name, group_name, weight = target["mesh"], target["vertex_group"], target["weight"]
    report = {"mesh": name, "vertex_group": group_name}
    obj = _mesh_object(name)
    if obj is None:
        return {**report, "error": "no mesh"}
    group = obj.vertex_groups.get(group_name)
    if group is None:
        return {**report, "error": "no vertex group"}
    index = group.index
    # Blender stores weights as float32: a painted 0.9 is 0.899999976, so compare in float32.
    (stored,) = struct.unpack("f", struct.pack("f", weight))
    assigned = at_weight = 0
    for vertex in obj.data.vertices:
        for element in vertex.groups:
            if element.group == index:
                assigned += 1
                at_weight += element.weight == stored
                break
    return {
        **report,
        "vertices": len(obj.data.vertices),
        "assigned": assigned,
        "at_weight": at_weight,
    }


def texture_report(target):
    name, maps = target["mesh"], target["maps"]
    obj = _mesh_object(name)
    if obj is None:
        return {"mesh": name, "error": "no mesh"}
    files = _saved_image_files(obj)
    return {
        "mesh": name,
        "maps": {
            texture_map: any(f.endswith(f"{name}_{texture_map}.png") for f in files)
            for texture_map in maps
        },
    }


def uv_report(target):
    name = target["mesh"]
    obj = _mesh_object(name)
    if obj is None:
        return {"mesh": name, "error": "no mesh"}
    if obj.mode == "EDIT":  # Blender empties the mesh's UV arrays until edit mode ends.
        return {"mesh": name, "error": "in edit mode"}
    polygons = obj.data.polygons
    starts = array("i", [0]) * len(polygons)
    totals = array("i", [0]) * len(polygons)
    polygons.foreach_get("loop_start", starts)
    polygons.foreach_get("loop_total", totals)
    return {
        "mesh": name,
        "faces": len(polygons),
        "uv_maps": [
            _uv_map_report(layer, starts, totals) for layer in obj.data.uv_layers
        ],
    }


def _uv_map_report(layer, starts, totals):
    coords = array("f", [0]) * (2 * len(layer.uv))
    layer.uv.foreach_get("vector", coords)
    us, vs = coords[0::2], coords[1::2]
    zero_area = stretched = 0
    for start, total in zip(starts, totals, strict=True):
        u, v = us[start : start + total], vs[start : start + total]
        doubled_area = sum(u[i - 1] * v[i] - u[i] * v[i - 1] for i in range(total))
        zero_area += doubled_area == 0
        stretched += min(u) == 0 and max(u) == 1 and min(v) == 0 and max(v) == 1
    return {
        "name": layer.name,
        "zero_area": zero_area,
        "possible_stretched_faces": stretched,
    }


def _mesh_object(name):
    obj = bpy.context.scene.objects.get(name)
    return obj if obj is not None and obj.type == "MESH" else None


def _saved_image_files(obj):
    files = set()
    for slot in obj.material_slots:
        material = slot.material
        if material is None or material.node_tree is None:
            continue
        for node in material.node_tree.nodes:
            image = node.image if node.type == "TEX_IMAGE" else None
            if image is None or image.source != "FILE":
                continue
            path = bpy.path.abspath(image.filepath, library=image.library)
            if os.path.isfile(path):
                files.add(os.path.basename(path))
    return files
