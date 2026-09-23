"""Build The Setup Edit static site into ./docs (served by GitHub Pages).

Edit SETUPS below and re-run:  python build.py
Product images are free-license Unsplash photos (credits in CREDITS below); no Amazon images are used,
and no prices are shown (Amazon Associates rules).
"""
import pathlib, shutil, html, re, datetime, json

ROOT = pathlib.Path(__file__).resolve().parent
OUT = ROOT / "docs"
TAG = "thesetupedi0e-20"
SITE_NAME = "The Setup Edit"
BASE_URL = "https://qman122.github.io/thesetupedit/"

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

# ---- Guides / articles -------------------------------------------------------------
# Body HTML may use [[ASIN]] to drop in a product card for any item already listed in SETUPS.
# Links to setup pages are relative to docs/guides/ (e.g. ../setups/trading-desk-setup.html).
ARTICLES = [
    dict(slug="how-to-build-a-trading-desk-setup", img="trading.jpg", eyebrow="Trading desk guide",
         title="How to Build a Trading Desk Setup (Step by Step)",
         desc="A step-by-step guide to building a trading desk setup: choosing screens, a desk that can carry them, monitor arms, lighting, input devices and cable management.",
         setups=["trading-desk-setup", "cable-management"],
         body="""
<p>A trading desk is a workspace you stare at for hours while making decisions that matter. That changes the priorities. It is less about looking impressive and more about seeing everything at a glance, staying comfortable through long sessions, and removing small distractions. This guide walks through the build in the order that makes sense, so each decision supports the next one.</p>

<h2>Step 1: Decide how many screens you actually need</h2>
<p>Start with your workflow, not with a picture of a wall of monitors. Write down what you need visible at the same time: a main chart, a watchlist, an order entry window, news, maybe a second timeframe. Most people find that two screens cover this comfortably. One screen is the main chart directly in front of you; the other holds everything you glance at.</p>
<p>A useful rule: your primary screen should sit straight ahead at a comfortable viewing distance, and anything you look at constantly should not force you to turn your neck far to either side. If a third screen would only hold something you check occasionally, a window on screen two is often the better answer.</p>

<h2>Step 2: Pick a desk that can carry the load</h2>
<p>Multiple monitors, arms and a laptop add up. You want a stable desk with a solid top that a clamp can grip, and enough depth that screens are not right in your face. If you split your day between research and active sessions, a sit-stand desk lets you change position without breaking focus.</p>
[[B08BHPMYGK]]
<p>Memory presets matter more than they sound. If switching heights takes one button press, you are far more likely to actually do it during a long session.</p>

<h2>Step 3: Mount the monitors instead of using the stands</h2>
<p>Stock monitor stands take up desk space and rarely go high enough. A monitor arm clamps to the back edge of the desk and lets you set height, tilt and angle independently for each screen. For a two-screen layout, a dual arm keeps both displays aligned at the same height, which makes moving your eyes between them easier.</p>
[[B009S750LA]]
<p>Set the top of each screen at or slightly below eye level, and angle the side screen inward so it faces you. If you only run one large display, or you want to add a single screen above a laptop, a single arm does the same job.</p>
[[B00B21TLQU]]

<h2>Step 4: Get the lighting right</h2>
<p>Lighting is the most overlooked part of a trading setup. A bright screen in a dark room is harsh, and a desk lamp that shines onto the screen creates glare on your charts. The fix is two kinds of light: task light on the desk, and soft ambient light behind the screens.</p>
<p>A monitor light bar sits on top of the screen and throws light down onto the desk without reflecting off the display, and it takes up no desk space at all.</p>
[[B076VNFZJG]]
<p>Bias lighting, a strip of LEDs on the back of the monitor, adds a gentle glow to the wall behind the screen. It reduces the contrast between a bright display and a dark room, which many people find more comfortable during evening sessions.</p>
[[B01LG99NW4]]

<h2>Step 5: Choose input devices for long sessions</h2>
<p>You will click, scroll and zoom through charts all day, so the mouse is worth choosing carefully. Look for a shape that supports your whole hand, a fast scroll wheel for moving through timeframes, and programmable buttons for actions you repeat constantly.</p>
[[B0B11LJ69K]]
<p>Keep the keyboard and mouse close to the front edge of the desk at elbow height, so your shoulders stay relaxed rather than reaching forward.</p>

<h2>Step 6: Tame the cables before they tame you</h2>
<p>Two or three monitors, a laptop, a light bar, bias lighting and chargers can mean a lot of cables. Deal with them at the build stage, while everything is already unplugged. Mount a power strip under the desk, run every cable along the monitor arm and down one leg, and leave just enough slack for the desk to move if it is a standing model. Our <a href="cable-management-101-hide-desk-cables.html">cable management guide</a> walks through the process, and the <a href="../setups/cable-management.html">Cable Management Kit</a> lists the parts.</p>

<h2>Step 7: Build the desk behind the desk</h2>
<p>Hardware helps you see the market clearly; it does not make decisions for you. Many traders keep a short shelf of books within reach as a reminder of their process and rules. Two widely read starting points:</p>
[[0735201447]]
[[1535585951]]

<h2>Common mistakes to avoid</h2>
<ul>
<li><strong>Buying screens before measuring the desk.</strong> Check width and depth first so the layout fits.</li>
<li><strong>Placing the main screen off to one side.</strong> The screen you watch most belongs directly in front of you.</li>
<li><strong>Ignoring room lighting.</strong> Glare and harsh contrast are easy to fix and make a real difference to comfort.</li>
<li><strong>Leaving cables for later.</strong> Later rarely comes, and a messy desk is a constant low-level distraction.</li>
</ul>
<p>To see every item from this guide in one place, visit <a href="../setups/trading-desk-setup.html">The Trading Desk Setup</a>.</p>
""",
         faq=[
             ("How many monitors do I need for trading?", "Two screens suit most workflows: one for your main chart and one for watchlists, orders and news. Add more only if you regularly need more information visible at the same time."),
             ("Should monitors be at eye level?", "A common guideline is to place the top of the screen at or slightly below eye level, at roughly arm's length, so you look slightly down at the middle of the display."),
             ("Is a standing desk worth it for a trading setup?", "It is useful if you spend long hours at the desk and like changing position. Choose one with memory presets and enough stability for monitor arms."),
             ("What is bias lighting?", "A light source behind the monitor that softly lights the wall, reducing the contrast between a bright screen and a dark room."),
         ]),

    dict(slug="cable-management-101-hide-desk-cables", img="cable.jpg", eyebrow="Cable management guide",
         title="Cable Management 101: How to Hide Desk Cables for Good",
         desc="A practical cable management guide: how to get power strips off the floor, route desk cables along one path, keep chargers within reach and keep it tidy.",
         setups=["cable-management", "trading-desk-setup"],
         body="""
<p>Cable management is the desk upgrade with the biggest before-and-after for the least effort. A tangle of cords makes even a well-designed desk look chaotic, collects dust, and turns cleaning into a chore. The good news is that you do not need special skills, just an afternoon and a clear method. This guide breaks it down into steps that work for almost any desk.</p>

<h2>Why desk cables get messy</h2>
<p>Most cable chaos comes from four sources: power cables for monitors and lamps, display cables between screens and your computer, charging cables for phones and earbuds, and peripheral cables for keyboards, speakers and hubs. Each gets added at a different time, routed whichever way is easiest that day, and never revisited. The result is a web of cords taking different paths across the desk and floor.</p>
<p>The fix is to give every cable the same short journey: from the device, along a single route, to one power point hidden under the desk.</p>

<h2>Step 1: Unplug everything and take stock</h2>
<p>It sounds drastic, but it is faster than untangling in place. Unplug every cable, lay them out, and ask three questions of each one: is it still needed, is it the right length, and does it belong on the desk at all? You will often find old chargers, duplicate cables and adapters for devices you no longer own. Removing them is the easiest win of the whole project.</p>

<h2>Step 2: Get power off the floor</h2>
<p>A power strip on the floor is where most mess starts. Every cable has to reach down to it, and the strip itself collects dust and gets kicked. Mount it under the desk instead, inside a cable tray attached to the underside of the desktop. Power bricks and excess cable sit in the tray too, so only one cable runs from the desk to the wall.</p>
[[B09J5HH2LR]]
<p>Position the tray toward the back of the desk, where it is out of sight and away from your knees. If your desk is a standing model, place it so the one cable down to the wall has enough slack for the full height range.</p>

<h2>Step 3: Route everything along one path</h2>
<p>Pick a single route from the desktop to the tray, usually down the back edge or along one desk leg, and send every cable that way. If you use a monitor arm, run display and power cables along the arm with ties or clips so they drop neatly behind the desk instead of hanging in a loop.</p>
[[B009S750LA]]
<p>Bundle cables that travel together with reusable hook-and-loop ties rather than zip ties, so adding or swapping a device later does not mean cutting everything apart.</p>

<h2>Step 4: Keep the cables you touch within reach</h2>
<p>Some cables need to stay accessible: phone chargers, a USB-C cable for a laptop, a headphone cable. These are the ones that constantly slip off the back of the desk. Adhesive cable clips along the desk edge hold each one in place, ready to grab.</p>
[[B071FXZBMV]]
<p>Limit these to the cables you use daily. Everything else lives in the tray.</p>

<h2>Step 5: Remove cables you do not need</h2>
<p>The tidiest cable is the one that is not there. A wireless keyboard and mouse remove two cables from the most visible part of the desk. Many wireless peripherals also charge only occasionally, so they spend most of their time cable-free.</p>
[[B0CNT61VMZ]]
[[B0B11LJ69K]]

<h2>Step 6: Label and leave some slack</h2>
<p>Before closing everything up, label both ends of each power cable with a small tag or piece of tape. When you need to unplug one device later, you will not be guessing. Leave a little slack at each device so you can move a monitor or lamp a few inches without pulling cables tight.</p>

<h2>Keeping it tidy long term</h2>
<ul>
<li><strong>Add new devices the same way.</strong> Every new cable goes along the same route to the tray, never straight to the floor.</li>
<li><strong>Do a quick check every few months.</strong> Remove anything you have stopped using.</li>
<li><strong>Keep spare ties in a drawer.</strong> Having them on hand makes it easy to do the job properly.</li>
</ul>
<p>Everything used in this guide is collected in <a href="../setups/cable-management.html">The Cable Management Kit</a>. If you are building a multi-monitor desk from scratch, see <a href="how-to-build-a-trading-desk-setup.html">how to build a trading desk setup</a>.</p>
""",
         faq=[
             ("How do I hide cables on a desk without drilling?", "Use a no-screw under-desk cable tray that clamps or hooks onto the desktop, plus adhesive clips along the edge. Both install without tools."),
             ("Where should the power strip go?", "Under the desk, inside a cable tray near the back edge. That way only a single cable runs from the desk to the wall outlet."),
             ("Zip ties or hook-and-loop ties?", "Reusable hook-and-loop ties are easier to live with, because you can add or remove a cable without cutting anything."),
             ("How do I manage cables on a standing desk?", "Route everything to a tray attached to the desktop so it moves with the desk, and leave enough slack on the single cable to the wall for the full height range."),
         ]),

    dict(slug="small-home-office-ideas", img="small.jpg", eyebrow="Small space guide",
         title="Small Home Office Ideas That Actually Work",
         desc="Practical small home office ideas for corners, bedrooms and apartments: use vertical space, raise screens, light without clutter and keep the floor clear.",
         setups=["small-space-office", "minimal-desk-setup"],
         body="""
<p>A small home office is not a compromise if every item earns its place. The challenge is fitting a real workstation, with a proper screen height, good light and somewhere to put things, into a corner, a bedroom or a slice of a living room. These ideas focus on changes that genuinely free up space rather than just rearranging clutter.</p>

<h2>Start by measuring the real footprint</h2>
<p>Before buying anything, measure the space: width, depth, and the height up to any shelf or window sill. Also note where the nearest outlet is and where light comes from during the day. A compact desk that fits the space with room to push the chair in will always feel better than a larger desk wedged in tight.</p>
<p>Depth is the dimension people underestimate. A shallow desk saves floor space, but it makes it harder to place a screen far enough away. That is exactly where the next ideas come in.</p>

<h2>Go vertical to reclaim the desktop</h2>
<p>In a small office, the desk surface is precious, and the space above and below it is usually wasted. A monitor riser lifts the screen closer to eye level and creates a shelf underneath for a keyboard, notebooks or a laptop when it is closed.</p>
[[B094QTGHNZ]]
<p>If you work from a laptop, a stand does the same thing: it raises the screen and frees the area beneath it. Pair it with a separate keyboard and mouse and a laptop becomes a much more comfortable full-time workstation.</p>
[[B08BRCT4JH]]

<h2>Light the desk without using the desk</h2>
<p>Desk lamps with wide bases take up surprising room. Two alternatives save space entirely. A monitor light bar sits on top of the screen and lights the desk from above without glare on the display.</p>
[[B08DKQ3JG1]]
<p>A clamp-on swing arm lamp attaches to the desk edge and can be pushed out of the way when not needed, which is handy if the desk doubles as a dining or hobby table.</p>
[[B07R56PTMS]]

<h2>Keep the floor clear</h2>
<p>In a small room, the floor around the desk is visible from everywhere. A tangle of cables and a power strip on the floor make the whole room feel busier. Mount the power strip under the desk in a tray so only one cable reaches the wall. Our <a href="cable-management-101-hide-desk-cables.html">cable management guide</a> covers the full process, and the <a href="../setups/cable-management.html">Cable Management Kit</a> lists what you need.</p>
[[B09J5HH2LR]]

<h2>Add comfort you do not have to look at</h2>
<p>Compact spaces often mean a dining chair or a desk that is a little too high. A footrest under the desk gives your feet a stable place to rest and lets you adjust your sitting position without replacing furniture. It stays out of sight, so it adds comfort without adding visual clutter.</p>
[[B07PGLBCFG]]

<h2>Make it feel like a place, not a leftover corner</h2>
<p>A small office works better when it feels intentional. Define the space with a desk pad or a rug under the chair, and add one or two living touches. Small artificial plants fit on a riser or shelf and bring warmth without needing a sunny window or regular watering.</p>
[[B07VKJKFN2]]
<p>Choose a limited palette of two or three colors or materials, such as wood, white and green, so the corner reads as calm rather than crowded. For more on keeping things pared back, see our guide to a <a href="minimalist-desk-setup-essentials.html">minimalist desk setup</a>.</p>

<h2>Bedroom offices: set a boundary</h2>
<p>If your office shares a room with your bed, a clear visual boundary helps separate work from rest. Face the desk away from the bed if you can, keep work items in one tray or drawer, and clear the desk at the end of the day so the room returns to being a bedroom. A few minutes of reset each evening goes a long way.</p>
<p>You can find every item mentioned here in <a href="../setups/small-space-office.html">The Small Space Office</a>.</p>
""",
         faq=[
             ("What is the minimum space for a home office?", "It depends on the desk, but you need enough width for your screen and keyboard, enough depth to keep the screen at a comfortable distance, and room to pull the chair in and out."),
             ("How can I make a small desk feel bigger?", "Move things off the surface: raise the screen on a riser or stand, use a light bar or clamp lamp instead of a desk lamp, and hide cables and power strips under the desk."),
             ("Is a laptop stand worth it for a small space?", "Yes, if you work on a laptop for long periods. It raises the screen and frees space underneath, especially when paired with an external keyboard and mouse."),
             ("How do I separate work and sleep in a bedroom office?", "Face the desk away from the bed if possible, keep work items contained, and clear the desk at the end of each day."),
         ]),

    dict(slug="minimalist-desk-setup-essentials", img="minimal.jpg", eyebrow="Minimal desk guide",
         title="Minimalist Desk Setup: The Essentials and What to Skip",
         desc="How to build a minimalist desk setup: the few essentials worth having, the common extras worth skipping, and simple habits that keep a desk clean.",
         setups=["minimal-desk-setup", "cable-management"],
         body="""
<p>A minimalist desk is not an empty desk. It is a desk where everything on it has a job, and nothing is there out of habit. The payoff is a workspace that looks calm every time you sit down and is quick to clean. This guide covers the essentials worth having, the extras you can skip, and the habits that keep it that way.</p>

<h2>The principle: function first, then fewer and better</h2>
<p>Start by listing what you actually do at your desk: typing, reading, video calls, writing by hand, gaming. Each activity justifies a small set of tools. Anything that does not support one of them is a candidate to remove. Once you have the short list, choose versions that look good together, with a limited palette of materials such as wood, leather, metal or matte black.</p>

<h2>The essentials</h2>
<h3>A defined work surface</h3>
<p>A desk pad is the quickest way to make a desk look put together. It frames the working area, gives the mouse a consistent surface, and covers a worn or cold desktop.</p>
[[B082F5ZLS5]]

<h3>A compact keyboard</h3>
<p>A 75 percent layout keeps the arrow keys and function row but drops the number pad, which saves width and lets the mouse sit closer. Wireless removes one more cable from view.</p>
[[B0CNT61VMZ]]
<p>If you type for long stretches, a wrist rest in a matching material keeps the look consistent and gives your wrists a place to rest between bursts of typing.</p>
[[B09DPGVPG1]]

<h3>A comfortable mouse</h3>
<p>One good mouse beats a drawer of spares. Choose a shape that fits your hand and, ideally, a wireless model so there is nothing trailing across the pad.</p>
[[B0B11LJ69K]]

<h3>Light that stays out of the way</h3>
<p>A clamp-on swing arm lamp takes no desk space and folds away when you do not need it.</p>
[[B07R56PTMS]]

<h3>One screen, positioned well</h3>
<p>For many people, one well-positioned monitor is enough. A single monitor arm removes the bulky stand and lets you set the height and distance precisely, leaving the space under the screen clear.</p>
[[B00B21TLQU]]

<h3>A home for the small things</h3>
<p>Keys, pens, earbuds and cables need somewhere to go, or they spread across the desk. One tray gives them a boundary. When the tray is full, it is time to clear it out.</p>
[[B00KAZ12OS]]
<p>Headphones are the other common drifter. A stand gets them off the surface and keeps them within reach.</p>
[[B01GJQ7N94]]

<h2>What to skip</h2>
<ul>
<li><strong>Multi-compartment organizers.</strong> They invite you to keep more things. One simple tray is usually enough.</li>
<li><strong>A second monitor you rarely use.</strong> If it mostly shows a clock or a chat window, a window on your main screen may do.</li>
<li><strong>Decor for the sake of decor.</strong> Pick one or two objects you genuinely like, such as a small plant or a photo, and stop there.</li>
<li><strong>Visible chargers and power strips.</strong> Move them under the desk.</li>
<li><strong>Paper piles.</strong> Keep a single notebook on the desk and file or scan the rest.</li>
<li><strong>Duplicates.</strong> Several pens, spare mice and extra cables add clutter without adding function.</li>
</ul>

<h2>The hidden essential: cable management</h2>
<p>A minimal desk falls apart the moment cables are visible. Put a power strip in an under-desk tray, route cables along one path, and clip the one or two charging cables you use daily to the desk edge. The <a href="cable-management-101-hide-desk-cables.html">cable management guide</a> walks through it step by step, and the <a href="../setups/cable-management.html">Cable Management Kit</a> lists the parts.</p>
[[B09J5HH2LR]]

<h2>Keep it minimal with a daily reset</h2>
<p>Minimal desks stay minimal through habit, not willpower. At the end of each day, take two minutes to return items to the tray, put away anything that does not live on the desk, and push the chair in. Once a month, look at everything on the desk and ask whether it still earns its place.</p>
<p>See every item from this guide in <a href="../setups/minimal-desk-setup.html">The Clean Minimal Desk</a>. Working with limited space as well? Read our <a href="small-home-office-ideas.html">small home office ideas</a>.</p>
""",
         faq=[
             ("What do I need for a minimalist desk setup?", "A defined work surface, a compact keyboard, a comfortable mouse, space-saving light, a well-positioned screen, and one tray for small items. Hidden cable management ties it together."),
             ("Is one monitor enough for a minimalist setup?", "For many workflows, yes. A single monitor on an arm keeps the desk clear. Add a second only if you regularly need two things visible at once."),
             ("How do I keep a minimalist desk clean?", "Do a short reset at the end of each day, give small items a single tray, and move chargers and power strips under the desk."),
             ("Can a minimalist desk still have personality?", "Yes. Choose a consistent palette of materials and one or two objects you genuinely like, rather than many small decorations."),
         ]),
]


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
.article{max-width:760px;padding:40px 0 30px}.article h2{margin-top:1.3em}.article li{margin:.3em 0}
.article .cover{border-radius:22px;aspect-ratio:21/9;object-fit:cover;width:100%;margin:24px 0 8px}
.pick{background:var(--card);border:1px solid var(--line);border-radius:18px;padding:18px 22px;margin:20px 0;display:flex;gap:20px;align-items:center;justify-content:space-between}
.pick h3{margin:0}.pick p{margin:4px 0}.pick .model{font-size:14px;color:var(--muted)}.pick .btn{flex-shrink:0}
.faq h3{font-size:21px;margin:1.1em 0 .3em}.faq p{margin:0 0 .6em}
.related{display:flex;flex-wrap:wrap;gap:10px;margin:10px 0 0}
@media (max-width:760px){.hero,.grid,.items{grid-template-columns:1fr}.hero{padding:32px 0}.nav nav a{margin-left:14px;font-size:14px}.band{padding:26px}.pick{flex-direction:column;align-items:flex-start}}
@media (max-width:430px){.brand{font-size:13px;letter-spacing:.18em}.nav nav a{margin-left:10px;font-size:13px}}
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
<nav><a href="{root}index.html#setups">Setups</a><a href="{root}index.html#guides">Guides</a><a href="{root}disclosure.html">Disclosure</a></nav></div></header>
<main class="wrap">"""

FOOT = """</main><footer><div class="wrap"><p>{disc}</p>
<p>Photos from <a href="https://unsplash.com" rel="nofollow">Unsplash</a> ({credits}). Products shown in photos may differ from the linked items.</p>
<p>&copy; 2026 The Setup Edit</p></div></footer></body></html>"""


def page(title, desc, body, root="", og="img/hero.jpg"):
    credits = ", ".join(f'<a href="https://unsplash.com/photos/{i}" rel="nofollow">{html.escape(n)}</a>' for _, n, i in CREDITS)
    return (HEAD.format(title=html.escape(title), desc=html.escape(desc), og=root + og, root=root) + body
            + FOOT.format(disc=html.escape(DISCLOSURE), credits=credits))


PRODUCTS = {a: (n, m, w) for s in SETUPS for n, m, a, w in s["items"]}


def product_card(match):
    asin = match.group(1)
    n, m, w = PRODUCTS[asin]  # KeyError here means the ASIN isn't in SETUPS
    return (f"""<div class="pick"><div><h3>{html.escape(n)}</h3><p class="model">{html.escape(m)}</p><p>{html.escape(w)}</p></div>"""
            f"""<a class="btn" href="{amz(asin)}" rel="sponsored nofollow noopener" target="_blank">View on Amazon</a></div>""")


def related_guides(setup_slug):
    rel = [a for a in ARTICLES if setup_slug in a["setups"]]
    if not rel:
        return ""
    links = "".join(f'<a class="btn alt" href="../guides/{a["slug"]}.html">{html.escape(a["title"])}</a>' for a in rel)
    return f'<h2>Related guides</h2><div class="related">{links}</div><div style="height:30px"></div>'


def build_guides():
    (OUT / "guides").mkdir(exist_ok=True)
    titles = {s["slug"]: s["title"] for s in SETUPS}
    for a in ARTICLES:
        body_html = re.sub(r"\[\[([0-9A-Z]{10})\]\]", product_card, a["body"])
        faq = "".join(f"<h3>{html.escape(q)}</h3><p>{html.escape(ans)}</p>" for q, ans in a["faq"])
        ld = {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
            {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": ans}} for q, ans in a["faq"]]}
        setup_links = "".join(f'<a class="btn alt" href="../setups/{sl}.html">{html.escape(titles[sl])}</a>' for sl in a["setups"])
        body = f"""<article class="article"><div class="eyebrow">{html.escape(a['eyebrow'])}</div><h1>{html.escape(a['title'])}</h1>
<p class="lead">{html.escape(a['desc'])}</p><p class="note">{html.escape(DISCLOSURE)}</p>
<img class="cover" src="../img/{a['img']}" alt="{html.escape(a['title'])}">
{body_html}
<section class="faq"><h2>FAQ</h2>{faq}</section>
<h2>Shop the setups</h2><div class="related">{setup_links}</div>
<p style="margin-top:34px"><a class="btn alt" href="../index.html#guides">&larr; All guides</a></p></article>
<script type="application/ld+json">{json.dumps(ld)}</script><div style="height:30px"></div>"""
        (OUT / "guides" / f"{a['slug']}.html").write_text(
            page(f"{a['title']} | {SITE_NAME}", a["desc"], body, root="../", og=f"img/{a['img']}"), encoding="utf-8")


def build_sitemap():
    today = datetime.date.today().isoformat()
    paths = [""] + [f"setups/{s['slug']}.html" for s in SETUPS] + [f"guides/{a['slug']}.html" for a in ARTICLES] + ["disclosure.html"]
    urls = "".join(f"<url><loc>{BASE_URL}{p}</loc><lastmod>{today}</lastmod></url>\n" for p in paths)
    (OUT / "sitemap.xml").write_text('<?xml version="1.0" encoding="UTF-8"?>\n'
        f'<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{urls}</urlset>\n', encoding="utf-8")
    (OUT / "robots.txt").write_text(f"User-agent: *\nAllow: /\n\nSitemap: {BASE_URL}sitemap.xml\n", encoding="utf-8")


def build():
    if OUT.exists():
        shutil.rmtree(OUT)
    (OUT / "setups").mkdir(parents=True)
    shutil.copytree(ROOT / "img", OUT / "img")
    (OUT / "style.css").write_text(CSS, encoding="utf-8")
    (OUT / ".nojekyll").write_text("")
    if (ROOT / "media").exists(): shutil.copytree(ROOT / "media", OUT / "media")

    cards = "".join(f"""<a class="card" href="setups/{s['slug']}.html"><img src="img/{s['img']}" alt="{html.escape(s['title'])}" loading="lazy">
<div class="in"><div class="eyebrow">{len(s['items'])} items</div><h3>{html.escape(s['title'])}</h3><p>{html.escape(s['blurb'])}</p></div></a>""" for s in SETUPS)
    guide_cards = "".join(f"""<a class="card" href="guides/{a['slug']}.html"><img src="img/{a['img']}" alt="{html.escape(a['title'])}" loading="lazy">
<div class="in"><div class="eyebrow">{html.escape(a['eyebrow'])}</div><h3>{html.escape(a['title'])}</h3><p>{html.escape(a['desc'])}</p></div></a>""" for a in ARTICLES)
    home = f"""<section class="hero"><div><div class="eyebrow">Desk setups &amp; home office ideas</div>
<h1>Build a desk you actually want to sit at.</h1>
<p>Curated desk setups for traders, remote workers and anyone who spends their day at a desk. Every item is picked for how it looks and how it works, with a direct link to shop it.</p>
<p><a class="btn" href="#setups">Shop the setups</a></p></div>
<img src="img/hero.jpg" alt="Dual monitor desk setup with plants and warm lighting"></section>
<h2 id="setups">Shop the setups</h2><div class="grid">{cards}</div>
<h2 id="guides">Guides</h2><div class="grid">{guide_cards}</div>
<div class="band"><div><div class="eyebrow">From The Setup Edit</div><h2 style="margin:.2em 0">Guides &amp; wallpapers</h2>
<p>The Clean Desk Guide (15-page printable), a free Desk Cable Checklist, and a 4K minimalist wallpaper pack. Instant downloads.</p></div>
<div style="display:flex;gap:12px;flex-wrap:wrap"><a class="btn" href="https://payhip.com/b/XAPfb" rel="noopener" target="_blank">Free checklist</a>
<a class="btn" href="https://payhip.com/b/3MK0F" rel="noopener" target="_blank">The Clean Desk Guide</a>
<a class="btn" href="https://payhip.com/b/XqrMo" rel="noopener" target="_blank">Wallpaper pack</a></div></div>"""
    (OUT / "index.html").write_text(page("The Setup Edit | Desk Setups & Home Office Ideas",
        "Curated desk setups, home office ideas and trading desk gear, with links to shop every item.", home), encoding="utf-8")

    for s in SETUPS:
        items = "".join(f"""<div class="item"><div class="num"></div><h3>{html.escape(n)}</h3><p class="model">{html.escape(m)}</p>
<p>{html.escape(w)}</p><a class="btn" href="{amz(a)}" rel="sponsored nofollow noopener" target="_blank">View on Amazon</a></div>""" for n, m, a, w in s["items"])
        body = f"""<section class="setup-hero"><div class="eyebrow">Shop the setup</div><h1>{html.escape(s['title'])}</h1>
<p class="lead">{html.escape(s['blurb'])}</p><p class="note">{html.escape(DISCLOSURE)}</p>
<img src="../img/{s['img']}" alt="{html.escape(s['title'])}"></section>
<div class="items">{items}</div>
{related_guides(s['slug'])}<p><a class="btn alt" href="../index.html#setups">&larr; All setups</a></p><div style="height:50px"></div>"""
        (OUT / "setups" / f"{s['slug']}.html").write_text(page(f"{s['title']} | {SITE_NAME}", s["blurb"], body, root="../", og=f"img/{s['img']}"), encoding="utf-8")

    disc = f"""<div class="prose"><div class="eyebrow">Disclosure &amp; privacy</div><h1>Affiliate disclosure</h1>
<p>{html.escape(DISCLOSURE)}</p><p>Product picks are chosen for quality, reviews and how well they fit each setup. Prices and availability change, so always check the current details on Amazon before buying.</p>
<h2>Privacy</h2><p>This site doesn't use its own cookies or collect personal information. Amazon may set cookies when you click an affiliate link, as described in Amazon's own privacy notice.</p></div>"""
    (OUT / "disclosure.html").write_text(page(f"Disclosure | {SITE_NAME}", "Affiliate disclosure and privacy for The Setup Edit.", disc), encoding="utf-8")
    build_guides()
    build_sitemap()
    print("built", sum(1 for _ in OUT.rglob("*.html")), "pages")


if __name__ == "__main__":
    build()
