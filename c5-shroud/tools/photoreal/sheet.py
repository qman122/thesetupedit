import sys
from PIL import Image, ImageDraw, ImageFont
S, st, title, sub, out = sys.argv[1:6]
F = lambda s: ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', s)
R = lambda s: ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', s)
a = Image.open(f'{S}/out/{st}_34_white_glow.png'); b = Image.open(f'{S}/out/{st}_front_white_glow.png'); c = Image.open(f'{S}/out/{st}_hood34_amber_glow.png')
W = 2400; g = 14; top = 120
big = a.resize((W, int(a.height * W / a.width)))
hw = (W - g) // 2
b2 = b.resize((hw, int(b.height * hw / b.width))); c2 = c.resize((hw, int(c.height * hw / c.width)))
H = top + big.height + g + b2.height
im = Image.new('RGB', (W, H), (8, 8, 10)); d = ImageDraw.Draw(im)
d.text((40, 26), title, fill=(240, 240, 240), font=F(46)); d.text((40, 82), sub, fill=(165, 168, 174), font=R(24))
im.paste(big, (0, top)); im.paste(b2, (0, top + big.height + g)); im.paste(c2, (hw + g, top + big.height + g))
im.save(out, quality=92); print(im.size)
