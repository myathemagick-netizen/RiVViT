# Moving-target propagation experiment

This research tool tests the user's proposal that Earth's motion and intervening celestial geometry could contribute to the Saturn/MMS offset. It uses astronomical positions within an explicitly hypothetical propagation model. It is not a measured chronon speed or a blocking model.

## Model and frame

At a nominated departure date, freeze Saturn's source position and expand a spherical wave at one constant speed in the solar-system barycentric J2000 equatorial frame (SSB/EQJ). Find the first sampled crossing where the front reaches Earth's moving center. The receiving ray is then the straight segment from Saturn's departure position to Earth's arrival position. It is not aimed at Earth's departure position.

Simultaneous geometric positions come from Astronomy Engine 2.1.19 HelioVector, without optical light-time or aberration corrections. Subtract the Sun-to-SSB vector at each date to obtain a common approximately inertial barycentric frame. The Sun is therefore moving rather than held at the origin.

The seven departure seeds are the calendar-day renderings of the north-facing maxima in [the earlier observations](SATURN-WAVE-OBSERVATIONS.md), evaluated at 00:00 UTC. These are nominated model seeds, not observed emission events. Arrival targets are the existing fixed-wave calendar-day crests, not independently dated cultural events. Day rounding differs slightly from the preceding sub-day offset calculation.

Gravity, refraction, wavefront width, attenuation, obstruction effects, and an additional psychological/cultural response delay are not implemented. The direction of a receiving ray depends on its eventual interception; the assumption is an isotropic spherical front, not a transmitter anticipating Earth.

## First fit

An exploratory grid search over **20–35 km/s**, in **0.25 km/s** steps, chooses **24.25 km/s** as the best single speed for these seven configured targets. Its RMS arrival-date error is **9.03 days**. This is an in-sample fitted parameter, with grid resolution rather than statistical uncertainty, and must not be reported as a physical measurement.

For comparison, a one-parameter constant-delay baseline has **76.37 days RMS error**. Freezing Earth at its departure position and fitting one speed gives **59.71 days RMS error** (24.844 km/s). Allowing Earth to move improves this particular fit. It does not independently validate the wave's calibration or the proposed mechanism: Saturn's orbital geometry and the model's approximately Saturn-length period are already related.

| Departure seed | Configured wave crest | Moving-target arrival | Arrival minus target, days | Earth's radial velocity at departure, km/s |
|---|---|---|---:|---:|
| 1840-11-05 | 1842-12-30 | 1842-12-31 | +1.44 | +17.68 |
| 1870-10-01 | 1872-06-29 | 1872-07-13 | +14.36 | +28.66 |
| 1899-10-30 | 1901-12-30 | 1901-12-26 | −3.12 | +20.64 |
| 1929-09-28 | 1931-07-01 | 1931-07-07 | +6.05 | +29.21 |
| 1958-10-24 | 1960-12-29 | 1960-12-20 | −8.26 | +23.25 |
| 1988-09-25 | 1990-06-30 | 1990-07-02 | +2.31 | +29.48 |
| 2017-10-16 | 2019-12-29 | 2019-12-13 | −15.59 | +25.75 |

Positive Earth radial velocity means Earth moves away along the instantaneous Saturn-to-Earth direction. The report also gives the relative separation rate, subtracting Saturn's instantaneous velocity. Neither velocity is assumed constant throughout the trip. Arrival times are retained in the data; table dates are calendar-day renderings.

## Intervening bodies

The scan follows the journey rather than taking only a departure-date snapshot. It checks the Sun, Moon, Mercury, Venus, Mars, Jupiter, Uranus, Neptune, and Pluto. Earth and Saturn are the destination and source, so they are excluded as interveners. Other moons, asteroids, rings, atmospheres, fields, and any hypothetical wavefront width are not included.

Two quantities are deliberately separate:

- **Same-time proximity:** separation between a body's center and the traveling point on the receiving ray at that same instant. Compare this with an adopted spherical body radius to identify geometric sphere-overlap candidates.
- **Segment alignment:** closest approach to any point on the drawn source-to-arrival segment while the body's projection lies between the endpoints. The front may be somewhere else entirely at that time. This is a path alignment, not an obstruction encounter.

No same-time sphere-overlap candidates were found in the sampled seven fitted journeys. This is not an exhaustive occultation certification. The closest same-time body in these runs is the Moon, approaching the receiving ray near arrival but remaining outside its adopted radius.

An instructive distinction appears in the 1840 departure run: the Moon approaches the drawn segment to about **835 km** on **1840-12-31**, inside the adopted Moon radius. At that instant it is approximately **1.53 billion km** from the traveling point. It is a geometric line crossing at the wrong time, not a same-time overlap in this model. No blocking, delay, or amplification effect is assigned to either kind of proximity.

Planetary radii use the [JPL equatorial-radius table](https://ssd.jpl.nasa.gov/planets/phys_par.html); Sun and Moon radii use the constants in the pinned Astronomy Engine source. Spherical radii are simplified screening bounds, not detailed body shapes.

## Numerical limits and tests

The arrival search scans every 0.25 day for up to five model years, then bisects the first sampled sign-changing bracket. It can miss an exact grazing/tangent arrival. A no-solution result means none was found within the horizon, not permanent impossibility.

Encounter searches sample every 0.25 day, refine bracketed local minima including endpoint intervals, and retain the smallest separation. Faster or more complicated unmodeled motions can defeat finite sampling. Tests compare 0.5-day and 0.125-day scans for one real trajectory, including overlap classifications and closest-point distances; this is a convergence check for that case, not universal certification.

Tests also cover stationary and linearly moving targets with known solutions, toward/away velocity signs, missing arrivals, invalid parameters, root residuals, off-grid minima near boundaries, and a body crossing the segment without meeting the traveling point.

## Reproduce and extend

Run:

```
node tools/analyze-saturn-wave-offsets.mjs
node tools/run-moving-target-experiment.mjs
node tests/moving-target.test.mjs
```

The second script writes [the full experiment report](data/moving-target-experiment.json), including fitted speed, baselines, arrival residuals, required per-cycle speeds, Earth motion, and nine-body proximity records for every trajectory. `lib/moving-target.mjs` exposes reusable arrival, motion, and encounter calculations. These tools run offline using the vendored ephemeris library; there is no runtime UI or pressure-model change.

Next tests should use independently dated events, held-out cycles, alternative phase references, and a predeclared emission rule. A finite-speed-plus-response-delay model adds another parameter and should be evaluated against an equally flexible baseline. Any obstruction, influence-radius, or attenuation rule needs its own stated MMS hypothesis rather than being inferred automatically from an alignment.
