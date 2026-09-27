# C5 sleepy-eye pod carrier and shroud (v1, first fit)

For a 2000 C5 Corvette with the headlight door stops already fitted, holding three
2.9 × 1.8 in dual-lens LED pods per side. Like the KnightDriveTV kit, each side is one
carrier that bolts where the stock headlight unit bolted, plus a front shroud that
frames the three pods. The geometry is an original design; see
`../notes/c5-sleepy-eye-video.md` for the install video notes it follows.

![assembly preview](preview/assembly.png)

## What's measured and what's estimated

| Dimension | Value | Source |
|---|---|---|
| Pod size (W × H × D) | 73.7 × 45.7 × 71.1 mm (2.9 × 1.8 × 2.8 in) | the pods' product listing |
| Pod bracket bolt | M8 or 5/16 in, in a 24 mm fore-aft slot | photos; the slot absorbs the difference |
| Mounting wall, behind the pod faces | 95 mm | **estimate** |
| Stock headlight bolt positions | **not published anywhere** | the wall is left blank to drill (see below) |

No public source gives the C5 headlight mounting bolt spacing, so the carrier has a solid
**mounting wall** behind the pods. You drill it to match your car.

## Print list

From `stl/`, already oriented for printing:

- `carrier_driver.stl` and `carrier_passenger.stl` (284 × 92 × 75 mm): they stand on the back of the wall.
- `shroud_driver.stl` and `shroud_passenger.stl` (256 × 72 × 27 mm): face down.

`stl/split/` has the same parts cut in two with splice plates, in case you ever need to
print on a smaller bed.

Print `stl/fit_test_window.stl` first (about 15 minutes). Your pod's face should drop
through the window with a little play.

**Material:** ASA or ABS is best, since it sits near hot LEDs behind the grille; PETG
works. Don't use PLA, which softens in a hot engine bay. Use 4 walls, 40% gyroid
infill, and 6 top and bottom layers.

## Hardware (per side)

- 3 × the bolts that came with the pods' brackets, with washers and nylon lock nuts,
  through the floor slots
- The stock headlight bolts and nuts, into the holes you drill in the mounting wall
- 2 × M4 × 16 self-tapping screws, shroud tabs into the carrier bosses
- Split version only: 4 × M4 × 12 flat-head screws and nylon lock nuts for the floor splice,
  4 × M4 × 16 pan-head screws and nylon lock nuts for the wall splice, and epoxy (or acetone
  for ABS/ASA) for the shroud splice strip

## Fitting it

1. Bolt the three pods to the carrier floor through the slots, with lenses flush with the
   front edge, and feed the pigtails through the holes in the wall.
2. Take the stock headlight unit you removed. Hold its mounting tabs against the back
   of the carrier's wall with its lens lined up with the pod row. Mark the holes, then
   drill 6.5 mm.
3. Bolt the carrier in exactly as the video does: the two outer bolts, then the inner
   stud through the upper hole of the aiming pad, then the 10 mm nut on the up/down
   adjuster.
4. Cycle the lights and check the pods clear the door and bodywork all the way up and down.
5. Screw the shroud on from underneath with the two M4 screws.
6. Aim the lights with the stock adjusters.

## Changing the design

Every dimension is a setting at the top of `generate.py`. Change a number, then run
`python3 generate.py`; it needs the `manifold3d`, `trimesh`, `numpy` and `matplotlib`
Python packages. Once the stock bolt positions are measured, put them in
`mount_holes` and the holes come pre-drilled.
