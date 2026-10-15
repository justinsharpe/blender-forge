# example.py — a complete, runnable model (run: blender -P example.py)
import sys, os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import forge

sc = forge.fresh_scene()
forge.ortho_camera(sc)
forge.three_point_rig(sc)

base = forge.rounded_box(sc, "body", (0, 0, 0), (2, 2, 2))
mat = forge.glossy_material("mat", base=(0.2, 0.6, 1.0))
base.data.materials.append(mat)
forge.smooth(base)

forge.render(sc, os.path.join(os.path.dirname(os.path.abspath(__file__)), "example.png"))
print("rendered example.png")
