import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from wikipedia_history import date_span, extract_page, classify, merge_and_flag
from export_history_view import export_view

SOURCE = {'url':'https://en.wikipedia.org/wiki/1961','revision':123,'permalink':'https://en.wikipedia.org/w/index.php?oldid=123'}


class ChronologyTests(unittest.TestCase):
    def test_date_ranges_and_precision(self):
        self.assertEqual(date_span('January 4–7 – A summit',1961)[0]['end'],'1961-01-07')
        self.assertEqual(date_span('January 31 – February 2 – A conference',1961)[0]['end'],'1961-02-02')
        self.assertIsNone(date_span('February 30 – Impossible',1961))
        self.assertIsNone(date_span('In April a launch occurred',1961))
        self.assertEqual(date_span('May 1 – 2,000 people gather',1961)[0]['end'],'1961-05-01')

    def test_year_nested_dates_and_births(self):
        html = '''<div class="mw-parser-output"><h2 id="Events">Events</h2><h3>January</h3>
        <ul><li>January 1 – A new satellite launches.</li><li>January 2<ul><li>A treaty is signed.</li><li>A conference opens.</li></ul></li>
        <li>A month-only event takes place.</li></ul><h2>Births</h2><h3>March</h3><ul><li>March 4<ul><li>A Person, writer</li></ul></li></ul>
        <h2>References</h2><ul><li>This reference is not an event.</li></ul></div>'''
        records,audit = extract_page(html,'1961',SOURCE)
        self.assertEqual(audit['status'],'parsed')
        self.assertEqual(len(records),5)
        self.assertEqual([r['time']['start'] for r in records[:3]],['1961-01-01','1961-01-02','1961-01-02'])
        self.assertEqual(records[3]['time']['precision'],'month')
        self.assertEqual(records[4]['kind'],'birth')
        self.assertEqual(records[4]['time']['start'],'1961-03-04')

    def test_month_citations_and_entity_links(self):
        html = '''<div class="mw-parser-output"><table><tr><td><ul><li>Wrong navigation</li></ul></td></tr></table>
        <h2 id="January_1">January 1, 1961 (Sunday)</h2><ul><li>A flight arrives in <a href="/wiki/Paris">Paris</a>.
        <sup class="reference"><a href="#cite_note-1">[1]</a></sup></li><li>Born:<ul><li><a href="/wiki/A_Person">A Person</a>, singer</li></ul></li>
        <li>Died: Another Person, painter</li></ul><h2>References</h2><ol><li id="cite_note-1">Newspaper <a href="https://example.org/source">source</a></li></ol></div>'''
        records,_ = extract_page(html,'January_1961',SOURCE)
        self.assertEqual(len(records),3)
        self.assertEqual(records[0]['entities'][0]['title'],'Paris')
        self.assertNotIn('[1]',records[0]['text'])
        self.assertEqual(records[0]['sources'][0]['references'][0]['citation']['urls'],['https://example.org/source'])
        self.assertEqual([r['kind'] for r in records],['event','birth','death'])
        self.assertTrue(all(r['time']['start']=='1961-01-01' for r in records))
        self.assertTrue(all(r['location']['geometry'] is None for r in records))

    def test_no_forced_interpretation_or_silent_duplicate_merge(self):
        rules=json.loads((ROOT/'data/history-rules.json').read_text(encoding='utf-8'))
        record={'kind':'event','text':'The first human spaceflight occurs while a newspaper is banned.'}
        reading,_ = classify(record,rules)
        self.assertEqual(reading['suggestion'],'mixed')
        self.assertEqual(reading['label'],'unreviewed')
        self.assertEqual(classify({'kind':'event','text':'A meeting occurs.'},rules)[0]['suggestion'],'unreviewed')
        self.assertEqual(classify({'kind':'death','text':'First human dies, newspaper banned.'},rules)[0]['suggestion'],'unreviewed')
        html='<div class="mw-parser-output"><h2>Events</h2><ul><li>April 12 – A human space flight launches from a space port.</li><li>April 12 – A human space flight launches from a space port today.</li></ul></div>'
        rows,_=extract_page(html,'1961',SOURCE)
        merged=merge_and_flag(rows+[json.loads(json.dumps(rows[0]))])
        self.assertEqual(len(merged),2)
        self.assertEqual(len(merged[0]['sources'])+len(merged[1]['sources']),3)
        self.assertTrue(all(r.get('possibleDuplicates') for r in merged))

    def test_unsupported_layout_is_audited(self):
        rows,audit=extract_page('<html><body>Unavailable</body></html>','1961',SOURCE)
        self.assertEqual(rows,[])
        self.assertEqual(audit['status'],'unsupported-layout')

    def test_reviewed_neither_overrides_candidate_view(self):
        dataset={'year':1961,'license':{},'pages':[], 'events':[
            {'id':'a','classification':{'label':'neither','suggestion':'novelty'}},
            {'id':'b','classification':{'label':'unreviewed','suggestion':'novelty'}},
            {'id':'c','classification':{'label':'tradition','suggestion':'novelty'}}]}
        self.assertEqual([r['id'] for r in export_view(dataset,{'novelty','tradition'},True)['events']],['b','c'])
        self.assertEqual([r['id'] for r in export_view(dataset,{'novelty','tradition'})['events']],['c'])
        self.assertEqual(len(dataset['events']),3)


if __name__=='__main__':
    unittest.main()
