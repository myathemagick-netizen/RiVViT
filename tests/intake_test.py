import copy
import json
import sys
import tempfile
import threading
import unittest
import urllib.error
import urllib.request
from pathlib import Path

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from intake_store import IntakeStore,ValidationError,ConflictError,checked_time,normalize_usgs,normalize_em_csv,manual_record
from serve_intake import IntakeServer,usgs_query_url


def wiki():
    return {'year':1961,'license':{'name':'CC BY-SA 4.0'},'pages':[{'revision':123,'url':'https://en.wikipedia.org/wiki/1961'}],
            'events':[{'id':'a','kind':'event','text':'A sourced occurrence.','time':{'start':'1961-04-12','end':'1961-04-12','precision':'day'},
                       'sources':[{'url':'https://example.org/history','revision':123}],'classification':{'suggestion':'novelty'},'topics':['science']},
                      {'id':'b','kind':'event','text':'Another sourced occurrence.','time':{'start':'1961-05-01','end':'1961-05-01','precision':'day'},
                       'sources':[],'classification':{'suggestion':'tradition'},'topics':[]}]}


def earthquake():
    return {'type':'FeatureCollection','metadata':{'count':1},'features':[{'type':'Feature','id':'test-id','properties':{'time':0,'mag':0,'magType':'mw','place':'Test location','status':'reviewed','url':'https://earthquake.usgs.gov/test'},'geometry':{'type':'Point','coordinates':[20,10,7.5]}}]}


class StoreTests(unittest.TestCase):
    def setUp(self):
        self.directory=tempfile.TemporaryDirectory()
        self.store=IntakeStore(self.directory.name)
        self.collection=self.store.import_payload('wikipedia',wiki(),'1961')['id']

    def tearDown(self):
        self.directory.cleanup()

    def approved(self,identity='a'):
        current=self.store.get_record(self.collection,identity)
        review=copy.deepcopy(current['review'])
        review.update(label='novelty',reason='A contextual reading.',sourceChecked=True,dateChecked=True,placeChecked=True,duplicatesChecked=True)
        review['location']={'label':'A checked place','geometry':{'type':'Point','coordinates':[20,10]},'note':'Test fixture'}
        return review

    def test_originals_idempotency_restart_and_history(self):
        duplicate=self.store.import_payload('wikipedia',wiki(),'Again')
        self.assertTrue(duplicate['alreadyImported'])
        original=self.store.get_record(self.collection,'a')['record']
        review=self.approved();review['title']='Corrected review title'
        self.store.save_review(self.collection,'a',review,0)
        restarted=IntakeStore(self.directory.name)
        self.assertEqual(restarted.get_record(self.collection,'a')['record'],original)
        self.assertEqual(restarted.get_record(self.collection,'a')['review']['title'],'Corrected review title')
        with restarted.connect() as db:
            self.assertEqual(db.execute('SELECT COUNT(*) FROM review_history').fetchone()[0],1)

    def test_publication_checks_and_neither_exclusion(self):
        with self.assertRaises(ValidationError):
            self.store.save_review(self.collection,'a',self.store.get_record(self.collection,'a')['review'],0,'approved')
        self.store.save_review(self.collection,'a',self.approved(),0,'approved')
        exported=self.store.export_year(self.collection,1961)
        self.assertEqual(exported['records'],1)
        self.assertNotIn('original',exported['events'][0])
        review=self.approved();review['label']='neither'
        self.store.save_review(self.collection,'a',review,1)
        with self.assertRaises(ValidationError):self.store.export_year(self.collection,1961)
        self.assertEqual(len(self.store.rows(self.collection)),2)

    def test_conflict_prevents_overwrite(self):
        self.store.save_review(self.collection,'a',self.approved(),0)
        with self.assertRaises(ConflictError):self.store.save_review(self.collection,'a',self.approved(),0)
        self.assertEqual(self.store.get_record(self.collection,'a')['version'],1)

    def test_year_only_dates_do_not_become_january_events(self):
        payload=wiki()
        payload['events'][0]['time']={'start':'1961-01-01','end':'1961-12-31','precision':'year'}
        collection=self.store.import_payload('wikipedia',payload,'Coarse dates')['id']
        summary=self.store.summary(collection)
        self.assertEqual(summary['months'][0],0)
        self.assertEqual(sum(summary['months']),1)
        self.assertEqual(summary['coarseDatesExcludedFromMonths'],1)

    def test_private_account_not_exportable_until_permission(self):
        result=self.store.add_manual({'title':'Private account','account':'Firsthand narrative.','relationship':'firsthand','observerPseudonym':'Private name',
              'time':{'start':'1961-04-12','end':'1961-04-12','precision':'day'}},'account')
        current=self.store.get_record(result['id'],result['recordId'])
        review=self.approved();review['publicAllowed']=False;review['permissionNote']=''
        with self.assertRaises(ValidationError):self.store.save_review(result['id'],result['recordId'],review,0,'approved')
        review.update(publicAllowed=True,permissionNote='Author expressly permits publication of this account.')
        self.store.save_review(result['id'],result['recordId'],review,0,'approved')
        exported=self.store.export_year(result['id'],1961)
        self.assertNotIn('Private name',json.dumps(exported))
        self.assertEqual(exported['events'][0]['evidenceType'],'firsthand-account')

    def test_duplicate_and_geometry_validation(self):
        review=self.approved();review['location']['geometry']['coordinates']=[10,100]
        with self.assertRaises(ValidationError):self.store.save_review(self.collection,'a',review,0)
        review=self.approved();review['duplicateOf']='a'
        with self.assertRaises(ValidationError):self.store.save_review(self.collection,'a',review,0)
        review['duplicateOf']='b'
        with self.assertRaises(ValidationError):self.store.save_review(self.collection,'a',review,0,'approved')
        review['duplicateOf']='';review['location']['geometry']={'type':'Polygon','coordinates':[[[0,0],[1,0],[1,1],[0,0]]]}
        self.store.save_review(self.collection,'a',review,0,'approved')
        self.assertEqual(self.store.export_year(self.collection,1961)['events'][0]['location']['geometry']['type'],'Polygon')

    def test_restore_validation_is_atomic_and_downgrades_approval(self):
        self.store.save_review(self.collection,'a',self.approved(),0,'approved')
        bundle=self.store.review_bundle(self.collection)
        with tempfile.TemporaryDirectory() as directory:
            other=IntakeStore(directory)
            other.import_payload('wikipedia',wiki(),'1961')
            bad=copy.deepcopy(bundle);bad['reviews'].append({'collection':self.collection,'recordId':'b','review':{'label':'bad'}})
            with self.assertRaises(ValidationError):other.restore_bundle(bad)
            self.assertEqual(other.get_record(self.collection,'a')['version'],0)
            other.restore_bundle(bundle)
            self.assertEqual(other.get_record(self.collection,'a')['review']['status'],'reviewed')
            with self.assertRaises(ValidationError):other.export_year(self.collection,1961)


class AdapterTests(unittest.TestCase):
    def test_usgs_zero_magnitude_coordinate_order_depth_and_origin_time(self):
        records,_=normalize_usgs(earthquake())
        self.assertEqual(records[0]['measurements']['magnitude'],0)
        self.assertEqual(records[0]['measurements']['depthKm'],7.5)
        self.assertEqual(records[0]['location']['geometry']['coordinates'],[20,10])
        self.assertEqual(records[0]['time']['start'],'1970-01-01T00:00:00+00:00')
        historical=earthquake();historical['features'][0]['properties']['time']=-283996800000
        self.assertEqual(normalize_usgs(historical)[0][0]['time']['start'],'1961-01-01T00:00:00+00:00')
        bad=earthquake();bad['features'].append(bad['features'][0])
        with self.assertRaises(ValidationError):normalize_usgs(bad)

    def test_em_units_baseline_and_threshold(self):
        csv='timestamp,station,quantity,value,unit,baseline,baseline_note,threshold\n1961-04-12T06:07:00Z,Test,magnetic field,103,nT,100,quiet interval,2\n'
        records,_=normalize_em_csv(csv)
        self.assertEqual(records[0]['measurements']['delta'],3)
        self.assertTrue(records[0]['measurements']['anomalyCandidate'])
        self.assertFalse(records[0]['permission']['allowed'])
        with self.assertRaises(ValidationError):normalize_em_csv(csv.replace('quiet interval',''))
        with self.assertRaises(ValidationError):normalize_em_csv(csv.replace('103','NaN'))

    def test_time_precision_and_inclusive_query(self):
        with self.assertRaises(ValidationError):checked_time({'start':'1961-04-12T06:07:00','precision':'instant'})
        with self.assertRaises(ValidationError):checked_time({'start':'1961-02-01','end':'1961-02-27','precision':'month'})
        url=usgs_query_url({'start':'1961-04-01','end':'1961-04-30','magnitude':6})
        self.assertIn('23%3A59%3A59.999Z',url)
        with self.assertRaises(ValidationError):usgs_query_url({'start':'1961-01-01','end':'1963-01-01'})


class ServerTests(unittest.TestCase):
    def setUp(self):
        self.directory=tempfile.TemporaryDirectory()
        self.server=IntakeServer(('127.0.0.1',0),IntakeStore(self.directory.name))
        self.thread=threading.Thread(target=self.server.serve_forever,daemon=True);self.thread.start()
        self.base='http://127.0.0.1:'+str(self.server.server_port)

    def tearDown(self):
        self.server.shutdown();self.server.server_close();self.thread.join();self.directory.cleanup()

    def request(self,path,body=None,headers=None):
        data=None if body is None else json.dumps(body).encode()
        return urllib.request.urlopen(urllib.request.Request(self.base+path,data=data,headers=headers or {}))

    def test_same_origin_token_and_private_file_isolation(self):
        session=json.load(self.request('/api/session'))
        with self.assertRaises(urllib.error.HTTPError) as denied:self.request('/api/seed',{}, {'Content-Type':'application/json'})
        self.assertEqual(denied.exception.code,403)
        headers={'Content-Type':'application/json','Origin':self.base,'X-Intake-Token':session['token']}
        result=json.load(self.request('/api/import',{'kind':'wikipedia','payload':wiki(),'name':'Test'},headers))
        self.assertEqual(result['records'],2)
        with self.assertRaises(urllib.error.HTTPError) as denied:self.request('/.cache/intake/intake.sqlite3')
        self.assertEqual(denied.exception.code,404)
        with self.assertRaises(urllib.error.HTTPError) as denied:self.request('/api/session',headers={'Host':'attacker.example'})
        self.assertEqual(denied.exception.code,403)

    def test_backup_api_preserves_sources_and_history(self):
        session=json.load(self.request('/api/session'))
        headers={'Content-Type':'application/json','Origin':self.base,'X-Intake-Token':session['token']}
        result=json.load(self.request('/api/import',{'kind':'wikipedia','payload':wiki(),'name':'Test'},headers))
        current=self.server.store.get_record(result['id'],'a')
        review=current['review'];review.update(label='neither',reason='Excluded in this test.')
        json.load(self.request('/api/review',{'collection':result['id'],'id':'a','review':review,'version':0},headers))
        backup=json.load(self.request('/api/backup',{},headers))
        self.assertEqual(len(backup['sources'][0]['records']),2)
        self.assertEqual(len(backup['history']),1)
        with tempfile.TemporaryDirectory() as directory:
            restored=IntakeStore(directory)
            for source in backup['sources']:
                c=source['collection'];restored.add_collection(c['name'],c['kind'],source['records'],c['metadata'],c['id'])
            restored.restore_bundle(backup)
            self.assertEqual(restored.get_record(result['id'],'a')['version'],2)
            self.assertEqual(restored.get_record(result['id'],'a')['review']['label'],'neither')
            with restored.connect() as db:
                self.assertEqual(db.execute('SELECT COUNT(*) FROM review_history').fetchone()[0],2)


if __name__=='__main__':unittest.main()
