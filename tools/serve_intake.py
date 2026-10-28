"""Run the private, loopback-only RiVViT Intake workbench."""
import argparse
import csv
import hashlib
import json
import secrets
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import date, timedelta
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from intake_store import IntakeStore, ValidationError, ConflictError, encoded

ROOT=Path(__file__).resolve().parents[1]
MAX_BODY=24*1024*1024


def usgs_query_url(params):
    try:
        start=date.fromisoformat(params.get('start',''))
        end=date.fromisoformat(params.get('end',''))
        magnitude=float(params.get('magnitude',4.5))
    except (ValueError,TypeError):
        raise ValidationError('Supply valid start/end dates and minimum magnitude')
    if not 0<=(end-start).days<=366:
        raise ValidationError('Query up to 366 days at a time, with end on or after start')
    if not -2<=magnitude<=10:
        raise ValidationError('Minimum magnitude must be between -2 and 10')
    # Date fields are inclusive calendar days. Avoid silently dropping the final day.
    query={'format':'geojson','starttime':start.isoformat()+'T00:00:00Z',
           'endtime':end.isoformat()+'T23:59:59.999Z','minmagnitude':magnitude,
           'orderby':'time-asc','limit':1000}
    return 'https://earthquake.usgs.gov/fdsnws/event/1/query?'+urllib.parse.urlencode(query)


class IntakeServer(ThreadingHTTPServer):
    daemon_threads=True

    def __init__(self, address, store):
        self.store=store
        self.token=secrets.token_urlsafe(32)
        super().__init__(address,Handler)


class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        # Local records, account text and URLs are not logged.
        pass

    def reply(self, status, body, content_type='application/json; charset=utf-8'):
        data=encoded(body).encode('utf-8') if not isinstance(body,bytes) else body
        self.send_response(status)
        self.send_header('Content-Type',content_type)
        self.send_header('Content-Length',str(len(data)))
        self.send_header('Cache-Control','no-store')
        self.send_header('X-Content-Type-Options','nosniff')
        self.send_header('Referrer-Policy','no-referrer')
        self.send_header('Content-Security-Policy',"default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' data:; connect-src 'self'; object-src 'none'; base-uri 'none'; frame-ancestors 'none'; form-action 'self'")
        self.end_headers()
        self.wfile.write(data)

    def allowed_host(self):
        port=self.server.server_port
        return self.headers.get('Host') in {f'127.0.0.1:{port}',f'localhost:{port}'}

    def do_GET(self):
        if not self.allowed_host():
            return self.reply(403,{'error':'Use the local workbench address.'})
        parsed=urllib.parse.urlsplit(self.path)
        query=dict(urllib.parse.parse_qsl(parsed.query))
        store=self.server.store
        try:
            assets={'/':'index.html','/index.html':'index.html','/app.mjs':'app.mjs','/styles.css':'styles.css'}
            if parsed.path in assets:
                filename=assets[parsed.path]
                mime='text/html; charset=utf-8' if filename.endswith('.html') else 'text/javascript; charset=utf-8' if filename.endswith('.mjs') else 'text/css; charset=utf-8'
                return self.reply(200,(ROOT/'intake'/filename).read_bytes(),mime)
            if parsed.path=='/api/session':
                return self.reply(200,{'app':'rivvit-intake','token':self.server.token,'collections':store.collections(),'workspace':str(store.workspace),'version':'2026-10-28.1'})
            if parsed.path=='/api/collections':
                return self.reply(200,store.collections())
            if parsed.path=='/api/records':
                return self.reply(200,store.list_records(query.get('collection',''),query.get('q',''),query.get('kind',''),query.get('status',''),query.get('suggestion',''),max(0,int(query.get('offset',0))),min(100,max(1,int(query.get('limit',25))))))
            if parsed.path=='/api/record':
                return self.reply(200,store.get_record(query.get('collection',''),query.get('id','')))
            if parsed.path=='/api/summary':
                return self.reply(200,store.summary(query.get('collection','')))
            if parsed.path=='/api/history':
                with store.connect() as db:
                    rows=db.execute('SELECT version,body,saved FROM review_history WHERE collection_id=? AND record_id=? ORDER BY version DESC',(query.get('collection',''),query.get('id',''))).fetchall()
                    return self.reply(200,[{'version':r['version'],'saved':r['saved'],'review':json.loads(r['body'])} for r in rows])
            if parsed.path=='/api/templates/em.csv':
                return self.reply(200,b'timestamp,station,quantity,value,unit,latitude,longitude,place,baseline,baseline_note,threshold,source_url,notes\n','text/csv; charset=utf-8')
            return self.reply(404,{'error':'Not found'})
        except (ValueError,KeyError,TypeError) as error:
            return self.reply(400,{'error':str(error)})

    def do_POST(self):
        if not self.allowed_host():
            return self.reply(403,{'error':'Use the local workbench address.'})
        origins={f'http://127.0.0.1:{self.server.server_port}',f'http://localhost:{self.server.server_port}'}
        if self.headers.get('Origin') not in origins or not secrets.compare_digest(self.headers.get('X-Intake-Token',''),self.server.token):
            return self.reply(403,{'error':'Reload the local workbench before saving.'})
        if self.headers.get('Content-Type','').split(';')[0]!='application/json':
            return self.reply(415,{'error':'JSON request required'})
        try:
            size=int(self.headers.get('Content-Length','0'))
            if not 0<size<=MAX_BODY:
                return self.reply(413,{'error':'Split imports into files smaller than 24 MB.'})
            data=json.loads(self.rfile.read(size),parse_constant=lambda value: (_ for _ in ()).throw(ValidationError('Non-finite JSON number')))
            if not isinstance(data,dict):
                raise ValidationError('An object is required')
            path=urllib.parse.urlsplit(self.path).path
            store=self.server.store
            if path=='/api/import':
                return self.reply(200,store.import_payload(data.get('kind'),data.get('payload'),data.get('name') or 'Imported collection'))
            if path=='/api/seed':
                dataset=json.loads((ROOT/'data/history/wikipedia/1961.json').read_text(encoding='utf-8'))
                return self.reply(200,store.import_payload('wikipedia',dataset,'Wikipedia 1961'))
            if path=='/api/manual':
                return self.reply(200,store.add_manual(data.get('payload') or {},data.get('kind')))
            if path=='/api/review':
                return self.reply(200,store.save_review(data.get('collection'),data.get('id'),data.get('review'),data.get('version'),data.get('status','reviewed')))
            if path=='/api/batch-reading':
                identities=data.get('ids')
                if not isinstance(identities,list) or not 1<=len(identities)<=100:
                    raise ValidationError('Select 1–100 records')
                label=data.get('label')
                if label not in {'novelty','tradition','mixed','neither','unreviewed'}:
                    raise ValidationError('Choose a reading')
                reason=data.get('reason','').strip()
                if label!='unreviewed' and not reason:
                    raise ValidationError('Explain the batch reading')
                # Each outcome is explicit. Concurrent changes are skipped, not overwritten.
                prepared=[(identity,store.get_record(data.get('collection'),identity)) for identity in list(dict.fromkeys(identities))]
                results=[]
                for identity,current in prepared:
                    if current['review'].get('status')=='approved':
                        results.append({'id':identity,'status':'skipped-approved'})
                        continue
                    draft={**current['review'],'label':label,'reason':reason}
                    try:
                        store.save_review(data['collection'],identity,draft,current['version'],'reviewed')
                        results.append({'id':identity,'status':'saved'})
                    except ConflictError:
                        results.append({'id':identity,'status':'skipped-concurrent-change'})
                return self.reply(200,{'results':results})
            if path=='/api/backup':
                bundle=store.review_bundle(data.get('collection'))
                # A complete private backup includes source records so it can restore new intakes.
                bundle['sources']=[{'collection':c,'records':[r['record'] for r in store.rows(c['id'])]} for c in store.collections() if not data.get('collection') or c['id']==data['collection']]
                return self.reply(200,bundle)
            if path=='/api/restore':
                bundle=data.get('payload') or {}
                # Validate a full restore in a temporary workspace before mutating the live DB.
                import tempfile
                with tempfile.TemporaryDirectory(dir=store.workspace) as directory:
                    trial=IntakeStore(directory)
                    for source in bundle.get('sources',[]):
                        c=source['collection']
                        trial.add_collection(c['name'],c['kind'],source['records'],c['metadata'],c['id'])
                    trial.restore_bundle(bundle)
                existing={c['id'] for c in store.collections()}
                if any(s['collection']['id'] in existing for s in bundle.get('sources',[])):
                    raise ConflictError('Restore only into a workspace without these collections. Existing work is not overwritten.')
                for source in bundle.get('sources',[]):
                    c=source['collection']
                    store.add_collection(c['name'],c['kind'],source['records'],c['metadata'],c['id'])
                return self.reply(200,store.restore_bundle(bundle))
            if path=='/api/export-year':
                return self.reply(200,store.export_year(data.get('collection'),int(data.get('year',0))))
            if path=='/api/usgs-query':
                url=usgs_query_url(data)
                request=urllib.request.Request(url,headers={'User-Agent':'RiVViT-Intake/0.1 (https://github.com/myathemagick-netizen/RiVViT)'})
                with urllib.request.urlopen(request,timeout=35) as response:
                    if urllib.parse.urlsplit(response.url).hostname!='earthquake.usgs.gov':
                        raise ValidationError('Unexpected USGS redirect')
                    raw=response.read(12*1024*1024+1)
                    if len(raw)>12*1024*1024:
                        raise ValidationError('Response too large; narrow the query')
                payload=json.loads(raw)
                records,metadata=__import__('intake_store').normalize_usgs(payload)
                metadata['queryUrl']=url
                metadata['possiblyTruncated']=len(records)>=1000
                metadata['coverageNote']='Query cap is 1000 events. A full-size response may be truncated; narrow dates or increase minimum magnitude.'
                result=store.add_collection('USGS '+data['start']+' to '+data['end'],'usgs',records,metadata)
                return self.reply(200,{**result,'possiblyTruncated':metadata['possiblyTruncated']})
            return self.reply(404,{'error':'Not found'})
        except ConflictError as error:
            return self.reply(409,{'error':str(error)})
        except (ValidationError,ValueError,KeyError,TypeError) as error:
            return self.reply(400,{'error':str(error)})
        except (urllib.error.URLError,TimeoutError,OSError) as error:
            return self.reply(502,{'error':'The source or local storage could not be reached: '+str(error)})


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--port',type=int,default=8765)
    parser.add_argument('--workspace',type=Path,default=ROOT/'.cache/intake')
    parser.add_argument('--no-seed',action='store_true',help='Start an empty workspace, for restoring a private backup')
    parser.add_argument('--open-browser',action='store_true',help='Open the local workbench when started interactively')
    args=parser.parse_args()
    store=IntakeStore(args.workspace)
    if not args.no_seed and not store.collections():
        dataset=json.loads((ROOT/'data/history/wikipedia/1961.json').read_text(encoding='utf-8'))
        store.import_payload('wikipedia',dataset,'Wikipedia 1961')
    try:
        server=IntakeServer(('127.0.0.1',args.port),store)
    except OSError as error:
        if args.open_browser:
            try:
                with urllib.request.urlopen(f'http://127.0.0.1:{args.port}/api/session',timeout=2) as response:
                    existing=json.load(response)
                if existing.get('app')=='rivvit-intake':
                    import webbrowser
                    print('RiVViT Intake is already running; opening the existing workbench.',flush=True)
                    webbrowser.open(f'http://127.0.0.1:{args.port}')
                    return
            except (OSError,ValueError):
                pass
        parser.exit(1,f'Could not start the local service: {error}. If port {args.port} is already in use, use the existing workbench or choose --port 8766.\n')
    print(f'RiVViT Intake: http://127.0.0.1:{server.server_port}',flush=True)
    print(f'Private workspace: {store.workspace}',flush=True)
    print('Keep this process running while reviewing. Ctrl+C stops the tool; saved work remains.',flush=True)
    if args.open_browser:
        import threading
        import webbrowser
        timer=threading.Timer(.5,lambda:webbrowser.open(f'http://127.0.0.1:{server.server_port}'))
        timer.daemon=True
        timer.start()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__=='__main__':
    main()
