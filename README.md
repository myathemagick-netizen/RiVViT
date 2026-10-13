# RiVViT

**Riftline Virtual Visualization Tool** — an interactive Earth globe for exploring the Myathe Magick System's planetary geometry, sacred sites, and riftline network on the web and in immersive VR.

[Open the live globe](https://myathemagick-netizen.github.io/RiVViT/) · [Explore the Atlas](https://myathemagick.com/system/atlas/) · [Project documentation](doc/README.md)

## The map

RiVViT visualizes the Myathe Magick System's pataphysical model of Earth: twelve primary vortex nodes connected by thirty icosahedral edges, with twenty triangular faces. The Atlas gives those edges their corridor names and describes their geographic, mythological, and practical meanings within the system. Secondary sacred sites and regional overlays add context to the globe.

The displayed arcs are geometric connections between the primary nodes. They provide a framework for exploring the Atlas's corridors; the Atlas's descriptions include wider landscapes, sites, and branching paths beyond those arcs.

## Explore

- Drag to rotate the globe; scroll or pinch to zoom.
- Select a primary or secondary node to read its description and view its image.
- Open the layers menu to control the globe, interior geometry, faces, nodes, riftlines, and overlays.
- Toggle Australian Songlines, place annotations, or pause automatic rotation.

Riftlines are currently visible but do not yet have selectable corridor information. The next content step is to connect all thirty edges to their Atlas names, descriptions, and source links.

## Meta Quest VR

Open the live HTTPS site in Meta Quest Browser and select **Enter VR** when available.

- Trigger: select a node or interact with the VR menu and information panel.
- Left controller Y button: open or close the layers menu.
- Right thumbstick: rotate the globe.
- Left thumbstick: zoom, or scroll the description while the information panel is open.

Immersive WebXR requires a compatible browser and a secure origin. A plain HTTP address on a computer's local network does not satisfy that requirement on the headset.

## Current development

The modernization branch upgrades Three.js from r128 to pinned **0.186.1**, improves Quest session and controller handling, and adds two comparison layers, both off by default:

- **Dodeca · Site-pinned:** twenty face centres derived from the existing primary nodes, connected by thirty dual edges.
- **Russian Crystal · Ideal:** a regular icosahedron/dodecahedron comparison with twelve vertices, twenty face centres, and sixty lines.

Crystal points show their distance to the corresponding point in the other model. These changes are under review in [PR #1](https://github.com/myathemagick-netizen/RiVViT/pull/1); they are not yet deployed. Desktop preview checks pass; phone and physical Quest 3 validation remain pending.

## Develop locally

The app is a static site: `index.html` contains the UI, Three.js scene, and WebXR interactions. `data/` contains secondary nodes and overlay metadata; `images/` contains node photographs. There is no build step. Serve the repository with a static HTTP server and open its localhost URL for desktop development. For Quest testing, use an HTTPS origin accessible from the headset.

Keep changes targeted, preserve the primary coordinates and thirty-edge topology, and test desktop Chrome, a phone browser, and Meta Quest 3 before declaring a feature complete. New layers should default off and have controls in both web and VR menus.

## Sources and plans

The [Myathe Magick Atlas](https://myathemagick.com/system/atlas/) is the public reference for corridor names and system context. Atlas edge numbering differs from the app's edge array order: associate corridor records by their endpoint pair, not array position.

See [Architecture](doc/ARCHITECTURE.md), [Crystal Grid](doc/CRYSTAL-GRID.md), [Roadmap](doc/ROADMAP.md), and [Changelog](doc/CHANGELOG.md) for implementation details and planned work, including selectable riftlines, richer site readings, and the Novelty Wave timeline.
