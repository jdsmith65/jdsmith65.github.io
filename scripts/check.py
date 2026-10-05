"""Catch broken local links and inconsistent research records before publishing."""
from html.parser import HTMLParser
import json
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'dist'


class Page(HTMLParser):
    def __init__(self, path):
        super().__init__()
        self.path, self.ids, self.links, self.h1 = path, [], [], 0
        self.feed(path.read_text())

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if 'id' in a:
            self.ids.append(a['id'])
        for key in ('href', 'src'):
            if key in a:
                self.links.append(a[key])
        self.h1 += tag == 'h1'


pages = {path: Page(path) for path in OUT.glob('*.html')}
errors = []
for path, page in pages.items():
    if page.h1 != 1:
        errors.append(f'{path.name}: expected one main heading')
    if len(page.ids) != len(set(page.ids)):
        errors.append(f'{path.name}: duplicate section IDs')
    for href in page.links:
        u = urlsplit(href)
        if u.scheme:
            if u.scheme not in ('https', 'mailto', 'tel'):
                errors.append(f'{path.name}: unsupported link scheme: {href}')
            continue
        if u.netloc or u.path.startswith('/'):
            errors.append(f'{path.name}: link will not work on a GitHub project path: {href}')
            continue
        target = (path.parent / unquote(u.path)).resolve() if u.path else path
        if not target.exists():
            errors.append(f'{path.name}: missing local file: {href}')
        elif u.fragment and target in pages and unquote(u.fragment) not in pages[target].ids:
            errors.append(f'{path.name}: missing section: {href}')
data = json.loads((ROOT/'content/site.json').read_text())
dois = [p['doi'] for p in data['publications']]
if len(dois) != len(set(dois)):
    errors.append('Duplicate publication DOI')
for key in ('publications', 'working_papers', 'works_in_progress', 'permanent_working_papers'):
    for paper in data[key]:
        if not paper['title'].strip():
            errors.append(f'{key}: empty title')
        for item in paper.get('links', []):
            if not item['label'].strip() or not item['url'].startswith('https://'):
                errors.append(f'{key}: invalid paper link')
if errors:
    raise SystemExit('\n'.join(errors))
print(f'Passed: {len(pages)} pages; local files and anchors; project-path links; unique publication DOIs.')
print('External destination availability is not checked by this script.')
