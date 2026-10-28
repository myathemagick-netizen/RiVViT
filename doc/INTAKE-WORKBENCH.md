# RiVViT Intake

A working local intake and review tool, separate from the public globe. Its code is in `intake/`, with a Python standard-library service in `tools/serve_intake.py`. It loads the actual 2,456-entry 1961 collection, not the earlier six-record design sample.

## Start

On this Windows workstation, double-click **Start RiVViT Intake.cmd** in the repository root. It uses the bundled Python runtime when present, otherwise the Windows Python launcher. It opens `http://127.0.0.1:8765/`. Keep the serving window open while working; closing it stops the service, not the saved data. Starting it again reopens the workspace. A recognized existing intake service is reused.

Alternatively, run with an available Python 3 interpreter:

```sh
python tools/serve_intake.py
python tools/serve_intake.py --workspace "D:/Private Research/RiVViT"
```

The first run imports the bundled Wikipedia 1961 dataset if the workspace is empty. Other Wikipedia collections produced by `tools/import_wikipedia_history.py` can be imported through **Sources & intake**. Reimporting the exact same collection is idempotent.

This is an in-house single-user tool. It is not a GitHub Pages application or a shared authenticated service. It binds only to IPv4 loopback. No cloud storage, third-party scripts, account sign-in or paid model is required. Remote USGS queries need network access; file imports and existing records work offline.

## Where the data goes

The default workspace is `.cache/intake/`, explicitly ignored by Git. SQLite stores imported originals, review overlays and review revision history. This default is a private ignored directory inside the checkout, **not** a directory physically outside the checkout. Use `--workspace` to choose a location outside it, and back it up before moving or archiving the checkout.

The local service serves only its UI assets and explicit API routes; it does not expose a general file server for the repository or private workspace. Writes require a per-run token and matching local Origin/Host. These are safeguards for a local tool, not a replacement for authentication if hosted remotely.

The UI's workspace footer shows the active data directory. **Download private backup** includes original source records, current reviews, source manifests and saved review history. It can contain private accounts. It is not an approved public dataset.

To restore, start a new empty workspace without auto-seeding:

```sh
python tools/serve_intake.py --workspace "D:/Private Research/Restored RiVViT" --no-seed --port 8766
```

Choose **Restore backup**. Existing collections/reviews are not overwritten. Source contents and reviews are validated in a temporary workspace before restore. Restored current reviews become **reviewed drafts**, even if previously approved; their history is retained. Re-approve before creating new public exports. The browser currently accepts files below 23 MB; use smaller source batches/collections as the workspace grows. Whole-workspace backups above that size should be retained as SQLite workspace backups until streaming/split restore is added; do not rely on oversized browser exports as the only backup.

## Review desk

- Search source text and topics; filter kind, review status, candidate reading or missing geometry. Queue pages contain 25 entries.
- Read the original text, revision links, citations and available full source record. All imported text is displayed as text, never executed markup.
- Edit the reviewed title, date/interval and precision, place label and geometry. The original is immutable. Month/year precision uses a full envelope; timestamps require a timezone. Year-only entries are labeled as year-only in the queue.
- Record whether an entry concerns recognition, ceremony, research, discovery or publication. Awards default to recognition and **Needs research**. Research progress/questions and supporting URLs are available in a collapsible panel; unresolved research blocks approval. Supporting links and event role survive backup and approved export. The role does not automatically assign an MMS reading or manufacture a ceremony/discovery date.
- Place entry accepts Wikipedia DMS text (`59°19′46″N 18°4′7″E`), a GeoHack link, or decimal **latitude, longitude**. **Use pasted coordinates** converts it into the internal GeoJSON order without marking the location checked. Numeric controls and region polygons are under Advanced. City coordinates are not automatically venue/laboratory coordinates.
- Point geometry uses **longitude, latitude**, in degrees. Regions can use a closed GeoJSON Polygon. This version validates coordinate bounds and closed rings; it does not certify polygon topology or independently verify places.
- Set a reading: novelty, tradition, mixed, neither or unreviewed; record a reason. Candidate rules are only suggestions. Check source/date/place/duplicates separately.
- Compare flagged possible overlaps and, if appropriate, record another entry's ID under “Duplicate of.” Records remain in the collection. Cross-collection entity/event reconciliation and automatic semantic merging remain future work.
- Changes autosave after a short pause, with **Save review now** available. Before switching records or views, pending changes are flushed. Saved versions guard against overwriting changes from another browser session. Invalid drafts remain on screen with an error rather than being silently discarded.
- Selecting queue checkboxes allows **batch readings**, with a shared reason. This never approves records; already approved records are skipped and outcomes are reported. Batch operations validate IDs before writes; individual concurrent changes are skipped rather than overwritten.

Saving a review does not approve it. Any subsequent edit to an approved record resets the current status to a reviewed draft. Neither/duplicate records are excluded from included exports but remain available for future reinterpretation.

## Source-specific intake

### Wikipedia / chronology

Load 1961 or import a yearly RiVViT chronology JSON. Source attribution, revision links and CC BY-SA metadata are retained. Place names and coordinates remain unresolved until reviewed; linked nationality is not birthplace. The source collection's import coverage manifest is visible in Sources.

### USGS earthquakes

Import a USGS GeoJSON FeatureCollection or use the bounded catalog query form. Query dates include the complete final UTC day. Queries are limited to 366 days and 1,000 returned events. A full-size response is flagged as possibly truncated; narrow the interval or increase minimum magnitude. These limits do not imply complete catalog coverage.

Origin time, event ID, epicentre longitude/latitude, depth in km, magnitude and type, update/status fields and available errors remain with the record. Depth is not used as a latitude/longitude coordinate. Source updates produce separate snapshots; event IDs allow later reconciliation without silently changing reviewed originals. The tool does not infer novelty/tradition from magnitude or automatically approve coordinates merely because USGS supplied them.

The adapter follows the [USGS GeoJSON format](https://earthquake.usgs.gov/earthquakes/feed/v1.0/geojson.php) and [catalog query interface](https://earthquake.usgs.gov/fdsnws/event/1/).

### Electromagnetic observations

Enter one reading or import CSV using the downloadable header template. Required columns: `timestamp,station,quantity,value,unit`. Optional fields include coordinates, place, baseline, baseline note, deviation threshold and source URL. CSV timestamps must be timezone-qualified or explicitly day-only.

Readings default to private. If a baseline and positive threshold are provided, the adapter computes `delta = reading - baseline` and flags `abs(delta) >= threshold`, in the same declared units. A baseline requires a description of its origin/method. This is an explicit candidate test on supplied values, not a discovered natural baseline or explanation of cause. Raw values, units and notes remain intact. Continuous-series resampling, calibrated baselines and interval detection are future adapters, not features already implemented.

### Anecdotal accounts

Record firsthand/retold status, actual date or uncertainty interval, a named place and optional geometry, the account, optional pseudonym and source URL. **Private / no public export** is the default. Public permission requires a stated basis and later dataset approval. Observer pseudonyms and account metadata are omitted from public year files; the account text itself must still be reviewed for identifying details before permission is granted. Attachments are not uploaded in this version; references can be recorded in notes/source links.

## From review to year file

**Approve for dataset** requires an included MMS reading with a reason, checked source/date/location/duplicates, suitable Point/Polygon geometry, no duplicate-of designation, and explicit public-export permission with its basis. Partial dates retain their uncertainty. Neither/unreviewed records cannot be approved as included events.

**Year overview → Export approved year** downloads only eligible approved records whose date/interval overlaps that year. It retains source links, collection license/provenance, evidence type, reviewed time/location, measurements and the separate MMS interpretation. It omits private source originals and observer metadata. Downloading does not change the live map or commit anything to Git.

The monthly coverage chart includes exact-day/instant entries only. Coarse dates/intervals are counted separately; year-only records are not manufactured January events. Duplicate mentions remain possible. Collection coverage is not an intensity measurement.

The export type is `rivvit-reviewed-year`. Wiring these files into globe layers is the next application step; the current public globe is unchanged.

The first physics Nobel entry has an expandable, manually researched brief with primary/institutional sources. It illustrates separating Hofstadter's Stanford work, a 1953 publication, Mössbauer's Heidelberg work and award recognition. It is not an automatic biography-research service and does not create linked child events yet. See [the worked research case](NOBEL-RESEARCH-CASE.md). Original records and the user's saved edits are preserved.

## Validation and limits

`python tests/intake_test.py` covers immutable source records, restart persistence/history, idempotent imports, optimistic version conflicts, time/geometry validation, private-account and neither exclusion, polygon exports, atomic review restore, USGS units/coordinate order, EM baseline rules, inclusive query dates and local API isolation. Browser checks exercise the real collection, save/reload, private account intake/export blocking, measurement fields and overview. Synthetic QA records are kept in a separate ignored workspace, not the working collection.

Source facts and permissions still require reviewer judgment. No automatic contextual MMS model, background harvesting, shared reviewer accounts, source attachment storage or automated publishing is configured. The UI and adapters provide a functioning local review/export boundary now; new adapters can reuse the same record/review structure.
