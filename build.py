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

# Each setup: items are (name, model, ASIN, why). The first item is the "Start here" pick (see `start`).
SETUPS = [
    dict(slug="trading-desk-setup", title="The Trading Desk Setup", img="trading.jpg",
         blurb="A multi-monitor desk built for long sessions: floating screens, good light, and room to think.",
         meta="A trading desk setup, item by item: monitor arms, a screen light bar, a standing desk, an ergonomic chair and mouse, and two trading books.",
         good_for="Traders, and anyone who works across two screens for hours.",
         start="Everything else on this desk is placed around the screens, so mount them first.",
         intro="""<p>This desk is built around two screens at the same height, straight in front of you, with the space under them left clear. Arms carry the monitors, a light bar lights the desk without glare, and bias lighting softens the contrast during evening sessions.</p>
<p>The standing frame, the chair and the mouse are there for long days. The two books are the one part of the setup that has nothing to do with hardware.</p>""",
         items=[
             ("Dual Monitor Arm", "VIVO dual monitor desk mount", "B009S750LA", "Floats two screens off the desk so you get your whole surface back."),
             ("Single Monitor Arm", "VIVO single monitor arm", "B00B21TLQU", "One screen, fully adjustable height, tilt and swivel."),
             ("Monitor Light Bar", "BenQ ScreenBar", "B076VNFZJG", "Lights your desk, not your screen. No glare on late-night charts."),
             ("Electric Standing Desk", "FLEXISPOT EN1", "B08BHPMYGK", "Sit or stand at the push of a button, with 4 memory presets."),
             ("LED Monitor Backlight", "Luminoodle bias lighting", "B01LG99NW4", "USB-powered glow behind your screen, softer on your eyes at night."),
             ("Ergonomic Mouse", "Logitech MX Master 3S", "B0B11LJ69K", "Shaped for long days, with an ultra-fast scroll wheel."),
             ("Ergonomic Mesh Chair", "Ergonomic mesh office chair", "B07Y8BXBX8", "A breathable mesh back that stays cooler than foam through a long session."),
             ("Trading in the Zone", "Book by Mark Douglas", "0735201447", "The classic on trading psychology and discipline."),
             ("How to Day Trade for a Living", "Book by Andrew Aziz", "1535585951", "A beginner's guide to day trading tools and risk management."),
         ]),
    dict(slug="minimal-desk-setup", title="The Clean Minimal Desk", img="minimal.jpg",
         blurb="Fewer things, better things. Warm materials and a desk that looks calm every time you sit down.",
         meta="A clean, minimal desk setup: leather desk pad, compact wireless keyboard, walnut wrist rest, headphone stand, bamboo tray, faux plants and a clamp lamp.",
         good_for="Anyone who wants a desk that looks calm every time they sit down.",
         start="It defines the working area, and the rest of the desk is arranged on top of it.",
         intro="""<p>A calm desk is mostly about what you leave off. This one sticks to a few warm materials (leather, walnut and bamboo) and gives every loose item a place to live: a tray for the small things, a stand for the headphones.</p>
<p>The compact wireless keyboard and the clamp lamp keep the surface open, so the desk still looks tidy in the middle of a working day.</p>""",
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
         meta="A small space home office setup: monitor riser, laptop stand, monitor light bar, floating shelves, footrest and faux plants, chosen to free up desk space.",
         good_for="Bedrooms, corners and apartments where the desk has to stay small.",
         start="It lifts the screen and adds a shelf underneath, which frees more surface than anything else here.",
         intro="""<p>Every item here either lifts something off the desk or hides it underneath. The riser and the laptop stand raise screens to a better height and free the surface below them. The light bar and the floating shelves use space that was going to waste.</p>
<p>The footrest solves the usual small-space compromise: a chair or a desk that is not quite the right height.</p>""",
         items=[
             ("Monitor Riser", "WALI adjustable monitor stand", "B094QTGHNZ", "Raises your screen and adds storage underneath."),
             ("Laptop Stand", "BESIGN LS03 aluminum stand", "B08BRCT4JH", "Turns a laptop into a proper workstation."),
             ("Monitor Light Bar", "Quntis monitor lamp", "B08DKQ3JG1", "Desk light with zero footprint."),
             ("Floating Shelves", "Wall-mounted floating shelves", "B0DZWXJ9VZ", "Storage above the desk, so the desktop itself stays clear."),
             ("Under-Desk Footrest", "Everlasting Comfort memory foam", "B07PGLBCFG", "The comfort upgrade nobody sees."),
             ("Mini Desk Plants", "Der Rose artificial plants (3-pack)", "B07VKJKFN2", "Fits on shelves and small desks."),
         ]),
    dict(slug="cable-management", title="The Cable Management Kit", img="cable.jpg",
         blurb="Hide the mess in an afternoon. The cheapest upgrade with the biggest before-and-after.",
         meta="A cable management kit for any desk: an under-desk cable tray and adhesive cable clips, plus a simple method to hide desk cables in an afternoon.",
         good_for="Any desk with a power strip on the floor.",
         start="Getting the power strip off the floor is the single biggest step, and everything else routes to it.",
         intro="""<p>Two parts do most of the work. A tray under the desk holds the power strip and the chargers, so only one cable runs down to the wall. Clips along the desk edge keep the cables you touch every day from sliding off the back.</p>
<p>The rest is method: route every cable along one path, bundle them with reusable ties and label the ends. The <a href="../guides/cable-management-101-hide-desk-cables.html">cable management guide</a> walks through it, and the free checklist below puts it on paper.</p>""",
         items=[
             ("Under-Desk Cable Tray", "Scanfield no-screw tray (2-pack)", "B09J5HH2LR", "Power strips and chargers go under the desk, off the floor."),
             ("Adhesive Cable Clips", "OHill cable clips (16-pack)", "B071FXZBMV", "Chargers stop falling behind the desk."),
         ]),
]

# Products recommended in guides that are not part of a setup list: ASIN -> (name, model, why).
EXTRA_PRODUCTS = {
    "B099596F3B": ("Mini Faux Plants", "Small artificial potted plants", "Green on the desk or a shelf, with nothing to water."),
    "B07T5SY43L": ("Dual Monitor Arm", "Dual monitor desk mount", "Holds two screens at matching heights, and moves with a standing desk because it clamps to the top."),
    "B096S2Z9Q7": ("Felt Desk Mat", "Felt desk pad, 40 x 16 in", "A soft, quiet surface under the keyboard and mouse."),
    "B08HVH8FPF": ("Desk Ring Light", "Desk-mounted ring light", "An even, front-facing light for your face on calls."),
    "B01L3LL95O": ("Mic Boom Arm", "Clamp-on microphone boom arm", "Brings the microphone close to your mouth, then swings out of the way."),
    "B088NHGC48": ("Monitor Stand with Drawer", "2-tier monitor stand with drawer", "Raises the screen and hides small things in a drawer underneath."),
    "B01559O0WY": ("Clip-On Fan", "Small clip-on desk fan", "Clamps to a shelf or the desk edge to move air without using floor space."),
    "B09GTRVJQM": ("Compact Air Purifier", "Small-room air purifier", "A small footprint for a closed room you work and sleep in."),
    "B07HFDJCSL": ("Clamp-On Keyboard Tray", "Under-desk clamp keyboard tray", "Adds a lower surface for the keyboard, and clamps on without drilling."),
    "B0C3HCD34R": ("Noise-Cancelling Headphones", "Wireless ANC headphones", "Turns down a shared room so you can focus or take a call."),
    "B0B6P9J3J5": ("Monitor Light Bar", "LED monitor light bar", "Lights the desk from above the screen, without glare on the display."),
}

# Short role tag shown on each product card.
ROLE = {
    "B009S750LA": "Screens", "B00B21TLQU": "Screens", "B094QTGHNZ": "Screens", "B08BRCT4JH": "Screens",
    "B07T5SY43L": "Screens", "B088NHGC48": "Screens",
    "B076VNFZJG": "Light", "B01LG99NW4": "Light", "B08DKQ3JG1": "Light", "B07R56PTMS": "Light",
    "B08HVH8FPF": "Light", "B0B6P9J3J5": "Light",
    "B08BHPMYGK": "Desk", "B07Y8BXBX8": "Seating", "B07PGLBCFG": "Comfort", "B09DPGVPG1": "Comfort",
    "B0B11LJ69K": "Input", "B0CNT61VMZ": "Input", "B07HFDJCSL": "Input",
    "B082F5ZLS5": "Surface", "B096S2Z9Q7": "Surface",
    "B01GJQ7N94": "Storage", "B00KAZ12OS": "Storage", "B0DZWXJ9VZ": "Storage",
    "B07VKJKFN2": "Greenery", "B099596F3B": "Greenery",
    "B09J5HH2LR": "Cables", "B071FXZBMV": "Cables",
    "B01L3LL95O": "Audio", "B0C3HCD34R": "Audio", "B01559O0WY": "Air", "B09GTRVJQM": "Air",
    "0735201447": "Reading", "1535585951": "Reading",
}

# Photo credits: (used for, photographer, Unsplash photo id, image file in img/)
CREDITS = [
    ("Home page", "Roberto Nickson", "Gvm2wM3V5PA", "hero.jpg"), ("Trading desk", "João Inácio", "Wk_6p1TuhRE", "trading.jpg"),
    ("Minimal desk", "Muhammet Sain", "_g0SLFllfBY", "minimal.jpg"), ("Small space", "Behnam Norouzi", "j3b15qP-ckc", "small.jpg"),
    ("Cable management", "Bedirhan Gül", "I_3D0pVrMhY", "cable.jpg"),
    ("Bedroom guide", "Aleksandra Dementeva", "GzR2KS4ABYA", "bedroom.jpg"),
    ("Video call guide", "Adeniji Abdullahi A", "F5FrFqwIKAI", "video-call.jpg"),
    ("Standing desk guide", "EFFYDESK", "aDZ-UZSvhE4", "standing.jpg"),
    ("Cable checklist", "Jakub Żerdzicki", "weJ7qyjHYwk", "checklist.jpg"),
    ("Clean Desk Guide", "Max Andrey", "-8-2YWKt8Ag", "clean-desk.jpg"),
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
<p>Memory presets matter more than they sound. If switching heights takes one button press, you are far more likely to actually do it during a long session. The <a href="standing-desk-setup-guide.html">standing desk setup guide</a> covers how to find both heights.</p>

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
<p>Position the tray toward the back of the desk, where it is out of sight and away from your knees. If your desk is a standing model, place it so the one cable down to the wall has enough slack for the full height range. The <a href="standing-desk-setup-guide.html">standing desk setup guide</a> has more on that.</p>

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
<p>A clamp-on swing arm lamp attaches to the desk edge and can be pushed out of the way when not needed, which is handy if the desk doubles as a dining or hobby table. If you take video calls from the same desk, see <a href="how-to-light-a-desk-for-video-calls.html">how to light a desk for video calls</a>.</p>
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
<p>If your office shares a room with your bed, a clear visual boundary helps separate work from rest. Face the desk away from the bed if you can, keep work items in one tray or drawer, and clear the desk at the end of the day so the room returns to being a bedroom. A few minutes of reset each evening goes a long way. The <a href="best-desk-setup-for-small-bedrooms.html">bedroom desk setup guide</a> goes further, from desk placement to light and air.</p>
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

    dict(slug="standing-desk-setup-guide", img="standing.jpg", eyebrow="Standing desk guide", date="2026-09-24",
         title="Standing Desk Setup Guide: Heights, Screens and Cables",
         desc="How to set up a standing desk properly: find your sitting and standing heights, mount screens that move with the desk, give cables enough slack, and make switching easy.",
         setups=["trading-desk-setup", "cable-management"],
         body="""
<p>Buying a standing desk is the easy part. The benefit comes from setting two heights correctly, making sure everything on the desk can travel with it, and making the switch so effortless that you actually do it. This guide covers the setup in that order, from the frame to the habit.</p>

<h2>Choose a frame that suits what sits on it</h2>
<p>Add up what the desk will carry: monitors, arms, a laptop, speakers, a lamp. Check that the frame's weight rating covers it with room to spare, and look at how stable it is at your standing height, because that is where wobble shows up first. A dual-motor electric frame with memory presets is the most common choice for a full desk setup.</p>
[[B08BHPMYGK]]
<p>Presets matter more than they sound. If changing position takes one button press, you will do it several times a day. If it takes thirty seconds of holding a switch, you will stop.</p>

<h2>Find your two heights</h2>
<p>Set the standing height first. Stand relaxed with your shoulders down and your elbows bent at roughly a right angle. The desktop, or more precisely the keyboard, should sit at about the height of your forearms, so your wrists stay straight and you are not reaching up or hunching down. Save that as a preset.</p>
<p>Then sit down and repeat. With your feet flat on the floor and your thighs roughly level, bring the desk to the same elbow height and save it as the second preset. If the chair has to go high enough that your feet no longer rest flat, a footrest closes the gap.</p>
[[B07PGLBCFG]]

<h2>Mount the screens so they move with the desk</h2>
<p>Monitor stands work, but monitor arms are better on a standing desk. An arm clamped to the desktop rises and falls with it, and you can fine-tune the height separately for each position. A common guideline is to keep the top of the screen at or slightly below eye level, at about arm's length.</p>
[[B07T5SY43L]]
<p>After you set both presets, check the screen height in each one. Small differences in posture between sitting and standing often mean a slight adjustment is worth it.</p>

<h2>Keep the keyboard at elbow height</h2>
<p>If the desktop is at the right height, the keyboard can sit directly on it. Some desks, though, will not go low enough for shorter people when seated, or the desk is shared with someone taller. A clamp-on keyboard tray adds a second, lower surface without drilling into the desktop.</p>
[[B07HFDJCSL]]

<h2>Give the cables slack, not just tidiness</h2>
<p>This is where most standing desk setups go wrong. A cable that is neat at sitting height can pull tight at standing height, and a power strip on the floor means every cable has to stretch the full distance. Mount the power strip in a tray on the underside of the desk so it travels with everything plugged into it.</p>
[[B09J5HH2LR]]
<p>That leaves just one cable running from the desk to the wall. Give it enough slack for the full height range, then run the desk from its lowest to its highest position with nothing on the floor to snag. Adhesive clips keep the cables you use daily in place along the edge.</p>
[[B071FXZBMV]]
<p>The <a href="cable-management-101-hide-desk-cables.html">cable management guide</a> covers the full routing method, and the <a href="../setups/cable-management.html">Cable Management Kit</a> lists the parts.</p>

<h2>Do not skip the chair</h2>
<p>Most people with a standing desk still sit for much of the day, so the chair deserves as much thought as the frame. Look for adjustable seat height and a supportive back. A mesh back is a popular choice for long sessions because it breathes better than foam.</p>
[[B07Y8BXBX8]]

<h2>Build a switching habit</h2>
<p>The goal is not to stand all day. It is to change position regularly. Tie the switch to something you already do: stand for calls, sit for focused writing, stand after lunch. If you are new to standing, start with short stretches and build up. On a hard floor, comfortable shoes or a cushioned mat make standing periods easier.</p>

<h2>Common mistakes to avoid</h2>
<ul>
<li><strong>Standing with the desk too high.</strong> If your shoulders rise or your wrists bend upward, lower it.</li>
<li><strong>Forgetting the second preset.</strong> Save both heights on day one, so switching never means guessing.</li>
<li><strong>Tight cables.</strong> Test the full height range before you call the setup finished.</li>
<li><strong>Heavy screens on a light frame.</strong> Check the weight rating against everything on the desk, arms included.</li>
</ul>
<p>For a full multi-screen build around a standing frame, see <a href="how-to-build-a-trading-desk-setup.html">how to build a trading desk setup</a>, or shop every piece in <a href="../setups/trading-desk-setup.html">The Trading Desk Setup</a>.</p>
""",
         faq=[
             ("How high should a standing desk be?", "At standing height, the keyboard should sit at about elbow height with your arms relaxed and your elbows bent at roughly a right angle, so your wrists stay straight."),
             ("Should monitors move with a standing desk?", "Yes. Mount them on arms or stands attached to the desktop, so the screens keep the same relationship to you in both positions."),
             ("How do I manage cables on a standing desk?", "Put the power strip in a tray under the desktop so it moves with the desk, and leave enough slack on the single cable to the wall for the full height range."),
             ("How long should I stand at a standing desk?", "There is no single right number. The common advice is to change position regularly rather than stand all day, and to build up standing time gradually."),
         ]),

    dict(slug="how-to-light-a-desk-for-video-calls", img="video-call.jpg", eyebrow="Lighting guide", date="2026-09-24",
         title="How to Light a Desk for Video Calls",
         desc="Look clear and natural on video calls: use the window you have, place a main light in front of you, raise the camera to eye level and add soft light behind you.",
         setups=["small-space-office", "trading-desk-setup"],
         body="""
<p>Most video call problems are lighting problems. A webcam in a dim room produces a grainy, flat picture, and a bright window behind you turns you into a silhouette. The fix is rarely a new camera. It is putting the right light in the right place, which takes a few minutes and a lamp or two.</p>

<h2>Start with the window you already have</h2>
<p>Daylight is the best light you have, as long as it is in front of you. Face the window, or sit at an angle to it, so the light falls on your face. Never sit with a window behind you: the camera exposes for the bright glass and your face goes dark.</p>
<p>If direct sun is harsh, a sheer curtain softens it. Daylight changes through the day and disappears in the evening, so it works best combined with a lamp you control.</p>

<h2>Put your main light in front of you, a little above eye level</h2>
<p>Your main light, often called the key light, should sit behind or just beside the camera, a little above eye level, angled slightly down toward your face. Too low and it lights you from below. Too high and it leaves shadows under your eyes.</p>
<p>A desk ring light is the simplest way to do this. It sits behind the screen and lights your face evenly from the front.</p>
[[B08HVH8FPF]]
<p>Start at a low brightness and turn it up until your face looks clear, not washed out. If you wear glasses and see reflections of the light, raise it higher and move it slightly off to one side.</p>

<h2>Raise the camera to eye level</h2>
<p>A laptop on a desk looks up at you, which is rarely flattering and shows a lot of ceiling. Raising the laptop brings the camera to eye level, so you look straight into it.</p>
[[B08BRCT4JH]]
<p>With an external webcam on a monitor, the same rule applies: set the screen so the camera sits at about eye height. Pair a raised laptop with a separate keyboard and mouse so your typing position stays comfortable.</p>

<h2>Add soft light behind you and behind the screen</h2>
<p>A dark background makes the picture look grainy and makes you look cut out. A small lamp somewhere in the room behind you, even pointed at a wall, adds depth and helps the camera. A clamp-on swing arm lamp is easy to aim at a wall and push away after the call.</p>
[[B07R56PTMS]]
<p>Bias lighting behind the monitor softens the contrast between a bright screen and a dark room. It is more about your comfort than the camera, but it helps on evening calls.</p>
[[B01LG99NW4]]

<h2>Keep your work light separate</h2>
<p>A monitor light bar lights the desk, not your face, so it does not replace a key light. It is still worth having. You can read notes or write during a call without the glare that a desk lamp can cause on the screen.</p>
[[B0B6P9J3J5]]

<h2>Match the color of your lights</h2>
<p>Mixing a warm lamp with cool daylight gives patchy, uneven skin tones. If your lights are adjustable, set them to a similar color temperature, warmer in the evening and more neutral during the day. If they are not, turn off the one that clashes with your main light.</p>

<h2>Sound is half the call</h2>
<p>Good light makes you look better, but clear audio is what people notice first. A microphone on a boom arm sits close to your mouth, where it picks up your voice rather than the room, and swings out of shot when you are done.</p>
[[B01L3LL95O]]

<h2>A two-minute check before important calls</h2>
<ul>
<li><strong>Open your camera preview.</strong> Your face should be the brightest thing in the frame.</li>
<li><strong>Look for bright windows behind you.</strong> Close the blind or turn your seat.</li>
<li><strong>Check the framing.</strong> Your eyes should sit about a third of the way down the frame.</li>
<li><strong>Check your glasses.</strong> Move the light up or to the side if it reflects.</li>
</ul>
<p>Working from a small room? The <a href="../setups/small-space-office.html">Small Space Office</a> keeps lights and screens off the desk surface. For a bedroom office, read <a href="best-desk-setup-for-small-bedrooms.html">the best desk setup for small bedrooms</a>.</p>
""",
         faq=[
             ("Where should a light go for video calls?", "In front of you, behind or just beside the camera, a little above eye level and angled slightly down. Avoid having a bright window or lamp behind you."),
             ("Is a ring light good for video calls?", "It is an easy way to light your face evenly from the front. Keep the brightness moderate and raise it if you see reflections in glasses."),
             ("Why do I look dark on video calls?", "Usually because the brightest light is behind you, like a window, so the camera exposes for the background. Face the light instead."),
             ("Does a monitor light bar light my face?", "Not really. It aims down at the desk. It is great for reading and writing during calls, but you still need a light in front of you."),
         ]),

    dict(slug="best-desk-setup-for-small-bedrooms", img="bedroom.jpg", eyebrow="Bedroom office guide", date="2026-09-24",
         title="The Best Desk Setup for Small Bedrooms",
         desc="How to fit a real desk setup into a small bedroom: where to put the desk, how to use the wall, keep the room comfortable and separate work from sleep.",
         setups=["small-space-office", "minimal-desk-setup"],
         body="""
<p>A bedroom office has two jobs that pull in opposite directions. During the day it needs to work like a real desk, with a screen at a sensible height, good light and somewhere to put things. At night it needs to disappear, so the room still feels like a place to sleep. This guide covers both, starting with where the desk goes.</p>

<h2>Pick the spot before you pick the desk</h2>
<p>Look for a wall with an outlet nearby and, ideally, a window to one side. Side light is the easiest daylight to work with: it does not glare off the screen the way light from behind the desk can, and it does not silhouette you on calls the way a window behind you does.</p>
<p>Measure the width and depth of the space, then check the chair. You need room to push it back and stand up without hitting the bed or a wardrobe door. If you can, set the desk so that you face away from the bed while you work.</p>

<h2>Choose a shallow desk and make the depth work</h2>
<p>A shallow desk saves floor space, but it brings the screen closer to your face and leaves little room for the keyboard. Two additions solve most of that. A monitor stand raises the screen and adds a drawer for small things, so the desktop stays clear.</p>
[[B088NHGC48]]
<p>A clamp-on keyboard tray adds a lower surface at the front edge, which moves the keyboard toward you and gives your arms a more comfortable angle. It clamps on, so there is nothing to drill.</p>
[[B07HFDJCSL]]
<p>If you work from a laptop, a stand does the same job as the monitor stand. Add a separate keyboard and mouse so you are not hunching over the laptop keyboard.</p>
[[B08BRCT4JH]]

<h2>Build up the wall, not out into the room</h2>
<p>In a small bedroom, floor space is the scarcest thing you have. The wall above the desk is usually empty. Floating shelves hold books, a printer paper stack, chargers and a plant, and keep all of it off the desktop.</p>
[[B0DZWXJ9VZ]]
<p>Mount them into studs or with anchors rated for what you plan to put on them, and keep the lowest shelf high enough that you do not hit it when you stand up.</p>

<h2>Light the desk, not the bed</h2>
<p>A bright desk lamp lights the whole room, which matters if someone else is trying to sleep. A monitor light bar aims light down at the desk surface only, with no glare on the screen and much less spill across the room.</p>
[[B0B6P9J3J5]]
<p>If you take video calls, light your face from the front. The guide to <a href="how-to-light-a-desk-for-video-calls.html">lighting a desk for video calls</a> covers where to put it.</p>

<h2>Keep the air comfortable</h2>
<p>A small room with a computer running and the door closed warms up quickly. A clip-on fan moves air without taking any floor space, and it can clamp to a shelf or the desk edge.</p>
[[B01559O0WY]]
<p>Because you both work and sleep in the room, a compact air purifier can be worth considering. Check the recommended room size on the listing against your room before you buy.</p>
[[B09GTRVJQM]]

<h2>Handle noise if you share the space</h2>
<p>A bedroom office is often next to a shared living space, a partner, or a busy street. Noise-cancelling headphones turn that down so you can focus or take a call, and they double as a way to signal that you are working.</p>
[[B0C3HCD34R]]

<h2>Keep the floor clear</h2>
<p>Cables and a power strip on the floor are visible from the bed and make the whole room feel busier. Mount the power strip under the desk in a tray, so only one cable reaches the wall. The <a href="cable-management-101-hide-desk-cables.html">cable management guide</a> covers the method step by step.</p>
[[B09J5HH2LR]]

<h2>Close the office at night</h2>
<p>A short end-of-day reset is what makes a bedroom office work. Put work items in one drawer or tray, close the laptop, turn off the desk light and push the chair in. Keep work off the nightstand. One or two small plants on the shelf make the corner feel like part of the room rather than an office dropped into it.</p>
[[B099596F3B]]

<h2>Common mistakes to avoid</h2>
<ul>
<li><strong>A desk that is too deep for the room.</strong> Measure chair clearance before you buy.</li>
<li><strong>A window behind the screen.</strong> The glare is tiring during the day and hard to fix later.</li>
<li><strong>Storage on the desktop.</strong> Move it to the wall or into a drawer.</li>
<li><strong>Work spreading across the room.</strong> Give it one boundary and clear it every evening.</li>
</ul>
<p>Every piece for a compact desk is in <a href="../setups/small-space-office.html">The Small Space Office</a>. For more ideas, read <a href="small-home-office-ideas.html">small home office ideas that actually work</a>.</p>
""",
         faq=[
             ("Where should a desk go in a small bedroom?", "Against a wall near an outlet, ideally with a window to one side, and facing away from the bed if possible. Leave room to push the chair back."),
             ("How do I make a small desk work in a bedroom?", "Raise the screen on a stand or riser, use a clamp-on keyboard tray for extra depth, and move storage to floating shelves above the desk."),
             ("What lighting is best for a bedroom desk?", "A monitor light bar lights the desk surface without lighting the whole room, which helps if someone else is sleeping. Add a front light for video calls."),
             ("How do I separate work and sleep in one room?", "Face the desk away from the bed, keep work items in one tray or drawer, and do a short reset at the end of each day."),
         ]),
]


# ---- Stylesheet (written to docs/style.css) ---------------------------------------------
# Shape rule: buttons 6px, cards 12px, photos in cards 10px, thumbnails 6-8px, full-bleed photos square.
# Color rule: forest (--ink) carries text, Amazon buttons and dark surfaces; terracotta is the single accent
# (links, the free-checklist button, "Start here"). No other hues.
CSS = r"""
/* The Setup Edit */
:root{
  --paper:#F4EEE3; --cream:#ECE3D1; --card:#FBF7F0; --sand:#E2D5BF; --chip:#E6DCC9;
  --ink:#1E2A26; --ink-2:#2A3732; --moss:#33463E; --stone:#5E5A51;
  --clay:#C0582F; --clay-ink:#A2461F; --clay-hover:#8A3B19; --clay-soft:#E0915F;
  --on-dark:#F2EADB; --on-dark-2:#C4BDAF;
  --line:rgba(30,42,38,.13); --line-2:rgba(30,42,38,.26); --line-dark:rgba(242,234,219,.16);
  --serif:"Newsreader",Georgia,"Times New Roman",serif;
  --sans:"Schibsted Grotesk",ui-sans-serif,system-ui,-apple-system,"Segoe UI",sans-serif;
  --pad:clamp(16px,4vw,56px); --gut:clamp(16px,2vw,32px); --sec:clamp(72px,8.4vw,128px);
  --r-btn:6px; --r-card:12px; --r-img:10px;
  --shadow:0 1px 1px rgba(30,42,38,.04),0 18px 40px -24px rgba(30,42,38,.34);
  --ease:cubic-bezier(.16,1,.3,1);
  --z-dock:20; --z-skip:30;
}
*,*::before,*::after{box-sizing:border-box}
html{-webkit-text-size-adjust:100%;text-size-adjust:100%;color-scheme:light;scroll-padding-bottom:96px}
@media (prefers-reduced-motion:no-preference){html{scroll-behavior:smooth}}
body{margin:0;background:var(--paper);color:var(--ink);font:400 17px/1.6 var(--sans);-webkit-font-smoothing:antialiased;
  -moz-osx-font-smoothing:grayscale;overflow-wrap:break-word;font-kerning:normal;overflow-x:clip}
img{max-width:100%;height:auto;display:block}picture{display:block}
a{color:inherit;text-decoration:none}
h1,h2,h3{font-family:var(--serif);font-weight:400;margin:0;line-height:1.1;letter-spacing:-.018em;text-wrap:balance}
p{margin:0;text-wrap:pretty}ul,ol{margin:0;padding:0;list-style:none}figure{margin:0}
::selection{background:var(--ink);color:var(--on-dark)}
:focus-visible{outline:2px solid var(--clay-ink);outline-offset:3px;border-radius:2px}
.foot :focus-visible,.pcard.lead :focus-visible{outline-color:var(--clay-soft)}
.vh{position:absolute!important;width:1px;height:1px;overflow:hidden;clip:rect(0 0 0 0);clip-path:inset(50%);white-space:nowrap}
.skip{position:absolute;left:12px;top:-80px;z-index:var(--z-skip);background:var(--ink);color:var(--on-dark);padding:10px 14px;border-radius:var(--r-btn)}
.skip:focus{top:12px}
.wrap{width:100%;max-width:1360px;margin-inline:auto;padding-inline:var(--pad)}
.meta{font:500 14px/1.4 var(--sans);color:var(--stone)}
.tag{display:inline-block;font:600 12.5px/1 var(--sans);padding:6px 8px 5px;border-radius:4px;background:var(--chip);color:var(--ink)}
.tag-clay{background:var(--clay-ink);color:var(--on-dark)}
.ul{background:linear-gradient(currentColor,currentColor) 0 100%/0 1px no-repeat;transition:background-size .5s var(--ease)}
a:hover .ul,a:focus-visible .ul{background-size:100% 1px}

/* buttons and links */
.btn{display:inline-flex;align-items:center;justify-content:center;gap:.45em;min-height:48px;padding:0 22px;border-radius:var(--r-btn);
  font:600 15.5px/1.1 var(--sans);white-space:nowrap;background:var(--ink);color:var(--on-dark);cursor:pointer;
  transition:background-color .25s var(--ease),transform .2s var(--ease),box-shadow .25s var(--ease)}
.btn:hover{background:var(--moss)}
.btn:active{transform:scale(.98)}
.btn .ext{display:inline-block;transition:transform .35s var(--ease)}
.btn:hover .ext{transform:translate(2px,-2px)}
.btn-clay{background:var(--clay-ink)}.btn-clay:hover{background:var(--clay-hover)}
.btn-light{background:var(--on-dark);color:var(--ink)}.btn-light:hover{background:#FFF9EE}
.btn-line{background:transparent;color:var(--ink);box-shadow:inset 0 0 0 1px var(--line-2)}
.btn-line:hover{background:var(--card);box-shadow:inset 0 0 0 1px var(--ink)}
.tlink{text-decoration:underline;text-decoration-thickness:1px;text-underline-offset:.22em;text-decoration-color:var(--clay);transition:color .2s}
.tlink:hover{color:var(--clay-ink)}
.go{display:inline-flex;align-items:center;gap:10px;font:600 15px/1.2 var(--sans)}
.go::after{content:"";width:18px;height:1px;background:currentColor;transition:width .4s var(--ease)}
a:hover .go::after,a.go:hover::after{width:30px}
.media{display:block;overflow:hidden;background:var(--sand)}
.media img{width:100%;height:100%;object-fit:cover;transition:transform 1.2s var(--ease)}
a:hover .media img{transform:scale(1.025)}
@media (prefers-reduced-motion:reduce){.media img,.btn,.btn .ext,.ul,.go::after{transition:none}}

/* top bar + masthead */
.topbar{display:block;background:var(--ink);color:var(--on-dark);font:500 14px/1.35 var(--sans);text-align:center;padding:10px var(--pad)}
.topbar u{text-decoration-color:var(--clay-soft);text-underline-offset:.22em}
.topbar:hover u{text-decoration-color:currentColor}
.tb-long{display:none}
.mast{border-bottom:1px solid var(--line)}
.mast .wrap{display:flex;flex-wrap:wrap;align-items:center;justify-content:space-between;column-gap:24px}
.wordmark{font:400 25px/1 var(--serif);letter-spacing:-.02em;padding:18px 0 10px;font-variation-settings:"opsz" 36}
.wordmark i{font-weight:300}
.primary{display:flex;gap:24px;width:100%;padding:0 0 10px}
.primary a{font:500 15px/1 var(--sans);padding:9px 0 7px;border-bottom:2px solid transparent;transition:color .2s,border-color .2s}
.primary a:hover{color:var(--clay-ink)}
.primary a[aria-current]{border-bottom-color:var(--clay)}
@media (min-width:760px){.tb-long{display:inline}.tb-short{display:none}
  .wordmark{font-size:30px;padding:22px 0}.primary{width:auto;padding:0;gap:34px}}

/* breadcrumbs */
.crumbs ol{display:flex;flex-wrap:wrap;row-gap:4px;font:500 14px/1.4 var(--sans);color:var(--stone)}
.crumbs li+li::before{content:"/";margin:0 10px;color:var(--stone);opacity:.6}
.crumbs a{color:var(--ink);text-decoration:underline;text-decoration-color:var(--line-2);text-underline-offset:.22em;transition:text-decoration-color .2s}
.crumbs a:hover{text-decoration-color:var(--clay)}@media (max-width:699px){.crumbs li[aria-current]{display:none}}

/* home: hero */
.hero{display:grid;gap:28px;padding-top:clamp(28px,4.4vw,64px);padding-bottom:clamp(28px,3vw,44px)}
.hero-title{font-size:clamp(44px,5.6vw,82px);font-weight:350;letter-spacing:-.035em;line-height:1;font-variation-settings:"opsz" 72}
.hero-dek{font:400 clamp(18px,1.45vw,20px)/1.5 var(--sans);color:var(--ink-2);max-width:40ch;margin-top:22px}
.hero-ctas{display:flex;flex-wrap:wrap;align-items:center;gap:16px 26px;margin-top:30px}
.hero-ctas .tlink{font:600 15.5px/1.2 var(--sans);padding:12px 0}
.hero-fig .media{border-radius:var(--r-img)}
.hero-fig img{aspect-ratio:4/3}
.caption{display:flex;flex-wrap:wrap;justify-content:space-between;gap:2px 24px;padding-top:10px;font-size:13px;line-height:1.5;color:var(--stone)}
.caption a{text-decoration:underline;text-decoration-color:var(--line-2);text-underline-offset:.2em}
@media (min-width:1000px){
  .hero{grid-template-columns:repeat(12,minmax(0,1fr));column-gap:var(--gut);align-items:center}
  .hero-text{grid-column:1/8;padding-right:clamp(0px,2vw,32px)}
  .hero-fig{grid-column:8/13}
  .hero-fig img{aspect-ratio:auto;height:min(66vh,620px);min-height:440px}
}
@media (prefers-reduced-motion:no-preference){
  .hero-text>*{animation:rise .9s var(--ease) both}
  .hero-text>:nth-child(2){animation-delay:.07s}.hero-text>:nth-child(3){animation-delay:.14s}
  @keyframes rise{from{opacity:0;transform:translateY(14px)}}
}
.jump{display:flex;align-items:center;gap:10px;overflow-x:auto;scrollbar-width:none;padding:18px 0 4px;border-top:1px solid var(--line)}
.jump::-webkit-scrollbar{display:none}
.jump .meta{flex:0 0 auto;margin-right:6px}
.jump a{display:flex;align-items:center;gap:12px;flex:0 0 auto;padding:6px 16px 6px 6px;border-radius:10px;background:var(--card);
  box-shadow:inset 0 0 0 1px var(--line);font:500 15px/1.2 var(--sans);transition:box-shadow .25s var(--ease)}
.jump a:hover{box-shadow:inset 0 0 0 1px var(--ink)}
.jump img{width:44px;height:44px;border-radius:6px;object-fit:cover}

/* shared section heads */
.sec{padding-block:var(--sec)}
.sec-rule{position:relative}.sec-rule::before{content:"";position:absolute;top:0;left:var(--pad);right:var(--pad);border-top:1px solid var(--line)}
.sec-head{display:grid;gap:14px;margin-bottom:clamp(32px,4vw,56px);max-width:780px}
.sec-title{font-size:clamp(34px,4.2vw,58px);font-weight:350;letter-spacing:-.03em;line-height:1.03;font-variation-settings:"opsz" 72}
.sec-dek{color:var(--stone);max-width:56ch;font-size:17.5px}

/* home: setups bento */
.bento{display:grid;gap:44px var(--gut)}
.scard{display:flex;flex-direction:column;gap:18px}
.scard .media{border-radius:var(--r-img)}
.scard img{aspect-ratio:3/2}
.scard-body{display:grid;gap:8px;justify-items:start}
.scard-title{font:400 clamp(27px,2.4vw,36px)/1.08 var(--serif);letter-spacing:-.022em}
.scard-dek{color:var(--stone);max-width:44ch;font-size:16.5px;line-height:1.55}
.scard .go{margin-top:8px}
@media (min-width:1000px){
  .bento{grid-template-columns:repeat(12,minmax(0,1fr));row-gap:48px}
  .sc1{grid-column:1/8;grid-row:1/3}
  .sc1 .media{position:relative;flex:1 1 auto;min-height:440px}
  .sc1 picture,.sc1 img{position:absolute;inset:0;width:100%;height:100%}
  .sc1 .scard-title{font-size:clamp(34px,3.2vw,48px)}
  .sc2{grid-column:8/13;grid-row:1}.sc3{grid-column:8/13;grid-row:2}
  .sc2 img,.sc3 img{aspect-ratio:16/10}
  .sc4{grid-column:1/13;display:grid;grid-template-columns:repeat(12,minmax(0,1fr));column-gap:var(--gut);align-items:center;
    padding-top:48px;border-top:1px solid var(--line)}
  .sc4 .media{grid-column:1/8}.sc4 img{aspect-ratio:2/1}.sc4 .scard-body{grid-column:9/13}
}

/* home: free checklist */
.lead-band{background:var(--cream)}
.lead-grid{display:grid;gap:30px;align-items:center}
.lead-fig .media{border-radius:var(--r-img)}
.lead-fig img{aspect-ratio:4/3;object-position:60% 50%}
.lead-title{font-size:clamp(32px,3.8vw,54px);font-weight:350;letter-spacing:-.03em;line-height:1.04;margin:16px 0}
.lead-dek{color:var(--ink-2);max-width:46ch;font-size:17.5px}
.ticks{display:grid;gap:10px;margin:22px 0 28px}
.ticks li{position:relative;padding-left:30px}
.ticks li::before{content:"";position:absolute;left:3px;top:.45em;width:12px;height:6px;border:solid var(--clay-ink);border-width:0 0 2px 2px;transform:rotate(-45deg)}
.lead-note{margin-top:14px}
@media (min-width:1000px){
  .lead-grid{grid-template-columns:repeat(12,minmax(0,1fr));column-gap:var(--gut)}
  .lead-fig{grid-column:1/7}.lead-fig img{aspect-ratio:5/4}.lead-text{grid-column:8/13}
}

/* compact checklist promo (setup and guide pages) */
.promo{display:grid;gap:18px;padding:18px;border-radius:var(--r-card);background:var(--cream);align-items:center;font-family:var(--sans)}
.promo .media{border-radius:8px}
.promo img{aspect-ratio:3/2;object-position:60% 50%}
.promo .promo-title{font:400 clamp(24px,2.2vw,30px)/1.12 var(--serif);letter-spacing:-.02em;margin:12px 0 8px;color:var(--ink)}
.promo-text p{color:var(--ink-2);font-size:16px;line-height:1.55;max-width:48ch}
.promo .btn{margin-top:18px}
@media (min-width:700px){.promo{grid-template-columns:220px minmax(0,1fr);gap:30px;padding:22px}.promo img{aspect-ratio:1}}

/* home: guides */
.guides{display:grid;gap:40px}
.gfeat{display:grid;gap:18px;align-content:start}
.gfeat .media{border-radius:var(--r-img)}
.gfeat img{aspect-ratio:3/2}
.gfeat-title{display:block;font:400 clamp(28px,2.8vw,40px)/1.08 var(--serif);letter-spacing:-.025em;margin-top:6px}
.gfeat-dek{display:block;color:var(--stone);max-width:52ch;margin-top:8px}
.glist li+li{border-top:1px solid var(--line)}
.glist a{display:grid;grid-template-columns:minmax(0,1fr) 76px;gap:18px;align-items:center;padding:18px 0}
.glist li:first-child a{padding-top:0}
.glist .media{border-radius:6px}
.glist img{aspect-ratio:1}
.glist-title{display:block;font:400 21px/1.22 var(--serif);letter-spacing:-.012em;margin-top:6px}
@media (min-width:1000px){
  .guides{grid-template-columns:repeat(12,minmax(0,1fr));column-gap:var(--gut)}
  .gfeat{grid-column:1/7}.glist{grid-column:8/13}
  .glist a{grid-template-columns:minmax(0,1fr) 92px}
}

/* home: shop */
.prods{display:grid;gap:var(--gut)}
.prod{display:grid;gap:20px;padding:14px;border-radius:var(--r-card);background:var(--card);box-shadow:inset 0 0 0 1px var(--line)}
.prod-cover{border-radius:8px;overflow:hidden;aspect-ratio:4/5;background:var(--sand)}
.prod-cover img{width:100%;height:100%;object-fit:cover}
.prod-body{display:flex;flex-direction:column;align-items:flex-start;gap:10px;padding:4px 8px 8px}
.prod-name{font:400 clamp(26px,2.3vw,33px)/1.08 var(--serif);letter-spacing:-.02em;margin-top:6px}
.prod-desc{color:var(--ink-2);max-width:40ch}
.prod .ticks{margin:6px 0 14px;font-size:15.5px}
.prod .btn{margin-top:auto}
.cover-wall{position:relative;background:var(--ink)}
.cover-wall::before{content:"";position:absolute;width:34%;aspect-ratio:1;border-radius:50%;background:var(--clay);left:54%;bottom:calc(36% - 12%)}
.cover-wall::after{content:"";position:absolute;left:0;right:0;bottom:0;height:36%;background:var(--sand);box-shadow:0 -1px 0 rgba(242,234,219,.4)}
@media (min-width:700px){.prod{grid-template-columns:minmax(0,5fr) minmax(0,7fr);gap:26px;padding:16px}.prod-body{padding:10px 8px 8px 0}}
@media (min-width:1100px){.prods{grid-template-columns:1fr 1fr}}
.mini-prods{display:grid;gap:14px}
.mini{display:grid;grid-template-columns:84px minmax(0,1fr);gap:18px;align-items:center;padding:12px;border-radius:var(--r-card);
  background:var(--card);box-shadow:inset 0 0 0 1px var(--line);font-family:var(--sans);transition:box-shadow .25s var(--ease)}
.mini:hover{box-shadow:inset 0 0 0 1px var(--ink)}
.mini .prod-cover{border-radius:6px}
.mini-name{display:block;font:400 21px/1.15 var(--serif);letter-spacing:-.01em;color:var(--ink);margin-top:4px}
.mini .go{margin-top:8px;font-size:14.5px;color:var(--ink)}
@media (min-width:700px){.mini-prods{grid-template-columns:1fr 1fr}}

/* home: about */
.about{display:grid;gap:22px}
.about-lede{font:350 clamp(26px,2.8vw,40px)/1.2 var(--serif);letter-spacing:-.02em;max-width:30ch}
.about-body{display:grid;gap:18px;justify-items:start}
.about-body p{color:var(--stone);max-width:56ch}
@media (min-width:1000px){.about{grid-template-columns:repeat(12,minmax(0,1fr));column-gap:var(--gut);align-items:start}
  .about-lede{grid-column:1/8}.about-body{grid-column:9/13;padding-top:8px}}

/* footer */
.foot{background:var(--ink);color:var(--on-dark-2);padding:clamp(56px,7vw,96px) 0 32px;font-size:15px;line-height:1.6}
.foot a{color:var(--on-dark);transition:color .2s}
.foot a:hover{color:var(--clay-soft)}
.foot-top{display:grid;gap:14px;padding-bottom:36px}
.foot-mark{font:300 clamp(40px,6vw,84px)/.95 var(--serif);letter-spacing:-.04em;color:var(--on-dark);font-variation-settings:"opsz" 72}
.foot-tag{max-width:36ch}
.foot-cols{display:grid;grid-template-columns:1fr 1fr;gap:32px 24px;padding:32px 0;border-top:1px solid var(--line-dark)}
.fh{font:600 14px/1.3 var(--sans);color:var(--on-dark-2);margin-bottom:10px}
.fcol li{margin:8px 0;line-height:1.35}
.foot-legal{display:grid;gap:12px;padding-top:24px;border-top:1px solid var(--line-dark);font-size:13.5px}.foot-legal p:not(.foot-end){max-width:100ch}
.foot-legal a{text-decoration:underline;text-decoration-color:var(--line-dark);text-underline-offset:.2em}
.foot-end{display:flex;justify-content:space-between;gap:16px;margin-top:8px}
@media (min-width:1000px){
  .foot-top{grid-template-columns:repeat(12,minmax(0,1fr));column-gap:var(--gut);align-items:end}
  .foot-mark{grid-column:1/8}.foot-tag{grid-column:9/13}
  .foot-cols{grid-template-columns:repeat(4,minmax(0,1fr));column-gap:var(--gut)}
}

/* page heads (setup, guide, about, 404) */
.ph{padding-top:clamp(22px,3vw,44px);padding-bottom:clamp(32px,4vw,56px)}
.ph .crumbs{margin-bottom:clamp(24px,3.4vw,48px)}
.ph-grid{display:grid;gap:24px}
.ph-title{font-size:clamp(42px,6.4vw,96px);font-weight:350;letter-spacing:-.04em;line-height:.97;font-variation-settings:"opsz" 72}
.ph-dek{font:400 clamp(19px,1.6vw,22px)/1.45 var(--serif);color:var(--ink-2);max-width:40ch}
.ph-aside{display:grid;gap:16px;justify-items:start;align-content:start}
.disclosure{font-size:13.5px;line-height:1.55;color:var(--stone);max-width:52ch}
.disclosure strong{color:var(--ink);font-weight:600}
@media (min-width:1000px){
  .ph-grid{grid-template-columns:repeat(12,minmax(0,1fr));column-gap:var(--gut);align-items:end}
  .ph-title{grid-column:1/8}.ph-aside{grid-column:9/13;padding-bottom:6px}
}
.bleed img{width:100%;object-fit:cover;aspect-ratio:4/3}
@media (min-width:700px){.bleed img{aspect-ratio:16/9}}
@media (min-width:1000px){.bleed img{aspect-ratio:auto;height:min(64vh,600px);min-height:420px}}

/* setup page */
.sintro{display:grid;gap:18px;padding-top:clamp(48px,6vw,88px)}
.sintro h2{font-size:clamp(26px,2.4vw,34px);letter-spacing:-.02em}
.sintro-body{display:grid;gap:14px;font:400 19px/1.65 var(--serif);color:var(--ink-2);max-width:62ch;font-variation-settings:"opsz" 16}
.sintro-body a{text-decoration:underline;text-decoration-color:var(--clay);text-underline-offset:.2em}
.good{font:500 15.5px/1.5 var(--sans);margin-top:20px;padding-top:16px;border-top:1px solid var(--line);max-width:62ch}
.good strong{font-weight:600}
@media (min-width:1000px){.sintro{grid-template-columns:repeat(12,minmax(0,1fr));column-gap:var(--gut)}
  .sintro h2{grid-column:1/4;padding-top:4px}.sintro-main{grid-column:5/12}}
.picks{display:grid;padding-top:clamp(48px,6vw,88px);padding-bottom:clamp(40px,5vw,72px)}
.pindex{display:none}
.plist-head{display:grid;gap:8px;margin-bottom:22px}
.plist-head h2{font-size:clamp(30px,3vw,44px);letter-spacing:-.025em}
.plist{display:grid;gap:14px}
.pcard{display:grid;gap:18px;padding:22px;border-radius:var(--r-card);background:var(--card);box-shadow:inset 0 0 0 1px var(--line);
  scroll-margin-top:20px;transition:box-shadow .3s var(--ease)}
.pcard:hover{box-shadow:inset 0 0 0 1px var(--line-2),var(--shadow)}
.pcard-top{display:flex;flex-wrap:wrap;gap:8px}
.pcard-name{font:400 clamp(25px,2.2vw,31px)/1.1 var(--serif);letter-spacing:-.02em;margin-top:14px}
.pcard-model{font:500 14.5px/1.4 var(--sans);color:var(--stone);margin-top:6px}
.pcard-why{margin-top:10px;color:var(--ink-2);max-width:54ch;font-size:16.5px;line-height:1.55}
.pcard .btn{justify-self:start}
.pcard.lead{background:var(--ink);color:var(--on-dark);box-shadow:none;padding:26px}
.pcard.lead:hover{box-shadow:var(--shadow)}
.pcard.lead .tag:not(.tag-clay){background:rgba(242,234,219,.12);color:var(--on-dark)}
.pcard.lead .pcard-name{font-size:clamp(30px,2.8vw,40px)}
.pcard.lead .pcard-model{color:var(--on-dark-2)}.pcard.lead .pcard-why{color:var(--on-dark)}
.start-note{margin-top:16px;padding-top:14px;border-top:1px solid var(--line-dark);color:var(--on-dark-2);font-size:15.5px;line-height:1.55;max-width:54ch}
.plist-foot{margin-top:18px}
@media (min-width:700px){.pcard{grid-template-columns:minmax(0,1fr) auto;column-gap:32px;padding:26px 28px;align-items:end}
  .pcard.lead{padding:34px 32px}}
@media (min-width:1000px){.picks{grid-template-columns:repeat(12,minmax(0,1fr));column-gap:var(--gut)}
  .pindex{display:block;grid-column:1/4;position:sticky;top:24px;align-self:start;padding-top:8px}
  .plist-wrap{grid-column:5/13}}
.pindex ol,.toc ol{margin-top:12px;border-left:1px solid var(--line)}
.pindex a,.toc a{display:block;padding:7px 0 7px 16px;margin-left:-1px;border-left:2px solid transparent;font-size:14.5px;line-height:1.35;
  color:var(--stone);transition:color .2s,border-color .2s}
.pindex a:hover,.toc a:hover{color:var(--ink)}
.pindex a[aria-current],.toc a[aria-current]{color:var(--ink);border-left-color:var(--clay)}
.pindex .meta,.toc .meta{color:var(--ink);font-weight:600}
.after{display:grid;gap:clamp(56px,7vw,104px);padding-bottom:var(--sec)}
.block-title{font-size:clamp(28px,2.8vw,40px);letter-spacing:-.025em;margin-bottom:24px}
.rgrid{display:grid;gap:32px var(--gut)}
.rcard{display:grid;gap:12px;align-content:start}
.rcard .media{border-radius:var(--r-img)}
.rcard img{aspect-ratio:3/2}
.rcard-title{font:400 clamp(22px,1.9vw,27px)/1.16 var(--serif);letter-spacing:-.015em}
@media (min-width:700px){.rgrid{grid-template-columns:repeat(2,minmax(0,1fr))}}
.srows li+li{border-top:1px solid var(--line)}
.srows a{display:grid;grid-template-columns:96px minmax(0,1fr);gap:18px;align-items:center;padding:16px 0}
.srows li:first-child a{padding-top:0}
.srows .media{border-radius:6px}
.srows img{aspect-ratio:4/3}
.srow-title{display:block;font:400 clamp(22px,2vw,28px)/1.12 var(--serif);letter-spacing:-.018em;margin-bottom:4px}
@media (min-width:1000px){.after-2{grid-template-columns:repeat(12,minmax(0,1fr));column-gap:var(--gut)}
  .after-2>:first-child{grid-column:1/8}.after-2>:last-child{grid-column:9/13}
  .after-2 .rgrid{grid-template-columns:repeat(2,minmax(0,1fr))}}

/* guide page */
.guide-title{max-width:17ch}
.gh-row{display:grid;gap:18px;margin-top:clamp(22px,3vw,40px)}
.gh-dek{font:italic 350 clamp(20px,1.8vw,24px)/1.45 var(--serif);color:var(--ink-2);max-width:46ch}
.gh-meta{display:grid;gap:10px;align-content:start}
@media (min-width:1000px){.gh-row{grid-template-columns:repeat(12,minmax(0,1fr));column-gap:var(--gut)}
  .gh-dek{grid-column:1/8}.gh-meta{grid-column:9/13}}
.gfig .media{border-radius:var(--r-img)}
.gfig img{aspect-ratio:3/2}
@media (min-width:1000px){.gfig img{aspect-ratio:21/9}}
.article{display:grid;padding-top:clamp(36px,5vw,80px);padding-bottom:var(--sec)}
.toc{display:none}
.toc-m{margin-bottom:30px;border-radius:var(--r-card);background:var(--card);box-shadow:inset 0 0 0 1px var(--line)}
.toc-m summary{display:flex;justify-content:space-between;align-items:center;min-height:52px;padding:0 18px;font:600 15.5px/1.3 var(--sans);cursor:pointer;list-style:none}
.toc-m summary::-webkit-details-marker{display:none}
.toc-m summary::after{content:"+";font:400 22px/1 var(--sans);color:var(--stone)}
.toc-m[open] summary::after{content:"\2212"}
.toc-m ol{padding:0 18px 10px}
.toc-m a{display:block;padding:11px 0;font-size:15.5px;color:var(--ink-2);border-top:1px solid var(--line)}
@media (min-width:1000px){.article{grid-template-columns:repeat(12,minmax(0,1fr));column-gap:var(--gut)}
  .toc{display:block;grid-column:1/4;position:sticky;top:24px;align-self:start;padding-right:12px}
  .toc-m{display:none}.prose-col{grid-column:4/11}}

/* prose */
.prose{font:400 19px/1.7 var(--serif);color:var(--ink-2);max-width:68ch;font-variation-settings:"opsz" 16}
.prose>p+p{margin-top:1.05em}
.prose>p:first-child{font-size:1.1em;line-height:1.6;color:var(--ink)}
.prose h2{font-size:clamp(27px,2.4vw,34px);font-weight:400;letter-spacing:-.02em;line-height:1.14;color:var(--ink);margin:2.1em 0 .6em;scroll-margin-top:24px}
.prose h3{font:italic 400 23px/1.25 var(--serif);color:var(--ink);margin:1.8em 0 .45em}
.prose>h2+p,.prose>h3+p{margin-top:0}
.prose p a:not(.go),.prose>ul a{text-decoration:underline;text-decoration-thickness:1px;text-underline-offset:.2em;text-decoration-color:var(--clay);transition:color .2s}
.prose p a:not(.go):hover,.prose>ul a:hover{color:var(--clay-ink)}
.prose strong{font-weight:600;color:var(--ink)}
.prose>ul{margin:1.1em 0 1.3em}
.prose>ul>li{position:relative;padding:.4em 0 .4em 26px}
.prose>ul>li::before{content:"";position:absolute;left:2px;top:1.2em;width:12px;height:1px;background:var(--clay)}
.pick{display:grid;gap:16px;margin:1.6em 0;padding:22px;border-radius:var(--r-card);background:var(--card);box-shadow:inset 0 0 0 1px var(--line);font-family:var(--sans)}
.pick-name{font:400 25px/1.12 var(--serif);letter-spacing:-.02em;color:var(--ink);margin-top:12px}
.pick-model{font:500 14px/1.4 var(--sans);color:var(--stone);margin-top:4px}
.pick-why{font-size:16px;line-height:1.55;color:var(--ink-2);margin-top:8px;max-width:48ch}
.pick .btn{justify-self:start}
.pick+p{margin-top:0}
@media (min-width:700px){.pick{grid-template-columns:minmax(0,1fr) auto;column-gap:28px;align-items:end;padding:24px 26px}}
.quick{margin:1.8em 0 .6em;padding:20px 22px 8px;border-radius:var(--r-card);box-shadow:inset 0 0 0 1px var(--line-2);font-family:var(--sans)}
.quick-title{font:600 16.5px/1.3 var(--sans);color:var(--ink)}
.quick-sub{font-size:14.5px;line-height:1.5;color:var(--stone);margin-top:4px}
.quick-sub a{color:var(--ink);text-decoration:underline;text-decoration-color:var(--clay);text-underline-offset:.2em}
.quick ol{margin-top:12px}
.quick li{display:flex;justify-content:space-between;align-items:center;gap:16px;padding:10px 0;border-top:1px solid var(--line)}
.quick-name{font:500 16px/1.3 var(--sans);color:var(--ink)}
.quick-model{display:block;font-size:13.5px;font-weight:400;color:var(--stone);margin-top:2px}
.quick .q{flex:0 0 auto;font:600 14.5px/1.2 var(--sans);color:var(--ink);padding:10px 0;text-decoration:underline;text-decoration-color:var(--clay);text-underline-offset:.22em}
.quick .q:hover{color:var(--clay-ink)}
.faq{margin-top:1em}
.faq details{border-top:1px solid var(--line)}
.faq details:last-of-type{border-bottom:1px solid var(--line)}
.faq summary{display:flex;justify-content:space-between;align-items:center;gap:24px;padding:18px 0;cursor:pointer;list-style:none;
  font:400 21px/1.3 var(--serif);color:var(--ink);letter-spacing:-.01em}
.faq summary::-webkit-details-marker{display:none}
.faq summary:hover{color:var(--clay-ink)}
.faq summary i{position:relative;flex:0 0 14px;height:14px}
.faq summary i::before,.faq summary i::after{content:"";position:absolute;left:0;top:6.5px;width:14px;height:1.5px;background:currentColor;transition:transform .35s var(--ease)}
.faq summary i::after{transform:rotate(90deg)}
.faq details[open] summary i::after{transform:rotate(0)}
.faq details p{font:400 16.5px/1.6 var(--sans);color:var(--stone);padding:0 40px 22px 0;max-width:60ch}
.prose .promo,.prose .mini-prods{margin-top:2.2em}
.prose .block-title{margin:2.1em 0 .7em}
.back{margin-top:3em}
.prose-plain>p:first-child{font-size:1em}

/* sticky call to action */
.dock{position:fixed;z-index:var(--z-dock);left:0;right:0;bottom:0;display:flex;align-items:center;gap:12px;
  padding:10px var(--pad) calc(10px + env(safe-area-inset-bottom));background:rgba(251,247,240,.95);
  -webkit-backdrop-filter:blur(10px);backdrop-filter:blur(10px);box-shadow:0 -1px 0 var(--line),0 -14px 30px -22px rgba(30,42,38,.45);
  transform:translateY(115%);visibility:hidden;transition:transform .45s var(--ease),visibility 0s linear .45s}
.dock.on{transform:none;visibility:visible;transition:transform .45s var(--ease)}
.dock-text{flex:1;min-width:0;font:600 14.5px/1.3 var(--sans);color:var(--ink)}
.dock-text small{display:block;font-weight:400;font-size:13px;color:var(--stone);white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.dock .btn{min-height:44px;padding:0 16px;font-size:14.5px}
.dock-x{flex:0 0 auto;display:grid;place-items:center;width:40px;height:40px;margin-right:-8px;border:0;border-radius:var(--r-btn);background:none;
  color:var(--stone);font:400 24px/1 var(--sans);cursor:pointer;transition:background-color .2s,color .2s}
.dock-x:hover{color:var(--ink);background:var(--chip)}
@media (max-width:420px){.dock-text small{display:none}}
@media (min-width:760px){.dock{left:auto;right:24px;bottom:24px;width:min(520px,calc(100% - 48px));padding:14px 14px 14px 20px;
  border-radius:var(--r-card);box-shadow:inset 0 0 0 1px var(--line),var(--shadow)}.dock-x{margin-right:0}}
@media (prefers-reduced-motion:reduce){.dock,.dock.on{transition:none}}

/* 404 */
.nf-list{margin-top:clamp(40px,5vw,72px)}
.nf-list li+li{border-top:1px solid var(--line)}
.nf-list a{display:block;padding:18px 0;font:400 clamp(22px,2.4vw,32px)/1.15 var(--serif);letter-spacing:-.02em}
"""

# ---- Photo credits by image file (used for captions) ---------------------------------
PHOTO_BY = {img: (name, pid) for _, name, pid, img in CREDITS}

# ---- Digital products (Payhip) ------------------------------------------------------
CHECKLIST_URL = "https://payhip.com/b/XAPfb"
CHECKLIST_POINTS = ["12 steps, from tangle to tidy", "The short list of what you will need", "Two pages, ready to print"]
SHOP = [
    dict(kind="check", kicker="Free download", name="Desk Cable Checklist", url=CHECKLIST_URL, img="checklist.jpg",
         desc="A printable checklist for getting desk cables under control, one step at a time.", points=CHECKLIST_POINTS),
    dict(kind="guide", kicker="Printable guide", name="The Clean Desk Guide", url="https://payhip.com/b/3MK0F", img="clean-desk.jpg",
         desc="A 15-page printable guide to setting up a clean, calm desk, from clearing the surface to keeping it that way.",
         points=["15 printable pages", "Instant download through Payhip"]),
    dict(kind="wall", kicker="Digital download", name="Minimalist Wallpaper Pack", url="https://payhip.com/b/XqrMo", img=None,
         desc="Eight quiet wallpapers in forest, sand and terracotta tones, made to match calm, minimal desk setups.",
         points=["8 designs, each in 4K desktop and phone sizes", "16 image files, instant download"]),
]
PAID = [p for p in SHOP if p["kind"] != "check"]

esc = html.escape
AMZ_REL = 'rel="sponsored nofollow noopener" target="_blank"'
EXT = '<span class="ext" aria-hidden="true">&#8599;</span>'


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


def srcset(name, root, ext):
    stem = name.rsplit(".", 1)[0]
    return ", ".join(f"{root}img/web/{stem}-{x}.{ext} {x}w" for x in widths_for(name))


def pic(name, root, alt, sizes, cls="", eager=False):
    """<picture> with WebP + JPEG srcsets. CSS sets the displayed aspect ratio."""
    stem = name.rsplit(".", 1)[0]
    ws = widths_for(name)
    w, h = img_dims(name)
    fallback = f"{root}img/web/{stem}-{ws[min(1, len(ws) - 1)]}.jpg"
    load = 'loading="eager" fetchpriority="high"' if eager else 'loading="lazy"'
    c = f' class="{cls}"' if cls else ""
    return (f'<picture><source type="image/webp" srcset="{srcset(name, root, "webp")}" sizes="{sizes}">'
            f'<img{c} src="{fallback}" srcset="{srcset(name, root, "jpg")}" sizes="{sizes}" width="{w}" height="{h}" '
            f'alt="{esc(alt)}" {load} decoding="async"></picture>')


def preload_tag(name, root, sizes):
    return (f'<link rel="preload" as="image" type="image/webp" imagesrcset="{srcset(name, root, "webp")}" '
            f'imagesizes="{sizes}" fetchpriority="high">')


def thumb(name, root, alt, px=120):
    """Small square-ish thumbnail using the smallest web size."""
    stem = name.rsplit(".", 1)[0]
    w0 = widths_for(name)[0]
    return (f'<picture><source type="image/webp" srcset="{root}img/web/{stem}-{w0}.webp"><img src="{root}img/web/{stem}-{w0}.jpg" '
            f'width="{px}" height="{px}" alt="{esc(alt)}" loading="lazy" decoding="async"></picture>')


def credit(img):
    if img not in PHOTO_BY:
        return ""
    name, pid = PHOTO_BY[img]
    return f'Photo: <a href="https://unsplash.com/photos/{pid}" rel="nofollow">{esc(name)}</a> on Unsplash'


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
    return f'<p class="disclosure"><strong>Disclosure.</strong> {esc(DISCLOSURE)}</p>'


def setup_by(slug):
    return next(s for s in SETUPS if s["slug"] == slug)


def picks_label(s):
    return f"{len(s['items'])} picks"


ARTICLES_BY_DATE = sorted(ARTICLES, key=lambda a: a["date"], reverse=True)
IMG_ALT = {
    "hero.jpg": "A dual-monitor desk with plants, warm lamps and a wooden desktop",
    "trading.jpg": "A trading desk with a monitor on an arm, a laptop on a stand and warm backlighting",
    "minimal.jpg": "A minimal desk with a leather desk pad, a white mouse and a wooden tray",
    "small.jpg": "A compact home office desk with a raised monitor in a small room",
    "cable.jpg": "Cables coiled and clipped to the underside of a desk",
    "bedroom.jpg": "A small bedroom desk beside a bed, with a laptop and a white chair",
    "video-call.jpg": "A desk lit by a ring light, with a laptop, a tablet and plants",
    "standing.jpg": "A white standing desk with a monitor, a desk shelf and plants",
    "checklist.jpg": "A hand ticking boxes on a handwritten checklist in a notebook",
    "clean-desk.jpg": "A clean desk with a monitor, speakers and a large desk mat",
}


# ---- Page shell ----------------------------------------------------------------------------
FONTS = ("https://fonts.googleapis.com/css2?family=Newsreader:ital,opsz,wght@0,6..72,300..500;"
         "1,6..72,300..500&family=Schibsted+Grotesk:wght@400;500;600&display=swap")

JS = """(function(){var d=document,IO='IntersectionObserver' in window;
var links=[].slice.call(d.querySelectorAll('[data-spy] a'));
if(links.length&&IO){var map=new Map(),seen=new Map(),cur=null;
links.forEach(function(a){var t=d.getElementById(a.getAttribute('href').slice(1));if(t)map.set(t,a)});
var set=function(a){if(a===cur)return;cur=a;links.forEach(function(l){if(l.getAttribute('href')===a.getAttribute('href'))l.setAttribute('aria-current','true');else l.removeAttribute('aria-current')})};
var io=new IntersectionObserver(function(es){es.forEach(function(e){seen.set(e.target,e.isIntersecting)});
var f=null;map.forEach(function(a,t){if(!f&&seen.get(t))f=a});if(f)set(f)},{rootMargin:'-12% 0px -62% 0px'});
map.forEach(function(a,t){io.observe(t)})}
var k=d.getElementById('dock');if(!k||!IO)return;var ok=true;try{ok=sessionStorage.getItem('dock-x')!=='1'}catch(e){}
var past=false,block=new Set(),st=d.querySelector('[data-dock-start]');
var up=function(){k.classList.toggle('on',ok&&past&&block.size===0)};
if(st)new IntersectionObserver(function(es){var e=es[es.length-1];past=!e.isIntersecting&&e.boundingClientRect.top<0;up()}).observe(st);
var hb=new IntersectionObserver(function(es){es.forEach(function(e){if(e.isIntersecting)block.add(e.target);else block.delete(e.target)});up()});
[].forEach.call(d.querySelectorAll('[data-dock-hide]'),function(el){hb.observe(el)});
k.querySelector('.dock-x').addEventListener('click',function(){ok=false;up();try{sessionStorage.setItem('dock-x','1')}catch(e){}});
})();"""

CSS_VERSION = ""


def topbar():
    return (f'<a class="topbar" href="{CHECKLIST_URL}" rel="noopener" target="_blank">'
            f'<span class="tb-long">Free printable: the 12-step desk cable checklist. </span><u>Get the free checklist</u>'
            f'<span class="tb-short">: 12 steps, 2 pages</span> <span aria-hidden="true">&#8599;</span></a>')


def masthead(root, current):
    items = [("setups", "Setups", f"{root}index.html#setups"), ("guides", "Guides", f"{root}index.html#guides"),
             ("shop", "Shop", f"{root}index.html#shop"), ("about", "About", f"{root}disclosure.html")]
    links = "".join(f'<a href="{h}"' + (' aria-current="page"' if k == current else "") + f'>{t}</a>' for k, t, h in items)
    return f"""<a class="skip" href="#main">Skip to content</a>
{topbar()}
<header class="mast"><div class="wrap"><a class="wordmark" href="{root}index.html" translate="no"><i>The</i> Setup Edit</a>
<nav class="primary" aria-label="Primary">{links}</nav></div></header>"""


def footer(root):
    col = lambda title, lis: f'<div class="fcol"><p class="fh">{title}</p><ul>{lis}</ul></div>'
    setups = "".join(f'<li><a href="{root}setups/{s["slug"]}.html">{esc(s["title"])}</a></li>' for s in SETUPS)
    guides = "".join(f'<li><a href="{root}guides/{a["slug"]}.html">{esc(short_title(a))}</a></li>' for a in ARTICLES_BY_DATE)
    shop = "".join(f'<li><a href="{p["url"]}" rel="noopener" target="_blank">{esc(p["name"])}</a></li>' for p in SHOP)
    edit = (f'<li><a href="{root}disclosure.html">About &amp; disclosure</a></li>'
            f'<li><a href="{root}sitemap.xml">Sitemap</a></li>')
    credits = ", ".join(f'<a href="https://unsplash.com/photos/{i}" rel="nofollow">{esc(n)}</a>' for _, n, i, _ in CREDITS)
    return f"""<footer class="foot" data-dock-hide><div class="wrap">
<div class="foot-top"><p class="foot-mark" translate="no"><i>The</i> Setup Edit</p>
<p class="foot-tag">Curated desk setups, home office ideas and trading desks, researched and written by one independent editor.</p></div>
<div class="foot-cols">{col("Setups", setups)}{col("Guides", guides)}{col("Shop", shop)}{col("The Edit", edit)}</div>
<div class="foot-legal"><p>{esc(DISCLOSURE)} Picks come from research, not hands-on testing.</p>
<p>Photos from <a href="https://unsplash.com" rel="nofollow">Unsplash</a>: {credits}. Products shown in photos may differ from the linked items.</p>
<p class="foot-end"><span>&copy; 2026 The Setup Edit</span><a href="#top">Back to top</a></p></div>
</div></footer>"""


def dock(text, sub, href, label, cls="btn", external=True):
    tgt = ' rel="noopener" target="_blank"' if external else ""
    return (f'<aside class="dock" id="dock" aria-label="Suggested next step"><p class="dock-text">{text}<small>{sub}</small></p>'
            f'<a class="{cls}" href="{href}"{tgt}>{label}{EXT if external else ""}</a>'
            f'<button class="dock-x" type="button" aria-label="Dismiss">&times;</button></aside>')


def checklist_dock():
    return dock("12-step desk cable checklist", "Free, two pages, ready to print", CHECKLIST_URL, "Get the free checklist", "btn btn-clay")


def curly(doc):
    """Typographic apostrophes in visible text only (not in attributes, scripts or styles)."""
    parts = re.split(r"(<script\b.*?</script>|<style\b.*?</style>)", doc, flags=re.S)
    fix = lambda m: ">" + re.sub(r"(\w)(?:'|&#x27;)", "\\1\u2019", m.group(1)) + "<"
    return "".join(p if p.startswith(("<script", "<style")) else re.sub(r">([^<>]+)<", fix, p) for p in parts)


def ld(obj):
    return f'<script type="application/ld+json">{json.dumps(obj, ensure_ascii=False)}</script>'


def page(title, desc, body, root="", og="img/hero.jpg", path="", current="", extra_head="", preload="", dock_html="", schema=()):
    url = BASE_URL + path
    og_abs = og if og.startswith("http") else BASE_URL + og
    scripts = "".join(ld(s) for s in schema)
    return curly(f"""<!doctype html><html lang="en" id="top"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{esc(title)}</title><meta name="description" content="{esc(desc)}">
<link rel="canonical" href="{url}">
<meta property="og:title" content="{esc(title)}"><meta property="og:description" content="{esc(desc)}">
<meta property="og:image" content="{og_abs}"><meta property="og:url" content="{url}">
<meta property="og:type" content="{'article' if path.startswith('guides/') else 'website'}"><meta property="og:site_name" content="{SITE_NAME}">
<meta name="twitter:card" content="summary_large_image">
<meta name="p:domain_verify" content="77efeace518f495ac7564d61a39f2015"/>
<meta name="theme-color" content="#1E2A26">
<link rel="icon" href="{root}favicon.svg" type="image/svg+xml">
<link rel="icon" href="{root}img/web/icon-32.png" sizes="32x32" type="image/png">
<link rel="apple-touch-icon" href="{root}img/web/icon-180.png">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
{preload}<link rel="stylesheet" href="{root}style.css?v={CSS_VERSION}">
<link rel="stylesheet" href="{FONTS}" media="print" onload="this.media='all'"><noscript><link rel="stylesheet" href="{FONTS}"></noscript>
{extra_head}{scripts}</head>
<body>{masthead(root, current)}
<main id="main">{body}</main>
{footer(root)}
{dock_html}
<script>{JS}</script></body></html>""")


def breadcrumbs(trail):
    """trail: [(name, site-relative path, href or None for the current page)]. Returns (visible nav html, BreadcrumbList schema). Paths are site-relative."""
    items = []
    for k, (name, path, href) in enumerate(trail):
        if href:
            items.append(f'<li><a href="{href}">{esc(name)}</a></li>')
        else:
            items.append(f'<li aria-current="page">{esc(name)}</li>')
    schema = {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": k, "name": name, "item": BASE_URL + path} for k, (name, path, _) in enumerate(trail, 1)]}
    return f'<nav class="crumbs" aria-label="Breadcrumb"><ol>{"".join(items)}</ol></nav>', schema


# ---- Product blocks ------------------------------------------------------------------------
PRODUCTS = dict(EXTRA_PRODUCTS)
PRODUCTS.update({a: (n, m, w) for s in SETUPS for n, m, a, w in s["items"]})


def amazon_btn(asin, name, cls="btn"):
    return (f'<a class="{cls}" href="{amz(asin)}" {AMZ_REL}>View on Amazon<span class="vh">: {esc(name)}</span> {EXT}</a>')


def product_card(match):
    asin = match.group(1)
    n, m, w = PRODUCTS[asin]  # KeyError here means the ASIN isn't in SETUPS or EXTRA_PRODUCTS
    return (f'<aside class="pick" aria-label="{esc(n)}"><div class="pick-body"><span class="tag">{ROLE.get(asin, "Pick")}</span>'
            f'<p class="pick-name">{esc(n)}</p><p class="pick-model">{esc(m)}</p><p class="pick-why">{esc(w)}</p></div>'
            f'{amazon_btn(asin, n)}</aside>')


def checklist_promo(root, hide=True):
    return f"""<aside class="promo" aria-labelledby="promo-title"{' data-dock-hide' if hide else ''}>
<span class="media">{pic('checklist.jpg', root, IMG_ALT['checklist.jpg'], '(min-width: 700px) 220px, 100vw')}</span>
<div class="promo-text"><span class="tag tag-clay">Free printable</span>
<p class="promo-title" id="promo-title">The desk cable checklist</p>
<p>Twelve steps from a tangle to a tidy desk, plus the short list of what you will need. Two pages, ready to print.</p>
<a class="btn btn-clay" href="{CHECKLIST_URL}" rel="noopener" target="_blank">Get the free checklist{EXT}</a></div></aside>"""


def prod_cover(p, root):
    if p["img"]:
        return f'<span class="prod-cover">{pic(p["img"], root, IMG_ALT[p["img"]], "(min-width: 1100px) 20vw, (min-width: 700px) 40vw, 100vw")}</span>'
    return '<span class="prod-cover cover-wall" role="img" aria-label="Wallpaper pack artwork: a terracotta sun over a sand horizon on forest green"></span>'


def mini_prods(root, heading=True):
    cards = "".join(f"""<a class="mini" href="{p['url']}" rel="noopener" target="_blank">{prod_cover(p, root)}
<span><span class="meta">{p['kicker']}</span><span class="mini-name">{esc(p['name'])}</span><span class="go">View on Payhip</span></span></a>"""
                    for p in PAID)
    if not heading:
        return f'<div class="mini-prods">{cards}</div>'
    return f'<section aria-labelledby="mp-title"><h2 class="block-title" id="mp-title">From the shop</h2><div class="mini-prods">{cards}</div></section>'


# ---- Home ------------------------------------------------------------------------------------
BENTO = ["minimal-desk-setup", "trading-desk-setup", "small-space-office", "cable-management"]
BENTO_SIZES = ["(min-width: 1000px) 55vw, 100vw", "(min-width: 1000px) 38vw, 100vw",
               "(min-width: 1000px) 38vw, 100vw", "(min-width: 1000px) 55vw, 100vw"]


def build_home():
    cards = []
    for k, slug in enumerate(BENTO):
        s = setup_by(slug)
        cards.append(f"""<a class="scard sc{k + 1}" href="setups/{slug}.html">
<span class="media">{pic(s['img'], '', IMG_ALT[s['img']], BENTO_SIZES[k])}</span>
<span class="scard-body"><span class="meta">{picks_label(s)}</span><span class="scard-title"><span class="ul">{esc(s['title'])}</span></span>
<span class="scard-dek">{esc(s['blurb'])}</span><span class="go">Shop the list</span></span></a>""")
    jump = "".join(f'<a href="setups/{s["slug"]}.html">{thumb(s["img"], "", IMG_ALT[s["img"]], 44)}{esc(s["title"].replace("The ", "", 1))}</a>'
                   for s in SETUPS)
    feat, rest = ARTICLES_BY_DATE[0], ARTICLES_BY_DATE[1:]
    glist = "".join(f"""<li><a href="guides/{a['slug']}.html"><span><span class="meta">{esc(a['eyebrow'])}, {reading_time(a)} min read</span>
<span class="glist-title"><span class="ul">{esc(a['title'])}</span></span></span>
<span class="media">{thumb(a['img'], '', IMG_ALT[a['img']], 92)}</span></a></li>""" for a in rest)
    ticks = "".join(f"<li>{esc(t)}</li>" for t in CHECKLIST_POINTS)
    prods = "".join(f"""<article class="prod">{prod_cover(p, '')}<div class="prod-body"><span class="tag">{p['kicker']}</span>
<h3 class="prod-name">{esc(p['name'])}</h3><p class="prod-desc">{esc(p['desc'])}</p>
<ul class="ticks">{''.join(f'<li>{esc(t)}</li>' for t in p['points'])}</ul>
<a class="btn" href="{p['url']}" rel="noopener" target="_blank">View on Payhip<span class="vh">: {esc(p['name'])}</span> {EXT}</a></div></article>""" for p in PAID)
    hero_sizes = "(min-width: 1000px) 40vw, 100vw"
    body = f"""<section class="wrap hero" aria-labelledby="hero-title" data-dock-start>
<div class="hero-text"><h1 id="hero-title" class="hero-title">A desk you actually want to sit at.</h1>
<p class="hero-dek">Curated desk setups and practical guides for home offices, small rooms and trading desks, with every pick one click away.</p>
<p class="hero-ctas"><a class="btn" href="#setups">Browse the setups</a><a class="tlink" href="{CHECKLIST_URL}" rel="noopener" target="_blank">Get the free checklist <span aria-hidden="true">&#8599;</span></a></p></div>
<figure class="hero-fig"><span class="media">{pic('hero.jpg', '', IMG_ALT['hero.jpg'], hero_sizes, eager=True)}</span>
<figcaption class="caption"><span>Two screens, soft lamps and plenty of green.</span><span>{credit('hero.jpg')}</span></figcaption></figure>
</section>
<nav class="wrap" aria-label="Jump to a setup"><div class="jump"><span class="meta">Jump to a setup</span>{jump}</div></nav>

<section id="setups" class="wrap sec" aria-labelledby="setups-title">
<header class="sec-head"><h2 id="setups-title" class="sec-title">Four desks, edited down to what matters.</h2>
<p class="sec-dek">Each setup is a short shopping list with a note on why every piece is there, and where to start.</p></header>
<div class="bento">{''.join(cards)}</div>
</section>

<section id="checklist" class="lead-band sec" aria-labelledby="lead-title" data-dock-hide><div class="wrap lead-grid">
<figure class="lead-fig"><span class="media">{pic('checklist.jpg', '', IMG_ALT['checklist.jpg'], '(min-width: 1000px) 45vw, 100vw')}</span>
<figcaption class="caption"><span>{credit('checklist.jpg')}</span></figcaption></figure>
<div class="lead-text"><span class="tag tag-clay">Free printable</span>
<h2 id="lead-title" class="lead-title">Get your desk cables under control this weekend.</h2>
<p class="lead-dek">The Desk Cable Checklist turns the method from our cable guides into a list you can tick off, one step at a time.</p>
<ul class="ticks">{ticks}</ul>
<a class="btn btn-clay" href="{CHECKLIST_URL}" rel="noopener" target="_blank">Get the free checklist{EXT}</a>
<p class="meta lead-note">A free PDF, delivered through Payhip.</p></div>
</div></section>

<section id="guides" class="wrap sec" aria-labelledby="guides-title">
<header class="sec-head"><h2 id="guides-title" class="sec-title">Guides for a better desk.</h2>
<p class="sec-dek">Step-by-step reads on cables, light, small rooms and trading desks. Each one links to the setups it builds.</p></header>
<div class="guides"><a class="gfeat" href="guides/{feat['slug']}.html"><span class="media">{pic(feat['img'], '', IMG_ALT[feat['img']], '(min-width: 1000px) 48vw, 100vw')}</span>
<span><span class="meta">{esc(feat['eyebrow'])}, {reading_time(feat)} min read</span>
<span class="gfeat-title"><span class="ul">{esc(feat['title'])}</span></span>
<span class="gfeat-dek">{esc(feat['desc'])}</span></span></a>
<ol class="glist">{glist}</ol></div>
</section>

<section id="shop" class="wrap sec sec-rule" aria-labelledby="shop-title">
<header class="sec-head"><h2 id="shop-title" class="sec-title">Printables from The Setup Edit.</h2>
<p class="sec-dek">Two small things we made, sold as instant downloads through Payhip. The cable checklist above is free.</p></header>
<div class="prods">{prods}</div>
</section>

<section id="about" class="wrap sec sec-rule about" aria-labelledby="about-title">
<h2 id="about-title" class="about-lede">The Setup Edit is a small, independent guide to desks and home offices.</h2>
<div class="about-body"><p>Every pick is chosen for its design, its reviews and how well it fits the setup around it. Picks come from research, not hands-on testing: I compare the options, read the specs and the reviews, and include the ones that suit each desk.</p>
<p>Amazon links are affiliate links, which is how the site pays for itself. As an Amazon Associate I earn from qualifying purchases.</p>
<a class="go" href="disclosure.html">About &amp; disclosure</a></div>
</section>"""
    schema = [
        {"@context": "https://schema.org", "@type": "WebSite", "name": SITE_NAME, "url": BASE_URL,
         "description": "Curated desk setups, home office ideas and trading desk guides."},
        {"@context": "https://schema.org", "@type": "Organization", "name": SITE_NAME, "url": BASE_URL,
         "logo": BASE_URL + "img/web/icon-512.png"},
    ]
    (OUT / "index.html").write_text(page("The Setup Edit | Desk Setups, Home Office Ideas & Trading Desks",
        "Curated desk setups, home office ideas and trading desk guides, with a short note on why every item is there and a link to shop it.",
        body, preload=preload_tag("hero.jpg", "", hero_sizes), dock_html=checklist_dock(), schema=schema), encoding="utf-8")


# ---- Setup pages -------------------------------------------------------------------------
def build_setups():
    for s in SETUPS:
        n = len(s["items"])
        index = "".join(f'<li><a href="#item-{k:02d}">{esc(name)}</a></li>' for k, (name, _, _, _) in enumerate(s["items"], 1))
        cards = []
        for k, (name, model, asin, why) in enumerate(s["items"], 1):
            lead = k == 1
            tags = (f'<span class="tag tag-clay">Start here</span>' if lead else "") + f'<span class="tag">{ROLE.get(asin, "Pick")}</span>'
            note = f'<p class="start-note">{esc(s["start"])}</p>' if lead else ""
            cards.append(f"""<li class="pcard{' lead' if lead else ''}" id="item-{k:02d}"><div><div class="pcard-top">{tags}</div>
<h3 class="pcard-name">{esc(name)}</h3><p class="pcard-model">{esc(model)}</p><p class="pcard-why">{esc(why)}</p>{note}</div>
{amazon_btn(asin, name, 'btn btn-light' if lead else 'btn')}</li>""")
        rel = [a for a in ARTICLES_BY_DATE if s["slug"] in a["setups"]][:4]
        rel_html = "".join(f"""<a class="rcard" href="../guides/{a['slug']}.html"><span class="media">{pic(a['img'], '../', IMG_ALT[a['img']], '(min-width: 1000px) 28vw, (min-width: 700px) 45vw, 100vw')}</span>
<span class="meta">{esc(a['eyebrow'])}, {reading_time(a)} min read</span><span class="rcard-title"><span class="ul">{esc(a['title'])}</span></span></a>""" for a in rel)
        others = [o for o in SETUPS if o is not s]
        more = "".join(f"""<li><a href="{o['slug']}.html"><span class="media">{thumb(o['img'], '../', IMG_ALT[o['img']], 96)}</span>
<span><span class="srow-title"><span class="ul">{esc(o['title'])}</span></span><span class="meta">{picks_label(o)}</span></span></a></li>""" for o in others)
        crumbs, bc = breadcrumbs([("Home", "", "../index.html"), ("Setups", "index.html#setups", "../index.html#setups"),
                                  (s["title"], f"setups/{s['slug']}.html", None)])
        item_list = {"@context": "https://schema.org", "@type": "ItemList", "name": s["title"], "description": s["meta"],
                     "numberOfItems": n, "itemListElement": [
                         {"@type": "ListItem", "position": k, "name": f"{name} ({model})", "url": amz(asin)}
                         for k, (name, model, asin, _) in enumerate(s["items"], 1)]}
        body = f"""<section class="wrap ph" aria-labelledby="page-title">{crumbs}
<div class="ph-grid"><h1 id="page-title" class="ph-title">{esc(s['title'])}</h1>
<div class="ph-aside"><p class="ph-dek">{esc(s['blurb'])}</p><a class="btn" href="#picks">Shop the list<span class="vh"> of {n} picks</span></a>{disclosure_note()}</div></div>
</section>
<figure class="bleed" data-dock-start>{pic(s['img'], '../', IMG_ALT[s['img']], '100vw', eager=True)}
<figcaption class="wrap caption"><span>Products shown in photos may differ from the linked items.</span><span>{credit(s['img'])}</span></figcaption></figure>
<section class="wrap sintro" aria-labelledby="intro-title"><h2 id="intro-title">How this desk works</h2>
<div class="sintro-main"><div class="sintro-body">{s['intro']}</div><p class="good"><strong>Good for:</strong> {esc(s['good_for'])}</p></div></section>
<section class="wrap picks" id="picks" aria-labelledby="picks-title">
<nav class="pindex" aria-label="Picks in this setup"><p class="meta">The list, {n} picks</p><ol data-spy>{index}</ol></nav>
<div class="plist-wrap"><header class="plist-head"><h2 id="picks-title">The list</h2>
<p class="meta">Research-based picks, not hands-on tested. Links go to Amazon, and as an Amazon Associate I earn from qualifying purchases.</p></header>
<ol class="plist">{''.join(cards)}</ol>
<div class="plist-foot">{checklist_promo('../')}</div></div>
</section>
<div class="wrap after after-2">
<section aria-labelledby="rel-title"><h2 class="block-title" id="rel-title">Read the guides</h2><div class="rgrid">{rel_html}</div></section>
<section aria-labelledby="more-title"><h2 class="block-title" id="more-title">More setups</h2><ul class="srows">{more}</ul></section>
</div>"""
        (OUT / "setups" / f"{s['slug']}.html").write_text(
            page(f"{s['title']}: {n} Picks, Item by Item | {SITE_NAME}", s["meta"], body, root="../", og=f"img/{s['img']}",
                 path=f"setups/{s['slug']}.html", current="setups", preload=preload_tag(s["img"], "../", "100vw"),
                 dock_html=checklist_dock(), schema=[bc, item_list]), encoding="utf-8")


# ---- Guides --------------------------------------------------------------------------------
def build_guides():
    (OUT / "guides").mkdir(exist_ok=True)
    for a in ARTICLES:
        toc = []

        def h2_id(m):
            text = m.group(1)
            hid = slugify(text)
            toc.append((hid, re.sub(r"<[^>]+>", "", text)))
            return f'<h2 id="{hid}">{text}</h2>'
        body_html = re.sub(r"<h2>(.*?)</h2>", h2_id, a["body"])
        asins = list(dict.fromkeys(re.findall(r"\[\[([0-9A-Z]{10})\]\]", body_html)))
        body_html = re.sub(r"\[\[([0-9A-Z]{10})\]\]", product_card, body_html)
        main_setup = setup_by(a["setups"][0])
        rows = "".join(f"""<li><span class="quick-name">{esc(PRODUCTS[x][0])}<span class="quick-model">{esc(PRODUCTS[x][1])}</span></span>
<a class="q" href="{amz(x)}" {AMZ_REL}>View on Amazon<span class="vh">: {esc(PRODUCTS[x][0])}</span></a></li>""" for x in asins)
        quick = f"""<aside class="quick" aria-labelledby="quick-title"><p class="quick-title" id="quick-title">The picks in this guide</p>
<p class="quick-sub">Short on time? Here is everything recommended below. The full list is in <a href="../setups/{main_setup['slug']}.html">{esc(main_setup['title'])}</a>.</p>
<ol>{rows}</ol></aside>"""
        body_html = body_html.replace("</p>", "</p>" + quick, 1)
        toc += [("faq", "Questions, answered"), ("shop-setups", "Shop the setups")]
        toc_html = "".join(f'<li><a href="#{hid}">{esc(t)}</a></li>' for hid, t in toc)
        faq = "".join(f'<details><summary><span>{esc(q)}</span><i aria-hidden="true"></i></summary><p>{esc(ans)}</p></details>'
                      for q, ans in a["faq"])
        faq_ld = {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
            {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": ans}} for q, ans in a["faq"]]}
        art_ld = {"@context": "https://schema.org", "@type": "Article", "headline": a["title"], "description": a["desc"],
                  "image": BASE_URL + "img/" + a["img"], "datePublished": a["date"], "dateModified": a["date"],
                  "author": {"@type": "Organization", "name": SITE_NAME, "url": BASE_URL},
                  "publisher": {"@type": "Organization", "name": SITE_NAME, "logo": {"@type": "ImageObject", "url": BASE_URL + "img/web/icon-512.png"}},
                  "mainEntityOfPage": BASE_URL + f"guides/{a['slug']}.html"}
        crumbs, bc = breadcrumbs([("Home", "", "../index.html"), ("Guides", "index.html#guides", "../index.html#guides"),
                                  (short_title(a), f"guides/{a['slug']}.html", None)])
        setup_cards = "".join(f"""<a class="rcard" href="../setups/{sl}.html"><span class="media">{pic(setup_by(sl)['img'], '../', IMG_ALT[setup_by(sl)['img']], '(min-width: 700px) 30vw, 100vw')}</span>
<span class="meta">{picks_label(setup_by(sl))}</span><span class="rcard-title"><span class="ul">{esc(setup_by(sl)['title'])}</span></span></a>""" for sl in a["setups"])
        near = [b for b in ARTICLES_BY_DATE if b is not a and set(b["setups"]) & set(a["setups"])]
        near += [b for b in ARTICLES_BY_DATE if b is not a and b not in near]
        keep = "".join(f"""<a class="rcard" href="{b['slug']}.html"><span class="media">{pic(b['img'], '../', IMG_ALT[b['img']], '(min-width: 700px) 30vw, 100vw')}</span>
<span class="meta">{esc(b['eyebrow'])}, {reading_time(b)} min read</span><span class="rcard-title"><span class="ul">{esc(b['title'])}</span></span></a>""" for b in near[:2])
        toc_list = f'<ol data-spy>{toc_html}</ol>'
        body = f"""<article>
<header class="wrap ph guide-head">{crumbs}
<h1 id="page-title" class="ph-title guide-title">{esc(a['title'])}</h1>
<div class="gh-row"><p class="gh-dek">{esc(a['desc'])}</p>
<div class="gh-meta"><p class="meta"><time datetime="{a['date']}">{nice_date(a['date'])}</time>, {reading_time(a)} min read</p>{disclosure_note()}</div></div>
</header>
<figure class="wrap gfig" data-dock-start><span class="media">{pic(a['img'], '../', IMG_ALT[a['img']], '(min-width: 1360px) 1250px, 100vw', eager=True)}</span>
<figcaption class="caption"><span>{credit(a['img'])}</span><span>Products shown in photos may differ from the linked items.</span></figcaption></figure>
<div class="wrap article">
<nav class="toc" aria-label="In this guide"><p class="meta">In this guide</p>{toc_list}</nav>
<div class="prose-col">
<details class="toc-m"><summary>In this guide</summary><ol>{toc_html}</ol></details>
<div class="prose">{body_html}
<section class="faq" id="faq" aria-labelledby="faq-title"><h2 id="faq-title">Questions, answered</h2>{faq}</section>
{checklist_promo('../', hide=False)}
<section id="shop-setups" aria-labelledby="shop-setups-title" data-dock-hide><h2 id="shop-setups-title">Shop the setups</h2><div class="rgrid">{setup_cards}</div></section>
<section aria-labelledby="keep-title"><h2 class="block-title" id="keep-title">Keep reading</h2><div class="rgrid">{keep}</div></section>
{mini_prods('../')}
<p class="back"><a class="go" href="../index.html#guides">All guides</a></p>
</div></div></div></article>"""
        g_dock = dock(esc(main_setup["title"]), f"Every pick from this guide, {picks_label(main_setup)}",
                      f"../setups/{main_setup['slug']}.html", "Shop the list", external=False)
        (OUT / "guides" / f"{a['slug']}.html").write_text(
            page(f"{a['title']} | {SITE_NAME}", a["desc"], body, root="../", og=f"img/{a['img']}",
                 path=f"guides/{a['slug']}.html", current="guides",
                 preload=preload_tag(a["img"], "../", "(min-width: 1360px) 1250px, 100vw"),
                 dock_html=g_dock, schema=[bc, art_ld, faq_ld]), encoding="utf-8")


# ---- About / disclosure and 404 -------------------------------------------------------------------
def build_disclosure():
    crumbs, bc = breadcrumbs([("Home", "", "index.html"), ("About & disclosure", "disclosure.html", None)])
    body = f"""<section class="wrap ph" aria-labelledby="page-title">{crumbs}
<div class="ph-grid"><h1 id="page-title" class="ph-title">About the edit &amp; disclosure</h1></div></section>
<div class="wrap article"><div class="prose-col"><div class="prose prose-plain">
<p>The Setup Edit is a small, independent guide to desk setups, home offices and trading desks. Picks are chosen for their design, their reviews and how well they fit each setup. Picks come from research rather than hands-on testing: I compare the options and include the ones that suit each desk.</p>
<h2 id="affiliate-disclosure">Affiliate disclosure</h2>
<p>{esc(DISCLOSURE)}</p><p>Product picks are chosen for quality, reviews and how well they fit each setup. Prices and availability change, so always check the current details on Amazon before buying.</p>
<h2 id="shop">The shop</h2>
<p>The Desk Cable Checklist is free. The Clean Desk Guide and the Minimalist Wallpaper Pack are digital products made by The Setup Edit and sold through Payhip, which handles payment and delivery.</p>
{mini_prods('', heading=False)}
<h2 id="privacy">Privacy</h2><p>This site doesn't use its own cookies or collect personal information. Amazon may set cookies when you click an affiliate link, as described in Amazon's own privacy notice. Payhip handles any downloads under its own privacy policy.</p>
<p class="back"><a class="go" href="index.html">Back to the front page</a></p>
</div></div></div>"""
    (OUT / "disclosure.html").write_text(page(f"About & Disclosure | {SITE_NAME}",
        "About The Setup Edit: how picks are chosen (research, not hands-on testing), the Amazon affiliate disclosure, the shop and privacy.",
        body, path="disclosure.html", current="about", schema=[bc]), encoding="utf-8")


def build_404():
    root = "/thesetupedit/"  # 404 can be served at any path, so links are root-relative
    links = "".join(f'<li><a href="{root}setups/{s["slug"]}.html"><span class="ul">{esc(s["title"])}</span></a></li>' for s in SETUPS)
    body = f"""<section class="wrap ph nf" aria-labelledby="page-title">
<div class="ph-grid"><h1 id="page-title" class="ph-title">This page could not be found.</h1>
<div class="ph-aside"><p class="ph-dek">The link may be old, or the page has moved. Try one of the setups, or start again from the front page.</p>
<a class="btn" href="{root}index.html">Go to the front page</a></div></div>
<ul class="nf-list">{links}</ul></section>"""
    (OUT / "404.html").write_text(page(f"Page not found | {SITE_NAME}", "This page could not be found.", body, root=root),
                                  encoding="utf-8")


def build_sitemap():
    today = datetime.date.today().isoformat()
    paths = [("", today)] + [(f"setups/{s['slug']}.html", today) for s in SETUPS] + \
            [(f"guides/{a['slug']}.html", a["date"]) for a in ARTICLES_BY_DATE] + [("disclosure.html", today)]
    urls = "".join(f"<url><loc>{BASE_URL}{p}</loc><lastmod>{d}</lastmod></url>\n" for p, d in paths)
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
