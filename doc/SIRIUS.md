# Sirius timeline · preview build 2026-10-13.5

Open TIME / Events → Novelty Wave, then enable **Sirius timeline** on web or Quest. It defaults off. The lavender strip uses the same 1830–2026 dates as the wave, with its own 0–35 AU scale: physical A/B separation, not pressure or distance from Earth. Scrubbing and epoch buttons update distance, coordinates, binary separation, and a hypothetical travel-scale readout. The movable Quest panel grows while this layer is enabled; its header, reset and existing buttons retain their pixel hit zones.

## Data and approximation

[SIMBAD's Sirius catalogue entry](https://simbad.cds.unistra.fr/simbad/sim-basic?Ident=sirius) supplies J2000 ICRS coordinates, parallax 379.21 mas, proper motions −546.01/−1223.07 mas/year, and radial velocity −5.50 km/s (retrieved 2026-10-13). Convert these into a Cartesian position and constant space velocity; subtract Astronomy Engine's geometric heliocentric Earth vector at the selected date. The catalogue radial velocity indicates approach. This is an approximate Sirius A catalogue track, not a precision A/B system-barycentre ephemeris: binary reflex motion, catalogue epoch/systematic errors, perspective changes beyond the linear track, and stellar light-time/aberration are not fully modeled. Coordinates remain ICRS/J2000 rather than equator-of-date. Display precision makes small changes visible; it is not an accuracy claim.

[Bond et al. (2017), Table 4](https://arxiv.org/abs/1703.10625) supplies a 50.1284-year binary period, eccentricity 0.59142, periastron epoch 1994.5715, and angular semimajor axis 7.4957 arcseconds. Kepler's equation gives instantaneous physical separation using the catalogue parallax; the curve is neither projected sky separation nor Earth distance. Fractional epochs use Julian years relative to J2000. A/B component positions and a sky-orbit visualization remain future work.

## Travel and intensity

Distance divided by the Saturn experiment's fitted **24.25 km/s** gives roughly **106,000 years** at Sirius's distance. This is a static distance/speed scale comparison. It does not apply the Solar System moving-target solver over that duration, extrapolate the Sirius track that far, date an emission, or predict a present arrival. The roughly 8.6-year light travel time is a separate quantity.

The layer does not assume that Sirius's proposed force must travel at the Saturn speed. Intensity, attenuation, emission history, and chronon-force law are unspecified. A slow approach alone cannot supply those missing quantities. The novelty-wave calibration remains independent of this layer.

## Validation

`node tests/sirius.test.mjs` checks Kepler extrema and period, approach direction, J2000 coordinates, invalid inputs, and distance/speed scaling. Web checks cover the toggle, date/epoch updates, and unchanged MMS calibration. Quest checks must verify the enlarged panel, lavender strip readability, toggle off/on, grabbing/reset, overlapping panels, and scrubbing with the changed panel height. User Quest validation is pending.
