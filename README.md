# DexOmni project website

Live homepage: https://llltttwww.github.io/DexOmni-website/

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
Its source image is `dist/assets/dexomni-overview.jpg`
(SHA-256 `aa73db0a9231e0cff494e62f656603f77c64995874b6a4793fe704391281b628`).
The responsive WebP files and social card derive from this image. It is intentionally
independent of the current paper's first figure.

The author block and download PDF follow the current author-approved arXiv
manuscript, revision `5c49d6c131b957b261dcd0e2441f573457727990`. The PDF has 47 pages.
Image compression reduces download size without changing layout or page count;
all extracted text is verified unchanged against the compiled manuscript. Details and hashes are in `tools/paper-source.json`.
Author order, affiliations, and contribution markers are in `tools/author-source.json`.
The BibTeX citation remains unchanged.

The overview film uses the corrected copy in `tools/film-copy.ts`. Its conclusion
recognizes instruction grounding as well as contact, coordination, and goal
maintenance. Its explanation of the performance gap describes regression controls
for demonstration count and duration. The source video project is maintained
separately; refresh its font subsets after applying copy changes and render the
`Film` composition at 30 fps, preserving the complete 120-second soundtrack.

## Updating

Use an explicitly verified manuscript checkout and freshly compiled PDF:

```sh
python3 tools/sync-authors.py /path/to/current/root.tex --revision VERIFIED_COMMIT
python3 tools/update-paper.py --source /path/to/current/root.pdf --revision VERIFIED_COMMIT
python3 tools/prepare-social.py --font /path/to/sans-font.ttf
```

`prepare-assets.py` is for a complete media refresh. It requires an explicit
current manuscript tree, reviewed film, current PDF, and source revision so it
cannot silently reintroduce the old cached manuscript or film. It does not modify
the source manuscript, simulation assets, or video project.

## Validation

```sh
node tools/check-site.cjs
SITE_URL=https://llltttwww.github.io/DexOmni-website/ node tools/check-site.cjs
```

Requires Playwright and a browser. `PLAYWRIGHT_MODULE` and `BROWSER_PATH` may point
to existing installations. Checks cover the 66-task gallery, search, dialogs,
result tabs, citation copy, image loading, video playback, PDF download, and
mobile/tablet overflow. Review rendered PDF pages and changed film scenes before
publishing. `tools/qa/` is local-only and is not part of the public repository.
