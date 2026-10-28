"""Bulk chronology importer: public HTML, cached requests, reproducible JSON.

Example: python tools/import_wikipedia_history.py --year 1961
Range:   python tools/import_wikipedia_history.py --start-year 1830 --end-year 2026
"""
import argparse
import hashlib
import json
import re
import sys
import time
import urllib.error
import urllib.request
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import quote
from wikipedia_history import MONTHS, classify, extract_page, merge_and_flag

ROOT = Path(__file__).resolve().parents[1]
AGENT = 'RiVViT-Research/0.1 (https://github.com/myathemagick-netizen/RiVViT; historical chronology research)'
LICENSE = {'name':'CC BY-SA 4.0','url':'https://creativecommons.org/licenses/by-sa/4.0/',
           'attribution':'Wikipedia contributors; per-page source and history links in manifest.',
           'changes':'Dated list items extracted, reference markers removed, dates structured, exact duplicates merged, topic and interpretation candidate metadata added. No source text independently fact-checked.'}


def write_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(path.suffix+'.tmp')
    temp.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    temp.replace(path)


def fetch_page(title, args):
    path = args.cache/(title+'.html')
    meta_path = args.cache/(title+'.metadata.json')
    url = 'https://en.wikipedia.org/wiki/'+quote(title)
    if path.exists() and not args.refresh:
        raw = path.read_bytes()
        metadata = json.loads(meta_path.read_text(encoding='utf-8')) if meta_path.exists() else {
            'retrievedAt':datetime.fromtimestamp(path.stat().st_mtime,timezone.utc).isoformat(),
            'retrievalNote':'Cached HTML; retrieval timestamp taken from cache file modification time.'}
    else:
        if args.offline:
            raise RuntimeError('Not cached in offline mode')
        raw = None
        for attempt in range(3):
            time.sleep(args.delay if attempt == 0 else max(args.delay,2**attempt))
            try:
                request = urllib.request.Request(url,headers={'User-Agent':AGENT,'Accept':'text/html'})
                with urllib.request.urlopen(request,timeout=30) as response:
                    raw = response.read()
                    if 'text/html' not in response.headers.get('Content-Type',''):
                        raise RuntimeError('Unexpected content type')
                break
            except urllib.error.HTTPError as error:
                if error.code not in {429,500,502,503,504} or attempt == 2:
                    raise
            except (TimeoutError,urllib.error.URLError):
                if attempt == 2:
                    raise
        metadata = {'retrievedAt':datetime.now(timezone.utc).isoformat()}
        args.cache.mkdir(parents=True,exist_ok=True)
        path.write_bytes(raw)
    html = raw.decode('utf-8')
    revision = re.search(r'wgRevisionId[^\d]+(\d+)',html)
    if not revision:
        revision = re.search(r'oldid=(\d+)',html)
    if not revision:
        raise RuntimeError('No revision identifier; refusing an untraceable page')
    if 'mw-parser-output' not in html:
        raise RuntimeError('Article HTML not found')
    revision = int(revision[1])
    source = {**metadata,'title':title,'url':url,'revision':revision,
              'permalink':f'https://en.wikipedia.org/w/index.php?title={quote(title)}&oldid={revision}',
              'historyUrl':f'https://en.wikipedia.org/w/index.php?title={quote(title)}&action=history',
              'sha256':hashlib.sha256(raw).hexdigest(),'license':LICENSE['name']}
    write_json(meta_path,source)
    return html, source


def import_year(year, args, rules, reviews):
    titles = ([str(year)] if args.mode in {'year','both'} else []) + ([f'{m}_{year}' for m in MONTHS] if args.mode in {'month','both'} else [])
    pages, records = [], []
    for title in titles:
        try:
            html, source = fetch_page(title,args)
            extracted, audit = extract_page(html,title,source)
            records.extend(extracted)
            pages.append({**source,**audit})
            print(f'{title}: {len(extracted)} records ({audit["status"]})',flush=True)
        except (OSError,ValueError,RuntimeError) as error:
            pages.append({'title':title,'status':'failed','error':str(error)})
            print(f'{title}: FAILED {error}',file=sys.stderr,flush=True)
    result = merge_and_flag(records)
    for record in result:
        record['classification'],record['topics'] = classify(record,rules)
        review = reviews.get(record['id'])
        if review:
            label = review.get('label')
            if label not in {'novelty','tradition','mixed','neither','unreviewed'}:
                raise ValueError('Invalid review label for '+record['id'])
            record['classification'].update(label=label,reviewRequired=label=='unreviewed',review=review)
    views = {'noveltyCandidates':[],'traditionCandidates':[],'mixedCandidates':[],'unreviewed':[],
             'reviewedNovelty':[],'reviewedTradition':[],'reviewedMixed':[],'excludedNeither':[],'births':[],'deaths':[]}
    for record in result:
        c = record['classification']
        candidate = {'novelty':'noveltyCandidates','tradition':'traditionCandidates','mixed':'mixedCandidates'}.get(c['suggestion'])
        if candidate:
            views[candidate].append(record['id'])
        label_view = {'novelty':'reviewedNovelty','tradition':'reviewedTradition','mixed':'reviewedMixed','neither':'excludedNeither','unreviewed':'unreviewed'}[c['label']]
        views[label_view].append(record['id'])
        if record['kind'] in {'birth','death'}:
            views[record['kind']+'s'].append(record['id'])
    complete = all(page['status']=='parsed' for page in pages)
    report = {
        'completeRequestedPages':complete,'pagesRequested':len(titles),'pagesParsed':sum(p['status']=='parsed' for p in pages),
        'pageFailures':[p['title'] for p in pages if p['status']!='parsed'],
        'sourceMentions':len(records),'exactTextDuplicatesMerged':len(records)-len(result),'records':len(result),
        'kinds':dict(Counter(r['kind'] for r in result)),
        'datePrecision':dict(Counter(r['time']['precision'] for r in result)),
        'candidateSuggestions':dict(Counter(r['classification']['suggestion'] for r in result)),
        'recordsFlaggedForPossibleDuplicates':sum(bool(r.get('possibleDuplicates')) for r in result),
        'daysRepresented':len({r['time']['start'] for r in result if r['time']['precision']=='day'}),
        'locationsVerified':0,
        'limitations':['Not a complete record of world history; English Wikipedia has editorial, regional and temporal coverage biases.',
                      'Completeness means requested pages parsed, not that every event or bullet was extracted.',
                      'List-item parser excludes tables, prose-only sections, figures and navigation. Compound bullets may retain several occurrences.',
                      'Paraphrase duplicates remain pending review; mention counts are not independent event counts.',
                      'Birth/death location and event location are unresolved; linked entities are not map pins.',
                      'Candidate rules are lexical triage, not final MMS readings. No automatic neither/deletion.']
    }
    output = {'schemaVersion':1,'year':year,'language':'en','license':LICENSE,'rules':rules,
              'report':report,'pages':pages,'views':views,'events':result}
    write_json(args.output/f'{year}.json',output)
    return {'year':year,'file':f'{year}.json',**report}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--year',type=int)
    parser.add_argument('--start-year',type=int)
    parser.add_argument('--end-year',type=int)
    parser.add_argument('--mode',choices=['year','month','both'],default='both')
    parser.add_argument('--cache',type=Path,default=ROOT/'.cache/wikipedia')
    parser.add_argument('--output',type=Path,default=ROOT/'data/history/wikipedia')
    parser.add_argument('--rules',type=Path,default=ROOT/'data/history-rules.json')
    parser.add_argument('--reviews',type=Path,help='JSON object keyed by record ID; values include label and review notes')
    parser.add_argument('--offline',action='store_true')
    parser.add_argument('--refresh',action='store_true')
    parser.add_argument('--delay',type=float,default=1.0)
    args = parser.parse_args()
    if args.year is not None and (args.start_year is not None or args.end_year is not None):
        parser.error('Use --year OR --start-year/--end-year')
    start = args.year if args.year is not None else args.start_year or 1961
    end = args.year if args.year is not None else args.end_year or start
    if not 1 <= start <= end <= 9998:
        parser.error('Invalid year range')
    if args.delay < 1:
        parser.error('Request delay must be at least one second')
    if args.offline and args.refresh:
        parser.error('--offline and --refresh cannot be combined')
    rules = json.loads(args.rules.read_text(encoding='utf-8'))
    reviews = json.loads(args.reviews.read_text(encoding='utf-8')) if args.reviews else {}
    reports = [import_year(year,args,rules,reviews) for year in range(start,end+1)]
    # Preserve earlier years when extending a collection.
    index_path = args.output/'index.json'
    previous = json.loads(index_path.read_text(encoding='utf-8')).get('years',[]) if index_path.exists() else []
    by_year = {row['year']:row for row in previous+reports}
    write_json(index_path,{'schemaVersion':1,'license':LICENSE,'years':sorted(by_year.values(),key=lambda r:r['year'])})
    for row in reports:
        print(f"SUMMARY {row['year']}: {row['records']} records, {row['pagesParsed']}/{row['pagesRequested']} pages, {row['candidateSuggestions']}",flush=True)
    return 0 if all(row['completeRequestedPages'] for row in reports) else 2


if __name__ == '__main__':
    sys.exit(main())
