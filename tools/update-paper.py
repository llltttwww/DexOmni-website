"""Compress a freshly compiled, explicitly selected manuscript for the website."""
import argparse
import hashlib
import json
import re
from pathlib import Path

from pypdf import PdfReader, PdfWriter
from pypdf.generic import TextStringObject

parser = argparse.ArgumentParser()
parser.add_argument('--source', type=Path, required=True)
parser.add_argument('--revision', required=True, help='Verified manuscript Git commit')
args = parser.parse_args()
site = Path(__file__).resolve().parents[1]
target = site / 'dist/assets/DexOmni.pdf'
reader = PdfReader(args.source)
writer = PdfWriter(clone_from=reader)
removed = 0
for page in writer.pages:
    if 'prompt revision' not in page.extract_text():
        continue
    stream = page.get_contents()
    for operands, operator in stream.operations:
        if operator != b'TJ':
            continue
        parts = operands[0]
        for index in range(len(parts) - 1, -1, -1):
            if isinstance(parts[index], TextStringObject) and re.fullmatch(r'V\d+', str(parts[index])):
                del parts[index]
                if index < len(parts) and isinstance(parts[index], (int, float)):
                    del parts[index]
                removed += 1
    page.replace_contents(stream)
seen = set()
for page in writer.pages:
    for image in list(page.images):
        ref = image.indirect_reference
        if ref is None or ref.idnum in seen:
            continue
        seen.add(ref.idnum)
        im = image.image
        if im and im.width > 450 and im.height > 180:
            image.replace(im.convert('RGB'), quality=87, optimize=True)
candidate = target.with_suffix('.tmp.pdf')
writer.write(candidate)
after = PdfReader(candidate)
assert len(after.pages) == len(reader.pages)
for before, page in zip(reader.pages, after.pages):
    text = before.extract_text()
    expected = re.sub(r'\bV\d+\s+', '', text) if 'prompt revision' in text else text
    actual = page.extract_text()
    if expected != text:
        # Removing a label at a line end can leave its original line break.
        # Ignore that whitespace only on the page with the removed label.
        assert expected.split() == actual.split(), 'Unexpected change to manuscript text'
    else:
        assert expected == actual, 'Unexpected change to manuscript text'
assert not re.search(r'\bV\d+\s+prompt revision', '\n'.join(p.extract_text() for p in after.pages), re.I)
assert candidate.stat().st_size < 25 * 1024 * 1024
candidate.replace(target)
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
receipt = {
    'source': 'Current author-approved arXiv manuscript',
    'source_revision': args.revision,
    'source_pdf_sha256': sha(args.source),
    'website_pdf_sha256': sha(target),
    'pages': len(after.pages),
    'website_pdf_bytes': target.stat().st_size,
    'retired_internal_labels_removed': removed,
    'all_other_extracted_text_preserved': True,
    'text_validation': 'Exact text; whitespace normalized only on pages with a removed internal label',
    'image_compression': 'RGB JPEG quality 87; layout and page count preserved',
}
(site / 'tools/paper-source.json').write_text(json.dumps(receipt, indent=2) + '\n')
print(json.dumps(receipt, indent=2))
