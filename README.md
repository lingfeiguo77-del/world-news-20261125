# news-image-20261125 — Sum up 25 November's world news in one image

A program that draws a 1024×1024 PNG front page summing up Wednesday
25 November 2026's world news, using Pillow only. No network, no randomness,
no timestamps — two runs write byte-identical output.

## Run

```sh
python3 main.py
# writes /output/entry.png
```

Local testing with a different output path:

```sh
NEWS_IMAGE_OUTPUT=/tmp/entry.png python3 main.py
```

Requires Python 3.13 (also runs on 3.12) and Pillow.

## What's in the image

| # | Story |
|---|-------|
| 01 | Two oil tankers hit naval mines and catch fire in the Strait of Hormuz (IRGC statement) |
| 02 | Houthis hit Riyadh's tallest tower; 11 injured (Saudi civil defense) |
| 03 | Huawei convicted in US trial — trade-secret theft and bank fraud; racketeering cleared |
| 04 | Shenzhou-24 docks; a Pakistani astronaut becomes the first foreigner aboard Tiangong |

Footer ticker: US tariff proposal on 14 partners · Russia strikes Odesa (2 killed) ·
COP31 climate talks end without a deal.

Sources: Reuters, Just Security Early Edition (25 Nov 2026), Open Chronicle,
The Jerusalem Post, ECNS/Xinhua. See `TASKBOOK.md` for the full spec and sources.

## Files

- `main.py` — the program (entrypoint)
- `TASKBOOK.md` — the spec it was written from (no code)
- `fonts/` — DejaVu Sans / DejaVu Sans Bold (free license, bundled so the
  program does not depend on system fonts in the grading sandbox)
- `BUILD_LOG.md` — verification log
- `LICENSE` — MIT

## License

MIT. See `LICENSE`.
