# RiVViT Roadmap

Status key: ✅ shipped · 🟡 built, not yet deployed · 🔵 next up · ⚪ planned · 💭 idea

Phases are in rough order. Dates are recorded once something ships; planned items are left undated on purpose.

---

## Phase 1 — Foundation ✅

| Status | Feature |
|---|---|
| ✅ | Three.js globe with NASA Earth texture (fetch-to-blob to bypass CORS) and a drawn-map fallback |
| ✅ | 12 vortex nodes on Sanderson's belt layout (N pole + 5 upper + 5 lower + S pole) |
| ✅ | 30 icosahedral riftlines, missing edges restored |
| ✅ | Node corrections: Mt. Kailash moved to secondary nodes, poles restored at ±90° |
| ✅ | Hamburger menu with grouped sections (Geometry, Chronon Flow, Overlays, Events, Tools) |
| ✅ | Info panel (Inter / Cinzel), image-left layout, lightbox |
| ✅ | Pinch-to-zoom and auto-rotate toggle |

## Phase 2 — VR & Overlays ✅

| Status | Feature |
|---|---|
| ✅ | Meta Quest 3 support: laser pointers, trigger select, thumbstick rotate/zoom |
| ✅ | VR info plaque as a grounded "museum lectern", with image loading and VR lightbox |
| ✅ | Y-button VR menu, mirrored to the web panel's left-side position |
| ✅ | Overlay system via `data/overlays/manifest.json` |
| ✅ | Australian Songlines overlay (lat −37 to −12, opacity 0.55), off by default |
| ✅ | Secondary nodes in `data/nodes/secondary_nodes.json` with inline fallback |
| ✅ | 29 node images cropped to 600×600 |

## Runtime modernization 🟡

Three.js 0.186.1, Quest session fixes, Crystal Grid, named riftlines, and hover feedback are merged to stable after user-confirmed Quest validation.

## Phase 3 — Crystal Grid 🟡 (current priority)

Adds the Russian (Goncharov / Morozov / Makarov) dodecahedral layer: 20 new vortices at the icosahedron's face centres and 30 new riftlines. Stops short of the full Becker-Hagens UVG set. See [CRYSTAL-GRID.md](CRYSTAL-GRID.md).

| Status | Feature |
|---|---|
| 🟡 | **Dodeca · Site-pinned** layer: 20 face centres computed live from the vortex triangles + 30 dual riftlines |
| 🟡 | **Russian Crystal · Ideal** layer: perfect-solid 12 vertices + 20 face centres + 60 lines (Giza-anchored) |
| 🟡 | Info panel shows each point's distance to its counterpart in the other model, flagging agreement within ~130 km |
| 🟡 | Toggles in web menu and VR menu, both off by default |
| 🟡 | Phone-friendly Lite preview (no three.js) for checking geometry away from the computer |
| 🔵 | Deploy the three.js version to GitHub Pages and test on all three surfaces |
| 🔵 | Move the 12 primary vortices and 30 edges out of the HTML into `data/nodes/vortex_nodes.json`, so every layer follows the same data pattern |
| ⚪ | Move the Russian ideal coordinates into `data/grids/russian_crystal.json` |
| ⚪ | Proximity test: do secondary sites cluster near the new nodes more than random points would? |
| ⚪ | Name and describe the 20 new vortices in the MMS document; promote confirmed sites (e.g. Angkor Wat, Machu Picchu candidates) |
| 💭 | Mark the 30 points where each new riftline crosses an original one, as possible checkpoints |

## Phase 4 — Depth & Reading ⚪

| Status | Feature |
|---|---|
| ⚪ | Per-node "Read More" HTML pages (iframe on web, DOM overlay in VR) |
| ⚪ | Additional regional overlay maps beyond Australia |
| ⚪ | Search / jump-to-node |

## Phase 5 — Time: the Novelty Wave ⚪

| Status | Feature |
|---|---|
| 🟡 | Novelty Wave slider and named year markers, 1830–2026, in web and Quest preview |
| ⚪ | Levo / dextro event markers along the Novelty Wave |
| ⚪ | Events placeholder in the menu becomes live |

## Phase 6 — Identity ⚪

| Status | Feature |
|---|---|
| ⚪ | RiVViT frog mascot (🐸🔦) |
| ⚪ | Favicon from the mascot |

---

## Deliberately out of scope (for now)

- The full Becker-Hagens UVG grid (62 points, 120 triangles, 15 great circles). The Russian layer is the stopping point unless that changes.
