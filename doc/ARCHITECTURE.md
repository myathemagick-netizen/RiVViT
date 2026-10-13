# RiVViT Architecture

RiVViT is a single HTML file (`index.html`) served by GitHub Pages, plus a small `data/` folder for content that changes independently of the code.

## Repository layout

```
/
├── index.html                       the whole app: styles, menu markup, three.js scene, VR
├── data/
│   ├── nodes/
│   │   └── secondary_nodes.json     sacred sites (inline fallback in index.html)
│   └── overlays/
│       ├── manifest.json            list of regional map overlays
│       └── …                        overlay images (e.g. Australian Songlines)
├── images/                          node photos, 600×600
└── doc/                             this documentation
```

Planned additions: `data/nodes/vortex_nodes.json` (the 12 primaries + 30 edges) and `data/grids/russian_crystal.json`.

## Libraries

- **three.js r128** from cdnjs, for the globe, WebXR and controllers.
- **Google Fonts**: Inter (body), Cinzel (headings).
- Earth texture fetched as a blob from a list of mirrors (`TEX_URLS`), falling back to a drawn map.

## Coordinate convention

`ll2v(lat, lon, r)` converts latitude/longitude to a three.js vector. Every layer, including derived ones, goes through it, so all geometry stays in one frame.

## Main sections of `index.html`

Each section is marked with a `// ═══` banner comment.

| Section | Role |
|---|---|
| Vortex nodes / Edges | `VORTEX_NODES` (12) and `EDGES` (30 index pairs) |
| Secondary nodes | Fetches `secondary_nodes.json`, falls back to `SECONDARY_NODES_FALLBACK` |
| Texture | Tries `TEX_URLS` in order, otherwise draws the procedural map |
| Geometry | Riftline arcs (`surfaceArc`), faces, markers |
| Crystal grid *(new)* | Face centres, dual edges, Russian ideal solid |
| Annotations / Overlays | Overlay manifest loading and draping |
| Menu & layer map | Maps `data-l` menu keys to three.js groups |
| Info panel | `showInfo(node, set)`: tag, title, coordinates, image, text |
| VR | Controllers, raycasting, plaque, VR menu items |
| Animation loop | Riftline pulse, marker breathing, auto-rotate |

## How a layer works

1. Build a `THREE.Group`, add it to the globe group `G`, set `visible = false` if it should start off.
2. Register it in the layer map with a key, e.g. `dodeca: dodecaGrp`.
3. Add a menu row with `data-l="<key>"` to the web menu, and a `{type:'toggle', key:'<key>'}` entry to the VR menu list.
4. If its points are clickable, add a check in both the web click handler and the VR trigger handler, and a `set` branch in `showInfo` for the tag text.

The Crystal Grid layers follow exactly this pattern.

## Derived vs stored geometry

- **Derived** layers (Site-pinned Dodeca) are computed from `VORTEX_NODES` at load time. Move a vortex and they follow automatically. Nothing to keep in sync.
- **Stored** layers (Russian Ideal, overlays, secondary nodes) are fixed data. They live (or will live) in JSON.

## Preview builds

`rivvit-crystal-lite.html` is a standalone 2D canvas version with no external scripts, for checking geometry on a phone where three.js can't load. It reuses the same node, edge, secondary and coastline data. It is a preview tool, not a replacement: no VR, no textures, no photos.
