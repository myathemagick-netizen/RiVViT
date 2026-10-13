# Changelog

Newest first. Dates are recorded when known; earlier entries are summarised by milestone.

## 2026-10-13 — Sirius timeline preview

- Recorded the author’s pattern-seeking purpose, dextrogyre interpretation, historical-layer goals, and reason for the 200-year boundary.
- Added an optional Sirius timeline on web and Quest: approximate catalogue distance/coordinates, Kepler A/B separation curve, and static travel-scale scenario at the fitted Saturn speed.
- Intensity and a different Sirius force remain open; MMS calibration is unchanged. Quest validation pending.

## 2026-10-13 — Moving-target research experiment

- Added a barycentric straight-path, constant-speed arrival solver and Earth radial/separation-rate calculations.
- Added time-resolved Sun/Moon/planet proximity scans, distinguishing segment alignments from same-time sphere-overlap candidates.
- A single in-sample fitted speed yields 9.03-day RMS error against configured wave crests; constant-delay and stationary-distance baselines are documented separately.
- No same-time sphere-overlap candidates found in the seven sampled fitted journeys. No physical propagation speed or obstruction effects are asserted.
- Added reproducible report, assumptions, tests, and numerical limits. Runtime UI and stable app remain unchanged.

## 2026-10-13 — Crest offset and distance research notes

- Documented the user’s proposed chronon-pressure travel/response interpretation and the possible contribution of Earth–Saturn distance variation.
- Recorded the current fixed-wave mean offset (728.23 days / 1.994 years), separate named-year midpoint result, and the seven-cycle distance table.
- Included calibration/calendar limitations, descriptive correlations, and a proposed moving-target test.
- Added the reproducible calculation script and full JSON record. No runtime or astronomical/MMS model changes.

## 2026-10-13 — Observatory validated for stable release

- User confirmed the complete wave/Saturn comparison works on both web and Quest, and explicitly authorized merging PR #2 to stable.
- Release includes the 1830–2026 Novelty Wave, movable Quest timeline, independent pole curve, epoch table, Saturn astronomy/visuals, and all 30 route images.
- Phone validation has not been reported. The accepted route cards remain provisional schematic maps for later refinement.

## 2026-10-13 — Wave/pole comparison (preview build 2026-10-13.4)

- Added a cyan independent Saturn opening curve across 1830–2026, with separate degree and MMS scales.
- Added a web epoch comparison table, clickable markers, and sampled within-year ranges; Quest shows the selected marker range.
- Astronomy samples do not change when crest calibration changes. Tables only rebuild on reference changes, avoiding repeated DOM work during Quest scrubbing.
- Model independence and sample provenance tests pass; desktop comparison and calibration checks pass without captured errors. Quest comparison readability check pending.

## 2026-10-13 — Visual Saturn (preview build 2026-10-13.3)

- Added a separate Saturn view toggle to web and Quest menus, off by default.
- The visual planet, rings, and north-pole arrow use the selected date's Earth-facing tilt.
- Added an Earth/Saturn heliocentric longitude diagram with explicit illustrative-scale labels.
- Wide web layouts reserve room beside the timeline; the web model holds its apparent size during Earth zoom.
- Geometry/mapping tests pass and desktop checks show north-facing and near-edge-on changes. Quest visual validation pending.

## 2026-10-13 — Saturn tracking (preview build 2026-10-13.2)

- Added local date-driven Saturn astronomy using pinned Astronomy Engine 2.1.19 with its MIT license.
- Web and Quest show Earth-centered sky longitude/latitude, distance, apparent motion, Sun-centered orbital longitude, and signed Earth-facing pole/ring opening.
- Enlarged the movable Quest panel with a calculated astronomy section and schematic ring-opening icon.
- Astronomy remains separate from the MMS wave; no inferred pressure or corridor activation is displayed.
- Tests pass against a JPL Horizons reference and opposite-pole/edge-on configurations. Desktop date updates verified without captured errors; Quest check pending.

## 2026-10-13 — Riftline route images (preview build 2026-10-13.1)

- Added an original schematic globe card for each of the 30 corridors, generated from the existing node coordinates and procedural coast outlines.
- Riftline metadata now supplies image paths to the shared web and Quest panel/lightbox flow.
- Cards show the corridor number/name, actual geometric arc, endpoint codes, and endpoint names. They are route diagrams, not site photographs or precise local corridor boundaries.
- Verified all 30 images and metadata paths, inspected representative polar/Atlantic/Pacific cards, and checked desktop panel/lightbox loading without captured console errors. Quest image checks remain pending.

## 2026-10-12 — Movable Quest timeline (preview build 2026-10-12.6)

- User confirmed timeline scrubbing works on Quest and reported overlap with the globe and information panels.
- Added trigger-grab header to reposition and rotate the timeline, release-to-place, and Reset position.
- Overlapping VR panels now choose the nearest ray hit rather than giving the timeline priority over the information plaque.
- Grabs release when the timeline hides, the controller disappears, or the session ends. Only one controller owns a grab.
- Model and panel-priority tests pass. Physical Quest movement and overlap checks remain pending.

## 2026-10-12 — Stable release and Novelty Wave preview

- Merged PR #1 after the user confirmed the features work in Quest and explicitly authorized the stable release.
- Added preview build 2026-10-12.5: a shared web/Quest Novelty Wave timeline, limited to 1830–2026, with date controls, historical year markers, and phase labels.
- Defined a testable 29.5-year model with editable provisional crest reference. Year-only markers remain separate from the calculated curve.
- Quest panel supports trigger scrubbing, yearly steps, Now, and previous/next epoch controls; the web adds date entry and calibration controls.
- Model tests and desktop control/layout checks pass. Quest testing of the new slider remains pending. Saturn ephemerides are not connected yet.

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
