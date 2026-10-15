# forge.py — headless Blender modeling & render helpers (Blender 5.x, EEVEE)
# A reusable, de-branded pipeline for stylized 3D renders: fresh-scene setup,
# an orthographic camera, a calibrated three-point light rig, glossy materials,
# and boolean-union / smooth / pose helpers.
#
# Import inside a `blender -P script.py` run:
#   import sys; sys.path.append(FORGE_DIR); import forge
import bpy
import math
import mathutils


def fresh_scene(res_x=1248, res_y=862):
    """Clear the scene and set up a transparent-background EEVEE render."""
    for ob in list(bpy.data.objects):
        bpy.data.objects.remove(ob, do_unlink=True)
    sc = bpy.context.scene
    sc.render.engine = 'BLENDER_EEVEE'
    sc.render.film_transparent = True
    sc.render.resolution_x = res_x
    sc.render.resolution_y = res_y
    # 'Standard' transform keeps saturated yellows true; 'Filmic' desaturates them.
    sc.view_settings.view_transform = 'Standard'
    return sc


def ortho_camera(sc, ortho_scale=12.48):
    """Add an orthographic camera facing the origin and make it the active cam."""
    cd = bpy.data.cameras.new('FORGE_CAM')
    cd.type = 'ORTHO'
    cd.ortho_scale = ortho_scale
    cam = bpy.data.objects.new('FORGE_CAM', cd)
    cam.location = (0.0, -20.0, 0.0)
    cam.rotation_euler = (math.radians(90), 0, 0)
    sc.collection.objects.link(cam)
    sc.camera = cam
    return cam


def three_point_rig(sc, key_energy=2500):
    """Key + fill + rim area-light rig, calibrated for a bright stylized look.

    Defaults were tuned against the 'Standard' view transform: a warm key, a
    low amber fill for undersides, and a cool rim. Override ``key_energy`` (the
    fill and rim scale off it) or pass your own lights for a different look.
    """
    def area(name, loc, size, energy, color):
        d = bpy.data.lights.new(name, 'AREA')
        d.size = size
        d.energy = energy
        d.color = color
        o = bpy.data.objects.new(name, d)
        o.location = loc
        o.rotation_euler = (math.radians(90), 0, 0) if loc[1] < 0 else (math.radians(-90), 0, 0)
        sc.collection.objects.link(o)

    area('KEY', (1.5, -6.0, 5.0), 9.0, key_energy, (1.0, 0.97, 0.90))
    area('FILL', (-4.5, -5.0, -4.5), 9.0, key_energy * 0.48, (1.0, 0.60, 0.28))
    area('RIM', (5.5, 4.0, 3.0), 6.0, key_energy * 0.32, (0.85, 0.9, 1.0))


def glossy_material(name='glossy', base=(1.00, 0.52, 0.10), rough=0.25):
    """A Principled-BSDF material with an optional clear-coat. Any base color."""
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    b = m.node_tree.nodes.get('Principled BSDF')
    b.inputs['Base Color'].default_value = (*base, 1.0)
    b.inputs['Roughness'].default_value = rough
    try:
        b.inputs['Coat Weight'].default_value = 0.3
    except Exception:
        pass
    return m


def rounded_box(sc, name, center, dims, bevel=0.22, rot=(0, 0, 0)):
    """Add a cube at ``center`` with the given dimensions and a bevel modifier."""
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=center)
    o = bpy.context.active_object
    o.name = name
    o.dimensions = dims
    o.rotation_euler = rot
    bv = o.modifiers.new('BEV', 'BEVEL')
    bv.width = bevel
    bv.segments = 4
    return o


def union_all(sc, base, parts):
    """Exact-solver boolean union of ``parts`` into ``base``; returns base."""
    for p in parts:
        m = base.modifiers.new('U', 'BOOLEAN')
        m.operation = 'UNION'
        m.object = p
        m.solver = 'EXACT'
        bpy.context.view_layer.objects.active = base
        bpy.ops.object.modifier_apply(modifier='U')
        bpy.data.objects.remove(p, do_unlink=True)
    return base


def smooth(obj, sub_level=2):
    """Shade-smooth an object and add a subdivision-surface modifier."""
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.shade_smooth()
    s = obj.modifiers.new('SUB', 'SUBSURF')
    s.levels = sub_level
    s.render_levels = sub_level


def pose(obj, basis, loc):
    """Set an object's world matrix from three column basis vectors + a translation."""
    M = mathutils.Matrix((basis[0], basis[1], basis[2])).transposed().to_4x4()
    obj.matrix_world = mathutils.Matrix.Translation(loc) @ M


def render(sc, path):
    """Render the scene to ``path`` as a still image."""
    sc.render.filepath = path
    bpy.ops.render.render(write_still=True)
