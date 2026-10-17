# HandsOn project website

Live homepage: https://llltttwww.github.io/HandsOn-website/

A buildless research project page. Serve `dist/` with any static HTTP server:

```sh
python3 -m http.server 8765 --directory dist
```

## Publishing

GitHub Pages publishes the `docs/` directory on `main`. It is a byte-for-byte copy
of `dist/`, prepared by `python3 tools/prepare-pages.py` before each publication.
All assets use relative paths so the site works under the project URL above.
The canonical and social sharing URLs in `dist/index.html` point to that URL.
The homepage has its own public repository; the benchmark repository is separate.

## Content and provenance

`dist/index.html`, `style.css`, and `app.js` contain the page. The task catalog is
`dist/assets/tasks.json`. All media are local; the page needs no third-party CDN,
analytics, database, or build service. Core-50 and Transfer-16 results follow the
manuscript; DP is reported separately with its comparison caveat.

The page follows the conventional structure of research project pages such as
RoboCasa and Nerfies, without copying their code or media.

The opening figure retains the author's requested tall composition, natural arm
pose. The dangling cable beside the leftmost freestanding hand is removed.
Its source image is `dist/assets/handson-overview.jpg`
(SHA-256 `0faca42c35d1d03a4f1ec6dc3809dc69ae7855f052dfca9c0f57b8b96d6e2d4f`).
The responsive WebP files and social card derive from this image. It is intentionally
independent of the current paper's first figure.

The author block and download PDF follow the current author-approved arXiv
manuscript, revision `9dd5e12dd6896eea13b95b95b4f9d50ad5c92b1f`. The PDF has 47 pages.
The download is the compiled manuscript, with the approved HandsOn logo in the overview
and the vector NatureWill wordmark at the lower-right of the first-page title information block.
The NatureWill affiliation remains ordinary text.
All extracted text is verified exactly unchanged against the manuscript before the company-logo addition. Details and hashes are in `tools/paper-source.json`.
Author order, affiliations, and contribution markers are in `tools/author-source.json`.
The BibTeX citation remains unchanged.

The overview film (`dist/assets/overview.mp4`) is rendered from the `FilmV2` composition of
the separately maintained film project (`dexomni-film`, deliverable `out/HandsOn_film_web.mp4`)
and re-encoded for the page at 1280 px; its poster is the title card at 16.8 s. Source,
encode settings and hashes are in `tools/video-source.json`. Its wording follows the
current manuscript and this page, including the conclusion that instruction grounding and
physical contact both matter, and regression controls for demonstration count and duration.

`tools/film-copy.ts` is the copy of the earlier line-art cut (`Film` composition), kept for
reference; editing it does not change the published film.

## Updating

Use an explicitly verified manuscript checkout and freshly compiled PDF:

```sh
python3 tools/sync-authors.py /path/to/current/root.tex --revision VERIFIED_COMMIT
python3 tools/update-paper.py --source /path/to/current/root.pdf --revision VERIFIED_COMMIT
python3 tools/prepare-social.py --font /path/to/sans-font.ttf
```

`prepare-assets.py` is for a complete media refresh. Pass the source film project
and video cards directory explicitly, alongside the verified manuscript and film:

```sh
python3 tools/prepare-assets.py \
  --project-root /path/to/workspace \
  --film-root /path/to/film-project \
  --cards-dir /path/to/video-cards \
  --ffmpeg /path/to/ffmpeg \
  --manuscript-root /path/to/current/manuscript \
  --overview-video /path/to/reviewed/film.mp4 \
  --paper-pdf /path/to/current/root.pdf \
  --paper-revision VERIFIED_COMMIT
```

The workspace must contain `handson-release/`. The film project supplies
`public/fonts/InterTight-normal-200_900.woff2` and `public/img/rerender_{a,b,c,d}.png`.
The cards directory supplies `manifest.json`; relative `src` entries resolve
against that directory. If a source is unavailable, the script uses the matching
`sim_hammer.mp4` or `sim_spoon.mp4` in the cards directory.

The script regenerates website media but does not modify the source manuscript,
simulation assets, or video project. The explicit inputs prevent silently
selecting an old cached manuscript or film.

## Validation

```sh
node tools/check-site.cjs
SITE_URL=https://llltttwww.github.io/HandsOn-website/ node tools/check-site.cjs
```

Requires Playwright and a browser. `PLAYWRIGHT_MODULE` and `BROWSER_PATH` may point
to existing installations. Checks cover the 66-task gallery, search, dialogs,
result tabs, citation copy, image loading, video playback, PDF download, and
mobile/tablet overflow. Review rendered PDF pages and changed film scenes before
publishing. `tools/qa/` is local-only and is not part of the public repository.
