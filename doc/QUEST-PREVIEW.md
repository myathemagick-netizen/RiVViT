# Quest preview testing

Preview: https://myathemagick-netizen.github.io/RiVViT-preview/

Stable site: https://myathemagick-netizen.github.io/RiVViT/

The preview is deployed independently from the modernization branch to the `RiVViT-preview` repository's `main` branch. It does not deploy the stable repository's `main` branch. The header displays a preview build identifier; check it after reloading to confirm the version under test.

## Current build 2026-10-12.5

The validated globe features are merged to stable. New preview focus: open TIME → Novelty Wave, hold trigger over the plot to scrub, release to stop, and test the yearly/Now/epoch buttons. Check menu and plaque interactions while the timeline is visible, then exit/re-enter VR. See NOVELTY-WAVE.md for calibration and date precision.

The user confirmed build 2026-10-12.1 works on Quest with no reported issues. The new build adds hover feedback; point each controller at selectable nodes and verify the subtle glow appears and clears, including when layers are hidden. All 30 riftlines are now selectable: point between nodes to see the gold arc glow, then trigger to open the corridor name, number, summary, and endpoints. Check endpoint selection still opens the vortex, hidden riftlines cannot be selected, and far-side arcs do not intercept the pointer.

- Three.js 0.186.1 ES modules and sRGB color textures.
- Awaited Quest session startup, existing controller discovery, and exit cleanup.
- Frame-time handling for thumbsticks and globe rotation.
- Site-pinned and Russian ideal Crystal Grid comparison layers, off by default.

## Test in Meta Quest Browser

1. Open the preview HTTPS URL and check the build identifier.
2. Enter VR. Check globe placement, scale, and readability.
3. Select a primary node, open its image, close the lightbox, and scroll its description.
4. Press the left controller Y button. Toggle existing layers and both Crystal Grid layers. Check every menu row is accessible.
5. Select crystal points. Check counterpart-distance descriptions and that hidden layers cannot be selected.
6. Use the right thumbstick to rotate and the left to zoom. Check movement remains comfortable.
7. Exit VR and re-enter. Check the web globe restores its placement, controller input works again, and cursors do not remain on screen.
8. Disconnect/reconnect a controller during a session and verify input resumes.

Report headset model, browser version, build identifier, failing step, expected behavior, and actual behavior. Phone and desktop Chrome checks are also required before marking the modernization ready to merge.

## Next implementation order

First resolve device-test issues. Named riftlines are implemented in build 2026-10-12.3. Next build the Novelty Wave temporal control with a fixed, documented phase model and dated event records. Add Saturn ephemerides and orientation comparisons after the time model exists. Sirius and other observation layers follow.

The generated design comps are proposals; the current build does not implement the observatory dashboard or Novelty Wave controls yet.
