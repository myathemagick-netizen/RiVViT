"""Local intake persistence and source adapters. No third-party dependencies."""
import calendar
import csv
import hashlib
import io
import json
import math
import sqlite3
import uuid
from collections import Counter
from contextlib import contextmanager
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from urllib.parse import urlparse

LABELS = {'novelty','tradition','mixed','neither','unreviewed'}
EVENT_ROLES = {'unspecified','recognition','ceremony','research','discovery','publication','experience','other'}
SCHEMA = 1


class ValidationError(ValueError):
    pass


class ConflictError(ValueError):
    pass


def now():
    return datetime.now(timezone.utc).isoformat()


def encoded(value):
    return json.dumps(value,ensure_ascii=False,allow_nan=False,sort_keys=True)


def text(value, limit=100000):
    if value is None:
        return ''
    if not isinstance(value,str) or len(value)>limit:
        raise ValidationError('Expected text within the field limit')
    return value.strip()


def number(value, label, optional=False):
    if value in (None,'') and optional:
        return None
    if isinstance(value,bool):
        raise ValidationError(label+' must be a number')
    try:
        result=float(value)
    except (TypeError,ValueError):
        raise ValidationError(label+' must be a number')
    if not math.isfinite(result):
        raise ValidationError(label+' must be finite')
    return result


def moment(value):
    value=text(value,80)
    try:
        if len(value)==10:
            return datetime.combine(date.fromisoformat(value),datetime.min.time(),tzinfo=timezone.utc)
        result=datetime.fromisoformat(value.replace('Z','+00:00'))
        if result.tzinfo is None:
            raise ValueError()
        return result.astimezone(timezone.utc)
    except ValueError:
        raise ValidationError('Use YYYY-MM-DD or an ISO timestamp with a timezone')


def checked_time(value):
    if not isinstance(value,dict):
        raise ValidationError('A time record is required')
    start=text(value.get('start'),80)
    end=text(value.get('end') or start,80)
    a,b=moment(start),moment(end)
    if a>b:
        raise ValidationError('End must not precede start')
    precision=value.get('precision','day')
    if precision not in {'instant','day','month','year','interval','bounded'}:
        raise ValidationError('Unknown date precision')
    if precision=='instant' and (len(start)==10 or len(end)==10):
        raise ValidationError('Instant precision requires timezone-qualified timestamps')
    if precision in {'day','month','year','interval','bounded'} and (len(start)!=10 or len(end)!=10):
        raise ValidationError('Calendar precision requires calendar dates')
    if precision=='day' and start!=end:
        raise ValidationError('Different dates require interval or bounded precision')
    if precision=='month' and (a.day!=1 or b.month!=a.month or b.year!=a.year or b.day!=calendar.monthrange(a.year,a.month)[1]):
        raise ValidationError('Month precision requires the first through last day of one month')
    if precision=='year' and (a.month!=1 or a.day!=1 or b.month!=12 or b.day!=31 or b.year!=a.year):
        raise ValidationError('Year precision requires January 1 through December 31')
    return {'start':start,'end':end,'precision':precision,'note':text(value.get('note'),4000)}


def checked_geometry(value):
    if value is None:
        return None
    if not isinstance(value,dict):
        raise ValidationError('Geometry must be GeoJSON or null')
    def point(pair):
        if not isinstance(pair,list) or len(pair)!=2:
            raise ValidationError('Coordinates must be [longitude, latitude]')
        lon,lat=number(pair[0],'Longitude'),number(pair[1],'Latitude')
        if not -180<=lon<=180 or not -90<=lat<=90:
            raise ValidationError('Coordinates outside longitude/latitude bounds')
        return [lon,lat]
    if value.get('type')=='Point':
        return {'type':'Point','coordinates':point(value.get('coordinates'))}
    if value.get('type')=='Polygon':
        rings=value.get('coordinates')
        if not isinstance(rings,list) or not rings or len(rings)>20:
            raise ValidationError('Polygon needs coordinate rings')
        result=[]
        for ring in rings:
            if not isinstance(ring,list) or not 4<=len(ring)<=10000:
                raise ValidationError('Polygon rings need 4–10000 positions')
            positions=[point(p) for p in ring]
            if positions[0]!=positions[-1]:
                raise ValidationError('Polygon rings must be closed')
            result.append(positions)
        return {'type':'Polygon','coordinates':result}
    raise ValidationError('Supported geometry types are Point and Polygon')


def source_urls(raw):
    result=[]
    for source in raw.get('sources',[]):
        if not isinstance(source,dict):
            continue
        result.append({key:source[key] for key in ('url','permalink','revision','page','section','title','references') if key in source})
    return result


def normalize_wikipedia(payload):
    if not isinstance(payload,dict) or not isinstance(payload.get('events'),list):
        raise ValidationError('Expected a RiVViT Wikipedia collection JSON file')
    records=[]
    seen=set()
    for row in payload['events']:
        if not isinstance(row,dict):
            raise ValidationError('Each entry must be an object')
        identity=text(row.get('id'),200)
        if not identity or identity in seen:
            raise ValidationError('Entry IDs must be present and unique')
        seen.add(identity)
        timing=checked_time(row.get('time'))
        body=text(row.get('text'))
        if not body:
            raise ValidationError('An entry is missing source text')
        records.append({'id':identity,'kind':text(row.get('kind') or 'event',80),
                        'title':body[:180],'text':body,'time':timing,
                        'location':{'label':'','geometry':None,'note':'Linked articles are clues, not verified event places.'},
                        'suggestion':row.get('classification',{}).get('suggestion','unreviewed'),
                        'topics':row.get('topics',[]),'sources':source_urls(row),
                        'possibleDuplicates':row.get('possibleDuplicates',[]),'evidenceType':'encyclopedia-entry',
                        'permission':{'allowed':True,'note':'Public Wikipedia text; preserve attribution and CC BY-SA licensing.'},
                        'original':row})
    return records,{'license':payload.get('license'), 'pages':payload.get('pages',[]), 'coverage':payload.get('report',{}),'year':payload.get('year')}


def normalize_usgs(payload):
    if not isinstance(payload,dict) or payload.get('type')!='FeatureCollection' or not isinstance(payload.get('features'),list):
        raise ValidationError('Expected a USGS GeoJSON FeatureCollection')
    records=[]
    seen=set()
    for feature in payload['features']:
        if not isinstance(feature,dict) or feature.get('type')!='Feature':
            raise ValidationError('Invalid earthquake feature')
        identity=text(feature.get('id'),200)
        if not identity or identity in seen:
            raise ValidationError('Earthquake IDs must be present and unique in an import')
        seen.add(identity)
        p=feature.get('properties') or {}
        geometry=feature.get('geometry') or {}
        if geometry.get('type')!='Point':
            raise ValidationError('Earthquakes require Point geometry')
        coordinates=geometry.get('coordinates')
        if not isinstance(coordinates,list) or len(coordinates)<3:
            raise ValidationError('USGS coordinates require longitude, latitude and depth')
        geo=checked_geometry({'type':'Point','coordinates':coordinates[:2]})
        depth=number(coordinates[2],'Depth')
        try:
            timestamp=(datetime(1970,1,1,tzinfo=timezone.utc)+timedelta(milliseconds=number(p.get('time'),'Origin time'))).isoformat()
        except (ValueError,OverflowError,OSError):
            raise ValidationError('Invalid earthquake origin time')
        magnitude=number(p.get('mag'),'Magnitude',optional=True)
        place=text(p.get('place') or 'Location from USGS coordinates',2000)
        title=text(p.get('title') or f'Earthquake: {place}',2000)
        records.append({'id':'usgs-'+identity,'kind':'earthquake','title':title,'text':title,
                        'time':{'start':timestamp,'end':timestamp,'precision':'instant','note':'USGS origin time, UTC.'},
                        'location':{'label':place,'geometry':geo,'note':'Epicentre; depth is retained separately, not a surface footprint.'},
                        'suggestion':'unreviewed','topics':['geology','earthquake'],
                        'sources':[{'url':text(p.get('url') or 'https://earthquake.usgs.gov/',4000),'title':'USGS earthquake '+identity}],
                        'evidenceType':'instrument-catalog','permission':{'allowed':True,'note':'Public USGS catalog; source retained.'},
                        'measurements':{'magnitude':magnitude,'magnitudeType':p.get('magType'),'depthKm':depth,'status':p.get('status'),
                                        'updated':p.get('updated'),'rms':p.get('rms'),'horizontalError':p.get('horizontalError'),
                                        'depthError':p.get('depthError'),'magError':p.get('magError')},'original':feature})
    return records,{'provider':'USGS','feedMetadata':payload.get('metadata',{}),'license':{'name':'USGS source terms','url':'https://www.usgs.gov/information-policies-and-instructions/copyrights-and-credits'}}


def manual_record(payload, kind):
    title=text(payload.get('title'),2000)
    if not title:
        raise ValidationError('A title is required')
    timing=checked_time(payload.get('time'))
    location={'label':text(payload.get('place'),2000),'geometry':checked_geometry(payload.get('geometry')),
              'note':text(payload.get('locationNote'),4000)}
    permission={'allowed':payload.get('publicAllowed') is True,'note':text(payload.get('permissionNote'),4000)}
    if permission['allowed'] and not permission['note']:
        raise ValidationError('Record the basis for public export permission')
    row={'id':kind+'-'+str(uuid.uuid4()),'kind':kind,'title':title,'text':text(payload.get('account') or payload.get('notes')),
         'time':timing,'location':location,'suggestion':'unreviewed',
         'evidenceType':'firsthand-account' if kind=='account' and payload.get('relationship')=='firsthand' else 'retold-account' if kind=='account' else 'instrument-observation',
         'permission':permission,'topics':['reported-experience'] if kind=='account' else ['electromagnetism'],
         'sources':[{'url':text(payload.get('sourceUrl'),4000),'title':text(payload.get('sourceTitle') or 'Local intake record',2000)}],
         'original':payload}
    if kind=='em-observation':
        value=number(payload.get('value'),'Reading')
        baseline=number(payload.get('baseline'),'Baseline',optional=True)
        threshold=number(payload.get('threshold'),'Threshold',optional=True)
        if threshold is not None and threshold<=0:
            raise ValidationError('Deviation threshold must be positive')
        unit=text(payload.get('unit'),100)
        station=text(payload.get('station'),1000)
        quantity=text(payload.get('quantity'),200)
        if not unit or not station or not quantity:
            raise ValidationError('Station, measured quantity and unit are required')
        baseline_note=text(payload.get('baselineNote'),4000)
        if baseline is not None and not baseline_note:
            raise ValidationError('Describe how the baseline was established')
        delta=None if baseline is None else value-baseline
        row['measurements']={'station':station,'quantity':quantity,'value':value,'unit':unit,'baseline':baseline,
                             'baselineNote':baseline_note,'threshold':threshold,'delta':delta,
                             'anomalyCandidate':None if delta is None or threshold is None else abs(delta)>=threshold,
                             'method':'Absolute deviation from a supplied baseline, in the declared reading unit; no causal inference.'}
    else:
        if not row['text']:
            raise ValidationError('An account is required')
        row['accountMetadata']={'relationship':text(payload.get('relationship') or 'unspecified',100),
                                'observerPseudonym':text(payload.get('observerPseudonym'),1000),
                                'recordedAt':now()}
    return row


def normalize_em_csv(content):
    reader=csv.DictReader(io.StringIO(content.lstrip('\ufeff')))
    required={'timestamp','station','quantity','value','unit'}
    if not required.issubset(reader.fieldnames or []):
        raise ValidationError('CSV requires timestamp, station, quantity, value and unit columns')
    result=[]
    for index,row in enumerate(reader,2):
        try:
            geometry=None
            if row.get('longitude') or row.get('latitude'):
                geometry={'type':'Point','coordinates':[number(row.get('longitude'),'Longitude'),number(row.get('latitude'),'Latitude')]}
            record=manual_record({'title':row.get('title') or row['station']+' observation',
                 'time':{'start':row['timestamp'],'end':row['timestamp'],'precision':'day' if len(row['timestamp'])==10 else 'instant'},
                 'place':row.get('place') or row['station'],'geometry':geometry,'station':row['station'],'quantity':row['quantity'],
                 'value':row['value'],'unit':row['unit'],'baseline':row.get('baseline'),'baselineNote':row.get('baseline_note'),
                 'threshold':row.get('threshold'),'notes':row.get('notes'),'sourceUrl':row.get('source_url'),
                 'publicAllowed':False},'em-observation')
            record['id']='em-'+hashlib.sha256(encoded(row).encode()).hexdigest()[:24]
            result.append(record)
        except ValidationError as error:
            raise ValidationError(f'CSV row {index}: {error}')
    if len({r['id'] for r in result})!=len(result):
        raise ValidationError('CSV contains identical duplicate rows; remove duplicates before import')
    return result,{'format':'EM observation CSV','permission':'Private by default; public permission reviewed per record.'}


class IntakeStore:
    def __init__(self, workspace):
        self.workspace=Path(workspace).resolve()
        self.workspace.mkdir(parents=True,exist_ok=True)
        self.path=self.workspace/'intake.sqlite3'
        with self.connect() as db:
            db.executescript('''
            PRAGMA journal_mode=WAL;
            CREATE TABLE IF NOT EXISTS collections(id TEXT PRIMARY KEY,name TEXT NOT NULL,kind TEXT NOT NULL,created TEXT NOT NULL,metadata TEXT NOT NULL);
            CREATE TABLE IF NOT EXISTS records(collection_id TEXT NOT NULL,id TEXT NOT NULL,kind TEXT NOT NULL,start TEXT NOT NULL,search_text TEXT NOT NULL,raw TEXT NOT NULL,PRIMARY KEY(collection_id,id));
            CREATE TABLE IF NOT EXISTS reviews(collection_id TEXT NOT NULL,record_id TEXT NOT NULL,version INTEGER NOT NULL,status TEXT NOT NULL,body TEXT NOT NULL,PRIMARY KEY(collection_id,record_id));
            CREATE TABLE IF NOT EXISTS review_history(sequence INTEGER PRIMARY KEY AUTOINCREMENT,collection_id TEXT NOT NULL,record_id TEXT NOT NULL,version INTEGER NOT NULL,body TEXT NOT NULL,saved TEXT NOT NULL);
            CREATE INDEX IF NOT EXISTS record_dates ON records(collection_id,start);
            ''')

    @contextmanager
    def connect(self):
        db=sqlite3.connect(self.path,timeout=20)
        db.row_factory=sqlite3.Row
        try:
            with db:
                yield db
        finally:
            db.close()

    def add_collection(self, name, kind, records, metadata, identity=None):
        if not records:
            raise ValidationError('No records were found; existing collections are unchanged')
        if len(records)>50000:
            raise ValidationError('Split imports into batches of 50,000 records or fewer')
        identity=identity or hashlib.sha256(encoded({'kind':kind,'records':records,'metadata':metadata}).encode()).hexdigest()[:24]
        with self.connect() as db:
            if db.execute('SELECT id FROM collections WHERE id=?',(identity,)).fetchone():
                return {'id':identity,'records':len(records),'alreadyImported':True}
            db.execute('INSERT INTO collections VALUES(?,?,?,?,?)',(identity,text(name,2000),kind,now(),encoded(metadata)))
            for record in records:
                if record['suggestion'] not in LABELS:
                    record['suggestion']='unreviewed'
                db.execute('INSERT INTO records VALUES(?,?,?,?,?,?)',(identity,record['id'],record['kind'],record['time']['start'],
                            (record['title']+' '+record['text']+' '+' '.join(record.get('topics',[]))).lower(),encoded(record)))
        return {'id':identity,'records':len(records),'alreadyImported':False}

    def import_payload(self, kind, payload, name):
        if kind=='wikipedia':
            records,metadata=normalize_wikipedia(payload)
        elif kind=='usgs':
            records,metadata=normalize_usgs(payload)
        elif kind=='em-csv':
            records,metadata=normalize_em_csv(text(payload,15000000))
        else:
            raise ValidationError('Unknown collection type')
        return self.add_collection(name,kind,records,metadata)

    def add_manual(self, payload, kind):
        if kind not in {'account','em-observation'}:
            raise ValidationError('Unknown manual intake type')
        record=manual_record(payload,kind)
        identity='local-'+kind
        # Local journals are append-only source records; reviews edit overlays.
        with self.connect() as db:
            db.execute('INSERT OR IGNORE INTO collections VALUES(?,?,?,?,?)',(identity,'Accounts' if kind=='account' else 'Electromagnetic observations',kind,now(),encoded({'local':True,'permission':'Private by default'})))
            db.execute('INSERT INTO records VALUES(?,?,?,?,?,?)',(identity,record['id'],record['kind'],record['time']['start'],(record['title']+' '+record['text']).lower(),encoded(record)))
        return {'id':identity,'recordId':record['id'],'records':1}

    def collections(self):
        with self.connect() as db:
            result=[]
            for row in db.execute('SELECT c.*,COUNT(r.id) AS count FROM collections c LEFT JOIN records r ON r.collection_id=c.id GROUP BY c.id ORDER BY c.created'):
                result.append({'id':row['id'],'name':row['name'],'kind':row['kind'],'created':row['created'],'records':row['count'],'metadata':json.loads(row['metadata'])})
            return result

    def get_record(self, collection, identity):
        with self.connect() as db:
            row=db.execute('SELECT raw FROM records WHERE collection_id=? AND id=?',(collection,identity)).fetchone()
            if not row:
                raise ValidationError('Record not found')
            saved=db.execute('SELECT body,version,status FROM reviews WHERE collection_id=? AND record_id=?',(collection,identity)).fetchone()
            raw=json.loads(row['raw'])
            review={**self.initial_review(raw),**json.loads(saved['body'])} if saved else self.initial_review(raw)
            version=saved['version'] if saved else 0
            return {'record':raw,'review':review,'version':version,'issues':self.approval_issues(raw,review)}

    @staticmethod
    def initial_review(raw):
        return {'title':raw['title'],'time':raw['time'],'location':raw['location'],'label':'unreviewed','reason':'',
                'eventRole':'recognition' if raw['kind']=='award' else 'unspecified',
                'researchStatus':'needs-research' if raw['kind']=='award' else 'not-assessed',
                'researchQuestions':'Separate the award/ceremony from each recipient’s underlying work. Find research dates and locations; award-time affiliation is only a lead.' if raw['kind']=='award' else '',
                'researchSources':[],
                'sourceChecked':False,'dateChecked':False,'placeChecked':False,'duplicatesChecked':False,
                'duplicateOf':'','publicAllowed':raw['permission']['allowed'],'permissionNote':raw['permission']['note'],'status':'reviewed'}

    @staticmethod
    def approval_issues(raw, review):
        issues=[]
        if review.get('researchStatus','needs-research' if raw['kind']=='award' else 'not-assessed')=='needs-research':
            issues.append('Resolve the research questions before approving this event for the dataset.')
        if review.get('label') not in {'novelty','tradition','mixed'}:
            issues.append('Choose novelty, tradition or mixed for an included dataset record; neither is excluded.')
        for key,message in [('sourceChecked','Check the source.'),('dateChecked','Check the date or interval.'),('placeChecked','Check the location and its geometry.'),('duplicatesChecked','Complete the duplicate check.')]:
            if review.get(key) is not True:
                issues.append(message)
        if not review.get('location',{}).get('geometry'):
            issues.append('Supply point or regional geometry; a place label alone is not a map location.')
        if not review.get('location',{}).get('label'):
            issues.append('Supply a place label.')
        if not review.get('reason','').strip():
            issues.append('Explain the MMS reading.')
        if review.get('duplicateOf'):
            issues.append('This record is marked as a duplicate and will not be exported.')
        if review.get('publicAllowed') is not True or not review.get('permissionNote','').strip():
            issues.append('Public export permission and its basis are required.')
        return issues

    def prepare_review(self, collection, identity, body, status='reviewed'):
        current=self.get_record(collection,identity)
        raw=current['record']
        if status not in {'reviewed','approved'}:
            raise ValidationError('Invalid review status')
        if not isinstance(body,dict) or body.get('label') not in LABELS:
            raise ValidationError('Unknown MMS reading')
        location=body.get('location') or {}
        checked={'title':text(body.get('title'),2000),'time':checked_time(body.get('time')),
                 'location':{'label':text(location.get('label'),2000),'geometry':checked_geometry(location.get('geometry')),'note':text(location.get('note'),4000)},
                 'label':body['label'],'reason':text(body.get('reason'),12000),'duplicateOf':text(body.get('duplicateOf'),200),
                 'publicAllowed':body.get('publicAllowed') is True,'permissionNote':text(body.get('permissionNote'),4000),
                 'status':status,'savedAt':now()}
        prior={**self.initial_review(raw),**current['review']}
        checked['eventRole']=body.get('eventRole',prior['eventRole'])
        checked['researchStatus']=body.get('researchStatus',prior['researchStatus'])
        checked['researchQuestions']=text(body.get('researchQuestions',prior['researchQuestions']),12000)
        if checked['eventRole'] not in EVENT_ROLES or checked['researchStatus'] not in {'not-assessed','needs-research','ready'}:
            raise ValidationError('Unknown event role or research status')
        sources=body.get('researchSources',prior['researchSources'])
        if not isinstance(sources,list) or len(sources)>100:
            raise ValidationError('Supply a list of up to 100 supporting sources')
        checked['researchSources']=[]
        for source in sources:
            if not isinstance(source,dict):
                raise ValidationError('A supporting source needs a URL')
            url=text(source.get('url'),4000)
            parsed=urlparse(url)
            if parsed.scheme not in {'http','https'} or not parsed.hostname:
                raise ValidationError('Supporting sources need complete http/https URLs')
            checked['researchSources'].append({'url':url,'title':text(source.get('title'),1000)})
        if not checked['title']:
            raise ValidationError('A reviewed title is required')
        for key in ('sourceChecked','dateChecked','placeChecked','duplicatesChecked'):
            checked[key]=body.get(key) is True
        if checked['duplicateOf']:
            if checked['duplicateOf']==identity:
                raise ValidationError('A record cannot duplicate itself')
            self.get_record(collection,checked['duplicateOf'])
        issues=self.approval_issues(raw,checked)
        if status=='approved' and issues:
            raise ValidationError('Cannot approve: '+' '.join(issues))
        return checked,issues

    def save_review(self, collection, identity, body, expected_version, status='reviewed'):
        checked,issues=self.prepare_review(collection,identity,body,status)
        with self.connect() as db:
            db.execute('BEGIN IMMEDIATE')
            old=db.execute('SELECT version FROM reviews WHERE collection_id=? AND record_id=?',(collection,identity)).fetchone()
            version=old['version'] if old else 0
            if expected_version!=version:
                raise ConflictError('This review changed in another session. Reload the record before saving.')
            version+=1
            db.execute('INSERT OR REPLACE INTO reviews VALUES(?,?,?,?,?)',(collection,identity,version,status,encoded(checked)))
            db.execute('INSERT INTO review_history(collection_id,record_id,version,body,saved) VALUES(?,?,?,?,?)',(collection,identity,version,encoded(checked),now()))
        return {'review':checked,'version':version,'issues':issues}

    def rows(self, collection):
        with self.connect() as db:
            return [{'record':json.loads(r['raw']),'review':json.loads(r['body']) if r['body'] else None,'version':r['version'] or 0}
                    for r in db.execute('SELECT r.raw,v.body,v.version FROM records r LEFT JOIN reviews v ON v.collection_id=r.collection_id AND v.record_id=r.id WHERE r.collection_id=? ORDER BY r.start,r.id',(collection,))]

    def list_records(self, collection, query='',kind='',status='',suggestion='',offset=0,limit=25):
        result=[]
        for row in self.rows(collection):
            raw,review=row['record'],row['review']
            label=review['label'] if review else 'unreviewed'
            state='excluded' if label=='neither' or review and review.get('duplicateOf') else review['status'] if review else 'unreviewed'
            if kind and raw['kind']!=kind or suggestion and raw['suggestion']!=suggestion:
                continue
            if status=='needs-place':
                if (review or raw).get('location',{}).get('geometry'):
                    continue
            elif status=='needs-research':
                if (review or {}).get('researchStatus','needs-research' if raw['kind']=='award' else 'not-assessed')!='needs-research':
                    continue
            elif status and state!=status:
                continue
            title=review['title'] if review else raw['title']
            if query.lower() not in (title+' '+raw['text']+' '+' '.join(raw.get('topics',[]))).lower():
                continue
            result.append({'id':raw['id'],'title':title,'time':review['time'] if review else raw['time'],'kind':raw['kind'],
                           'status':state,'label':label,'suggestion':raw['suggestion'],'duplicates':len(raw.get('possibleDuplicates',[]))})
        return {'total':len(result),'offset':offset,'records':result[offset:offset+limit]}

    def summary(self, collection):
        rows=self.rows(collection)
        months=[0]*12
        coarse=0
        years=Counter()
        statuses=Counter()
        for row in rows:
            raw,review=row['record'],row['review']
            timing=(review or raw)['time']
            start=moment(timing['start'])
            if timing['precision'] in {'day','instant'}:
                months[start.month-1]+=1
            else:
                coarse+=1
            years[start.year]+=1
            label=(review or {}).get('label','unreviewed')
            statuses['excluded' if label=='neither' or review and review.get('duplicateOf') else review['status'] if review else 'unreviewed']+=1
        return {'records':len(rows),'kinds':dict(Counter(r['record']['kind'] for r in rows)),
                'statuses':dict(statuses),'years':dict(years),'months':months,'coarseDatesExcludedFromMonths':coarse,
                'withGeometry':sum(bool((r['review'] or r['record'])['location'].get('geometry')) for r in rows),
                'possibleOverlaps':sum(bool(r['record'].get('possibleDuplicates')) for r in rows)}

    def review_bundle(self, collection):
        with self.connect() as db:
            if collection:
                rows=db.execute('SELECT collection_id,record_id,version,body FROM reviews WHERE collection_id=?',(collection,)).fetchall()
            else:
                rows=db.execute('SELECT collection_id,record_id,version,body FROM reviews').fetchall()
            collections=self.collections()
            return {'schemaVersion':SCHEMA,'type':'rivvit-intake-reviews','exportedAt':now(),
                    'collections':[c for c in collections if not collection or c['id']==collection],
                    'history':[{'collection':r['collection_id'],'recordId':r['record_id'],'version':r['version'],'review':json.loads(r['body']),'saved':r['saved']}
                               for r in db.execute('SELECT * FROM review_history WHERE (? IS NULL OR collection_id=?) ORDER BY sequence',(collection,collection))],
                    'reviews':[{'collection':r['collection_id'],'recordId':r['record_id'],'version':r['version'],'review':json.loads(r['body'])} for r in rows]}

    def restore_bundle(self, payload):
        if payload.get('type')!='rivvit-intake-reviews' or not isinstance(payload.get('reviews'),list):
            raise ValidationError('Expected a RiVViT review bundle')
        # Add missing source collections first by importing their source files.
        # Backups restore as reviewed drafts, never silently re-approve publication.
        validated=[]
        seen=set()
        for row in payload['reviews']:
            key=(row['collection'],row['recordId'])
            if key in seen:
                raise ValidationError('Duplicate review in backup')
            seen.add(key)
            current=self.get_record(row['collection'],row['recordId'])
            if current['version']:
                raise ConflictError('Restore requires records without existing reviews; existing work is not overwritten.')
            checked,_=self.prepare_review(row['collection'],row['recordId'],row['review'],'reviewed')
            validated.append((row,checked))
        histories=[]
        versions={}
        history_keys=set()
        for row in payload.get('history',[]):
            key=(row['collection'],row['recordId'])
            version=row.get('version')
            if key not in seen or not isinstance(version,int) or isinstance(version,bool) or version<1 or (*key,version) in history_keys:
                raise ValidationError('Invalid or duplicate archived review revision')
            history_keys.add((*key,version))
            clean,_=self.prepare_review(*key,row['review'],'reviewed')
            clean['status']='approved' if row['review'].get('status')=='approved' else 'reviewed'
            moment(row['saved'])
            histories.append((row,clean))
            versions[key]=max(versions.get(key,0),version)
        with self.connect() as db:
            db.execute('BEGIN IMMEDIATE')
            for row,clean in histories:
                db.execute('INSERT INTO review_history(collection_id,record_id,version,body,saved) VALUES(?,?,?,?,?)',(row['collection'],row['recordId'],row['version'],encoded(clean),row['saved']))
            for row,checked in validated:
                if db.execute('SELECT 1 FROM reviews WHERE collection_id=? AND record_id=?',(row['collection'],row['recordId'])).fetchone():
                    raise ConflictError('A review changed while restoring; nothing was restored.')
                version=versions.get((row['collection'],row['recordId']),0)+1
                db.execute('INSERT INTO reviews VALUES(?,?,?,?,?)',(row['collection'],row['recordId'],version,'reviewed',encoded(checked)))
                db.execute('INSERT INTO review_history(collection_id,record_id,version,body,saved) VALUES(?,?,?,?,?)',(row['collection'],row['recordId'],version,encoded(checked),now()))
        return {'restored':len(validated),'status':'reviewed'}

    def export_year(self, collection, year):
        if not 1<=year<=9998:
            raise ValidationError('Invalid export year')
        events=[]
        for row in self.rows(collection):
            raw,review=row['record'],row['review']
            if not review or review['status']!='approved' or self.approval_issues(raw,review):
                continue
            if not moment(review['time']['start']).year<=year<=moment(review['time']['end']).year:
                continue
            events.append({'id':raw['id'],'kind':raw['kind'],'title':review['title'],'text':raw['text'],
                           'eventRole':review.get('eventRole','unspecified'),
                           'time':review['time'],'location':review['location'],'topics':raw.get('topics',[]),
                           'interpretation':{'label':review['label'],'reason':review['reason']},
                           'sources':source_urls(raw)+review.get('researchSources',[]),'evidenceType':raw['evidenceType'],
                           **({'measurements':raw['measurements']} if 'measurements' in raw else {})})
        if not events:
            raise ValidationError('No approved, export-permitted records with suitable geometry overlap this year.')
        meta=next((c for c in self.collections() if c['id']==collection),None)
        return {'schemaVersion':SCHEMA,'type':'rivvit-reviewed-year','year':year,'collection':collection,'exportedAt':now(),
                'license':meta['metadata'].get('license') if meta else None,
                'sourcePages':meta['metadata'].get('pages',[]) if meta else [],
                'records':len(events),'events':events,'note':'Explicit local export; not published to the public map.'}
