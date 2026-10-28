# Wikipedia chronology collection

The fifteen curated MMS anchors are not the population needed for a planet-wide, approximately 200-year pattern map. This importer collects broad chronology data first; selection and MMS readings happen downstream. It starts with the author's suggested [1961](https://en.wikipedia.org/wiki/1961) and [January 1961](https://en.wikipedia.org/wiki/January_1961) and extends through all twelve month pages.

## First completed import

1961: **13/13 requested pages parsed; 2,456 source entries**, including 1,330 ordinary event entries, 694 births, 427 deaths and 5 award entries. Dated entries cover all 365 days. These are extracted mentions, not independently verified unique occurrences. The importer flags 150 entries as possible overlaps; more paraphrase duplicates may remain.

- [Full normalized JSON](../data/history/wikipedia/1961.json).
- [Candidate-only JSON](../data/history/wikipedia/1961-candidates.json): 96 entries suggested by the initial rules, not approved MMS readings.
- [Coverage index](../data/history/wikipedia/index.json): requested pages, failures, precision, counts and limitations per year.
- [Editable rules](../data/history-rules.json).

The collection is not loaded into the globe yet. No stable/preview runtime, wave calibration, Saturn calculation or Sirius calculation changes.

## Information retained

Every record has an ID, calendar date or interval, precision, event/birth/death/award kind, source text, linked article entities, source page and revision permalink, section and item anchors, available cited references, topics, review flags, and interpretation metadata. Citations copied from Wikipedia are leads, not independently checked historical sources.

Births and deaths remain separate from other events. A linked country or nationality does not establish a birthplace or death place. Some bullets describe several occurrences or include later context: a mention of a later launch does not turn a March entry into an April launch record.

Locations remain unresolved: linked entities preserve geographic clues, but the importer does not silently convert a person's nationality, an organization, or a museum into an event point. A subsequent resolution stage needs to identify event-location relationships and source coordinates/footprints. This is bulk chronology ingestion, not completed geographic enrichment.

## Novelty / tradition / neither

`classification.label` is the reviewed reading: `novelty`, `tradition`, `mixed`, `neither`, or `unreviewed`. All initial labels are unreviewed.

`classification.suggestion` is a separate, explainable lexical triage. The starter rules look for a small set of opening/innovation or institutional-closure language; both types produce `mixed`, no match produces `unreviewed`. Births/deaths get no automatic directional reading. Topic tags support independent filters for arts, science, politics, conflict, environment, sport, economy and religion. Suggestions are not reliable semantic interpretations: a hypothetical future achievement, a failed invention or a law ending a ban can fool a phrase rule. Review the whole occurrence, not just the matched phrase.

This deliberately avoids forcing every occurrence onto one side of the wave. `neither` is an explicit reviewed decision, not a synonym for “our current rules did not recognize this.” A reviewed neither is omitted from relevant-event exports even if an earlier suggestion said novelty. The master collection stays available so changing an MMS reading does not require redownloading history. Nothing is ranked or classified using the selected wave phase, Saturn position or closeness to an epoch.

A future contextual classifier can propose readings in batches using the author's MMS definitions and return explanations plus uncertainty in the same schema. No external model calls or paid services are configured by this importer. Review files permit accepted interpretations now:

```json
{
  "wp-RECORD_ID": {
    "label": "neither",
    "reviewer": "project-author",
    "note": "Reason this occurrence is outside the current research lens."
  }
}
```

## Run and extend

Python 3 standard library only; no installation of scraping packages or server needed. Run from the repository root. The session used the bundled Python runtime; `python` below means an available Python 3 executable.

```sh
python tools/import_wikipedia_history.py --year 1961
python tools/import_wikipedia_history.py --year 1961 --offline
python tools/import_wikipedia_history.py --start-year 1830 --end-year 2026 --mode year
python tools/import_wikipedia_history.py --start-year 1960 --end-year 1969 --mode both
python tools/import_wikipedia_history.py --year 1961 --offline --reviews my-reviews.json
python tools/export_history_view.py data/history/wikipedia/1961.json --allow-suggestions --output data/history/wikipedia/1961-candidates.json
```

`--mode year` provides broad coverage cheaply; `--mode both` adds the daily month pages where they exist. **Only 1961 has been imported so far.** The range commands show how to expand; they are not claims that the 1830–2026 collection is complete. Earlier years may lack monthly pages. Missing, inaccessible or unsupported pages are recorded as failures; a partial run exits nonzero while preserving its results. Re-running resumes from cached pages. `--refresh` explicitly fetches new revisions; `--offline` never uses the network. The index preserves previously imported years.

Filtered export defaults to reviewed novelty/tradition/mixed records. `--allow-suggestions` also includes unreviewed candidates; `--labels` selects desired readings. Export refuses to overwrite its input. The first candidate export is a review queue, not a historical intensity series.

## Collection method and scaling

The script uses public HTML because API/REST endpoints returned service-unavailable errors in this session. It supplies an identifying User-Agent, serializes requests with at least one second between network fetches, caches pages under ignored `.cache/wikipedia/`, retries transient failures up to three times and preserves revision IDs, retrieval times and HTML hashes. See [MediaWiki API etiquette](https://www.mediawiki.org/wiki/API:Etiquette) for the corresponding Wikimedia request guidance. A current-cache replay is reproducible; `--refresh` intentionally changes the snapshot.

The parser supports chronology headings and nested lists, excluding reference lists, tables, prose-only sections, captions and navigation. Month/year-only dates retain their precision; it does not manufacture a day. Exact same-date/kind/text records merge with provenance; lexical overlap flags only suggest possible duplicates. Broader semantic/event-identity deduplication remains necessary before statistics.

For the globe, use year/month data shards and aggregate counts or densities at wide zoom, then reveal events as time/space narrows. Loading thousands of permanent labels into Quest is not the next rendering step. Track coverage and category separately: English Wikipedia reflects editorial interests and uneven reporting, not every occurrence everywhere. Compare occurrences and collection density without treating missing coverage as inactivity.

## Attribution and verification

Imported/adapted Wikipedia text and derived data files in `data/history/wikipedia/` are marked **CC BY-SA 4.0**, attributed to Wikipedia contributors through article/revision/history links, with transformations identified. This data license is separate from application code. No article images are imported. See [Wikimedia reuse terms](https://foundation.wikimedia.org/wiki/Policy:Terms_of_Use#7._Licensing_of_Content).

`python tests/wikipedia_history_test.py` checks nested date inheritance, intervals, invalid dates, numeric-text ambiguity, births/deaths, reference provenance, excluded navigation, duplicate behavior, triage and reviewed-neither export precedence. The real 1961 run has a per-page manifest. Dataset coverage is not a substitute for checking individual claims or event locations.
