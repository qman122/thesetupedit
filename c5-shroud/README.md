# C5 sleepy-eye pod carrier and shroud (v3)

For a 2000 C5 Corvette with the headlight door stops already fitted, holding three
3.0 × 1.8 in dual-lens LED pods per side. Like the KnightDriveTV kit, each side is one
carrier that bolts to the stock headlight mounting points (the fender-side arm and the
hood-side aiming pad), plus a front shroud that frames the three pods. The geometry is an
original design; see `../notes/c5-sleepy-eye-video.md` for the install video notes it follows.

![assembly preview](preview/assembly.png)
![mounting tabs from behind](preview/rear.png)

Assembly diagrams: `diagrams/exploded.png`, `diagrams/front.png`, `diagrams/rear.png`, `diagrams/side.png`.

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
| F | Front opening width | 11 in (279.4 mm) | shroud is 269.4 mm, 5 mm clear each side |
| — | Shroud windows | pod face + 2.3 mm left/right and + 1.3 mm top/bottom, centred 0.3 in up for the bracket lift | the 4-notch test frame fit but wanted a bit wider and a bit shorter |
| — | Pods | 3.0 × 1.8 in face, 1.8 in deep, 2.1 in tall with the bracket (maker's drawing) | pod slots: 22 mm forward, 10 mm back |
| — | Pod stud | about 8 mm (5/16 in), in 8.6 mm floor slots | — |
| — | Mounting bolts | M6 × 1.0, 10 mm flange nuts | — |

**Still estimated:** how far back the mounting wall sits behind the pod faces (95 mm) and
the pod height relative to the holes (arm hole 4 is 14 mm above the carrier floor). The
long pod slots and the shroud's slotted tabs take up the fore-aft part of that.

## The curve

The three pods follow the curve of the headlight opening instead of sitting in a straight
line. The middle pod faces straight ahead, and the two outer pods sit about 6 mm further
back and turn outward by 8° (`pod_arc_deg` in `generate.py`; 0 makes the row straight).

- **Carrier:** a beam under the pods with a pocket for each pod's bracket foot. Each pocket
  is turned to match its pod, so the pods sit square on the curve. Each pod still slides
  straight fore and aft in its slot (16 mm forward, 10 mm back). Angled knees at each end
  run back to the arm and pad tabs.
- **Bezel:** the face has one flat panel per pod, angled with the curve. Each window and its
  cell are square to their pod.

## The bezel

The front piece is a full bezel, not just a frame. Its edge wraps back 78 mm on the top,
bottom and both sides, so with the door up you see only the bezel face and the three
lenses. The carrier, bolts and pocket stay hidden. The back is open for the wiring and
stops 3.5 mm short of the mounting nuts.

- **Cells:** each window has its own 12 mm deep sleeve around the pod bezel, so every lens
  sits in its own recess and the gaps between the pods are hidden. The carrier's locating
  ribs stop behind the cells.
- **Mounting:** four M4 × 16 self-tapping screws. Two go up through the front tabs into
  bosses under the carrier floor, and two go up through the bottom wall into posts at the
  back of the floor. All four holes are 16 mm slots, so the bezel can slide forward
  (never back) to follow the pods if you move them forward.
- **Sealing to the door:** the top has a 10 mm wide, 1 mm deep recess. Stick a strip of
  adhesive foam weatherstrip in it (about 10 mm wide, thick enough to touch the underside
  of the door) to close the last gap. The gap between the bezel and the door wasn't
  measured, so the foam takes it up.
- **Fit on the car:** it's 269 mm wide in the 279 mm opening. Cycle the door slowly by hand
  and check the wrap doesn't touch anything inside the pocket.

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

`python3 check.py` runs 40 checks. They all pass:

- The hole spacing matches A, H, B and D.
- Every slot is open, with solid material past its ends.
- A 15 mm flange nut at either end of every slot clears the carrier and the pods.
- The pods clear the carrier across their whole slot travel, and there's always at least
  7 mm behind them for the wiring.
- The pods clear the shroud, which clears the carrier.
- The shroud fits the opening.
- The carrier stays clear of the arm's pivot bolt and the pad's square adjuster, and the
  middle of the back is open.
- The driver part is a true mirror of the passenger part.
- Every STL is one watertight solid lying flat on the bed.

The small-bed split files were dropped: the curved bezel doesn't split cleanly, and bed size isn't a concern for this build.

## Print order

1. `stl/fit_test_window.stl` (about 15 minutes).
      Now three frames, 1-3 notches: 2.0/1.6, 2.3/1.3 and 2.6/1.0 mm of gap (sides/top-bottom).
   The shroud uses the 2-notch size.
2. `stl/fit_test_mount_driver.stl` (about 20 minutes, two small flat tabs). Bolt the taller
   tab to the arm (holes 1 and 4) and the shorter one to the aiming pad (both holes).
   The bolts should go through snugly without forcing.
3. `stl/carrier_driver.stl` and `stl/bezel_driver.stl`, then the passenger pair. The bezel prints face down.
4. `stl/spacer_washers.stl`: only if a tab doesn't sit flat against the arm or the pad.

**Material:** ASA or ABS is best; PETG works. Don't use PLA, which softens in a hot engine
bay. Use 4 walls, 40% gyroid infill, and 6 top and bottom layers.

## Hardware (per side)

- 4 × M6 × 1.0 × 20 mm bolts and 10 mm flange nuts (the stock headlight bolts work), with a flat
  washer under each nut so it doesn't dig into the plastic. The nut can't pull through: the slots
  are 6.3 mm wide and an M6 nut is 10 mm across.
- 3 × M6 bolts, washers and nylon lock nuts for the pods, through the floor slots
- 4 × M4 × 16 self-tapping screws for the bezel
- Adhesive foam weatherstrip, about 10 mm wide, for the top of the bezel

## Fitting

1. With the headlight door up, hold the carrier in front of the arm and the pad. Push the bolts
   through from behind the arm (holes 1 and 4) and the pad (both holes), then through the
   carrier's slots, and add the flange nuts on the front. Leave them finger tight.
2. If there's a gap at the arm or the pad, fill it with spacer washers.
3. Bolt the pods on through the floor slots. Slide them forward or back so the lenses sit
   where you want them in the opening, then tighten.
4. Screw the shroud on from underneath. Its slotted tabs follow the pods forward or back.
5. Cycle the lights slowly by hand with the motor knob and check nothing touches the door
   or the body, then tighten everything.
6. Aim the lights with the stock adjusters.

## Changing the design

Every dimension is a setting at the top of `generate.py`. Change a number, run
`python3 generate.py`, then `python3 check.py`. It needs the `manifold3d`, `trimesh`,
`numpy` and `matplotlib` Python packages.
