"""Synchronize the static website author block from the arXiv root.tex."""
import argparse
import hashlib
import html
import json
import re
from pathlib import Path

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('manuscript', type=Path)
parser.add_argument('--revision', required=True, help='Verified manuscript Git commit')
args = parser.parse_args()
source = args.manuscript.read_text()
site = Path(__file__).resolve().parents[1]
block = source.split(r'\author{', 1)[1].split(r'\role[', 1)[0]

def marker(value):
    return value.replace(r'\ddagger', '‡').replace(r'\dagger', '†')

authors = [
    {'name': name.replace('~', ' '), 'markers': marker(braced or single)}
    for name, braced, single in re.findall(
        r'([A-Za-z]+(?:~[A-Za-z]+)+)\$\^(?:\{([^}]+)\}|(\d+))\$', block)
]
institutions = dict(re.findall(r'\$\^(\d+)\$([^\\}]+)', block))
institutions = {key: value.strip() for key, value in institutions.items()}
roles = [(marker(key), text.rstrip('.')) for key, text in
         re.findall(r'\\role\[([^]]+)\]\{([^}]+)\}', source)]
metadata_names = re.search(r'pdfauthor=\{([^}]+)\}', source).group(1).split(', ')
assert [a['name'] for a in authors] == metadata_names, 'Author order or parser mismatch'
assert institutions and roles, 'Missing affiliations or roles'
for author in authors:
    for item in author['markers'].split(','):
        assert item in institutions or item in dict(roles), f'Unknown author marker: {item}'

author_html = '\n'.join('        ' + ''.join(
    f'<span>{html.escape(a["name"])}<sup>{html.escape(a["markers"])}</sup></span>'
    for a in authors[start:start + 6]) for start in range(0, len(authors), 6))
affiliation_html = ''.join(f'<span><sup>{key}</sup>{html.escape(value)}</span>'
                           for key, value in institutions.items())
role_html = ' · '.join(f'{key} {html.escape(text)}' for key, text in roles)
replacement = (f'<div class="authors" aria-label="Authors">\n{author_html}\n      </div>\n'
               f'      <div class="affiliations">{affiliation_html}</div>\n'
               f'      <p class="equal">{role_html}</p>')
page = site / 'dist/index.html'
original = page.read_text()
updated, count = re.subn(
    r'<div class="authors" aria-label="Authors">.*?<p class="equal">.*?</p>',
    lambda _: replacement, original, count=1, flags=re.S)
assert count == 1, 'Website author block not found'
page.write_text(updated)
provenance = {
    'source': 'Current author-approved arXiv manuscript root.tex',
    'revision': args.revision,
    'root_tex_sha256': hashlib.sha256(source.encode()).hexdigest(),
    'authors': authors,
    'institutions': institutions,
    'roles': dict(roles),
}
(site / 'tools/author-source.json').write_text(json.dumps(provenance, indent=2, ensure_ascii=False) + '\n')
print(f'Synchronized {len(authors)} authors, {len(institutions)} institutions, {len(roles)} role notes.')
