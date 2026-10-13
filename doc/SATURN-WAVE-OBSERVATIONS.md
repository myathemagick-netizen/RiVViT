# Saturn and Novelty Wave observations

Recorded 2026-10-13 from the user's RiVViT comparisons and follow-up calculations. These are research notes for the MMS pataphysical model. The observed astronomical geometry, the configured wave, and the proposed mechanism are kept distinct.

## Observation 1 The crest offset

The user proposes that the interval between Saturn's maximum north-facing orientation and the Novelty Wave crest represents time for a chronon-pressure wave to reach Earth, break through, and inspire people. This is a candidate MMS interpretation, not a measured transit time.

For this calculation, a Saturn crest means the maximum **positive Earth-facing ring-plane opening**, not the north pole pointing directly at Earth. RiVViT's current cosine wave has a fixed 29.5-year period, 365.2425 days per model year, and the provisional **1931-07-01** crest reference. That reference is editable calibration, not an asserted date for Dalí's painting.

Seven calculated wave crests lie in 1830–2026. Their mean offset after the nearest cycle's Saturn north-facing maximum is **728.23 days**, or **23.93 months / 1.994 model years**. Offsets range from **1.743 to 2.202 years**.

| Saturn north-facing maximum | Calculated MMS crest | Offset, days | Distance at Saturn maximum, AU | Distance at MMS crest, AU |
|---|---|---:|---:|---:|
| 1840-11-05 | 1842-12-30 | 784.88 | 10.846 | 11.027 |
| 1870-10-01 | 1872-06-29 | 636.76 | 10.273 | 9.027 |
| 1899-10-30 | 1901-12-30 | 790.91 | 10.756 | 11.014 |
| 1929-09-28 | 1931-07-01 | 640.30 | 10.179 | 9.025 |
| 1958-10-24 | 1960-12-29 | 797.46 | 10.649 | 11.001 |
| 1988-09-25 | 1990-06-30 | 643.14 | 10.097 | 9.025 |
| 2017-10-16 | 2019-12-29 | 804.15 | 10.529 | 10.990 |

Dates are approximate calendar-day renderings of model extrema; offsets retain the underlying sub-day calculation. The peak search uses a five-day grid within six years on either side of each crest, then refines the winning neighborhood. The small annual Earth-viewing oscillations are retained rather than smoothed away, so this definition selects a local annual high within each broad Saturn maximum.

### Named epochs are a separate comparison

Using July 1 as a sample for each year-only named MMS crest gives a mean offset of **2.138 years**, with a **0.745–3.705-year** range. This should not be substituted for the fixed-wave result.

| Named crest year | Mid-year sample offset, years |
|---|---:|
| 1842 | 1.651 |
| 1871 | 0.745 |
| 1901 | 1.666 |
| 1931 | 1.753 |
| 1961 | 2.685 |
| 1991 | 2.762 |
| 2021 | 3.705 |

Year-only markers are not exact creative-event dates. Changing the wave reference shifts the calculated mean offset; the approximately two-year result is therefore a property of the current calibration, not an independently discovered propagation delay.

## Observation 2 Distance and offset variation

The user proposes that changing Earth–Saturn distance contributes to the varying offset. The same seven cycles show greater distances generally accompanying longer offsets.

At Saturn's north-facing maxima, distance ranges from **10.097 to 10.846 AU**. Expressed as maximum divided by minimum minus one, that is a **7.42%** spread. The delay spread, calculated the same way, is **26.29%**. A simple model using departure-date distance divided by one fixed speed would not reproduce the full spread from these distances alone.

At the calculated MMS crests, distances alternate more strongly: roughly **9 AU versus 11 AU**. The 29.5-year period also alternates crests between mid-year and year-end, so Earth's seasonal orbital position and the configured calendar phase contribute to this pattern. The seven rows are not independent evidence of a transmission mechanism.

For reproducibility, the Pearson correlation between maximum-date distance and offset is **0.899**; between crest-date distance and offset it is **0.996**. These are descriptive statistics for a small, calibration-dependent sample, not causal tests. AU means astronomical unit, approximately the mean Earth–Sun distance.

The distance values use Astronomy Engine's light-time-corrected geocentric vectors. They are astronomical distances at the listed observation dates, not a solved path for the hypothetical chronon wave. No propagation speed has been measured or adopted in RiVViT.

## Proposed next test

Define the hypothetical emission event explicitly, then use Saturn's position at departure and Earth's position at arrival in a common inertial frame. Test whether one proposed speed, or a speed plus a separately specified response delay, predicts the offsets across cycles. Keep the model reference and independently dated cultural events fixed during that test; do not tune each epoch separately. Compare results against the simpler phase/calendar explanation.

## Reproduction

Run `node tools/analyze-saturn-wave-offsets.mjs` from the repository. It regenerates [the full calculation record](data/saturn-wave-observations.json), including the fixed-wave rows, named-year midpoint rows, averages, distances, and correlations. Inputs are `lib/saturn.mjs`, the pinned Astronomy Engine 2.1.19 module, `lib/novelty-wave.mjs`, and `data/novelty-events.json`.

Astronomy model sources and the existing JPL reference check are documented in [SATURN.md](SATURN.md). The wave calibration and marker precision are documented in [NOVELTY-WAVE.md](NOVELTY-WAVE.md).

## Moving-target extension

The user subsequently proposed accounting for Earth moving toward or away from the wave and for bodies between Earth and Saturn. [Moving-target propagation experiment](MOVING-TARGET-EXPERIMENT.md) records the implemented constant-speed experiment, comparison baselines, and the distinction between a path alignment and a same-time body encounter.
