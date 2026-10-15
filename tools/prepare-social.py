"""Create the share card from the retained homepage figure, without cropping it."""
import argparse
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

parser = argparse.ArgumentParser()
parser.add_argument('--font', required=True, help='Path to a TrueType or OpenType sans font')
args = parser.parse_args()
assets = Path(__file__).resolve().parents[1] / 'dist/assets'
scale = 2
card = Image.new('RGB', (1200 * scale, 630 * scale), 'white')
draw = ImageDraw.Draw(card)
ink, muted, accent = '#183449', '#53697a', '#2d6c98'
def text(x, y, value, size, fill=ink):
    draw.text((x*scale, y*scale), value, font=ImageFont.truetype(args.font, size*scale), fill=fill)
draw.rectangle((0, 0, 1200*scale, 8*scale), fill=ink)
text(48, 82, 'DEXTEROUS MANIPULATION BENCHMARK', 14, accent)
text(45, 125, 'DexOmni', 69)
for i, line in enumerate(['Generalizable dexterous', 'manipulation, measured.']):
    text(48, 222+i*40, line, 29)
draw.line((48*scale, 340*scale, 455*scale, 340*scale), fill='#dbe4eb', width=2)
text(48, 368, '66 tasks', 31)
text(48, 414, '18,000 human demonstrations', 22, muted)
text(48, 452, 'One shared evaluation platform', 22, muted)
text(48, 548, 'Core-50  /  Transfer-16', 17, accent)
with Image.open(assets / 'dexomni-overview.jpg') as hero:
    hero = hero.convert('RGB')
    hero.thumbnail((650*scale, 570*scale), Image.Resampling.LANCZOS)
    card.paste(hero, (530*scale + (650*scale-hero.width)//2, (630*scale-hero.height)//2))
card.resize((1200, 630), Image.Resampling.LANCZOS).save(assets / 'social.jpg', quality=94, optimize=True)
print(assets / 'social.jpg')
