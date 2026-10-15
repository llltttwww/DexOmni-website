"""Copy the reviewed static site to the GitHub Pages publication directory."""
import hashlib
import shutil
from pathlib import Path

site = Path(__file__).resolve().parents[1]
source = site / 'dist'
target = site / 'docs'
if target.exists():
    shutil.rmtree(target)
shutil.copytree(source, target)
(target / '.nojekyll').touch()
for path in source.rglob('*'):
    if path.is_file():
        published = target / path.relative_to(source)
        assert hashlib.sha256(path.read_bytes()).digest() == hashlib.sha256(published.read_bytes()).digest()
print('GitHub Pages files match dist/')
