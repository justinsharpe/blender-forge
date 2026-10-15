# blender-forge

Headless Blender modeling & render helpers (Blender 5.x, EEVEE). A small
library of functions you import inside a `blender -P script.py` run to build a
stylized 3D scene fast: a fresh-scene setup, an orthographic camera, a
calibrated three-point light rig, glossy materials, and boolean-union / smooth
/ pose helpers.

## Requirements

- Blender 5.x (the `bpy` module exists only inside Blender's Python — there is
  no way to `pip install` it, and this library cannot run outside Blender).

## Usage

```python
# inside a script run with:  blender -P render_me.py
import sys, os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import forge

sc = forge.fresh_scene()
forge.ortho_camera(sc)
forge.three_point_rig(sc, key_energy=2500)

base = forge.rounded_box(sc, "body", (0, 0, 0), (2, 2, 2))
mat = forge.glossy_material("mat", base=(0.2, 0.6, 1.0))  # any color
base.data.materials.append(mat)
forge.smooth(base)

forge.render(sc, "/tmp/render.png")
```

See `example.py` for a complete, runnable model.

## What each helper does

| Function | What |
|---|---|
| `fresh_scene(res_x, res_y)` | clears the scene; transparent EEVEE render; `Standard` view transform |
| `ortho_camera(sc, ortho_scale)` | orthographic camera facing the origin, made active |
| `three_point_rig(sc, key_energy)` | key + fill + rim area lights (calibrated defaults) |
| `glossy_material(name, base, rough)` | Principled-BSDF material with optional clear-coat |
| `rounded_box(sc, name, center, dims, bevel, rot)` | cube + bevel modifier |
| `union_all(sc, base, parts)` | exact-solver boolean union |
| `smooth(obj, sub_level)` | shade-smooth + subdivision surface |
| `pose(obj, basis, loc)` | set world matrix from basis vectors + translation |
| `render(sc, path)` | render a still to disk |

## The one calibration note

`fresh_scene` pins the view transform to `Standard`, not the Blender default
`Filmic`. Filmic is great for realistic lighting but desaturates saturated
colors (bright yellows go brownish); `Standard` keeps them true. If you are
rendering a realistic scene rather than a stylized one, switch it back in your
own script — everything else is look-agnostic.

## License

MIT — see [LICENSE](LICENSE).
