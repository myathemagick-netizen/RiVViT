# Changelog

Newest first. Dates are recorded when known; earlier entries are summarised by milestone.

## 2026-10-12 — Web legend (preview build 2026-10-12.4)

- Added violet site-pinned and dashed coral Russian ideal line samples, plus the gold riftline hover sample.
- Regional map overlays now add their names and map swatches to the legend when the manifest loads.
- Improved legend text contrast.

## 2026-10-12 — Named riftlines (preview build 2026-10-12.3)

- Added all 30 corridor records from MMS v37 section 4.8, with attributed summaries and Atlas chapter links.
- Added whole-arc hover highlights and wider pick targets for web, touch, and Quest.
- Shared point-priority selection at corridor endpoints, with hidden-layer and globe occlusion checks.
- Corridor information appears in web panels and VR plaques; web panels link to the Atlas. Long VR titles fit the available width.
- Verified unique complete edge mapping, syntax, desktop selection, node priority, hidden-line behavior, and no captured console warnings/errors. Quest selection awaits testing.

## 2026-10-12 — Hover feedback (preview build 2026-10-12.2)

- User confirmed the previous preview works on Quest with no reported issues.
- Added subtle color-matched hover glows for selectable vortices, sacred sites, crystal points, and annotations, on desktop and both Quest pointers.
- Shared nearest-visible-target picking between hover and selection; the globe blocks far-side targets, and VR panels take pointer priority.
- Glows clear when pointers leave, layers hide, or VR ends. No postprocessing pass is required.
- Desktop node hover and selection checked with no captured console errors. Quest hover feedback awaits user testing; riftlines are still pending selectable metadata.

## 2026-10-12 — Project README (branch preview)

- Expanded the root README with purpose, controls, Quest requirements, development instructions, current branch status, and documentation links.
- Linked the public Myathe Magick Atlas as the reference for named riftline corridors; recorded that future corridor metadata must match endpoint pairs rather than array positions.

## 2026-10-12 — Three.js and Quest modernization (branch preview)

- Upgraded r128 to pinned Three.js 0.186.1 ES modules, with explicit sRGB texture handling.
- Awaited WebXR session initialization; added startup input-source discovery and session cleanup.
- Made controller motion and globe inertia account for frame time; corrected Quest HTTPS guidance.
- Implemented the two documented Crystal Grid comparison layers in the main app, off by default, with web/VR controls and counterpart distance descriptions.
- Fixed selection of hidden primary and secondary layers.
- Desktop in-app Chromium preview renders both layers without captured console errors; module syntax check passes. Physical phone and Quest 3 checks remain pending. Not deployed.

## 2026-10-12 — Crystal Grid (preview)

- Added two Crystal Grid layers, both off by default: **Dodeca · Site-pinned** (20 face centres derived live from the vortex triangles, 30 dual riftlines) and **Russian Crystal · Ideal** (12 + 20 points, 60 lines, Giza-anchored).
- Info panel for crystal points shows distance to the counterpart in the other model.
- Toggles added to web and VR menus.
- Built a dependency-free Lite preview for phones.
- Not yet deployed to GitHub Pages.
- Added `/doc/` (README, ROADMAP, ARCHITECTURE, CRYSTAL-GRID, CHANGELOG).

## Earlier milestones

- **VR & overlays:** Quest 3 controllers, lectern-style plaque, VR menu, overlay manifest, Australian Songlines overlay ("Restoring the gravity in Australia"), secondary nodes JSON, 600×600 node images.
- **Foundation:** three.js globe, Sanderson belt layout, 30-edge topology corrections, Mt. Kailash moved to secondary, poles restored at ±90°, menu and info panel, pinch-zoom and auto-rotate.
