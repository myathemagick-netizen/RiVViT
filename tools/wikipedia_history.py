"""Extract dated Wikipedia chronology list items; Python standard library only.

Network access lives in import_wikipedia_history.py. Imported text is separately
attributed CC BY-SA 4.0 data, never a source of executable instructions.
"""
import calendar
import hashlib
import re
import unicodedata
from datetime import date
from html.parser import HTMLParser
from urllib.parse import unquote, urljoin, urlparse

MONTHS = list(calendar.month_name)[1:]
MONTH_PATTERN = '|'.join(MONTHS)
VOID = {'area','base','br','col','embed','hr','img','input','link','meta','param','source','track','wbr'}
SKIP_CLASSES = {'navbox','vertical-navbox','infobox','sidebar','hatnote','thumb','mw-editsection','reflist','reference','mw-ref','shortdescription','metadata','toc','noprint'}


class Node:
    def __init__(self, tag, attrs=(), parent=None):
        self.tag, self.attrs, self.parent, self.children = tag, dict(attrs), parent, []

    def walk(self, tag=None):
        if tag is None or self.tag == tag:
            yield self
        for child in self.children:
            if isinstance(child, Node):
                yield from child.walk(tag)

    def skipped(self):
        return self.tag in {'script','style','table','figure','nav','footer'} or bool(set(self.attrs.get('class','').split()) & SKIP_CLASSES)

    def text(self, own=False):
        parts = []
        for child in self.children:
            if isinstance(child, str):
                parts.append(child)
            elif not child.skipped() and not (own and child.tag in {'ul','ol'}):
                parts.append(' ' if child.tag == 'br' else child.text(own))
        return re.sub(r'\s+', ' ', ''.join(parts)).strip()


class Tree(HTMLParser):
    def __init__(self, html):
        super().__init__(convert_charrefs=True)
        self.root = Node('root')
        self.current = self.root
        self.feed(html)

    def handle_starttag(self, tag, attrs):
        node = Node(tag, attrs, self.current)
        self.current.children.append(node)
        if tag not in VOID:
            self.current = node

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        if tag not in VOID:
            self.handle_endtag(tag)

    def handle_endtag(self, tag):
        node = self.current
        while node.parent is not None:
            if node.tag == tag:
                self.current = node.parent
                return
            node = node.parent

    def handle_data(self, data):
        self.current.children.append(data)


def normalized(text):
    text = unicodedata.normalize('NFKC', text).casefold()
    return re.sub(r'\W+', ' ', text).strip()


def date_span(text, year):
    """Return a date prefix and its consumed length; never use embedded dates."""
    pattern = rf'^({MONTH_PATTERN})\s+(\d{{1,2}})(?!\d)(?:\s*[–—−-]\s*(?:({MONTH_PATTERN})\s+)?(\d{{1,2}})(?!\d|,\d{{3}}))?'
    match = re.match(pattern, text)
    if not match:
        return None
    month = MONTHS.index(match[1])+1
    try:
        start = date(year, month, int(match[2])).isoformat()
        end = date(year, MONTHS.index(match[3])+1 if match[3] else month, int(match[4])).isoformat() if match[4] else start
    except ValueError:
        return None
    if end < start:
        return None
    return {'start':start, 'end':end, 'precision':'day' if start == end else 'interval'}, match.end()


def year_span(year):
    return {'start':f'{year}-01-01','end':f'{year}-12-31','precision':'year'}


def month_span(year, month):
    return {'start':f'{year}-{month:02d}-01','end':f'{year}-{month:02d}-{calendar.monthrange(year, month)[1]}','precision':'month'}


def own_nodes(node):
    for child in node.children:
        if isinstance(child, Node) and not child.skipped() and child.tag not in {'ul','ol'}:
            yield child
            yield from own_nodes(child)


def article_link(node):
    href = node.attrs.get('href', '')
    url = urljoin('https://en.wikipedia.org/wiki/', href)
    parsed = urlparse(url)
    if parsed.netloc != 'en.wikipedia.org' or not parsed.path.startswith('/wiki/'):
        return None
    title = unquote(parsed.path[6:]).replace('_',' ')
    if ':' in title or title in MONTHS or re.fullmatch(rf'(?:{MONTH_PATTERN}) \d{{1,2}}|\d{{1,4}}', title):
        return None
    return {'title':title, 'text':node.text(), 'url':url.split('#')[0]}


def extract_page(html, title, source):
    root = Tree(html).root
    article = next((n for n in root.walk('div') if 'mw-parser-output' in n.attrs.get('class','').split()), None)
    if article is None:
        return [], {'status':'unsupported-layout','reason':'No mw-parser-output article container'}
    year = int(title.split('_')[-1])
    monthly = '_' in title
    base_month = MONTHS.index(title.split('_')[0])+1 if monthly else None
    family = 'event' if monthly else None
    current_date = month_span(year, base_month) if monthly else year_span(year)
    section_id, section_text = '', ''
    records, issues = [], []
    references = {}
    for node in article.walk('li'):
        if node.attrs.get('id','').startswith('cite_note'):
            references[node.attrs['id']] = {
                'text':node.text(),
                'urls':list(dict.fromkeys(a.attrs.get('href','') for a in node.walk('a') if a.attrs.get('href','').startswith(('https://','http://'))))
            }

    def add_li(node, inherited_date, inherited_kind, inherited_context=None):
        text = node.text(own=True)
        local_date, kind = inherited_date.copy(), inherited_kind
        parsed = date_span(text, year)
        if parsed:
            local_date, consumed = parsed
            text = text[consumed:].lstrip(' –—−-:')
        if re.match(r'^(?:Born|Births)\s*:', text, re.I):
            kind = 'birth'
            text = re.sub(r'^(?:Born|Births)\s*:\s*', '', text, flags=re.I)
        elif re.match(r'^(?:Died|Deaths)\s*:', text, re.I):
            kind = 'death'
            text = re.sub(r'^(?:Died|Deaths)\s*:\s*', '', text, flags=re.I)
        links, seen = [], set()
        for child in own_nodes(node):
            if child.tag == 'a':
                link = article_link(child)
                if link and link['title'] not in seen:
                    links.append(link)
                    seen.add(link['title'])
        # Do not walk nested bullet citations twice.
        refs = []
        def collect_refs(n):
            for child in n.children:
                if not isinstance(child, Node) or child.tag in {'ul','ol'}:
                    continue
                if child.tag == 'a' and '#cite_note' in child.attrs.get('href',''):
                    key = child.attrs['href'].split('#')[-1]
                    refs.append({'id':key,'url':(source.get('permalink') or source['url'])+'#'+key, 'citation':references.get(key)})
                collect_refs(child)
        collect_refs(node)
        children = [child for child in node.children if isinstance(child, Node) and child.tag in {'ul','ol'}]
        meaningful = bool(re.search(r'[A-Za-z]', text)) and len(text) >= 8
        # Pure date / Born / Died grouping labels are containers, not occurrences.
        if meaningful:
            key = '|'.join([local_date['start'],local_date['end'],kind,normalized(text)])
            records.append({
                'id':'wp-'+hashlib.sha256(key.encode()).hexdigest()[:20],
                'kind':kind, 'time':{**local_date,'basis':'chronology-heading-or-leading-date','timezone':None},
                'text':text, 'context':inherited_context,
                'entities':links,
                'location':{'status':'unresolved','geometry':None,'note':'Linked entities are clues, not verified event locations; nationality is not birthplace.'},
                'sources':[{'page':title,'revision':source.get('revision'),'url':source['url'],'permalink':source.get('permalink'),
                    'section':section_text,'sectionId':section_id,'itemAnchor':node.attrs.get('id'), 'references':refs}],
                'quality':{'historicallyVerified':False,'needsReview':True,'compoundItemPossible':bool(children or ';' in text)},
            })
        for container in children:
            for child in container.children:
                if isinstance(child, Node) and child.tag == 'li':
                    add_li(child, local_date, kind, text or inherited_context)

    def visit(node):
        nonlocal family, current_date, section_id, section_text
        if node.skipped():
            return
        if re.fullmatch('h[2-6]', node.tag):
            heading = node.text()
            section_text, section_id = heading, node.attrs.get('id','')
            parsed = date_span(heading, year)
            if monthly and parsed:
                family, current_date = 'event', parsed[0]
            elif heading.casefold() in {'events','births','deaths','nobel prizes','nobel prize'}:
                family = {'events':'event','births':'birth','deaths':'death','nobel prizes':'award','nobel prize':'award'}[heading.casefold()]
                current_date = year_span(year)
            elif not monthly and family and heading in MONTHS:
                current_date = month_span(year, MONTHS.index(heading)+1)
            elif heading.casefold() in {'date unknown','undated','unknown dates'} and family:
                current_date = year_span(year)
            elif node.tag == 'h2':
                family = None
            return
        if node.tag in {'ul','ol'}:
            if family:
                for child in node.children:
                    if isinstance(child, Node) and child.tag == 'li':
                        add_li(child,current_date,family)
            return
        for child in node.children:
            if isinstance(child, Node):
                visit(child)
    visit(article)
    if not records:
        issues.append('No supported dated list items; inspect article structure')
    return records, {'status':'parsed' if records else 'empty','records':len(records),'issues':issues}


def classify(record, rules):
    """Explainable triage only: do not use epoch phase, astronomy or sentiment."""
    matches = []
    if record['kind'] not in {'birth','death'}:
        for rule in rules['interpretationRules']:
            hits = [pattern for pattern in rule['patterns'] if re.search(pattern, record['text'], re.I)]
            if hits:
                matches.append({'rule':rule['id'],'suggestion':rule['suggestion'],'patterns':hits})
    labels = {match['suggestion'] for match in matches}
    suggestion = 'mixed' if len(labels) > 1 else next(iter(labels)) if labels else 'unreviewed'
    topics = [rule['topic'] for rule in rules['topicRules'] if re.search(rule['pattern'],record['text'],re.I)]
    if record['kind'] in {'birth','death'}:
        topics.append(record['kind'])
    return {'label':'unreviewed','suggestion':suggestion,'reviewRequired':True,'ruleVersion':rules['version'],'matches':matches}, sorted(set(topics))


def merge_and_flag(records):
    merged = {}
    for record in records:
        if record['id'] in merged:
            merged[record['id']]['sources'].extend(record['sources'])
        else:
            merged[record['id']] = record
    result = sorted(merged.values(), key=lambda r:(r['time']['start'],r['kind'],r['id']))
    # Conservative same-date token overlap flags; never collapse paraphrases or
    # same-day separate occurrences merely because they mention the same subject.
    buckets = {}
    for record in result:
        if record['time']['precision'] != 'day':
            continue
        key = (record['kind'],record['time']['start'])
        tokens = set(normalized(record['text']).split())
        for other, old_tokens in buckets.get(key, []):
            if len(tokens) < 5 or len(old_tokens) < 5:
                continue
            score = len(tokens & old_tokens)/len(tokens | old_tokens)
            if score >= .45:
                record.setdefault('possibleDuplicates',[]).append({'id':other['id'],'tokenOverlap':round(score,3)})
                other.setdefault('possibleDuplicates',[]).append({'id':record['id'],'tokenOverlap':round(score,3)})
        buckets.setdefault(key, []).append((record,tokens))
    return result
