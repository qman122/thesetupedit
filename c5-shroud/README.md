# C5 sleepy-eye pod carrier and bezel (v9)

For a 2000 C5 Corvette with the headlight door stops already fitted, holding three
3.0 × 1.8 in dual-lens LED pods per side. Like the KnightDriveTV kit, each side is one
carrier that bolts to the stock headlight mounting points (the fender-side arm and the
hood-side aiming pad), plus a one-piece bezel: a thin shell that wraps round the lights
and screws to the headlight door's side flanges where the stock bezel does. The geometry is an original design; see `../notes/c5-sleepy-eye-video.md` for the install video notes it follows.

![assembly preview](preview/assembly.png)
![mounting tabs from behind](preview/rear.png)

Assembly diagrams: `diagrams/exploded.png`, `diagrams/front.png`, `diagrams/rear.png`, `diagrams/side.png`.
Step size options (6, 9, 12 and 15 mm) side by side: `diagrams/step_options.png`.
What to measure on the stock bezel and headlight: `diagrams/measure_stock_bezel.png`.
How the pods sit on the bracket (carrier), with the bezel hidden: `diagrams/pods_on_bracket.png`.
The bezel on its own, in matte black: `diagrams/shell.png`. How each ear fits the imprint the stock
ear leaves on the door: `diagrams/ear_imprint.png` and `diagrams/ears_on_door.png`. On the door from six sides: `diagrams/on_door.png`.
The bezel against the owner's model of the headlight doors: `diagrams/cover_fit.png`, and
rendered with the door on: `diagrams/with_door.png`.

## Measurements used

Taken with a tape on the car. The owner says they're approximate, so every mounting hole
is a short slot, sized snug (6.3 mm) on an M6 bolt so the bolt stays put while you line up.

| | Measurement | Value | Adjustment built in |
|---|---|---|---|
| A | Fender arm, hole 1 to hole 4 | 1.7 in (43.2 mm) | — |
| H | Aiming pad, upper hole to lower hole | 0.8 in measured; 19.0 mm after the test tab showed it a bit wide | — |
| B | Across the car, pad upper hole to arm hole 4 | 8.75 in (222.3 mm) | arm slots ±3.7 mm side to side |
| D | Pad upper hole above arm hole 4 | 0.76 in (19.3 mm) | pad slots ±1.8 mm up and down |
| C | Pad face vs arm face, front to back | unknown | printed spacer washers, 2 / 4 / 6 mm |
| F | Front opening width | 11 in (279.4 mm) | bezel is 269.4 mm, 5 mm clear each side |
| — | Bezel windows | pod face + 2.0 mm left/right and + 1.6 mm top/bottom, centred 0.3 in up for the bracket lift | matches the 1-notch test frame, which fit on the car |
| — | Pods | 3.0 × 1.8 in face, 1.8 in deep, 2.1 in tall with the bracket (maker's drawing) | pod slots: 16 mm forward, 10 mm back |
| — | Pod stud | about 8 mm (5/16 in), in 8.6 mm floor slots | — |
| — | Mounting bolts | M6 × 1.0, 10 mm flange nuts | — |

**Still estimated:**
- How far back the mounting wall sits behind the pod faces (95 mm).
- The pod height relative to the holes (arm hole 4 is 14 mm above the carrier floor).
- The bezel's outside shape and where its top sits against the cover: see "The bezel"
  below. `diagrams/measure_stock_bezel.png` shows the seven numbers that pin these down
  (S1 to S5 on the stock bezel, V and D on the stock headlight with the bezel screwed back on).

The long pod slots and the bezel's slotted tabs take up the fore-aft part of that.

## The curve

Like the KnightDriveTV Gen 2 bracket, the pods follow the curve of the headlight opening
with a staircase, not by turning. All three face straight ahead, and each pocket sits a
little further back than the one beside it:

| Pod | Set back from the hood-side pod |
|---|---|
| Hood side | 0 mm |
| Middle | 12 mm |
| Fender side | 24 mm |

The step is `pod_step` in `generate.py`. It's estimated from photos, so change it if the
pods don't line up with the curve on the car. Steps from 6 to 12 mm pass every check.
At 15 mm the fender-side pod has only 3 mm of wiring room if you slide it all the way back.
At 18 mm it hits the arm's nuts.

- **Carrier:** a stepped beam under the pods with a pocket for each pod's bracket foot. Each
  pod still slides straight fore and aft in its slot (16 mm forward, 10 mm back). Knees at
  each end run back to the arm and pad tabs.
- **Bezel:** one continuous front sweeps back along the same line as the pods (see below).

## The bezel

One continuous shell, 3 mm thick everywhere and open at the back, modelled on the owner's
reference photo. It's modelled in one piece and split in two for printing (see below).

- **From above it's a U.**
  - The front follows the nose's curve, which matches the door's front edge to within
    1.4 mm.
  - At each end it turns back round a 30 mm radius (`corner_r`) into a flat side.
- **Nothing shows past the door from above.** The whole bezel is clipped to the door's outline
  seen from above, 0.2 mm inside it (`outline_gap`), front included.
- **Each side is one wall, from the corner back to the tip.** No separate ear and no seam.
  - Its outside follows the door's outline from above, just inside it.
  - Where the door's side flange and screw tabs come out toward it, the inside of the wall
    is pocketed 0.8 mm clear of them (`ear_gap`), leaving at least 1 mm (`min_wall`).
  - `cover_scan.py` measures the outline, the flange (on a 1 mm grid) and the door's edge
    from the owner's model of the doors and saves them in `cover_sides.json`.
- **The top edge follows the door's edge all the way round.** From the start of each corner
  back to the tip, the top runs 0.05 mm under the door's edge (`rim_gap`), so nothing stands
  above the door and there's no gap under it.
  - Round the corners the door's lip sits up to 15 mm inside the wall. A 2.4 mm shelf
    (`shelf_t`) runs along the inside of the wall's top, just under the lip, to 2 mm past it
    (`shelf_under`), so you can't see in under the door's edge. It narrows wherever the
    door's flange hangs down beside the wall.
  - The door's edge is the lowest line of its outer skin, measured round the corner and
    along each side.
  - It blends in from the front over the first 25 mm of each corner, so there's no step
    where the corner starts.
- **The tip is where the door's edge comes lowest** at the back of each side. The bottom edge
  runs level round the corner, then in a straight line back to the tip, following the line
  of the door's bottom edge.
- **Screw holes:**
  - There's a 6.5 mm hole at every hole in the flange, with a boss behind it reaching the
    flange. The stock ear screws go through the side and the flange into the headlight, as
    in the owner's photo of a stock headlight.
  - Hood end: the front and rear round holes and the slot between them. Fender end: the
    slot and the round hole.
- **Three windows,** one rounded rectangle per pod with 15 mm corners (`window_r`).
  - The outer two run round into the corners.
  - The posts are what's left between the windows: 6 mm wide on the gaps between the
    pods, flaring into the floor and the blade.
  - They stand 4 mm back from the front edge (`post_setback`) so every lens still sees
    10° either side of straight ahead.
- **Below the windows:** just a rounded 7 mm lip (`lip_r`) rolling back into a shallow
  22 mm floor. No apron.
- **Top:** a flat 3 mm blade, 38 mm (1.5 in) deep, matching the stock bezel as measured (S4).
  - A raised bead runs along its front edge (`bead_r`). The door's lip closes down behind
    it.
  - The blade follows the lip's height (up to about 9 mm higher at the hood end).
  - It's trimmed wherever the door's underside comes lower (`door_clearance`, measured
    from the door model), so the door touches only the blade.
- **Clip tongue:** a flat tongue, tapered from 40 mm and slotted along its middle, runs
  back from the middle of the blade.
  - The clip's cross bar drops into a groove across it.
  - A chamfered tooth behind the groove catches the bar, and the clip's legs sit either
    side of it.
- **No screws into the carrier.** The shell hangs from the door alone: the tongue on the
  clip, and the ears screwed through the door's flanges, like the stock bezel.
- **Printing:**
  - It's split through the middle of the hood-side post into a hood piece (about
    123 × 226 mm) and a fender piece (about 218 × 197 mm). Both fit the A1's 256 mm bed.
  - Two 3 mm dowels, 12 mm long, cross the cut: one where the post meets the floor, one
    where it meets the blade. Glue the joint as well.
  - Each piece prints upside down on its blade, tipped to lie as flat as it goes. The bead
    and the lip-following top mean it needs supports under the blade.

**Before printing the bezel,** print the two halves of `stl/fit_test_blade_driver_*.stl`
(the blade, bead and tongue only) and tape them together. Slide it in under the front of
the headlight door and check:
- the tongue clicks onto the clip,
- the door's lip sits down on the blade at both ends, just behind the bead.

## What changed in v9: one thin shell, like the owner's reference photo

The owner's reference photo is now the target.
- **Before:** a curved face panel with a letterbox slot and rim, inside masks and set-back
  round posts, separate ears, and screws into the carrier.
- **Now:** one thin U-shaped shell:
  - 30 mm corners into flat tapering ears,
  - three rounded windows whose posts flare into the floor and blade,
  - a small lip into a shallow floor,
  - a flat blade with a bead and a tapered slotted tongue.

Details are in "The bezel" above.

**What moved:**
- **The door's front edge sits 2.5 mm behind the bezel's front** (`cover_edge_n`), and the
  bezel is clipped flush under the door's outline, so none of the front shows from above.
  - The clip groove and the flange holes moved with it; `cover_scan.py` re-measured them.
- **The bezel no longer screws to the carrier.**
  - The wing screws and the tabs under the front are gone. The carrier's bosses for them
    are still on the carrier, unused.
  - The carrier and pods haven't moved.
- **The inside wings, masks, rolled rim and access hole are gone.** The hood-end access
  hole isn't in the photo.
- **The ears fill the stock ear's imprint on the door.** They're shaped to the recess below
  the flange's raised band (see "The bezel"), so they fit in the way the stock ear does.
- **The window gap round each pod is open.** You can see past the pods' tops into the
  headlight at the top of each window (there are no masks).

## What changed in v8: marked up by the owner

- **Flat bottom:** everything below a straight line just under the light slot is cut off.
  - The sagging chin is gone: `bottom_sag` is 0.
  - The bottom is level at z = -18 at both ends (`bezel_h_*` = 79.6). Before, it was
    -38 at the hood end, -16 at the fender end, and 8 mm lower again in the middle.
  - -18 is as high as it can go: the carrier's lip comes down to -13 and the bezel's
    screw tabs under it to -16, so it still hides them.
  - The lower corners are 12 mm (`corner_r`) and the roll-back at the bottom is 8 mm
    (`face_tuck`).
- **Ears fill the gap:**
  - Each ear runs up to the door's painted edge, back past the rear screw, and down to
    the same flat bottom.
  - Its back edge rises in a straight line to the rear screw, as marked.

## What changed in v7: fitted to the headlight doors

The owner sent a full model of the C5 headlight doors (`Covers.stl`, the pair, about 190 MB,
not kept here). `cover_scan.py` measures it and puts the door on the bezel; run it with the
file's path.

- **The clip under the door** is a U-shaped rib hanging about 9 mm under the skin. It is a
  cross bar 3.5 mm thick with a short leg running back from each end, 26 mm apart inside.
  It's about 61 mm behind the front edge, a little toward the hood from the middle. The bar
  runs about 20° off square to the edge, nearer the edge at the fender end. The v6 fork
  stopped about 8 mm short of it, so it never engaged.
- **New clip tongue:** the blade carries on back under the clip as a 23 mm tongue that fits
  between the legs. A groove across it, skewed to match the bar, takes the bar's bottom
  (it hangs 1.2 mm below the lip). Behind the groove a chamfered tooth ramps under the bar
  as the blade slides in, so it clicks in. It comes out the stock way: tip the bezel down
  and pull forward. The tongue is flush with the blade, so nothing sticks up.
- **The top follows the door's lip.** The lip is about level over the hood half and drops
  about 9 mm toward the fender, so a level blade would have hit it on the fender half.
  - The blade and everything above the pod windows now rise to meet it: up to 9 mm at the
    hood end, nothing at the fender end.
  - The slot gets that much taller toward the hood, with the black mask filling in above
    the pods, like the stock bezel, which is taller at the hood end.
  - The pods, windows and screws don't move.
  - `lip_follow` (0 = level top) and `lip_roll` (extra tilt, degrees) adjust it.
- **The front curve already matched.** Seen from above, the door's front edge follows the
  bezel's 12 mm bow to within 1.4 mm across the middle 220 mm. At the very corners the
  door rounds back 2–4 mm further than the bezel.
- **Printing:** the top is no longer flat, so the bezel is tipped to lay the blade as flat
  as it goes. The blade ends then sit up to about 4 mm off the bed; turn on supports (tree
  supports are fine; that face hides under the door).
- **Ears where the stock ones go:** outside ears screwed through the door's side-flange
  holes, like the stock ear in the owner's photo (above).
  - The flange holes are 75 and 210 mm (hood end) and 78 and 115 mm (fender end) behind the
    bezel front.
  - The door is now centred across the bezel on these two flanges: they bolt to the
    headlight, which is centred on the opening. It moved 4.5 mm toward the hood from the
    first placement. Their insides are then 139.3 mm either side of centre, right at the
    edge of the 279.4 mm opening.
  - The front of the door's fender-side flange comes down over the fender wing's top.
    The wing is trimmed up to 2.5 mm to clear it (`door_corner_cut`).
- **Fixed:** the blade test print was trimming up to 6 mm off the front of the curved nose.
- **New checks (48 now):**
  - the lip sits on the blade all the way across,
  - the bar sits in the groove,
  - pulled forward, the bar catches on the tooth,
  - the tongue fits between the legs,
  - each ear is clear of the bezel, carrier and pods, with a screw hole on every flange hole.
- **Still an assumption:** how the door sits relative to the bezel. The door is placed with
  its lip on the blade at the clip and its front edge 1 mm behind the blade's nose. Its tilt
  is taken as it lies in the file. The blade test print on the car checks exactly this; if
  one end gaps or rocks, change `lip_roll`.

## What changed in v6

- **The top slides into the headlight cover like the stock bezel,** with the same flat top
  blade and forked tab onto the cover's clip. This replaces the foam strip.
- **The bezel is built like KnightDriveTV's:** a curved shell face with a letterbox slot
  cut through it. It has a rolled rim, a door-shaped outline with big lower corners, a
  lens-only mask, and root-flared posts, instead of a box with a front face.
- **To follow the body exactly, the face needs a scan of the nose.** A LiDAR iPhone with
  Polycam, exported as STL or OBJ, is enough. Profiles from a contour gauge at 3–4 places
  across the headlight pocket also work.
- **The outside follows the stock and KnightDriveTV shape.** It's taller at the hood end,
  with a rolled lip along the bottom and up both ends, so it goes all the way down.
- **New quick print, `fit_test_blade_*.stl`:** the top blade and fork only, to check the
  slide-in before the big print.
- **New sheet, `diagrams/measure_stock_bezel.png`:** seven numbers off the stock bezel and
  headlight that replace the estimates.
- **The wings are full side walls,** running back past the pods to just in front of the
  arm and the pad, like the stock and KnightDriveTV ears.
- The unused split-plate code is gone from `generate.py`.

## What changed in v5

- **The bezel is restyled after the KnightDriveTV TripLED bezel,** with a swept front,
  tunnels, a rounded lower lip, a top rail and side wings (see above). It replaces the
  boxy wrap.
- **The carrier's two rear posts for the bezel are gone.** Two side bosses for the wing
  screws replace them.
- The mockup now mirrors the pods for the driver side. Before, the stepped pods were
  drawn the wrong way round on that side; the STL files were right.

## What changed in v4

- **The pods are stepped instead of angled.** All three face straight ahead, with each pod
  12 mm behind its neighbour, like the KnightDriveTV Gen 2 bracket.
- **The windows match the 1-notch test frame:** 2.0 mm of gap each side and 1.6 mm top and bottom.
- The mounting tabs and hole spacing are unchanged; the mount test fit.

## What changed in v3

- **The back is two small tabs instead of a full wall.** On the first mount test, the
  plastic around the holes hit parts of the car, so the bolts couldn't line up. Each tab
  now leaves only about 6 mm of plastic around its slots, and the middle is open.
  - The pad tab stops below the square aim adjuster.
  - Nothing near the arm reaches the pivot bolt below hole 4.
- **The bolt holes are snug and the slots shorter.** 6.3 mm for M6 bolts; the spacing
  checked out.
- **The shroud windows are a little bigger:** 1.3 mm of gap around each pod face instead of 0.8.

## Checks

`python3 check.py` runs 52 checks. They all pass:

- The hole spacing matches A, H, B and D.
- Every slot is open, with solid material past its ends.
- A 15 mm flange nut at either end of every slot clears the carrier and the pods.
- The pods clear the carrier across their whole slot travel, and there's always at least
  7 mm behind them for the wiring.
- The pods clear the bezel, which clears the carrier.
- Every lens has a clear view 10° either side of straight ahead.
- The door's lip sits on the top blade all the way across, the clip's cross bar sits in the
  tongue's groove and catches on its tooth, and the tongue fits between the clip's legs.
- The bezel is one piece, with a screw hole on every hole in the door's side flanges
  (`cover_scan.py` also checks the bezel against the door itself).
- The two print pieces are each one solid and fit the 256 mm bed, and the dowel holes go
  into both.
- The carrier stays clear of the arm's pivot bolt and the pad's square adjuster, and the
  middle of the back is open.
- The driver part is a true mirror of the passenger part.
- Every STL is one watertight solid lying on the bed.

## Print order

1. `stl/fit_test_window.stl` (about 15 minutes).
   Three frames, 1-3 notches: 2.0/1.6, 2.3/1.3 and 2.6/1.0 mm of gap (sides/top-bottom).
   The bezel uses the 1-notch size, which fit on the car. Already done.
2. `stl/fit_test_mount_driver.stl` (about 20 minutes, two small flat tabs). Bolt the taller
   tab to the arm (holes 1 and 4) and the shorter one to the aiming pad (both holes).
   The bolts should go through snugly without forcing. Already done: the spacing fit.
3. `stl/fit_test_blade_driver_hood_piece.stl` and `..._fender_piece.stl` (about 40 minutes;
   supports on). Tape them together and slide them in under the front of the headlight
   door. Check the tongue clicks onto the clip and the lip sits down behind the bead at
   both ends.
4. `stl/carrier_driver.stl`, then `stl/bezel_driver_hood_piece.stl` and
   `stl/bezel_driver_fender_piece.stl`, then the passenger set.
   - The bezel pieces print upside down on the blade; turn supports on.
   - Join them with two 3 mm × 12 mm dowel pins and glue.
   - `bezel_*_one_piece.stl` is the whole bezel for reference; it's too wide for the A1.
   - The carrier is 263 mm wide, still over the A1's bed.
5. `stl/spacer_washers.stl`: only if a tab doesn't sit flat against the arm or the pad.

**Material:** ASA or ABS is best; PETG works. Don't use PLA, which softens in a hot engine
bay. Use 4 walls, 40% gyroid infill, and 6 top and bottom layers.

## Hardware (per side)

- 4 × M6 × 1.0 × 20 mm bolts and 10 mm flange nuts (the stock headlight bolts work), with a flat
  washer under each nut so it doesn't dig into the plastic. The nut can't pull through: the slots
  are 6.3 mm wide and an M6 nut is 10 mm across.
- The pods' own studs and nuts, through the floor slots. Under each slot, two rails hold
  the nut (M8 or 5/16 in) so it slides with the stud but can't turn, and each pod
  tightens from above with one hand, as in the owner's bracket sketch.
- The stock bezel ear screws, through each ear and the door's flange into the headlight, as
  stock (2 at the hood end in the photo; use the fender end's as found)
- 2 × 3 mm × 12 mm dowel pins, and glue, for the two bezel pieces

## Fitting

1. With the headlight door up, hold the carrier in front of the arm and the pad. Push the bolts
   through from behind the arm (holes 1 and 4) and the pad (both holes), then through the
   carrier's slots, and add the flange nuts on the front. Leave them finger tight.
2. If there's a gap at the arm or the pad, fill it with spacer washers.
3. Bolt the pods on through the floor slots. Slide them forward or back so the lenses sit
   where you want them in the opening, then tighten.
4. Slide the bezel's top blade in under the front of the headlight door until the tongue
   clicks onto the clip, like the stock bezel. Then hold each ear against the door's side
   flange and put the stock ear screws back in through the ear and the flange.
5. Cycle the lights slowly by hand with the motor knob and check nothing touches the door
   or the body, then tighten everything.
6. Aim the lights with the stock adjusters.

## Changing the design

Every dimension is a setting at the top of `generate.py`. Change a number, run
`python3 generate.py`, then `python3 check.py`. It needs the `manifold3d`, `trimesh`,
`numpy` and `matplotlib` Python packages.
