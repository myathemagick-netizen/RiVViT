# Saturn tracker

The selected Novelty Wave date now drives Saturn astronomy on web and Quest. Calculations run locally using the pinned MIT-licensed Astronomy Engine 2.1.19 module, vendored under `vendor/astronomy-engine/`. There is no live API dependency while scrubbing.

## Displayed quantities

- Earth-centered apparent ecliptic longitude and latitude, in the true ecliptic/equinox of the selected date. These are sky coordinates, not longitude/latitude on Earth.
- Earth–Saturn distance in astronomical units (AU).
- Direct or retrograde apparent sky motion, estimated from the longitude change over a one-day centered interval.
- Sun-centered orbital longitude, distinct from apparent sky position.
- Signed ring-plane opening angle toward Earth: positive for the north face, negative for the south face. Near edge-on is a display classification within 0.5 degrees.

All values refer to **00:00 UTC** on the selected date. They update with scrubbing, date entry, epoch selection, and Now. Now selects today's date, not a second-by-second live position.

## Pole geometry

`lib/saturn.mjs` uses the IAU axis returned by RotationAxis and an unaberrated, light-time-corrected Earth-to-Saturn vector, both in J2000 equatorial coordinates. The axis is evaluated at the backdated light-emission time. The signed opening angle is the arcsine of the pole dotted with the Saturn-to-Earth unit direction. The internal north-pole/observer angle is 90 degrees minus that opening angle.

The Quest icon sketches ring opening; it does not show the sky position angle, true size, terrain, or hexagon imagery. North-face visibility is viewing geometry, not a calculated measure of hexagon visibility or chronon pressure.

## Sources and validation

- [Astronomy Engine reference](https://github.com/cosinekitty/astronomy/blob/master/source/js/README.md)
- [JPL Horizons documentation](https://ssd.jpl.nasa.gov/horizons/manual.html)

The regression test uses Horizons target 699 (Saturn), center 500@399 (Earth), 2017-06-21 at 00:00 UTC, observer quantities 31, 20, and 14, retrieved 2026-10-13. Position and distance agree within 0.01 degree and 0.001 AU respectively. Horizons planetographic subobserver latitude is converted using its equatorial/polar radii before comparing to the planetocentric ring-plane opening. Differences in ephemerides and coordinate conventions mean these displays are not navigation-grade or exact JPL replicas.

Additional checks cover the opposite pole in 2000, the near-edge-on configuration in March 2025, and timeline range endpoints. Desktop date-driven UI checks pass; the expanded Quest panel needs device testing.

## MMS relationship

Astronomy and the 29.5-year MMS wave remain separate calculations sharing a selected date. Saturn values do not automatically set a pressure score, refit the wave, or activate Earth corridors. Those relationships need explicit, versioned MMS rules. Site-specific altitude/azimuth, a 3D Saturn scene, and comparisons of pole opening against wave phase are follow-up work.
