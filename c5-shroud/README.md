# C5 sleepy-eye pod carrier and bezel (v7)

For a 2000 C5 Corvette with the headlight door stops already fitted, holding three
3.0 × 1.8 in dual-lens LED pods per side. Like the KnightDriveTV kit, each side is one
carrier that bolts to the stock headlight mounting points (the fender-side arm and the
hood-side aiming pad), plus a front bezel with the outside shape of the stock C5 bezel,
which the KnightDriveTV TripLED bezel also copies. The geometry is an original design; see `../notes/c5-sleepy-eye-video.md` for the install video notes it follows.

![assembly preview](preview/assembly.png)
![mounting tabs from behind](preview/rear.png)

Assembly diagrams: `diagrams/exploded.png`, `diagrams/front.png`, `diagrams/rear.png`, `diagrams/side.png`.
Step size options (6, 9, 12 and 15 mm) side by side: `diagrams/step_options.png`.
What to measure on the stock bezel and headlight: `diagrams/measure_stock_bezel.png`.
How the pods sit on the bracket (carrier), with the bezel hidden: `diagrams/pods_on_bracket.png`.
How the bezel attaches (tongue onto the door's clip, 4 screws): `diagrams/bezel_attach.png`.
The bezel against the owner's model of the headlight doors: `diagrams/cover_fit.png`.

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

The bezel copies the outside of the stock C5 bezel (GM 10435411 left, 10435412 right).
The KnightDriveTV TripLED bezel copies it too, then opens the front up for three lights. The
stock bezel is held three ways, and so is this one:

- **Top blade into the headlight cover.** The stock bezel has a flat top that slides in
  under the front edge of the headlight cover. A forked tab on it slides onto a clip on the
  underside of the cover. Corvette Central's how-to describes it: "the tab on the top of
  the bezel that slides onto a clip on the underside of the headlight cover". The
  KnightDriveTV install video shows it too: at 13:02, "Remove bezel by rotating downward and
  forward, while spreading the outer ears". This bezel has the same 30 mm top blade, with
  a tongue behind its middle that clicks onto the clip (`blade_depth`, `clip_*`, `tongue_*`
  in `generate.py`). Both are fitted to the owner's model of the doors (see below).
- **Ears (wings) at both ends.** Like the stock and KnightDriveTV ears, they are full
  side walls. Each runs from the front back past the pods to 5 mm in front of the arm and
  the pad, and from the top blade down over the carrier, so the sides are covered too.
  - The stock ears screw to the stock headlight; here each wing takes one M4 × 12 screw
    into a boss on the carrier, in a slot so the bezel can sit further forward.
  - The hood-end wing has a 28 mm hole for reaching the aiming adjuster, like the stock
    ear's. Its position is an estimate (`access_hole_yz`).
- **Two tabs under the front.** These are this design's own, not stock. Each takes an
  M4 × 16 screw up into a boss under the carrier floor.

**Shape:**
- **Built like KnightDriveTV's:** a curved 3 mm face with a letterbox slot cut through it,
  not a box with a front.
  - **Outline:** follows the stock bezel and the door. It is a rounded rectangle with
    28 mm lower corners sweeping up into the sides and 10 mm corners under the door.
    It's about 100 mm tall at the hood end and 78 mm at the fender end
    (`bezel_h_hood`, `bezel_h_fender`; estimates until the stock bezel is measured).
  - **Curve:**
    - The face bows 12 mm forward in the middle of its width.
    - Seen from the side, it swells 7 mm forward halfway down and rolls 12 mm back at its
      lower edge, like a chin.
    - The lower edge curves 8 mm down in the middle instead of running straight.
    - A 5 mm rolled edge runs right round the outside of the face.
    - Settings: `front_bow`, `face_belly`, `face_tuck`, `bottom_sag` and `edge_r`.
    - Following the body exactly needs profiles of the nose; see "What changed in v6".
  - **Slot:** about 5:1, lofted back to the pods through 13 sections that ease in. It is
    9 mm wider at the ends and 4 mm lower along the bottom at the front, so the ends wrap
    round. A 3 mm shell forms its walls. Its corners are 16 mm at the back and 25 mm at
    the front edge, so the ends are nearly round, like the reference scan. Its lower lip
    dips 5 mm in the middle in a slight smile (`slot_smile`).
  - **Rim:** a 6 mm rolled rim runs down each side and along the bottom of the slot. Its
    ends tuck into the top blade.
  - **Shadow line:** a 1.5 mm groove runs under the blade along the top of the slot.
  - **Mask:** a black plate just in front of each pod has one rounded window the size of
    the pod face. The window uses the 1-notch test frame's gap (2.0 mm each side, 1.6 mm
    top and bottom), which fit on the car. Thin walls join the masks where the pods step
    back, so the gaps between pods stay hidden.
  - **Posts:** one in front of each gap between pods, 9 mm wide and 13 mm front to back.
    They spread into the floor like roots (9 mm extra over 22 mm) and only just flare into
    the blade.
  - **Pods:** sit 14 mm deeper than they have to (`pod_recess`).
  - **Light the posts block** (checked by casting rays from each lens, seen from above at
    lens height):
    - Every lens is completely clear for at least 11° either side of straight ahead.
      `check.py` tests 10°.
    - The lens on the hood side of the middle and fender pods loses some light at wide
      angles toward the hood: about 18% at 20° and 27% at 30°.
  - **Not copied:** KnightDriveTV's fender end flares outward like a bell and their hood
    end runs into a long flat tongue. Both follow the pocket past the 279 mm opening, so
    they need the nose profiles. The side walls here stay straight, 5 mm inside the
    opening.

**Before printing the full bezel,** print `stl/fit_test_blade_driver.stl`. It's just the
top blade and clip tongue, 3.7 mm thick, following the door's lip. Slide it in under the
front of the headlight cover the way the stock bezel went, and check four things:
- the tongue clicks onto the clip (the clip's cross bar drops into the groove),
- the door's lip sits down on the blade at both ends, with no gap and no rocking,
- the front edge lines up with the cover,
- the ends sit inside the opening.

Then send the numbers on `diagrams/measure_stock_bezel.png`, and the outline and position
get set from them.

**Fit on the car:** it's 269 mm wide in the 279 mm opening. Cycle the door slowly by hand
and check the lip and wings don't touch anything as it goes down into the pocket.

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
- **Fixed:** the blade test print was trimming up to 6 mm off the front of the curved nose.
- **New checks (42 now):**
  - the lip sits on the blade all the way across,
  - the bar sits in the groove,
  - pulled forward, the bar catches on the tooth,
  - the tongue fits between the legs.
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

`python3 check.py` runs 42 checks. They all pass:

- The hole spacing matches A, H, B and D.
- Every slot is open, with solid material past its ends.
- A 15 mm flange nut at either end of every slot clears the carrier and the pods.
- The pods clear the carrier across their whole slot travel, and there's always at least
  7 mm behind them for the wiring.
- The pods clear the bezel, which clears the carrier.
- Every lens has a clear view 10° either side of straight ahead.
- The door's lip sits on the top blade all the way across, the clip's cross bar sits in the
  tongue's groove and catches on its tooth, and the tongue fits between the clip's legs.
- The bezel fits the opening.
- The carrier stays clear of the arm's pivot bolt and the pad's square adjuster, and the
  middle of the back is open.
- The driver part is a true mirror of the passenger part.
- Every STL is one watertight solid lying on the bed.

The small-bed split files were dropped: the stepped bezel doesn't split cleanly, and bed size isn't a concern for this build.

## Print order

1. `stl/fit_test_window.stl` (about 15 minutes).
   Three frames, 1-3 notches: 2.0/1.6, 2.3/1.3 and 2.6/1.0 mm of gap (sides/top-bottom).
   The bezel uses the 1-notch size, which fit on the car. Already done.
2. `stl/fit_test_mount_driver.stl` (about 20 minutes, two small flat tabs). Bolt the taller
   tab to the arm (holes 1 and 4) and the shorter one to the aiming pad (both holes).
   The bolts should go through snugly without forcing. Already done: the spacing fit.
3. `stl/fit_test_blade_driver.stl` (about 40 minutes, one strip; supports on, since it
   follows the door's lip). Slide it in under the front of the headlight cover like the
   stock bezel, and check the tongue clicks onto the clip and the lip sits down on it at
   both ends.
4. `stl/carrier_driver.stl` and `stl/bezel_driver.stl`, then the passenger pair. Wait for
   the measurements on `diagrams/measure_stock_bezel.png` before printing the bezel. It
   prints upside down, standing on its top blade (tipped so the blade lies as flat as it
   can). Turn supports on for the blade ends, the shelf, the lip and the tabs under the
   front.
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
- 2 × M4 × 16 and 2 × M4 × 12 self-tapping screws for the bezel

## Fitting

1. With the headlight door up, hold the carrier in front of the arm and the pad. Push the bolts
   through from behind the arm (holes 1 and 4) and the pad (both holes), then through the
   carrier's slots, and add the flange nuts on the front. Leave them finger tight.
2. If there's a gap at the arm or the pad, fill it with spacer washers.
3. Bolt the pods on through the floor slots. Slide them forward or back so the lenses sit
   where you want them in the opening, then tighten.
4. Slide the bezel's top blade in under the front of the headlight cover until the tongue
   clicks onto the clip, like the stock bezel. Then screw it on: two screws up through the tabs
   under the front and one through each wing. If the lenses sit too far back behind the
   posts, slide the pods forward in their slots to meet it.
5. Cycle the lights slowly by hand with the motor knob and check nothing touches the door
   or the body, then tighten everything.
6. Aim the lights with the stock adjusters.

## Changing the design

Every dimension is a setting at the top of `generate.py`. Change a number, run
`python3 generate.py`, then `python3 check.py`. It needs the `manifold3d`, `trimesh`,
`numpy` and `matplotlib` Python packages.
