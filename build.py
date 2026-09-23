"""Build The Setup Edit static site into ./docs (served by GitHub Pages).

Edit SETUPS below and re-run:  python build.py
Product images are free-license Unsplash photos (credits in CREDITS below); no Amazon images are used,
and no prices are shown (Amazon Associates rules).
"""
import pathlib, shutil, html

ROOT = pathlib.Path(__file__).resolve().parent
OUT = ROOT / "docs"
TAG = "thesetupedi0e-20"
SITE_NAME = "The Setup Edit"

def amz(asin):
    return f"https://www.amazon.com/dp/{asin}?tag={TAG}"

SETUPS = [
    dict(slug="trading-desk-setup", title="The Trading Desk Setup", img="trading.jpg",
         blurb="A multi-monitor desk built for long sessions: floating screens, good light, and room to think.",
         items=[
             ("Dual Monitor Arm", "VIVO dual monitor desk mount", "B009S750LA", "Floats two screens off the desk so you get your whole surface back."),
             ("Single Monitor Arm", "VIVO single monitor arm", "B00B21TLQU", "One screen, fully adjustable height, tilt and swivel."),
             ("Monitor Light Bar", "BenQ ScreenBar", "B076VNFZJG", "Lights your desk, not your screen. No glare on late-night charts."),
             ("Electric Standing Desk", "FLEXISPOT EN1", "B08BHPMYGK", "Sit or stand at the push of a button, with 4 memory presets."),
             ("LED Monitor Backlight", "Luminoodle bias lighting", "B01LG99NW4", "USB-powered glow behind your screen, softer on your eyes at night."),
             ("Ergonomic Mouse", "Logitech MX Master 3S", "B0B11LJ69K", "Shaped for long days, with an ultra-fast scroll wheel."),
             ("Trading in the Zone", "Book by Mark Douglas", "0735201447", "The classic on trading psychology and discipline."),
             ("How to Day Trade for a Living", "Book by Andrew Aziz", "1535585951", "A beginner's guide to day trading tools and risk management."),
         ]),
    dict(slug="minimal-desk-setup", title="The Clean Minimal Desk", img="minimal.jpg",
         blurb="Fewer things, better things. Warm materials and a desk that looks calm every time you sit down.",
         items=[
             ("Leather Desk Pad", "Aothia leather desk pad", "B082F5ZLS5", "The fastest way to make a desk look put together."),
             ("75% Mechanical Keyboard", "AULA F75 wireless", "B0CNT61VMZ", "Compact, wireless, hot-swappable, and a creamy sound."),
             ("Wooden Wrist Rest", "Faluber walnut wrist rest", "B09DPGVPG1", "Wrist support that matches a warm wood desk."),
             ("Headphone Stand", "New Bee headphone stand", "B01GJQ7N94", "Gets your headphones off the desk and within reach."),
             ("Bamboo Organizer Tray", "Lipper bamboo tray", "B00KAZ12OS", "A home for keys, pens and small gadgets."),
             ("Mini Desk Plants", "Der Rose artificial plants (3-pack)", "B07VKJKFN2", "Warmth without watering."),
             ("Swing Arm Desk Lamp", "LEPOWER clamp lamp", "B07R56PTMS", "Clamps on, saves space, and aims light where you need it."),
         ]),
    dict(slug="small-space-office", title="The Small Space Office", img="small.jpg",
         blurb="A full workstation for a corner, a bedroom or an apartment. Every item earns its space.",
         items=[
             ("Monitor Riser", "WALI adjustable monitor stand", "B094QTGHNZ", "Raises your screen and adds storage underneath."),
             ("Laptop Stand", "BESIGN LS03 aluminum stand", "B08BRCT4JH", "Turns a laptop into a proper workstation."),
             ("Monitor Light Bar", "Quntis monitor lamp", "B08DKQ3JG1", "Desk light with zero footprint."),
             ("Under-Desk Footrest", "Everlasting Comfort memory foam", "B07PGLBCFG", "The comfort upgrade nobody sees."),
             ("Mini Desk Plants", "Der Rose artificial plants (3-pack)", "B07VKJKFN2", "Fits on shelves and small desks."),
         ]),
    dict(slug="cable-management", title="The Cable Management Kit", img="cable.jpg",
         blurb="Hide the mess in an afternoon. The cheapest upgrade with the biggest before-and-after.",
         items=[
             ("Under-Desk Cable Tray", "Scanfield no-screw tray (2-pack)", "B09J5HH2LR", "Power strips and chargers go under the desk, off the floor."),
             ("Adhesive Cable Clips", "OHill cable clips (16-pack)", "B071FXZBMV", "Chargers stop falling behind the desk."),
         ]),
]

CREDITS = [
    ("Home page", "Roberto Nickson", "Gvm2wM3V5PA"), ("Trading desk", "João Inácio", "Wk_6p1TuhRE"),
    ("Minimal desk", "Muhammet Sain", "_g0SLFllfBY"), ("Small space", "Behnam Norouzi", "j3b15qP-ckc"),
    ("Cable management", "Bedirhan Gül", "I_3D0pVrMhY"),
]

DISCLOSURE = ("The Setup Edit is reader-supported. As an Amazon Associate I earn from qualifying purchases. "
              "Links to Amazon are affiliate links: if you buy through them, I may earn a small commission at no extra cost to you.")

CSS = """
:root{--bg:#EFE6D6;--card:#F7F1E7;--fg:#22302B;--muted:#5B645F;--accent:#C0582F;--line:#D9CDB8;--dark:#1E2A26;--cream:#F2EADB}
*{box-sizing:border-box}html{-webkit-text-size-adjust:100%}
body{margin:0;background:var(--bg);color:var(--fg);font:17px/1.6 Inter,system-ui,-apple-system,Segoe UI,sans-serif}
a{color:inherit}img{max-width:100%;display:block}
.wrap{max-width:1080px;margin:0 auto;padding:0 20px}
header{border-bottom:1px solid var(--line)}
.nav{display:flex;align-items:center;justify-content:space-between;height:68px}
.brand{font:600 15px/1 Inter,sans-serif;letter-spacing:.28em;text-transform:uppercase;text-decoration:none}
.nav nav a{margin-left:22px;text-decoration:none;font-size:15px;color:var(--muted)}
.nav nav a:hover{color:var(--fg)}
.eyebrow{font:600 13px Inter,sans-serif;letter-spacing:.24em;text-transform:uppercase;color:var(--accent)}
h1,h2,h3{font-family:"DM Serif Display",Georgia,serif;font-weight:400;line-height:1.1;margin:.2em 0 .4em}
h1{font-size:clamp(38px,6vw,64px)}h2{font-size:clamp(28px,4vw,40px)}h3{font-size:22px}
.hero{display:grid;grid-template-columns:1.05fr 1fr;gap:40px;align-items:center;padding:56px 0}
.hero p{font-size:19px;color:var(--muted);max-width:30em}
.hero img{border-radius:22px;aspect-ratio:4/3;object-fit:cover;width:100%}
.btn{display:inline-block;background:var(--fg);color:var(--cream);text-decoration:none;padding:13px 22px;border-radius:999px;font-weight:600;font-size:15px}
.btn.alt{background:transparent;color:var(--fg);border:2px solid var(--fg)}
.btn:hover{opacity:.9}
.grid{display:grid;grid-template-columns:repeat(2,1fr);gap:26px;padding:10px 0 60px}
.card{background:var(--card);border-radius:22px;overflow:hidden;text-decoration:none;display:flex;flex-direction:column;border:1px solid var(--line)}
.card img{aspect-ratio:3/2;object-fit:cover;width:100%}
.card .in{padding:20px 22px 24px}.card p{margin:0;color:var(--muted)}
.card:hover{transform:translateY(-2px);transition:transform .2s}
.setup-hero{padding:40px 0 10px}.setup-hero img{border-radius:22px;aspect-ratio:21/9;object-fit:cover;width:100%;margin-top:22px}
.lead{font-size:19px;color:var(--muted);max-width:36em}
.items{display:grid;grid-template-columns:repeat(2,1fr);gap:18px;padding:30px 0 50px;counter-reset:n}
.item{background:var(--card);border:1px solid var(--line);border-radius:18px;padding:20px 22px;display:flex;flex-direction:column;gap:6px}
.item .num{counter-increment:n;font:600 13px Inter,sans-serif;letter-spacing:.2em;color:var(--accent)}
.item .num::before{content:counter(n,decimal-leading-zero)}
.item h3{margin:0}.item .model{font-size:14px;color:var(--muted);margin:0}.item p{margin:4px 0 12px}
.item .btn{align-self:flex-start;margin-top:auto}
.band{background:var(--dark);color:var(--cream);border-radius:22px;padding:36px;margin:10px 0 60px;display:flex;gap:30px;align-items:center;justify-content:space-between;flex-wrap:wrap}
.band p{color:#B8B2A4;margin:0;max-width:34em}.band .btn{background:var(--cream);color:var(--dark)}
.note{font-size:14px;color:var(--muted);background:var(--card);border:1px solid var(--line);border-radius:14px;padding:12px 16px;margin:18px 0 0}
footer{border-top:1px solid var(--line);padding:30px 0 50px;font-size:14px;color:var(--muted)}
footer a{color:var(--muted)}
.prose{max-width:720px;padding:40px 0 60px}
@media (max-width:760px){.hero,.grid,.items{grid-template-columns:1fr}.hero{padding:32px 0}.nav nav a{margin-left:14px;font-size:14px}.band{padding:26px}}
"""

HEAD = """<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title}</title><meta name="description" content="{desc}">
<meta property="og:title" content="{title}"><meta property="og:description" content="{desc}">
<meta property="og:image" content="{og}"><meta name="p:domain_verify" content="77efeace518f495ac7564d61a39f2015"/>
<link rel="icon" href="{root}img/icon.png">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=DM+Serif+Display&family=Inter:wght@400;600&display=swap" rel="stylesheet">
<link rel="stylesheet" href="{root}style.css"></head><body>
<header><div class="wrap nav"><a class="brand" href="{root}index.html">The Setup Edit</a>
<nav><a href="{root}index.html#setups">Setups</a><a href="{root}disclosure.html">Disclosure</a></nav></div></header>
<main class="wrap">"""

FOOT = """</main><footer><div class="wrap"><p>{disc}</p>
<p>Photos from <a href="https://unsplash.com" rel="nofollow">Unsplash</a> ({credits}). Products shown in photos may differ from the linked items.</p>
<p>&copy; 2026 The Setup Edit</p></div></footer></body></html>"""


def page(title, desc, body, root="", og="img/hero.jpg"):
    credits = ", ".join(f'<a href="https://unsplash.com/photos/{i}" rel="nofollow">{html.escape(n)}</a>' for _, n, i in CREDITS)
    return (HEAD.format(title=html.escape(title), desc=html.escape(desc), og=root + og, root=root) + body
            + FOOT.format(disc=html.escape(DISCLOSURE), credits=credits))


def build():
    if OUT.exists():
        shutil.rmtree(OUT)
    (OUT / "setups").mkdir(parents=True)
    shutil.copytree(ROOT / "img", OUT / "img")
    (OUT / "style.css").write_text(CSS, encoding="utf-8")
    (OUT / ".nojekyll").write_text("")

    cards = "".join(f"""<a class="card" href="setups/{s['slug']}.html"><img src="img/{s['img']}" alt="{html.escape(s['title'])}" loading="lazy">
<div class="in"><div class="eyebrow">{len(s['items'])} items</div><h3>{html.escape(s['title'])}</h3><p>{html.escape(s['blurb'])}</p></div></a>""" for s in SETUPS)
    home = f"""<section class="hero"><div><div class="eyebrow">Desk setups &amp; home office ideas</div>
<h1>Build a desk you actually want to sit at.</h1>
<p>Curated desk setups for traders, remote workers and anyone who spends their day at a desk. Every item is picked for how it looks and how it works, with a direct link to shop it.</p>
<p><a class="btn" href="#setups">Shop the setups</a></p></div>
<img src="img/hero.jpg" alt="Dual monitor desk setup with plants and warm lighting"></section>
<h2 id="setups">Shop the setups</h2><div class="grid">{cards}</div>
<div class="band"><div><div class="eyebrow">Coming soon</div><h2 style="margin:.2em 0">Desk wallpapers &amp; the Clean Desk Guide</h2>
<p>A 4K minimalist wallpaper pack and a step-by-step cable management guide, made by The Setup Edit.</p></div></div>"""
    (OUT / "index.html").write_text(page("The Setup Edit | Desk Setups & Home Office Ideas",
        "Curated desk setups, home office ideas and trading desk gear, with links to shop every item.", home), encoding="utf-8")

    for s in SETUPS:
        items = "".join(f"""<div class="item"><div class="num"></div><h3>{html.escape(n)}</h3><p class="model">{html.escape(m)}</p>
<p>{html.escape(w)}</p><a class="btn" href="{amz(a)}" rel="sponsored nofollow noopener" target="_blank">View on Amazon</a></div>""" for n, m, a, w in s["items"])
        body = f"""<section class="setup-hero"><div class="eyebrow">Shop the setup</div><h1>{html.escape(s['title'])}</h1>
<p class="lead">{html.escape(s['blurb'])}</p><p class="note">{html.escape(DISCLOSURE)}</p>
<img src="../img/{s['img']}" alt="{html.escape(s['title'])}"></section>
<div class="items">{items}</div>
<p><a class="btn alt" href="../index.html#setups">&larr; All setups</a></p><div style="height:50px"></div>"""
        (OUT / "setups" / f"{s['slug']}.html").write_text(page(f"{s['title']} | {SITE_NAME}", s["blurb"], body, root="../", og=f"img/{s['img']}"), encoding="utf-8")

    disc = f"""<div class="prose"><div class="eyebrow">Disclosure &amp; privacy</div><h1>Affiliate disclosure</h1>
<p>{html.escape(DISCLOSURE)}</p><p>Product picks are chosen for quality, reviews and how well they fit each setup. Prices and availability change, so always check the current details on Amazon before buying.</p>
<h2>Privacy</h2><p>This site doesn't use its own cookies or collect personal information. Amazon may set cookies when you click an affiliate link, as described in Amazon's own privacy notice.</p></div>"""
    (OUT / "disclosure.html").write_text(page(f"Disclosure | {SITE_NAME}", "Affiliate disclosure and privacy for The Setup Edit.", disc), encoding="utf-8")
    print("built", sum(1 for _ in OUT.rglob("*.html")), "pages")


if __name__ == "__main__":
    build()
