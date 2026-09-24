"""Build The Setup Edit static site into ./docs (served by GitHub Pages).

Edit SETUPS below and re-run:  python build.py
Product images are free-license Unsplash photos (credits in CREDITS below); no Amazon images are used,
and no prices are shown (Amazon Associates rules).
"""
import pathlib, shutil, html, re, datetime, json, math, subprocess, struct, hashlib

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
    dict(slug="how-to-build-a-trading-desk-setup", img="trading.jpg", eyebrow="Trading desk guide", date="2026-09-23",
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

    dict(slug="cable-management-101-hide-desk-cables", img="cable.jpg", eyebrow="Cable management guide", date="2026-09-23",
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

    dict(slug="small-home-office-ideas", img="small.jpg", eyebrow="Small space guide", date="2026-09-23",
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

    dict(slug="minimalist-desk-setup-essentials", img="minimal.jpg", eyebrow="Minimal desk guide", date="2026-09-23",
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


# ---- Stylesheet (written to docs/style.css) ---------------------------------------------
CSS = r"""
/* The Setup Edit: editorial stylesheet */
:root{
  --paper:#F6F1E7; --cream:#EFE6D6; --sand:#E5D8C2; --ink:#1E2A26; --ink-2:#22302B; --moss:#2C3A34;
  --stone:#5C5A53; --clay:#C0582F; --clay-ink:#9C4320; --clay-soft:#E39A76;
  --on-dark:#F2EADB; --on-dark-2:#BDB6A8; --rule:rgba(30,42,38,.16); --rule-dark:rgba(242,234,219,.18);
  --serif:"Newsreader",Georgia,"Times New Roman",serif; --sans:"Inter Tight","Helvetica Neue",Arial,system-ui,sans-serif;
  --pad:clamp(20px,4.4vw,64px); --gut:clamp(16px,1.8vw,28px); --sec:clamp(80px,10vw,152px);
  --ease:cubic-bezier(.2,.7,.2,1);
}
*,*::before,*::after{box-sizing:border-box}
html{-webkit-text-size-adjust:100%;text-size-adjust:100%}
@media (prefers-reduced-motion:no-preference){html{scroll-behavior:smooth}}
body{margin:0;background:var(--paper);color:var(--ink);font:400 17px/1.6 var(--sans);-webkit-font-smoothing:antialiased;
  -moz-osx-font-smoothing:grayscale;overflow-wrap:break-word;font-kerning:normal;overflow-x:hidden}
img{max-width:100%;height:auto;display:block}picture{display:block}
a{color:inherit;text-decoration:none}
h1,h2,h3{font-family:var(--serif);font-weight:400;margin:0;line-height:1.08;letter-spacing:-.015em;text-wrap:balance}
p{margin:0;text-wrap:pretty}ul,ol{margin:0;padding:0;list-style:none}figure{margin:0}
em,i{font-style:italic}
::selection{background:var(--clay);color:var(--paper)}
:focus-visible{outline:2px solid var(--clay-ink);outline-offset:3px;border-radius:1px}
.band-dark :focus-visible,.foot :focus-visible{outline-color:var(--clay-soft)}
.skip{position:absolute;left:12px;top:-60px;z-index:10;background:var(--ink);color:var(--paper);padding:10px 14px;font-size:14px}
.skip:focus{top:12px}
.wrap{width:100%;max-width:1440px;margin-inline:auto;padding-inline:var(--pad)}
.label{font:600 11.5px/1.35 var(--sans);letter-spacing:.14em;text-transform:uppercase}
.kicker{color:var(--clay-ink)}
.section{padding-block:var(--sec)}
.band{padding-block:var(--sec)}
.band-cream{background:var(--cream)}
.band-dark{background:var(--ink);color:var(--on-dark)}
.band-dark .kicker{color:var(--clay-soft)}

/* links */
.ulink{background:linear-gradient(currentColor,currentColor) 0 100%/0 1px no-repeat;transition:background-size .4s var(--ease)}
.ulink:hover{background-size:100% 1px}
.uline{background:linear-gradient(currentColor,currentColor) 0 96%/0 1px no-repeat;transition:background-size .5s var(--ease)}
a:hover .uline,a:focus-visible .uline{background-size:100% 1px}
.cta{display:inline-flex;align-items:center;gap:.55em;font:600 12px/1 var(--sans);letter-spacing:.12em;text-transform:uppercase;
  white-space:nowrap;padding:.9em 0 .75em;border-bottom:1px solid currentColor;transition:color .25s,border-color .25s}
.cta .arr{display:inline-block;font-family:var(--sans);letter-spacing:0;transition:transform .35s var(--ease)}
.cta:hover{color:var(--clay-ink)}.cta:hover .arr{transform:translateX(4px)}
.cta-back:hover .arr{transform:translateX(-4px)}
.band-dark .cta:hover{color:var(--clay-soft)}
.media{display:block;overflow:hidden;background:var(--sand)}
.media img{width:100%;height:100%;object-fit:cover;transition:transform 1.4s var(--ease)}
a:hover .media img,a.media:hover img{transform:scale(1.02)}

/* reveal */
.js .reveal{opacity:0;transform:translateY(16px);transition:opacity 1s var(--ease),transform 1s var(--ease)}
.js .reveal.in{opacity:1;transform:none}
@media (prefers-reduced-motion:reduce){.js .reveal{opacity:1;transform:none;transition:none}.media img,.cta .arr,.ulink,.uline{transition:none}}

/* masthead */
.mast-top{display:flex;justify-content:space-between;gap:16px;padding:12px 0 11px;color:var(--stone);border-bottom:1px solid var(--rule)}
.mast-top span:first-child{display:none}
.mast-main{display:flex;flex-wrap:wrap;align-items:baseline;justify-content:space-between;padding:18px 0 0;border-bottom:1px solid var(--ink)}
.wordmark{font:400 29px/1 var(--serif);letter-spacing:-.025em;padding-bottom:16px;font-variation-settings:"opsz" 48}
.wordmark i{font-weight:300}
.primary{display:flex;width:100%;justify-content:space-between;border-top:1px solid var(--rule);padding:11px 0 12px}
.primary a{font:500 12px/1 var(--sans);letter-spacing:.14em;text-transform:uppercase;padding:4px 0;border-bottom:1px solid transparent;transition:border-color .3s,color .3s}
.primary a:hover{color:var(--clay-ink)}
.primary a[aria-current]{border-bottom-color:var(--ink)}
@media (min-width:700px){
  .mast-top span:first-child{display:inline}
  .mast-main{flex-wrap:nowrap;padding:24px 0 20px}
  .wordmark{font-size:34px;padding:0}
  .primary{width:auto;border:0;padding:0;gap:clamp(22px,3vw,44px)}
}

/* shared type */
.sec-head{display:grid;gap:14px;padding-bottom:28px;border-bottom:1px solid var(--ink);margin-bottom:0}
.sec-title{font-size:clamp(38px,5.6vw,80px);font-weight:300;letter-spacing:-.03em;line-height:1;font-variation-settings:"opsz" 72}
.sec-title em{font-weight:300}
.sec-count{color:var(--stone)}
.caption{display:flex;flex-direction:column;gap:4px;padding-top:12px;font-size:13px;line-height:1.5;color:var(--stone)}
.caption .label{color:var(--ink);margin-right:.8em}
.model{font:600 11px/1.4 var(--sans);letter-spacing:.13em;text-transform:uppercase;color:var(--stone)}
.disclosure{font-size:13px;line-height:1.55;color:var(--stone);border-top:1px solid var(--rule);padding-top:14px;margin-top:22px;max-width:52ch}
.disclosure .label{color:var(--ink);margin-right:.5em;font-size:10.5px}

/* cover */
.cover{padding-top:clamp(36px,6vw,96px)}
.cover-lines{display:none}
.cover-title{font-size:clamp(50px,13.4vw,168px);font-weight:300;letter-spacing:-.045em;line-height:.9;max-width:11.5ch;
  font-variation-settings:"opsz" 72}
.cover-title em{font-weight:300;letter-spacing:-.03em}
.cover-row{display:grid;gap:14px;margin-top:clamp(28px,4vw,56px);padding:18px 0 clamp(28px,3.4vw,44px);border-top:1px solid var(--ink)}
.cover-dek{font:400 19px/1.5 var(--serif);color:var(--ink-2);max-width:46ch}
.cover-row .cta{justify-self:start}
.bleed img{width:100%;object-fit:cover}
.cover-fig img{aspect-ratio:4/3}
.setup-fig img{aspect-ratio:4/3}
@media (min-width:700px){.cover-title{font-size:clamp(50px,10.4vw,168px)}}
@media (min-width:1000px){
  .cover-top{display:grid;grid-template-columns:repeat(12,minmax(0,1fr));column-gap:var(--gut);align-items:end}
  .cover-title{grid-column:1/10}
  .cover-lines{display:block;grid-column:10/13;border-top:1px solid var(--ink);padding-top:10px;margin-bottom:10px}
  .cover-lines li{border-bottom:1px solid var(--rule)}
  .cover-lines a{display:flex;gap:14px;align-items:baseline;padding:11px 0;font:400 18px/1.25 var(--serif);letter-spacing:-.01em}
  .cover-row{grid-template-columns:repeat(12,minmax(0,1fr));column-gap:var(--gut);align-items:start}
  .cover-row .label{grid-column:1/4;padding-top:6px}
  .cover-row .cover-dek{grid-column:4/9;font-size:21px}
  .cover-row .cta{grid-column:11/13;justify-self:end;padding-top:.4em}
  .cover-fig img{aspect-ratio:auto;height:min(78vh,760px);min-height:480px}
  .setup-fig img{aspect-ratio:auto;height:min(72vh,680px);min-height:440px}
  .caption{flex-direction:row;justify-content:space-between;gap:24px}
}

/* setups index */
.feature{display:grid;gap:22px;padding-block:clamp(40px,7vw,120px);border-bottom:1px solid var(--rule)}
.feature:last-child{border-bottom:0;padding-bottom:0}
.feature-media img{aspect-ratio:4/3}
.f2 .feature-media img{aspect-ratio:4/5}.f3 .feature-media img{aspect-ratio:3/2}.f4 .feature-media img{aspect-ratio:16/10}
.no{display:flex;align-items:baseline;gap:10px;color:var(--clay-ink)}
.no-n{font:300 clamp(56px,6vw,92px)/.8 var(--serif);letter-spacing:-.04em;color:var(--clay);font-variant-numeric:lining-nums;font-variation-settings:"opsz" 72}
.feature-title{font-size:clamp(32px,3.5vw,52px);font-weight:350;letter-spacing:-.025em;line-height:1.02;margin:22px 0 14px}
.feature-title a{background:linear-gradient(currentColor,currentColor) 0 96%/0 1px no-repeat;transition:background-size .5s var(--ease)}
.feature-title a:hover{background-size:100% 1px}
.feature-dek{color:var(--stone);max-width:38ch}
.feature-meta{display:flex;align-items:center;justify-content:space-between;gap:16px;margin-top:26px;border-top:1px solid var(--rule);padding-top:6px}
@media (min-width:1000px){.feature-meta{max-width:420px}}
.feature-meta .label{color:var(--stone)}
@media (min-width:1000px){
  .sec-head{grid-template-columns:repeat(12,minmax(0,1fr));column-gap:var(--gut);align-items:end}
  .sec-head>.label:first-child{grid-column:1/4;align-self:start;padding-top:10px}
  .sec-title{grid-column:4/11}
  .sec-count{grid-column:11/13;justify-self:end}
  .feature{grid-template-columns:repeat(12,minmax(0,1fr));column-gap:var(--gut);row-gap:0;align-items:end}
  .feature>*{grid-row:1}
  .f1 .feature-media{grid-column:6/13}.f1 .feature-text{grid-column:1/5}
  .f2 .feature-media{grid-column:1/6}.f2 .feature-text{grid-column:8/12;align-self:center}
  .f3 .feature-media{grid-column:5/12}.f3 .feature-text{grid-column:1/5;align-self:start}
  .f4 .feature-media{grid-column:2/9}.f4 .feature-text{grid-column:9/13;padding-left:var(--gut)}
}

/* guides list */
.guide-row a{display:grid;grid-template-columns:minmax(0,1fr) 88px;column-gap:18px;row-gap:12px;padding:28px 0;border-bottom:1px solid var(--rule)}
.gr-meta{grid-column:1/-1;display:flex;gap:18px;color:var(--stone)}
.gr-text{grid-column:1}
.gr-title{font-size:clamp(24px,2.6vw,36px);font-weight:400;letter-spacing:-.02em;line-height:1.1;margin:10px 0 10px}
.gr-dek{color:var(--stone);font-size:15.5px;line-height:1.55;max-width:58ch;display:none}
.gr-thumb{grid-column:2;grid-row:2}
.gr-thumb img{aspect-ratio:1}
@media (min-width:700px){.gr-dek{display:block}}
@media (min-width:1000px){
  .guide-row a{grid-template-columns:repeat(12,minmax(0,1fr));column-gap:var(--gut);padding:40px 0;align-items:start}
  .gr-meta{grid-column:1/4;flex-direction:column;gap:6px;padding-top:6px}
  .gr-text{grid-column:4/10}
  .gr-thumb{grid-column:10/13;grid-row:1}
  .gr-thumb img{aspect-ratio:3/2}
}

/* shop */
.shop-grid{display:grid;gap:48px}
.shop-head .sec-title{margin:16px 0 20px;color:var(--on-dark)}
.shop-head p:last-child{color:var(--on-dark-2);max-width:36ch}
.products{display:grid;gap:36px}
.product{display:grid;grid-template-columns:112px minmax(0,1fr);gap:20px;align-items:start;align-content:start}
.product-name{font-size:26px;font-weight:400;letter-spacing:-.02em;margin:8px 0 8px;color:var(--on-dark)}
.product-desc{color:var(--on-dark-2);font-size:15.5px;line-height:1.55;margin-bottom:10px;max-width:34ch}
.tile{position:relative;display:flex;flex-direction:column;justify-content:space-between;aspect-ratio:4/5;padding:12px;overflow:hidden;
  transition:transform .8s var(--ease)}
.tile:hover{transform:translateY(-4px)}
.tile-brand{font:600 7.5px/1.2 var(--sans);letter-spacing:.16em;text-transform:uppercase}
.tile-name{font:400 15px/1.02 var(--serif);letter-spacing:-.02em;position:relative}
.tile-check{background:var(--cream);color:var(--ink)}
.tile-guide{background:var(--clay);color:var(--paper)}
.tile-wall{background:var(--moss);color:var(--on-dark)}
.tile-lines{display:grid;gap:12px;margin:auto 0 auto 2px}
.tile-lines i{display:block;height:1px;background:rgba(30,42,38,.3);position:relative;margin-left:14px}
.tile-lines i::before{content:"";position:absolute;left:-14px;top:-4px;width:8px;height:8px;border:1px solid var(--ink)}
.tile-lines i:nth-child(-n+2)::after{content:"";position:absolute;left:-12px;top:-3px;width:4px;height:2px;border:solid var(--clay);border-width:0 0 1.5px 1.5px;transform:rotate(-45deg)}
.tile-pp{font:300 italic 34px/1 var(--serif);margin:auto 0;opacity:.9}
.tile-horizon{position:absolute;inset:0}
.tile-horizon::before{content:"";position:absolute;left:0;right:0;top:52%;height:1px;background:rgba(242,234,219,.35)}
.tile-horizon i{position:absolute;width:24%;aspect-ratio:1;border-radius:50%;background:var(--clay);left:60%;top:calc(52% - 12%)}
@media (min-width:700px){
  .products{grid-template-columns:repeat(3,minmax(0,1fr));gap:var(--gut)}
  .product{grid-template-columns:1fr;gap:22px}
  .tile{padding:18px}
  .tile-brand{font-size:9px}.tile-name{font-size:clamp(20px,2vw,28px)}
  .tile-lines{gap:14px}.tile-lines i{margin-left:22px}
  .tile-lines i::before{left:-22px;top:-6px;width:12px;height:12px}
  .tile-lines i:nth-child(-n+2)::after{left:-19px;top:-4px;width:6px;height:3px}
  .tile-pp{font-size:clamp(48px,5vw,72px)}
}
@media (min-width:1000px){
  .shop-grid{grid-template-columns:repeat(12,minmax(0,1fr));column-gap:var(--gut)}
  .shop-head{grid-column:1/5;align-self:start;position:sticky;top:40px}
  .products{grid-column:6/13}
}

/* about */
.about{display:grid;gap:18px}
.about-text{display:grid;gap:22px;max-width:760px}
.about-lede{font:350 clamp(26px,2.8vw,40px)/1.18 var(--serif);letter-spacing:-.02em}
.about-text p:not(.about-lede){color:var(--stone);max-width:56ch}
.about-text .cta{justify-self:start}
@media (min-width:1000px){.about{grid-template-columns:repeat(12,minmax(0,1fr));column-gap:var(--gut)}
  .about>.label{grid-column:1/4;padding-top:12px}.about-text{grid-column:4/11}
  .about-text p:not(.about-lede){margin-left:calc(100% / 7)}
  .about-text .cta{margin-left:calc(100% / 7)}}

/* footer */
.foot{background:var(--ink);color:var(--on-dark-2);padding:clamp(64px,8vw,112px) 0 36px;font-size:14px;line-height:1.6}
.foot a{color:var(--on-dark)}
.foot-top{display:grid;gap:18px;padding-bottom:40px}
.foot-mark{font:300 clamp(44px,7.6vw,120px)/.9 var(--serif);letter-spacing:-.045em;color:var(--on-dark);font-variation-settings:"opsz" 72}
.foot-tag{max-width:34ch;font-size:15px}
.foot-cols{display:grid;grid-template-columns:1fr 1fr;gap:36px 24px;padding:32px 0 40px;border-top:1px solid var(--rule-dark);border-bottom:1px solid var(--rule-dark)}
.fcol .label{color:var(--on-dark-2);margin-bottom:14px}
.fcol li{margin:7px 0;line-height:1.35}
.foot-legal{display:grid;gap:12px;padding-top:28px;font-size:13px;max-width:92ch}
.foot-end{display:flex;justify-content:space-between;gap:16px;margin-top:16px}
@media (min-width:1000px){
  .foot-top{grid-template-columns:repeat(12,minmax(0,1fr));column-gap:var(--gut);align-items:end}
  .foot-mark{grid-column:1/9}.foot-tag{grid-column:10/13}
  .foot-cols{grid-template-columns:repeat(4,minmax(0,1fr));column-gap:var(--gut)}
  .foot-legal{max-width:none;grid-template-columns:repeat(12,minmax(0,1fr));column-gap:var(--gut)}
  .foot-legal p{grid-column:1/9}.foot-legal .foot-end{grid-column:1/-1}
}

/* page heads (setup, guide, about, 404) */
.page-head{padding-top:clamp(28px,4.4vw,72px);padding-bottom:clamp(32px,4.4vw,64px)}
.crumbs{display:flex;gap:10px;color:var(--stone);margin-bottom:clamp(24px,3.4vw,48px)}
.crumbs a{color:var(--ink)}
.ph-grid{display:grid;gap:24px}
.ph-title{font-size:clamp(46px,7.6vw,120px);font-weight:300;letter-spacing:-.04em;line-height:.94;font-variation-settings:"opsz" 72}
.ph-title em{font-weight:300}
.ph-dek{font:400 21px/1.42 var(--serif);color:var(--ink-2);max-width:40ch}
.ph-meta{margin-top:18px;color:var(--stone)}
@media (min-width:1000px){
  .ph-grid{grid-template-columns:repeat(12,minmax(0,1fr));column-gap:var(--gut);align-items:end}
  .ph-title{grid-column:1/9}.ph-aside{grid-column:9/13;padding-bottom:6px}
}

/* shopping list */
.list-grid{display:grid;padding-top:clamp(48px,6vw,96px);padding-bottom:clamp(48px,6vw,96px)}
.list-index{display:none}
.shop-list{border-top:1px solid var(--ink)}
.item{display:grid;grid-template-columns:44px minmax(0,1fr);column-gap:14px;padding:26px 0 28px;border-bottom:1px solid var(--rule);scroll-margin-top:24px}
.item-no{font:300 30px/1 var(--serif);color:var(--clay);letter-spacing:-.03em;font-variant-numeric:lining-nums tabular-nums;padding-top:2px}
.item-name{font-size:clamp(26px,2.4vw,34px);font-weight:400;letter-spacing:-.02em;line-height:1.08}
.item .model{margin-top:10px}
.item-why{margin-top:12px;color:var(--ink-2);max-width:52ch;font-size:16.5px;line-height:1.55}
.item .cta{grid-column:2;justify-self:start;margin-top:14px}
@media (min-width:700px){
  .item{grid-template-columns:72px minmax(0,1fr) auto;column-gap:24px;padding:34px 0 36px}
  .item-no{font-size:40px}
  .item .cta{grid-column:3;grid-row:1;align-self:start;margin-top:0}
}
@media (min-width:1000px){
  .list-grid{grid-template-columns:repeat(12,minmax(0,1fr));column-gap:var(--gut)}
  .list-index{display:block;grid-column:1/4;align-self:start;position:sticky;top:32px;padding-top:18px}
  .shop-list{grid-column:5/13}
}
.list-index ol,.toc ol{margin-top:16px;border-left:1px solid var(--rule)}
.list-index a,.toc a{display:flex;gap:12px;padding:7px 0 7px 16px;margin-left:-1px;border-left:1px solid transparent;font-size:14px;line-height:1.35;color:var(--stone);transition:color .25s,border-color .25s}
.list-index a:hover,.toc a:hover{color:var(--ink)}
.list-index a[aria-current],.toc a[aria-current]{color:var(--ink);border-left-color:var(--clay)}
.ix-n{font:600 11px/1.6 var(--sans);letter-spacing:.08em;color:var(--clay-ink);font-variant-numeric:tabular-nums}

/* related + next */
.related{display:grid;gap:18px;padding-top:0}
.rel-list{border-top:1px solid var(--ink)}
.rel-list a{display:grid;grid-template-columns:minmax(0,1fr) auto;gap:8px 20px;align-items:center;padding:24px 0;border-bottom:1px solid var(--rule)}
.rel-list .label{grid-column:1/-1;color:var(--stone)}
.rel-title{font:400 clamp(24px,2.6vw,36px)/1.1 var(--serif);letter-spacing:-.02em;text-wrap:balance}
.rel-list .arr{font-size:22px;transition:transform .35s var(--ease)}
.rel-list a:hover .arr{transform:translateX(6px)}
@media (min-width:1000px){.related{grid-template-columns:repeat(12,minmax(0,1fr));column-gap:var(--gut)}
  .related>.label{grid-column:1/4;padding-top:6px}.rel-list{grid-column:5/13}}
.next{padding-block:clamp(56px,7vw,112px)}
.next-link{display:grid;gap:24px}
.next-text{display:grid;gap:16px;align-content:center}
.next-text .label{color:var(--clay-ink)}
.next-title{font:300 clamp(40px,6vw,92px)/.95 var(--serif);letter-spacing:-.04em;text-wrap:balance;font-variation-settings:"opsz" 72}
.next-dek{color:var(--stone);max-width:44ch}
.next-media img{aspect-ratio:3/2}
@media (min-width:1000px){.next-link{grid-template-columns:repeat(12,minmax(0,1fr));column-gap:var(--gut)}
  .next-text{grid-column:1/8}.next-media{grid-column:9/13}}

/* guide page */
.guide-title{max-width:17ch}
.gh-row{display:grid;gap:8px;margin-top:clamp(26px,3.4vw,48px);padding-top:22px;border-top:1px solid var(--ink)}
.gh-dek{font:italic 350 clamp(20px,1.9vw,25px)/1.42 var(--serif);color:var(--ink-2);max-width:44ch}
.gh-meta .label{color:var(--stone);margin-top:14px}
.gh-meta .disclosure{margin-top:14px}
.guide-fig{display:grid}
.guide-fig img{aspect-ratio:3/2}
@media (min-width:1000px){
  .gh-row{grid-template-columns:repeat(12,minmax(0,1fr));column-gap:var(--gut)}
  .gh-dek{grid-column:1/8}.gh-meta{grid-column:9/13}.gh-meta .label{margin-top:6px}
  .guide-fig{grid-template-columns:repeat(12,minmax(0,1fr));column-gap:var(--gut)}
  .guide-fig picture{grid-column:1/11}
  .guide-fig img{aspect-ratio:16/9}
  .guide-fig .caption{grid-column:11/13;flex-direction:column;justify-content:flex-end;padding:0 0 4px;border-bottom:1px solid var(--rule);padding-bottom:12px;align-self:end}
}
.article-grid{display:grid;padding-top:clamp(48px,6vw,96px);padding-bottom:var(--sec)}
.toc{display:none}
@media (min-width:1000px){
  .article-grid{grid-template-columns:repeat(12,minmax(0,1fr));column-gap:var(--gut)}
  .toc{display:block;grid-column:1/4;align-self:start;position:sticky;top:32px;padding-right:12px}
  .prose{grid-column:4/11}
}

/* prose */
.prose{font:400 19px/1.68 var(--serif);color:var(--ink-2);max-width:68ch;font-variation-settings:"opsz" 16}
.prose>p+p{margin-top:1.05em}
.prose>p:first-child{font-size:1.12em;line-height:1.6;color:var(--ink)}
.prose>p:first-child::first-letter{float:left;font:300 4.3em/.8 var(--serif);color:var(--clay);padding:.07em .09em 0 0;font-variation-settings:"opsz" 72}
.prose h2{font-size:clamp(28px,2.6vw,36px);font-weight:400;letter-spacing:-.02em;line-height:1.12;color:var(--ink);margin:2.3em 0 .7em;scroll-margin-top:24px}
.prose h3{font-size:23px;font-style:italic;font-weight:400;color:var(--ink);margin:1.9em 0 .45em}
.prose>h2+p,.prose>h3+p{margin-top:0}
.prose p a,.prose li a{text-decoration:underline;text-decoration-thickness:1px;text-underline-offset:.2em;text-decoration-color:var(--clay);transition:color .25s}
.prose p a:hover,.prose li a:hover{color:var(--clay-ink)}
.prose strong{font-weight:600;color:var(--ink)}
.prose ul{margin:1.2em 0 1.4em;border-top:1px solid var(--rule)}
.prose li{position:relative;padding:.75em 0 .75em 28px;border-bottom:1px solid var(--rule)}
.prose li::before{content:"";position:absolute;left:0;top:1.45em;width:14px;height:1px;background:var(--clay)}
.pick{display:grid;gap:14px;margin:1.9em 0;padding:22px 22px 18px;background:var(--cream);border-top:1px solid var(--ink);font-family:var(--sans)}
.pick-kicker{color:var(--clay-ink)}
.pick-name{font:400 25px/1.12 var(--serif);letter-spacing:-.02em;color:var(--ink);margin-top:10px}
.pick .model{margin-top:8px}
.pick-why{font-size:15.5px;line-height:1.55;color:var(--stone);margin-top:10px;max-width:50ch}
.pick .cta{justify-self:start;color:var(--ink)}
.pick + p{margin-top:0}
@media (min-width:700px){.pick{grid-template-columns:minmax(0,1fr) auto;column-gap:32px;padding:26px 28px 24px}
  .pick .cta{align-self:end}}
.faq{margin-top:1em}
.faq h2{margin-bottom:.6em}
.faq details{border-top:1px solid var(--rule)}
.faq details:last-of-type{border-bottom:1px solid var(--rule)}
.faq summary{display:flex;justify-content:space-between;align-items:center;gap:24px;padding:20px 0;cursor:pointer;list-style:none;
  font:400 21px/1.3 var(--serif);color:var(--ink);letter-spacing:-.01em}
.faq summary::-webkit-details-marker{display:none}
.faq summary:hover{color:var(--clay-ink)}
.faq summary i{position:relative;flex:0 0 14px;height:14px}
.faq summary i::before,.faq summary i::after{content:"";position:absolute;left:0;top:6.5px;width:14px;height:1px;background:currentColor;transition:transform .35s var(--ease)}
.faq summary i::after{transform:rotate(90deg)}
.faq details[open] summary i::after{transform:rotate(0)}
.faq details p{font:400 16.5px/1.6 var(--sans);color:var(--stone);padding:0 40px 24px 0;max-width:60ch}
.shop-setups-grid{display:grid;gap:28px;margin-top:8px}
.shop-setup{display:grid;gap:12px;font-family:var(--sans)}
.shop-setup img{aspect-ratio:3/2}
.shop-setup .label{color:var(--stone);margin-top:4px}
.shop-setup-title{font:400 25px/1.12 var(--serif);letter-spacing:-.02em;color:var(--ink)}
@media (min-width:700px){.shop-setups-grid{grid-template-columns:1fr 1fr;gap:var(--gut)}}
.prose .back a{text-decoration:none}
.back{margin-top:3.2em}
.prose-plain>p:first-child::first-letter{float:none;font:inherit;color:inherit;padding:0}

/* 404 */
.nf-list{margin-top:clamp(48px,6vw,96px);border-top:1px solid var(--ink)}
.nf-list a{display:flex;gap:18px;align-items:baseline;padding:18px 0;border-bottom:1px solid var(--rule);font:400 clamp(22px,2.4vw,32px)/1.15 var(--serif);letter-spacing:-.02em}
.nf .ph-aside p+p{margin-top:24px}
"""

# ---- Photo credits by image file (used for captions) ---------------------------------
CREDIT_IMG = {"Home page": "hero.jpg", "Trading desk": "trading.jpg", "Minimal desk": "minimal.jpg",
              "Small space": "small.jpg", "Cable management": "cable.jpg"}
PHOTO_BY = {CREDIT_IMG[label]: (name, pid) for label, name, pid in CREDITS if label in CREDIT_IMG}

# ---- Digital products (Payhip) ------------------------------------------------------
SHOP = [
    dict(kind="check", kicker="Free download", name="Desk Cable Checklist", cover="Cable Checklist", url="https://payhip.com/b/XAPfb",
         desc="A printable checklist for getting desk cables under control, one step at a time.", cta="Download free"),
    dict(kind="guide", kicker="Printable guide", name="The Clean Desk Guide", cover="Clean Desk Guide", url="https://payhip.com/b/3MK0F",
         desc="A 15-page printable guide to setting up a clean, calm desk.", cta="View on Payhip"),
    dict(kind="wall", kicker="Digital download", name="Minimalist Wallpaper Pack", cover="Wallpapers", url="https://payhip.com/b/XqrMo",
         desc="A pack of quiet, minimalist 4K wallpapers for your desktop.", cta="View on Payhip"),
]

EDITION = "Autumn 2026 Edition"
esc = html.escape
AMZ_REL = 'rel="sponsored nofollow noopener" target="_blank"'
ARROW = '<span class="arr" aria-hidden="true">&rarr;</span>'


# ---- Images: responsive web versions + dimensions ----------------------------------------
WEB_WIDTHS = (480, 800, 1200)
_DIMS = {}


def jpeg_size(path):
    """Return (width, height) of a JPEG by reading its SOF marker."""
    with open(path, "rb") as f:
        data = f.read()
    i = 2
    while i < len(data):
        if data[i] != 0xFF:
            i += 1
            continue
        marker = data[i + 1]
        if marker in (0xC0, 0xC1, 0xC2, 0xC3, 0xC5, 0xC6, 0xC7, 0xC9, 0xCA, 0xCB, 0xCD, 0xCE, 0xCF):
            h, w = struct.unpack(">HH", data[i + 5:i + 9])
            return w, h
        if marker in (0xD8, 0x01) or 0xD0 <= marker <= 0xD7:
            i += 2
            continue
        i += 2 + struct.unpack(">H", data[i + 2:i + 4])[0]
    raise ValueError(f"no JPEG size in {path}")


def img_dims(name):
    if name not in _DIMS:
        _DIMS[name] = jpeg_size(ROOT / "img" / name)
    return _DIMS[name]


def widths_for(name):
    w = img_dims(name)[0]
    return [x for x in WEB_WIDTHS if x <= w] or [w]


def make_web_images():
    """Create img/web/<name>-<w>.jpg/.webp and favicons with ffmpeg (from imageio_ffmpeg). Skips up-to-date files."""
    webdir = ROOT / "img" / "web"
    webdir.mkdir(exist_ok=True)
    jobs = []
    for src in sorted((ROOT / "img").glob("*.jpg")):
        for w in widths_for(src.name):
            jobs.append((src, webdir / f"{src.stem}-{w}.jpg", ["-vf", f"scale={w}:-2", "-q:v", "3"]))
            jobs.append((src, webdir / f"{src.stem}-{w}.webp", ["-vf", f"scale={w}:-2", "-c:v", "libwebp", "-quality", "78"]))
    icon = ROOT / "img" / "icon.png"
    if icon.exists():  # crop the desk glyph (no small text) onto the brand background
        glyph = "crop=600:340:200:257,pad=600:600:0:130:color=0x1E2A26"
        for size, name in ((32, "icon-32.png"), (180, "icon-180.png"), (512, "icon-512.png")):
            jobs.append((icon, webdir / name, ["-vf", f"{glyph},scale={size}:{size}:flags=lanczos"]))
    todo = [j for j in jobs if not j[1].exists() or j[1].stat().st_mtime < j[0].stat().st_mtime]
    if not todo:
        return
    try:
        import imageio_ffmpeg
        ff = imageio_ffmpeg.get_ffmpeg_exe()
    except Exception:
        raise SystemExit("Web images are missing and ffmpeg isn't available: pip install imageio-ffmpeg")
    for src, out, args in todo:
        subprocess.run([ff, "-y", "-loglevel", "error", "-i", str(src), "-map_metadata", "-1", *args, str(out)], check=True)
    print("made", len(todo), "web images")


def pic(name, root, alt, sizes, cls="", eager=False):
    """<picture> with WebP + JPEG srcsets. CSS sets the displayed aspect ratio."""
    stem = name.rsplit(".", 1)[0]
    ws = widths_for(name)
    w, h = img_dims(name)
    srcset = lambda ext: ", ".join(f"{root}img/web/{stem}-{x}.{ext} {x}w" for x in ws)
    fallback = f"{root}img/web/{stem}-{ws[min(1, len(ws) - 1)]}.jpg"
    load = 'loading="eager" fetchpriority="high"' if eager else 'loading="lazy"'
    c = f' class="{cls}"' if cls else ""
    return (f'<picture><source type="image/webp" srcset="{srcset("webp")}" sizes="{sizes}">'
            f'<img{c} src="{fallback}" srcset="{srcset("jpg")}" sizes="{sizes}" width="{w}" height="{h}" '
            f'alt="{esc(alt)}" {load} decoding="async"></picture>')


def credit(img, root=""):
    if img not in PHOTO_BY:
        return ""
    name, pid = PHOTO_BY[img]
    return f'Photograph: <a class="ulink" href="https://unsplash.com/photos/{pid}" rel="nofollow">{esc(name)}</a> / Unsplash'


# ---- Helpers ---------------------------------------------------------------------------
def slugify(text):
    return re.sub(r"[^a-z0-9]+", "-", re.sub(r"<[^>]+>", "", text).lower()).strip("-")


def short_title(a):
    return a["title"].split(":")[0].split(" (")[0]


def reading_time(a):
    words = len(re.sub(r"<[^>]+>|\[\[[0-9A-Z]{10}\]\]", " ", a["body"]).split())
    words += sum(len(q.split()) + len(x.split()) for q, x in a["faq"])
    return max(1, math.ceil(words / 230))


def nice_date(iso):
    d = datetime.date.fromisoformat(iso)
    return d.strftime("%b ") + str(d.day) + d.strftime(", %Y")


def disclosure_note():
    return f'<p class="disclosure"><span class="label">Disclosure</span> {esc(DISCLOSURE)}</p>'


# ---- Page shell ----------------------------------------------------------------------------
FONTS = ("https://fonts.googleapis.com/css2?family=Newsreader:ital,opsz,wght@0,6..72,300..600;"
         "1,6..72,300..600&family=Inter+Tight:wght@400;500;600&display=swap")

JS = """(function(){var d=document,io='IntersectionObserver' in window,
rm=window.matchMedia&&matchMedia('(prefers-reduced-motion: reduce)').matches,r=d.querySelectorAll('.reveal');
if(!io||rm){for(var i=0;i<r.length;i++)r[i].classList.add('in')}else{var o=new IntersectionObserver(function(es){
es.forEach(function(e){if(e.isIntersecting){e.target.classList.add('in');o.unobserve(e.target)}})},
{rootMargin:'0px 0px -6% 0px',threshold:0.06});r.forEach(function(e){o.observe(e)})}
var l=[].slice.call(d.querySelectorAll('[data-spy] a'));if(!l.length)return;
var t=l.map(function(a){return d.getElementById(a.getAttribute('href').slice(1))}),q=0;
function spy(){q=0;var y=Math.min(innerHeight*.25,180),k=-1;for(var i=0;i<t.length;i++){if(t[i]&&t[i].getBoundingClientRect().top<y)k=i}
if(k>-1&&innerHeight+scrollY>=d.documentElement.scrollHeight-4){var lb=t[t.length-1];if(lb&&lb.getBoundingClientRect().top<innerHeight)k=t.length-1}
l.forEach(function(a,i){if(i===k)a.setAttribute('aria-current','true');else a.removeAttribute('aria-current')})}
addEventListener('scroll',function(){if(!q){q=1;requestAnimationFrame(spy)}},{passive:true});spy();})();"""

CSS_VERSION = ""


def masthead(root, current):
    items = [("setups", "Setups", f"{root}index.html#setups"), ("guides", "Guides", f"{root}index.html#guides"),
             ("shop", "Shop", f"{root}index.html#shop"), ("about", "About", f"{root}disclosure.html")]
    links = "".join(f'<a href="{h}"' + (' aria-current="page"' if k == current else "") + f'>{t}</a>' for k, t, h in items)
    return f"""<a class="skip" href="#main">Skip to content</a>
<header class="mast"><div class="wrap">
<div class="mast-top label"><span>Desk setups, home offices &amp; trading desks</span><span>{EDITION}</span></div>
<div class="mast-main"><a class="wordmark" href="{root}index.html"><i>The</i> Setup Edit</a>
<nav class="primary" aria-label="Primary">{links}</nav></div></div></header>"""


def footer(root):
    col = lambda title, lis: f'<div class="fcol"><p class="label">{title}</p><ul>{lis}</ul></div>'
    setups = "".join(f'<li><a class="ulink" href="{root}setups/{s["slug"]}.html">{esc(s["title"])}</a></li>' for s in SETUPS)
    guides = "".join(f'<li><a class="ulink" href="{root}guides/{a["slug"]}.html">{esc(short_title(a))}</a></li>' for a in ARTICLES)
    shop = "".join(f'<li><a class="ulink" href="{p["url"]}" rel="noopener" target="_blank">{esc(p["name"])}</a></li>' for p in SHOP)
    edit = (f'<li><a class="ulink" href="{root}disclosure.html">About &amp; disclosure</a></li>'
            f'<li><a class="ulink" href="{root}sitemap.xml">Sitemap</a></li>')
    credits = ", ".join(f'<a class="ulink" href="https://unsplash.com/photos/{i}" rel="nofollow">{esc(n)}</a>' for _, n, i in CREDITS)
    return f"""<footer class="foot"><div class="wrap">
<div class="foot-top"><p class="foot-mark"><i>The</i> Setup Edit</p>
<p class="foot-tag">Curated desk setups, home office ideas and trading desks. Chosen for design, reviews and fit.</p></div>
<div class="foot-cols">{col("Setups", setups)}{col("Guides", guides)}{col("Shop", shop)}{col("The Edit", edit)}</div>
<div class="foot-legal"><p>{esc(DISCLOSURE)}</p>
<p>Photos from <a class="ulink" href="https://unsplash.com" rel="nofollow">Unsplash</a> ({credits}). Products shown in photos may differ from the linked items.</p>
<p class="foot-end"><span>&copy; 2026 The Setup Edit</span><a class="ulink" href="#top">Back to top &uarr;</a></p></div>
</div></footer>"""


def page(title, desc, body, root="", og="img/hero.jpg", path="", current="", extra_head=""):
    url = BASE_URL + path
    og_abs = og if og.startswith("http") else BASE_URL + og
    return f"""<!doctype html><html lang="en" id="top"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{esc(title)}</title><meta name="description" content="{esc(desc)}">
<link rel="canonical" href="{url}">
<meta property="og:title" content="{esc(title)}"><meta property="og:description" content="{esc(desc)}">
<meta property="og:image" content="{og_abs}"><meta property="og:url" content="{url}">
<meta property="og:type" content="{'article' if path.startswith('guides/') else 'website'}"><meta property="og:site_name" content="{SITE_NAME}">
<meta name="twitter:card" content="summary_large_image">
<meta name="p:domain_verify" content="77efeace518f495ac7564d61a39f2015"/>
<meta name="theme-color" content="#F6F1E7">
<link rel="icon" href="{root}favicon.svg" type="image/svg+xml">
<link rel="icon" href="{root}img/web/icon-32.png" sizes="32x32" type="image/png">
<link rel="apple-touch-icon" href="{root}img/web/icon-180.png">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="{FONTS}" rel="stylesheet">
<link rel="stylesheet" href="{root}style.css?v={CSS_VERSION}">
<script>document.documentElement.className+=' js'</script>{extra_head}</head>
<body>{masthead(root, current)}
<main id="main">{body}</main>
{footer(root)}
<script>{JS}</script></body></html>"""


# ---- Product blocks ------------------------------------------------------------------------
PRODUCTS = {a: (n, m, w) for s in SETUPS for n, m, a, w in s["items"]}


def amazon_cta(asin):
    return f'<a class="cta" href="{amz(asin)}" {AMZ_REL}>View on Amazon{ARROW}</a>'


def product_card(match):
    asin = match.group(1)
    n, m, w = PRODUCTS[asin]  # KeyError here means the ASIN isn't in SETUPS
    return (f'<aside class="pick" aria-label="{esc(n)}"><div class="pick-body"><p class="label pick-kicker">The pick</p>'
            f'<p class="pick-name">{esc(n)}</p><p class="model">{esc(m)}</p><p class="pick-why">{esc(w)}</p></div>'
            f'{amazon_cta(asin)}</aside>')


# ---- Home ------------------------------------------------------------------------------------
FEATURE_SIZES = ["(min-width: 1000px) 58vw, 100vw", "(min-width: 1000px) 40vw, 100vw",
                 "(min-width: 1000px) 58vw, 100vw", "(min-width: 1000px) 50vw, 100vw"]


def shop_tile(p):
    art = {
        "check": '<span class="tile-lines" aria-hidden="true"><i></i><i></i><i></i><i></i></span>',
        "guide": '<span class="tile-pp" aria-hidden="true">15&thinsp;pp.</span>',
        "wall": '<span class="tile-horizon" aria-hidden="true"><i></i></span>',
    }[p["kind"]]
    return (f'<a class="tile tile-{p["kind"]}" href="{p["url"]}" rel="noopener" target="_blank" tabindex="-1" aria-hidden="true">'
            f'<span class="tile-brand">The Setup Edit</span>{art}<span class="tile-name">{esc(p.get("cover", p["name"]))}</span></a>')


def build_home():
    total = sum(len(s["items"]) for s in SETUPS)
    feats = []
    for i, s in enumerate(SETUPS):
        href = f"setups/{s['slug']}.html"
        feats.append(f"""<article class="feature f{i % 4 + 1} reveal">
<a class="feature-media media" href="{href}" tabindex="-1" aria-hidden="true">{pic(s['img'], '', s['title'], FEATURE_SIZES[i % 4])}</a>
<div class="feature-text"><p class="no"><span class="label">No.</span><span class="no-n">{i + 1:02d}</span></p>
<h3 class="feature-title"><a href="{href}">{esc(s['title'])}</a></h3>
<p class="feature-dek">{esc(s['blurb'])}</p>
<p class="feature-meta"><span class="label">{len(s['items']):02d} pieces</span><a class="cta" href="{href}">Shop the list{ARROW}</a></p></div>
</article>""")
    rows = "".join(f"""<li class="guide-row reveal"><a href="guides/{a['slug']}.html">
<p class="gr-meta label"><time datetime="{a['date']}">{nice_date(a['date'])}</time><span>{reading_time(a)} min read</span></p>
<div class="gr-text"><p class="label kicker">{esc(a['eyebrow'])}</p><h3 class="gr-title"><span class="uline">{esc(a['title'])}</span></h3>
<p class="gr-dek">{esc(a['desc'])}</p></div>
<div class="gr-thumb media">{pic(a['img'], '', '', '(min-width: 1000px) 22vw, 96px')}</div></a></li>""" for a in ARTICLES)
    products = "".join(f"""<div class="product">{shop_tile(p)}<div class="product-text">
<p class="label kicker">{p['kicker']}</p><h3 class="product-name">{esc(p['name'])}</h3><p class="product-desc">{esc(p['desc'])}</p>
<a class="cta" href="{p['url']}" rel="noopener" target="_blank">{p['cta']}{ARROW}</a></div></div>""" for p in SHOP)

    cover_lines = "".join(f'<li><a href="setups/{s["slug"]}.html"><span class="ix-n">{k:02d}</span><span class="uline">{esc(s["title"])}</span></a></li>'
                          for k, s in enumerate(SETUPS, 1))
    body = f"""<section class="cover wrap" aria-labelledby="cover-title">
<div class="cover-top"><h1 id="cover-title" class="cover-title">A desk you actually <em>want</em> to sit&nbsp;at.</h1>
<ol class="cover-lines" aria-label="Setups in this edition">{cover_lines}</ol></div>
<div class="cover-row"><p class="label">In this edition</p>
<p class="cover-dek">{len(SETUPS)} curated desk setups, {len(ARTICLES)} step-by-step guides and a small shop of printables, for traders, remote workers and anyone who spends the day at a desk.</p>
<a class="cta" href="#setups">Read the index<span class="arr" aria-hidden="true">&darr;</span></a></div>
</section>
<figure class="bleed cover-fig">{pic('hero.jpg', '', 'A dual-monitor desk with plants, warm lamps and a wooden desktop', '100vw', eager=True)}
<figcaption class="wrap caption"><span><span class="label">On the cover</span> Two screens, soft lamps and plenty of green.</span><span>{credit('hero.jpg')}</span></figcaption></figure>

<section id="setups" class="wrap section" aria-labelledby="setups-title">
<header class="sec-head reveal"><p class="label">The Setups</p><h2 id="setups-title" class="sec-title">Four desks, <em>edited</em> down to what matters.</h2>
<p class="label sec-count">{len(SETUPS):02d} edits &middot; {total} pieces</p></header>
{''.join(feats)}
</section>

<section id="guides" class="band band-cream" aria-labelledby="guides-title"><div class="wrap">
<header class="sec-head reveal"><p class="label">Guides</p><h2 id="guides-title" class="sec-title">Long reads for a <em>better</em> desk.</h2>
<p class="label sec-count">{len(ARTICLES):02d} guides</p></header>
<ol class="guide-list">{rows}</ol></div></section>

<section id="shop" class="band band-dark" aria-labelledby="shop-title"><div class="wrap shop-grid">
<header class="shop-head reveal"><p class="label kicker">The Shop</p><h2 id="shop-title" class="sec-title">Printables &amp; <em>downloads</em></h2>
<p>Three small things made by The Setup Edit. Instant downloads, delivered through Payhip.</p></header>
<div class="products reveal">{products}</div></div></section>

<section id="about" class="wrap section about" aria-labelledby="about-title">
<p class="label" id="about-title">About the edit</p>
<div class="about-text reveal"><p class="about-lede">The Setup Edit is a small, independent guide to desks and home offices. Every pick is chosen for its design, its reviews and how well it fits the setup around it.</p>
<p>Picks come from research, not hands-on testing: I compare the options, read the specs and the reviews, and include the ones that suit each desk. Amazon links are affiliate links, which is how the site pays for itself.</p>
<a class="cta" href="disclosure.html">About &amp; disclosure{ARROW}</a></div>
</section>"""
    (OUT / "index.html").write_text(page("The Setup Edit | Desk Setups & Home Office Ideas",
        "Curated desk setups, home office ideas and trading desk gear, with links to shop every item.", body), encoding="utf-8")


# ---- Setup pages -------------------------------------------------------------------------
def build_setups():
    for i, s in enumerate(SETUPS):
        n = len(s["items"])
        index = "".join(f'<li><a href="#item-{k:02d}"><span class="ix-n">{k:02d}</span>{esc(name)}</a></li>'
                        for k, (name, _, _, _) in enumerate(s["items"], 1))
        items = "".join(f"""<li class="item" id="item-{k:02d}"><span class="item-no" aria-hidden="true">{k:02d}</span>
<div class="item-body"><h2 class="item-name">{esc(name)}</h2><p class="model">{esc(model)}</p><p class="item-why">{esc(why)}</p></div>
{amazon_cta(asin)}</li>""" for k, (name, model, asin, why) in enumerate(s["items"], 1))
        rel = [a for a in ARTICLES if s["slug"] in a["setups"]]
        related = ""
        if rel:
            related = "".join(f"""<li><a href="../guides/{a['slug']}.html"><span class="label">{reading_time(a)} min read</span>
<span class="rel-title"><span class="uline">{esc(a['title'])}</span></span>{ARROW}</a></li>""" for a in rel)
            related = f"""<section class="wrap section related reveal" aria-labelledby="rel-title">
<p class="label" id="rel-title">Read the guide{'s' if len(rel) > 1 else ''}</p><ul class="rel-list">{related}</ul></section>"""
        nxt = SETUPS[(i + 1) % len(SETUPS)]
        nk = (i + 1) % len(SETUPS) + 1
        body = f"""<section class="wrap page-head" aria-labelledby="page-title">
<p class="crumbs label"><a class="ulink" href="../index.html#setups">The Setups</a><span aria-hidden="true">/</span>No. {i + 1:02d}</p>
<div class="ph-grid"><h1 id="page-title" class="ph-title">{esc(s['title'])}</h1>
<div class="ph-aside"><p class="ph-dek">{esc(s['blurb'])}</p><p class="label ph-meta">{n:02d} pieces</p>{disclosure_note()}</div></div>
</section>
<figure class="bleed setup-fig">{pic(s['img'], '../', s['title'], '100vw', eager=True)}
<figcaption class="wrap caption"><span>Products shown in photos may differ from the linked items.</span><span>{credit(s['img'])}</span></figcaption></figure>
<section class="wrap list-grid" aria-label="The shopping list">
<nav class="list-index" aria-label="Items in this setup"><p class="label">The list &middot; {n:02d}</p><ol data-spy>{index}</ol></nav>
<ol class="shop-list">{items}</ol>
</section>
{related}
<nav class="next band band-cream" aria-label="Next setup"><div class="wrap"><a class="next-link" href="{nxt['slug']}.html">
<span class="next-text"><span class="label">Next in the edit &middot; No. {nk:02d}</span><span class="next-title"><span class="uline">{esc(nxt['title'])}</span></span>
<span class="next-dek">{esc(nxt['blurb'])}</span></span>
<span class="next-media media">{pic(nxt['img'], '../', '', '(min-width: 1000px) 30vw, 100vw')}</span></a></div></nav>"""
        (OUT / "setups" / f"{s['slug']}.html").write_text(
            page(f"{s['title']} | {SITE_NAME}", s["blurb"], body, root="../", og=f"img/{s['img']}",
                 path=f"setups/{s['slug']}.html", current="setups"), encoding="utf-8")


# ---- Guides --------------------------------------------------------------------------------
def build_guides():
    (OUT / "guides").mkdir(exist_ok=True)
    titles = {s["slug"]: s["title"] for s in SETUPS}
    for a in ARTICLES:
        toc = []

        def h2_id(m):
            text = m.group(1)
            hid = slugify(text)
            toc.append((hid, re.sub(r"<[^>]+>", "", text)))
            return f'<h2 id="{hid}">{text}</h2>'
        body_html = re.sub(r"<h2>(.*?)</h2>", h2_id, a["body"])
        body_html = re.sub(r"\[\[([0-9A-Z]{10})\]\]", product_card, body_html)
        toc.append(("faq", "Questions, answered"))
        toc_html = "".join(f'<li><a href="#{hid}">{esc(t)}</a></li>' for hid, t in toc)
        faq = "".join(f'<details><summary><span>{esc(q)}</span><i aria-hidden="true"></i></summary><p>{esc(ans)}</p></details>'
                      for q, ans in a["faq"])
        ld = {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
            {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": ans}} for q, ans in a["faq"]]}
        art_ld = {"@context": "https://schema.org", "@type": "Article", "headline": a["title"], "description": a["desc"],
                  "image": BASE_URL + "img/" + a["img"], "datePublished": a["date"],
                  "author": {"@type": "Organization", "name": SITE_NAME}, "publisher": {"@type": "Organization", "name": SITE_NAME},
                  "mainEntityOfPage": BASE_URL + f"guides/{a['slug']}.html"}
        setup_links = "".join(f"""<a class="shop-setup" href="../setups/{sl}.html"><span class="media">{pic(next(s['img'] for s in SETUPS if s['slug'] == sl), '../', '', '(min-width: 700px) 30vw, 100vw')}</span>
<span class="label">No. {[s['slug'] for s in SETUPS].index(sl) + 1:02d} &middot; {len(next(s['items'] for s in SETUPS if s['slug'] == sl)):02d} pieces</span>
<span class="shop-setup-title"><span class="uline">{esc(titles[sl])}</span></span></a>""" for sl in a["setups"])
        body = f"""<article>
<header class="wrap page-head guide-head">
<p class="crumbs label"><a class="ulink" href="../index.html#guides">Guides</a><span aria-hidden="true">/</span>{esc(a['eyebrow'])}</p>
<h1 id="page-title" class="ph-title guide-title">{esc(a['title'])}</h1>
<div class="gh-row"><p class="gh-dek">{esc(a['desc'])}</p>
<div class="gh-meta"><p class="label"><time datetime="{a['date']}">{nice_date(a['date'])}</time> &middot; {reading_time(a)} min read</p>{disclosure_note()}</div></div>
</header>
<figure class="wrap guide-fig">{pic(a['img'], '../', a['title'], '(min-width: 1000px) 80vw, 100vw', eager=True)}
<figcaption class="caption"><span>{credit(a['img'])}</span><span>Products shown in photos may differ from the linked items.</span></figcaption></figure>
<div class="wrap article-grid">
<nav class="toc" aria-label="In this guide"><p class="label">In this guide</p><ol data-spy>{toc_html}</ol></nav>
<div class="prose">{body_html}
<section class="faq" id="faq" aria-labelledby="faq-title"><h2 id="faq-title">Questions, answered</h2>{faq}</section>
<section class="shop-setups" aria-labelledby="shop-setups-title"><h2 id="shop-setups-title">Shop the setups</h2><div class="shop-setups-grid">{setup_links}</div></section>
<p class="back"><a class="cta cta-back" href="../index.html#guides"><span class="arr" aria-hidden="true">&larr;</span>All guides</a></p>
</div></div></article>
<script type="application/ld+json">{json.dumps(ld)}</script>
<script type="application/ld+json">{json.dumps(art_ld)}</script>"""
        (OUT / "guides" / f"{a['slug']}.html").write_text(
            page(f"{a['title']} | {SITE_NAME}", a["desc"], body, root="../", og=f"img/{a['img']}",
                 path=f"guides/{a['slug']}.html", current="guides"), encoding="utf-8")


# ---- About / disclosure and 404 -------------------------------------------------------------------
def build_disclosure():
    body = f"""<section class="wrap page-head" aria-labelledby="page-title">
<p class="crumbs label">The Edit<span aria-hidden="true">/</span>About &amp; disclosure</p>
<div class="ph-grid"><h1 id="page-title" class="ph-title">About the edit &amp; <em>disclosure</em></h1></div></section>
<div class="wrap article-grid"><div class="prose prose-plain">
<p>The Setup Edit is a small, independent guide to desk setups, home offices and trading desks. Picks are chosen for their design, their reviews and how well they fit each setup. Picks come from research rather than hands-on testing: I compare the options and include the ones that suit each desk.</p>
<h2 id="affiliate-disclosure">Affiliate disclosure</h2>
<p>{esc(DISCLOSURE)}</p><p>Product picks are chosen for quality, reviews and how well they fit each setup. Prices and availability change, so always check the current details on Amazon before buying.</p>
<h2 id="privacy">Privacy</h2><p>This site doesn't use its own cookies or collect personal information. Amazon may set cookies when you click an affiliate link, as described in Amazon's own privacy notice.</p>
<p class="back"><a class="cta cta-back" href="index.html"><span class="arr" aria-hidden="true">&larr;</span>Back to the edit</a></p>
</div></div>"""
    (OUT / "disclosure.html").write_text(page(f"About & Disclosure | {SITE_NAME}", "About The Setup Edit, affiliate disclosure and privacy.",
                                              body, path="disclosure.html", current="about"), encoding="utf-8")


def build_404():
    root = "/thesetupedit/"  # 404 can be served at any path, so links are root-relative
    links = "".join(f'<li><a href="{root}setups/{s["slug"]}.html"><span class="ix-n">{k:02d}</span><span class="uline">{esc(s["title"])}</span></a></li>'
                    for k, s in enumerate(SETUPS, 1))
    body = f"""<section class="wrap page-head nf" aria-labelledby="page-title">
<p class="crumbs label">Error<span aria-hidden="true">/</span>No. 404</p>
<div class="ph-grid"><h1 id="page-title" class="ph-title">This page was <em>edited out.</em></h1>
<div class="ph-aside"><p class="ph-dek">The link may be old, or the page has moved. Try one of the setups, or start again from the front page.</p>
<p><a class="cta" href="{root}index.html">Go to the front page{ARROW}</a></p></div></div>
<ol class="nf-list">{links}</ol></section>"""
    (OUT / "404.html").write_text(page(f"Page not found | {SITE_NAME}", "This page could not be found.", body, root=root),
                                  encoding="utf-8")


def build_sitemap():
    today = datetime.date.today().isoformat()
    paths = [""] + [f"setups/{s['slug']}.html" for s in SETUPS] + [f"guides/{a['slug']}.html" for a in ARTICLES] + ["disclosure.html"]
    urls = "".join(f"<url><loc>{BASE_URL}{p}</loc><lastmod>{today}</lastmod></url>\n" for p in paths)
    (OUT / "sitemap.xml").write_text('<?xml version="1.0" encoding="UTF-8"?>\n'
        f'<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{urls}</urlset>\n', encoding="utf-8")
    (OUT / "robots.txt").write_text(f"User-agent: *\nAllow: /\n\nSitemap: {BASE_URL}sitemap.xml\n", encoding="utf-8")


FAVICON_SVG = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64"><rect width="64" height="64" rx="14" fill="#1E2A26"/>
<g fill="none" stroke="#F2EADB" stroke-width="3.4" stroke-linecap="round" stroke-linejoin="round">
<rect x="10" y="15" width="19" height="14" rx="2.5"/><rect x="35" y="15" width="19" height="14" rx="2.5"/>
<path d="M19.5 29v8M44.5 29v8M7 38h50M11 38v9M53 38v9"/></g>
<path d="M14 25l4-3 3 1.5 4-4" fill="none" stroke="#E0875F" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"/></svg>"""


def build():
    global CSS_VERSION
    make_web_images()
    CSS_VERSION = hashlib.sha1(CSS.encode()).hexdigest()[:8]
    if OUT.exists():
        shutil.rmtree(OUT)
    (OUT / "setups").mkdir(parents=True)
    shutil.copytree(ROOT / "img", OUT / "img")
    (OUT / "style.css").write_text(CSS, encoding="utf-8")
    (OUT / "favicon.svg").write_text(FAVICON_SVG, encoding="utf-8")
    (OUT / ".nojekyll").write_text("")
    if (ROOT / "media").exists(): shutil.copytree(ROOT / "media", OUT / "media")
    build_home()
    build_setups()
    build_disclosure()
    build_guides()
    build_404()
    build_sitemap()
    print("built", sum(1 for _ in OUT.rglob("*.html")), "pages")


if __name__ == "__main__":
    build()
