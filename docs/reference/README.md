# Reference build: Paw Playlists

<p align="center"><img src="paw-playlists.gif" alt="Paw Playlists hero: a dog, bird, frog, hamster and cat slide in from the edges, blink, sing together with drifting music notes, then all look surprised" width="560"></p>

[▶ Watch the full 18 s clip with sound](paw-playlists.mp4) · [poster frame](paw-playlists-poster.jpg)

An earlier agent built this hero for a pet-playlist brief. It is the **quality bar** for the storybook / mascot
register: study it, don't clone it. A new brief gets a new cast, a new palette and a new composition.

## Why it works

| Move | What happens | Why it lands |
|---|---|---|
| Edge bleed | Characters are big and cropped by the viewport: a dog head from the left, a bird from the right, a frog mid-leap | The page feels like a window into a world, not a row of stickers |
| Staggered entrances | Each character slides in from its own edge, one beat apart, then the headline types on | One thing to watch per beat |
| Acting faces | Same pose, the face changes: neutral → blink → sing → surprised | A face swap reads as acting; a whole-pose swap reads as a slideshow |
| Chorus beat | Everyone sings at once and music notes drift up | The page has a moment, not just a loop |
| Shared reaction | The whole cast reacts together | It answers the visitor |
| Generated art | Flat pastel fills, thick dark outline, blush cheeks, no SVG characters | Illustrated cutouts never look like clip-art |

## Build one like it

- Register **D · Sunny** in `tools/brief.py` / `tools/treatments.py`.
- Cast and cutouts: `recipes/character-scene/` and `tools/cast_cut.py`.
- Acting faces: generate the neutral pose first, then make each expression by *editing that same image*, so
  the body stays pixel-identical and only the face changes.

Reference made by Swapnil Agrawal (BDS intern) with her agent.
