"""Prepare the website from the project's existing, authored research assets."""
import argparse
import ast
import json
import re
import shutil
import subprocess
from pathlib import Path
from PIL import Image, ImageOps

parser = argparse.ArgumentParser()
parser.add_argument('--project-root', type=Path, required=True)
parser.add_argument('--ffmpeg', required=True)
parser.add_argument('--manuscript-root', type=Path, required=True, help='Verified current manuscript source tree')
parser.add_argument('--overview-video', type=Path, required=True, help='Reviewed current rendered film')
parser.add_argument('--paper-pdf', type=Path, required=True, help='Freshly compiled current manuscript')
parser.add_argument('--paper-revision', required=True)
args = parser.parse_args()
root = args.project_root
site = Path(__file__).resolve().parents[1]
out = site / 'dist' / 'assets'
out.mkdir(parents=True, exist_ok=True)

def web_image(source, name, width=1200, quality=87):
    with Image.open(source) as im:
        im = ImageOps.exif_transpose(im).convert('RGB')
        im.thumbnail((width, width))
        im.save(out / name, quality=quality, method=6)

for name in ['dexomni-mark.svg', 'dexomni-wordmark.svg']:
    shutil.copy2(root / 'dexomni-release/docs/pics' / name, out / name)
shutil.copy2(root / 'dexomni-film/public/fonts/InterTight-normal-200_900.woff2', out / 'inter-tight.woff2')
web_image(args.manuscript_root / 'figures/teleop-setup.png', 'teleoperation.webp', 1817, 92)
web_image(root / 'dexomni-release/docs/pics/release-cameras.jpg', 'cameras.webp', 1600)
for suffix in 'abcd':
    web_image(root / f'dexomni-film/public/img/rerender_{suffix}.png', f'appearance-{suffix}.webp', 800)

# The release registry is the source of task membership and public identifiers.
tree = ast.parse((root / 'dexomni-release/dexomni/dexomni/tasks/registry.py').read_text())
catalog = None
for node in tree.body:
    if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == '_CONFIG_MODULES' for t in node.targets):
        catalog = ast.literal_eval(node.value)
assert catalog and len(catalog) == 66
tasks = []
for key in sorted(catalog, key=lambda k: (not k.startswith('t'), k)):
    if key.startswith('t'):
        short, slug = key.split('_', 1)
        family = 'core'
        label = short.upper()
        picture = short[1:] + '.png'
    else:
        _, short, slug = key.split('_', 2)
        family = {'comb': 'composition', 'gen': 'generalization', 'flex': 'deformable'}[short[:-2]]
        label = short[:-2].capitalize() + '-' + short[-2:]
        picture = 'EVAL-' + short[:-2].capitalize() + short[-2:] + '.png'
    title = slug.replace('_', ' ').capitalize()
    text = (root / 'dexomni-release/configs/multi_task' / (key + '.yaml')).read_text()
    match = re.search(r'^prompt:\s*(.+)$', text, re.M)
    try:
        prompt = ast.literal_eval(match[1]) if match else ''
    except (ValueError, SyntaxError):
        prompt = ''
    # Human-facing summaries for implementation-oriented or obsolete config wording.
    overrides = {
        't06_fit_device_cover': 'Align the cover with the device body and fit the two pieces together.',
        't10_lift_carton': 'Support the carton from both lower sides, lift it clear of the table, and maintain a stable hold.',
        't18_open_micropipette_box': 'Open the articulated micropipette box while preserving stable contact.',
        'eval_comb05_scrub_bottle_then_fill_cup': 'Scrub the bottle, then position the cup for filling, completing the stages in order.',
        'eval_gen03_orient_bottle_upright': 'Pick up the yellow mustard bottle, place it upright, release it, and maintain the final pose.',
    }
    prompt = overrides.get(key, prompt) or title + '.'
    image_name = key + '.webp'
    web_image(args.manuscript_root / 'figures/tasks' / picture, image_name, 854)
    tasks.append(dict(id=key, short=label, title=title, family=family, description=prompt,
                      image='assets/' + image_name))
(out / 'tasks.json').write_text(json.dumps(tasks, ensure_ascii=False, indent=2) + '\n')

def encode(source, target, width=854, duration=None, start=None, audio=False):
    cmd = [args.ffmpeg, '-y', '-hide_banner', '-loglevel', 'error']
    if start is not None:
        cmd += ['-ss', str(start)]
    cmd += ['-i', str(source)]
    if duration is not None:
        cmd += ['-t', str(duration)]
    cmd += ['-vf', f'scale={width}:-2', '-c:v', 'libx264', '-preset', 'fast', '-crf', '25', '-pix_fmt', 'yuv420p', '-threads', '4']
    cmd += ['-c:a', 'aac', '-b:a', '96k'] if audio else ['-an']
    cmd += ['-movflags', '+faststart', str(out / target)]
    subprocess.run(cmd, check=True)

manifest = json.loads((root / 'dexomni-intro-video/build/cards/manifest.json').read_text())
for key, name in [('sim_hammer', 'hammer'), ('sim_spoon', 'scooping')]:
    source = Path(manifest[key]['src'])
    if not source.exists():
        source = root / f'dexomni-intro-video/build/cards/{key}.mp4'
    encode(source, name + '.mp4', duration=10)
    subprocess.run([args.ffmpeg, '-y', '-hide_banner', '-loglevel', 'error', '-ss', '2', '-i', str(out / (name + '.mp4')), '-frames:v', '1', str(out / (name + '.jpg'))], check=True)
encode(args.overview_video, 'overview.mp4', width=1280, audio=True)
subprocess.run([args.ffmpeg, '-y', '-hide_banner', '-loglevel', 'error', '-ss', '37', '-i', str(out / 'overview.mp4'), '-frames:v', '1', str(out / 'overview.jpg')], check=True)

# Require an explicit verified manuscript; never select an old cached PDF.
import sys
subprocess.run([sys.executable, str(site / 'tools/update-paper.py'),
                '--source', str(args.paper_pdf), '--revision', args.paper_revision], check=True)
print(json.dumps({'tasks': len(tasks), 'assets_bytes': sum(p.stat().st_size for p in out.iterdir())}, indent=2))
