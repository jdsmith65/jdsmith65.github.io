"""Build the public website with Python's standard library. No packages required."""
from html import escape
import json
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'dist'
data = json.loads((ROOT / 'content/site.json').read_text())
p = data['profile']
phone_href = 'tel:+1' + ''.join(c for c in p['phone'] if c.isdigit())


def e(value):
    return escape(str(value), quote=True)


def link(url, label, cls=''):
    return f'<a href="{e(url)}" class="{e(cls)}">{e(label)}</a>'


def paper_list(papers, published=False):
    result = []
    previous_year = None
    for paper in papers:
        year = paper.get('year', '')
        same_year = bool(year) and year == previous_year
        year_label = f'<span class="sr-only">{e(year)}</span>' if same_year else e(year)
        row_class = 'paper same-year' if same_year else 'paper'
        previous_year = year
        title = e(paper['title'])
        if published:
            title = f'<a href="https://doi.org/{e(paper["doi"])}">{title}</a>'
        authors = f'<p class="coauthors">With {e(paper["coauthors"])}</p>' if paper.get('coauthors') else ''
        venue = ''
        if published:
            venue = f'<p class="venue"><cite>{e(paper["journal"])}</cite> · {e(paper["details"])}</p>'
        elif paper.get('status'):
            venue = f'<p class="status">{e(paper["status"])}</p>'
        links = [link('https://doi.org/' + paper['doi'], 'Journal article')] if published else []
        links.extend(link(item['url'], item['label']) for item in paper.get('links', []))
        access = f'<div class="paper-links">{"".join(links)}</div>' if links else ''
        result.append(f'<li class="{row_class}"><span class="year">{year_label}</span><div><h3>{title}</h3>{authors}{venue}{access}</div></li>')
    return '<ol class="paper-list">' + ''.join(result) + '</ol>'


def section(title, ident, content, intro=''):
    intro_html = f'<p class="section-intro">{e(intro)}</p>' if intro else ''
    return f'<section id="{ident}" class="content-section" aria-labelledby="{ident}-heading"><div class="section-label"><h2 id="{ident}-heading">{e(title)}</h2>{intro_html}</div><div class="section-body">{content}</div></section>'


def rows(items):
    return '<dl class="cv-rows">' + ''.join(f'<div><dt>{e(item[0])}</dt><dd>{e(item[1])}' + (f'<span>{e(item[2])}</span>' if len(item)>2 else '') + '</dd></div>' for item in items) + '</dl>'


def shell(title, body, is_cv=False):
    desc = f'{p["name"]}, {p["title"]} and {p["distinction"]} at {p["university"]}. Research, publications, working papers, and teaching.'
    nav = '<a href="index.html#publications">Publications</a><a href="index.html#working-papers">Working papers</a><a href="index.html#teaching">Teaching</a><a href="assets/cv.pdf">CV (PDF)</a>'
    return f'''<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{e(title)}</title>
  <meta name="description" content="{e(desc)}">
  <meta name="theme-color" content="#a91830">
  <meta property="og:title" content="{e(title)}">
  <meta property="og:description" content="{e(desc)}">
  <meta property="og:type" content="website">
  <link rel="icon" type="image/svg+xml" href="assets/favicon.svg">
  <link rel="stylesheet" href="assets/style.css">
</head>
<body>
  <a class="skip-link" href="#main">Skip to content</a>
  <header class="site-header"><div class="header-inner"><a class="wordmark" href="index.html" aria-label="Jared D. Smith, home">JDS<span aria-hidden="true">.</span></a><nav aria-label="Main navigation">{nav}</nav></div></header>
  <main id="main" class="{'cv-page' if is_cv else 'home-page'}">{body}</main>
  <footer><div><strong>{e(p['name'])}</strong><span>{e(p['department'])} · NC State University</span></div><div>{link('mailto:'+p['email'],p['email'])}<span>Updated {e(p['updated'])}</span></div></footer>
</body>
</html>
'''


profile_links = link('assets/cv.pdf', 'Curriculum vitae (PDF)', 'button') + link(p['faculty_url'], 'NC State profile')
if p.get('scholar_url'):
    profile_links += link(p['scholar_url'], 'Google Scholar')
journal_links = ['<cite>' + link(item['url'], item['label']) + '</cite>' for item in p.get('selected_journals', [])]
selected_journals = (', '.join(journal_links[:-1]) + ', and ' + journal_links[-1]) if len(journal_links) > 2 else ' and '.join(journal_links)
journal_line = f'<p class="credentials">Publications include work in {selected_journals}.</p>' if selected_journals else ''
institutional_line = ''
if p.get('institutional_citations'):
    citations = p['institutional_citations']
    policy_links = ' and the '.join(link(item['url'], item['label']) for item in citations if item['kind'] == 'policy')
    research_links = ' and '.join(link(item['url'], item['label']) for item in citations if item['kind'] == 'research')
    mentions = []
    if policy_links:
        mentions.append('policy reports from the ' + policy_links)
    if research_links:
        mentions.append(research_links)
    institutional_line = '<p class="institutional">My research is cited in ' + ', and in '.join(mentions) + '.</p>'
hero = f'''<section class="hero" aria-labelledby="name">
  <div class="hero-copy"><p class="eyebrow">{e(p['college'])} · NC State</p>
  <h1 id="name">{e(p['name'])}</h1><p class="position">{e(p['title'])} <span>&amp; {e(p['distinction'])}</span></p>
  <p class="bio">{e(p['bio'])}</p>{journal_line}{institutional_line}
  <div class="profile-links">{profile_links}</div></div>
  <figure class="portrait"><img src="assets/jared-smith.jpg" alt="Jared D. Smith" width="6192" height="4128" fetchpriority="high"></figure>
</section>'''
publications = section('Publications', 'publications', paper_list(data['publications'], True), 'Journal articles and available working-paper versions.')
working = section('Working papers', 'working-papers', paper_list(data['working_papers']))
progress = section('Research in progress', 'research-in-progress', paper_list(data['works_in_progress']) + '<details><summary>Permanent working paper</summary>' + paper_list(data['permanent_working_papers']) + '</details>')
teaching_items = ''.join('<div class="course"><h3>' + e(c['title']) + '</h3>' + (f'<p>{e(c["audience"])}</p>' if c['audience'] else '') + f'<p class="course-meta">NC State · {e(c["dates"])}</p></div>' for c in data['teaching'])
teaching = section('Teaching', 'teaching', '<div class="courses">'+teaching_items+'</div>')
contact = section('Contact', 'contact', f'<div class="contact-columns"><address>{link("mailto:"+p["email"],p["email"])}<br>{link(phone_href,p["phone"])}<br>{e(p["office"])}<br>{e(p["location"])}</address><p>{e(p["personal"])}</p></div>')
home = shell(p['name']+' | Professor of Finance', hero+publications+working+progress+teaching+contact)

cv_intro = f'<div class="cv-title"><p class="eyebrow">Curriculum vitae · {e(p["cv_date"])}</p><h1>{e(p["name"])}</h1><p class="position">{e(p["title"])} · {e(p["university"])}</p><p>{link("mailto:"+p["email"],p["email"])}</p><p class="print-note">A concise academic CV. To save a PDF, use your browser’s Print menu.</p></div>'
cv_body = cv_intro + section('Appointments', 'appointments', rows(data['cv']['appointments'])) + section('Education', 'education', rows(data['cv']['education'])) + publications + working + progress + section('Honors & awards', 'honors', rows(data['cv']['honors'])) + teaching + section('Earlier teaching', 'earlier-teaching', rows(data['cv']['earlier_teaching']))
OUT.mkdir(exist_ok=True)
shutil.copytree(ROOT/'assets', OUT/'assets', dirs_exist_ok=True)
(OUT/'index.html').write_text(home)
(OUT/'cv.html').write_text(shell('Curriculum vitae | '+p['name'], cv_body, True))
(OUT/'.nojekyll').touch()
print(f'Built index.html and cv.html in {OUT}')
