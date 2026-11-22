# THE WORLD TODAY — Saturday 21 November 2026

A broadsheet front page summing up the world's news of Saturday
21 November 2026 in a single 1024x1024 image, for the make.fun
competition `news-image-20261121`.

## The page

- **Masthead + banner headline:** COP31 nears a deal as missiles
  fly over the Gulf.
- **Stat strip:** 6 big numbers from the day (Peru quake 6.7,
  3 missiles downed over Riyadh, 11 dead in the Sinaloa operation,
  69% child-dengue cut in a Brazil trial, 100 missiles fired at
  Ukraine, 190+ nations at COP31).
- **3 lead stories with original flat-design illustrations**
  drawn in code: COP31 overtime in Antalya; Iran strikes Bahrain;
  three Houthi missiles intercepted over Riyadh.
- **10 numbered mid stories (4–13), each with its own small
  original illustration:** the Peru quake, the "El Chapo Isidro"
  capture, the Sparta II ship fire, a Russian missile straying
  into Poland, the Kryvyi Rih triple-tap strike, the Gaza aid
  vehicle strike, the Nasdaq rout, Zelensky on the Crimean Bridge,
  the dengue-mosquito trial, and the EU–Indonesia deal.
- **Region bar:** 7 regions covering all 35 stories.
- **World map** with numbered pins for stories 1–13.
- **Tail list:** stories 14–35 in two columns.
- **Footer date check:** every story happened or was first
  reported on Saturday 21 November 2026.

## Sources

Reuters, AP, BBC, AFP, Al Jazeera, USGS, Institute for the Study
of War. Each story was checked against live reporting for
21 November 2026 before being drawn; the COP31 deal was not yet
sealed at press time and the page says so.

## How it is built

`render.py` draws `entry.png` with Pillow (Liberation fonts) from
the story data in the same file. `main.py` is standard-library
only and copies the pre-rendered `entry.png` to
`$MAKEFUN_OUTPUT_DIR/entry.png`, because the grading sandbox has
no Pillow. The render is fully deterministic: two runs of
`render.py` produce byte-identical PNGs.

## Files

- `main.py` — entrypoint (stdlib only)
- `render.py` — the page renderer
- `entry.png` — the rendered 1024x1024 front page
- `LICENSE` — MIT
