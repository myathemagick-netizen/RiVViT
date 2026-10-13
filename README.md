# RiVViT

**Riftline Virtual Visualization Tool** — an interactive Earth globe for exploring the Myathe Magick System's planetary geometry, sacred sites, and riftline network on the web and in immersive VR.

[Open the Quest preview](https://myathemagick-netizen.github.io/RiVViT-preview/) · [Quest test checklist](doc/QUEST-PREVIEW.md) · [Open the live globe](https://myathemagick-netizen.github.io/RiVViT/) · [Explore the Atlas](https://myathemagick.com/system/atlas/) · [Project documentation](doc/README.md)

## The map

RiVViT seeks pataphysical patterns across one historical record, using astronomy as a common reference. Its approximately 200-year timeline emphasizes periods with richer collected data. Planned layers include conflicts, invention and art, religions, animal migration, weather, electromagnetic anomalies, and geology, with multiple MMS interpretations preserved. See [research purpose](doc/PATAPHYSICAL-RESEARCH.md).

RiVViT visualizes the Myathe Magick System's pataphysical model of Earth: twelve primary vortex nodes connected by thirty icosahedral edges, with twenty triangular faces. The Atlas gives those edges their corridor names and describes their geographic, mythological, and practical meanings within the system. Secondary sacred sites and regional overlays add context to the globe.

The displayed arcs are geometric connections between the primary nodes. They provide a framework for exploring the Atlas's corridors; the Atlas's descriptions include wider landscapes, sites, and branching paths beyond those arcs.

## Explore

- Drag to rotate the globe; scroll or pinch to zoom.
- Select a primary or secondary node to read its description and view its image.
- Open the layers menu to control the globe, interior geometry, faces, nodes, riftlines, and overlays.
- Toggle Australian Songlines, place annotations, or pause automatic rotation.

The preview supports all thirty named riftline corridors: hover for a gold highlight, then select a line for its MMS summary and endpoint details. The web panel links to the matching Atlas chapter. Point markers take priority where corridors meet.

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

Crystal points show their distance to the corresponding point in the other model. The modernization was merged in [PR #1](https://github.com/myathemagick-netizen/RiVViT/pull/1) after user-confirmed Quest validation and is deployed to the stable site. The temporal observatory includes the [Novelty Wave slider](doc/NOVELTY-WAVE.md), limited to 1830–2026, with independent Saturn comparison and visual views. The user validated this release on web and Quest; see [PR #2](https://github.com/myathemagick-netizen/RiVViT/pull/2). Open Events → Novelty Wave on web or TIME → Novelty Wave in VR. The provisional MMS wave is displayed alongside calculated [Saturn astronomy](doc/SATURN.md), both driven by the selected date. Astronomy does not determine a chronon-pressure score.

## Develop locally

The app is a static site: `index.html` contains the UI, Three.js scene, and WebXR interactions. `data/` contains secondary nodes and overlay metadata; `images/` contains node photographs. There is no build step. Serve the repository with a static HTTP server and open its localhost URL for desktop development. For Quest testing, use an HTTPS origin accessible from the headset.

Keep changes targeted, preserve the primary coordinates and thirty-edge topology, and test desktop Chrome, a phone browser, and Meta Quest 3 before declaring a feature complete. New layers should default off and have controls in both web and VR menus.

## Sources and plans

The [Myathe Magick Atlas](https://myathemagick.com/system/atlas/) is the public reference for corridor names and system context. Atlas edge numbering differs from the app's edge array order: associate corridor records by their endpoint pair, not array position.

See [Architecture](doc/ARCHITECTURE.md), [Crystal Grid](doc/CRYSTAL-GRID.md), [Roadmap](doc/ROADMAP.md), and [Changelog](doc/CHANGELOG.md) for implementation details and planned work, including selectable riftlines, richer site readings, and the Novelty Wave timeline.
