# Photoreal renders (Blender Cycles)

Product-shot renders straight from the CAD files: the real bezel geometry, the printed diffusers
glowing as the light line, modelled projectors (glass lens, smoked reflector bowl, cut-off shield),
satin black plastic, a dark studio (softbox, top strip, rim lights linked to the headlight only) and
a glossy floor that falls off into the dark.

```sh
python3 -m venv /tmp/bpyenv && /tmp/bpyenv/bin/pip install bpy     # Blender as a module (keep it out of the main env: it pins numpy 1.x)
cd c5-shroud/tools/photoreal
python3 prep.py P3R P3J P3V                 # geometry -> scene/<style>/ (COVER_JSON=... adds the pop-up door)
/tmp/bpyenv/bin/python render.py P3R 34 white out/P3R_34_white.png 100 128
python3 glow.py out/P3R_34_white.png out/P3R_34_white_glow.png
python3 sheet.py . P3R "TITLE" "subtitle" out/R.jpg   # needs the 34/white, front/white and hood34/amber shots
```

Shots: `34` (3/4 front, fender side), `front` (head on), `hood34` (3/4 from the hood side, the light
rig mirrored), `low`, `close`. Light line: `white`, `amber` or `off`. About 4 minutes a shot at
1800 x 1100 and 128 samples on 4 CPU cores. The door mesh comes from a third-party car scan and
isn't in the repo, so renders with it stay out of the repo too.
