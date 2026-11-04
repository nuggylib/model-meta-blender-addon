import struct

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
    name, inputs = target["mesh"], target["inputs"]
    obj = _mesh_object(name)
    if obj is None:
        return {"mesh": name, "error": "no mesh"}
    return {
        "mesh": name,
        "materials": [
            _material_inputs(slot.material, inputs) for slot in obj.material_slots
        ],
    }


def _mesh_object(name):
    obj = bpy.context.scene.objects.get(name)
    return obj if obj is not None and obj.type == "MESH" else None


def _material_inputs(material, inputs):
    shader = _surface_shader(material)
    found = {}
    for name in inputs:
        socket = None if shader is None else shader.inputs.get(name)
        found[name] = None if socket is None else _has_image(socket, set())
    return {"material": None if material is None else material.name, "inputs": found}


def _surface_shader(material):
    if material is None or material.node_tree is None or not material.use_nodes:
        return None
    output = material.node_tree.get_output_node("ALL")
    surface = None if output is None else output.inputs.get("Surface")
    if surface is None:
        return None
    links = [link for link in surface.links if not link.is_muted]
    return links[0].from_node if links else None


def _has_image(socket, seen):
    for link in socket.links:
        node = link.from_node
        if link.is_muted or node.name in seen:
            continue
        seen.add(node.name)
        if node.type == "TEX_IMAGE" and node.image is not None:
            return True
        if any(_has_image(upstream, seen) for upstream in node.inputs):
            return True
    return False
