# Preview and render tools

For trying bezel changes quickly, without the 10-minute full build.

```sh
cd c5-shroud/tools
BEZEL_STYLE=P3J BEZEL_H=0.5 python3 preview_style.py   # coarse bezel, ~3-4 min -> viewer/style_P3J/
BEZEL_STYLE=P3J python3 proj_parts.py                  # projector stand-ins, lenses, bracket + clash check
BEZEL_STYLE=P3J python3 quickchk.py                    # one piece? print split OK? misalignment clash? bracket clash?
BEZEL_STYLE=P3J python3 vischk.py                      # the stand-ins don't poke through the bezel
```

Every number those print should be 0.00 mm3 (or "1 piece", "[1, 1]", dowel wall 1.00). Then
the real checks run on the full build: `python3 bezel_sdf.py` (BEZEL_STYLE set), then
`LIGHTS=projectors BEZEL_STYLE=P3J python3 generate.py` and `... check.py` from `c5-shroud/`.
The only expected fail is "the door's lip sits on the top rail" (a known 0.4 mm gap).

Run at most two preview builds at once: five at once ran the machine out of memory.

## Renders

Serve `viewer/` and screenshot with Playwright (Chromium is at /opt/pw-browsers/chromium):

```sh
cd c5-shroud/tools/viewer && python3 -m http.server 8799 --bind 127.0.0.1 &
VIEW=view.html node viewshot.js "/path/out.png|dir=style_P3J&side=passenger&satin=1&podcol=0b0b0d&drl=1&drlcol=f4f9ff&drlglow=1.8&carcol=1c1d20&cover=0&pos=-60,40,700&tgt=-10,30,0&fov=26"
```

Useful parameters: `satin=1` or `gloss=1` (bezel finish), `glass=1` (dark lenses instead of lit
ones), `drlcol=ff5a00&drlglow=0.6` (amber), `bg=07090c` (night). Camera: `pos` and `tgt` in the
viewer's frame (x = -model x, y = model z, z = model y); head on is `pos=-60,40,700`, three-quarter
`pos=-420,190,360&tgt=-10,30,-20`, fender side `pos=-560,120,-40&tgt=-60,28,-50`. Keep `cover=0`: the
pop-up door mesh comes from a third-party car scan and isn't in the repo.
