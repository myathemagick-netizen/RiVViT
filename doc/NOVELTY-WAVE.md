# Novelty Wave timeline

The first preview is limited to 1830–2026, approximately the last 200 years. Open Events → Novelty Wave on the web, or TIME → Novelty Wave in the Quest Y menu. The panel defaults off.

## Model

The shared calculation in `lib/novelty-wave.mjs` uses a cosine wave, equivalently a phase-shifted sine wave, with a 29.5-year period. One model year is 365.2425 days. A documented crest reference fixes its phase; this does not derive phase from the separately displayed Saturn astronomy.

The default reference is **1931-07-01**, a provisional mid-year calibration for the 1931 Surrealist Epoch. It does not claim Dalí painted on that date. Change the crest reference in the web panel's Model section to inspect other calibrations. The web and VR views use the same reference in the current session.

Positive values represent novelty and negative values tradition in the MMS interpretation. Four equal quarter-cycle intervals are named Waning, Collapse, Renewal, and Ascent, measured forward from a crest. The exact extrema display Novelty crest or Tradition trough. These are implementation conventions for the first model; the MMS narratives remain separate records.

## Historical records

`data/novelty-events.json` stores named epoch and trough markers from MMS v37 section 3.4. The records currently have **year precision only**. A marker is drawn at the year's midpoint for navigation, with an explicit year-only label; it is not an asserted event timestamp or an exact calculated extremum. The wave is never refitted to the markers.

The first set covers the Romantic, Commune, Tesla, Surrealist, Beat, Grunge, and Trans/Hyperpop epochs, and the 1916, 1946, 1976, and 2006 trough references. Exact dated events and uncertainty intervals can be added separately when verified.

## Web controls

Drag the range slider, enter a date, click the wave or a marker, choose an epoch, or select Now. Keyboard Home and End reach the date limits. The phase, date, cursor, and selected event text update together. Date calculations use UTC calendar days.

## Quest controls

Enable Novelty Wave from the Y menu. Aim at the chart and hold the trigger to scrub. The panel has one-year backward/forward controls, Now, and previous/next historical markers. Release the trigger to stop scrubbing. Hold trigger on the top grab bar to move and rotate the panel; release to place it. Reset position returns it to the starting pose. Placement lasts for the current page session. The panel highlights when targeted and blocks selection of globe objects behind it. When it overlaps another panel, the closest panel under the pointer receives input. It is hidden outside immersive VR, where the HTML panel is used instead.

## Validation and next work

Pure model tests cover period, extrema, negative-time phase wrapping, quarters, hard bounds, slider mapping, and reference changes. Desktop preview checks cover historical selection, date limits, calibration edits, and rendered layout. The user confirmed the panel and subsequent movement/comparison features work on Quest.

The globe's positions and corridors do not yet change with the selected date. Saturn position/orientation now appears alongside the wave; see SATURN.md. Temporal events on the globe, rules connecting astronomy to the MMS model, and saved calibration remain follow-up work. There is no calculated chronon-pressure measurement in this build.

## Research observations

See [Saturn and Novelty Wave observations](SATURN-WAVE-OBSERVATIONS.md) for the calculated phase offset, the role of the provisional crest reference, and the Earth–Saturn distance comparison. These notes do not change the wave calculation or establish a measured propagation delay.
